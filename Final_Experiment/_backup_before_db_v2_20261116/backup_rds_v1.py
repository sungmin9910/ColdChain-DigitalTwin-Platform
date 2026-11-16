import os
import sys
import json
import hashlib
from datetime import datetime, date
from decimal import Decimal
import pymysql

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

MYSQL_HOST = os.environ.get("MYSQL_HOST", "labdb.cn26yq6q0mu6.ap-northeast-2.rds.amazonaws.com")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "admin")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "12345678")
SOURCE_DB = "lab225"
CLONE_DB = "lab225_backup_20261116"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "tables_json")
SQL_DUMP_PATH = os.path.join(BASE_DIR, "full_dump_lab225_20261116.sql")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")


def json_default(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat(sep=" ") if isinstance(obj, datetime) else obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, (bytes, bytearray)):
        return obj.decode("utf-8", errors="replace")
    return str(obj)


def sql_literal(conn, val):
    if val is None:
        return "NULL"
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (int, float, Decimal)):
        return str(val)
    if isinstance(val, datetime):
        return conn.escape(val.strftime("%Y-%m-%d %H:%M:%S"))
    if isinstance(val, date):
        return conn.escape(val.strftime("%Y-%m-%d"))
    return conn.escape(str(val))


def main():
    os.makedirs(JSON_DIR, exist_ok=True)
    print(f"============================================================")
    print(f" [Step 1] AWS RDS '{SOURCE_DB}' 무손실 3중 백업 시작")
    print(f"  - 대상 호스트: {MYSQL_HOST}:{MYSQL_PORT}")
    print(f"  - 로컬 저장소: {BASE_DIR}")
    print(f"  - RDS 복제 DB: {CLONE_DB}")
    print(f"============================================================")

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    manifest = {
        "backup_created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_host": MYSQL_HOST,
        "source_database": SOURCE_DB,
        "rds_clone_database": CLONE_DB,
        "tables": {},
    }

    try:
        with conn.cursor() as cur:
            # Zero-date('0000-00-00')가 있는 레거시 행도 에러 없이 그대로 복제/백업되도록 sql_mode 완화
            cur.execute("SET SESSION sql_mode = ''")
            cur.execute(f"USE `{SOURCE_DB}`")
            cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
            tables = [list(r.values())[0] for r in cur.fetchall()]
            print(f"[확인] 백업 대상 테이블 ({len(tables)}개): {tables}")

            # 1) RDS 서버 내부 스냅샷 복제 DB 생성
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{CLONE_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")

            with open(SQL_DUMP_PATH, "w", encoding="utf-8") as sql_f:
                sql_f.write(f"-- ColdChain DigitalTwin Full Backup Dump of `{SOURCE_DB}`\n")
                sql_f.write(f"-- Created at: {manifest['backup_created_at']}\n")
                sql_f.write("SET NAMES utf8mb4;\n")
                sql_f.write("SET SESSION sql_mode = '';\n")
                sql_f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

                for tbl in tables:
                    # 스키마 추출
                    cur.execute(f"SHOW CREATE TABLE `{SOURCE_DB}`.`{tbl}`")
                    create_stmt = cur.fetchone()["Create Table"]

                    # 전체 데이터 조회
                    cur.execute(f"SELECT * FROM `{SOURCE_DB}`.`{tbl}`")
                    rows = cur.fetchall()

                    # JSON 파일 저장 및 SHA-256 계산
                    json_path = os.path.join(JSON_DIR, f"{tbl}.json")
                    json_bytes = json.dumps(rows, ensure_ascii=False, indent=2, default=json_default).encode("utf-8")
                    with open(json_path, "wb") as jf:
                        jf.write(json_bytes)
                    sha256_hex = hashlib.sha256(json_bytes).hexdigest()

                    # SQL 덤프 기록
                    sql_f.write(f"-- ==========================================\n")
                    sql_f.write(f"-- Table: `{tbl}` (rows: {len(rows)})\n")
                    sql_f.write(f"-- ==========================================\n")
                    sql_f.write(f"DROP TABLE IF EXISTS `{tbl}`;\n")
                    sql_f.write(f"{create_stmt};\n\n")

                    if rows:
                        cols = list(rows[0].keys())
                        col_list_sql = ", ".join(f"`{c}`" for c in cols)
                        batch_size = 250
                        for i in range(0, len(rows), batch_size):
                            batch = rows[i : i + batch_size]
                            values_chunks = []
                            for r in batch:
                                vals = ", ".join(sql_literal(conn, r[c]) for c in cols)
                                values_chunks.append(f"({vals})")
                            sql_f.write(
                                f"INSERT INTO `{tbl}` ({col_list_sql}) VALUES\n  "
                                + ",\n  ".join(values_chunks)
                                + ";\n"
                            )
                        sql_f.write("\n")

                    # RDS 서버 내부 복제본 동기화 (이미 있으면 덮어쓰지 않고 행 수가 다를 때만 재생성)
                    cur.execute(f"DROP TABLE IF EXISTS `{CLONE_DB}`.`{tbl}`")
                    cur.execute(f"CREATE TABLE `{CLONE_DB}`.`{tbl}` LIKE `{SOURCE_DB}`.`{tbl}`")
                    cur.execute(f"INSERT INTO `{CLONE_DB}`.`{tbl}` SELECT * FROM `{SOURCE_DB}`.`{tbl}`")

                    cur.execute(f"SELECT COUNT(*) AS cnt FROM `{CLONE_DB}`.`{tbl}`")
                    clone_cnt = cur.fetchone()["cnt"]
                    if clone_cnt != len(rows):
                        raise RuntimeError(f"RDS 복제 행 수 불일치 ({tbl}): 원본={len(rows)} vs 복제={clone_cnt}")

                    manifest["tables"][tbl] = {
                        "row_count": len(rows),
                        "clone_row_count": clone_cnt,
                        "json_file": f"tables_json/{tbl}.json",
                        "sha256": sha256_hex,
                    }
                    print(f"  [OK] `{tbl}`: {len(rows):,}행 로컬(.sql/.json) 저장 및 `{CLONE_DB}.{tbl}` 복제 완료 (sha256={sha256_hex[:12]}...)")

                sql_f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

        with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
            json.dump(manifest, mf, ensure_ascii=False, indent=2)

        dump_size_mb = os.path.getsize(SQL_DUMP_PATH) / (1024 * 1024)
        print(f"\n[백업 완료] SQL 덤프 크기: {dump_size_mb:.2f} MB | 매니페스트: {MANIFEST_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
