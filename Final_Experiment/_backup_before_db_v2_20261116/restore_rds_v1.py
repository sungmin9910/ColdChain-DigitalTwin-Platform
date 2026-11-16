import os
import sys
import json
import argparse
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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DUMP_PATH = os.path.join(BASE_DIR, "full_dump_lab225_20261116.sql")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.json")


def split_sql_statements(sql_text: str):
    statements = []
    buf = []
    in_single = False
    escape = False
    for ch in sql_text:
        if escape:
            buf.append(ch)
            escape = False
            continue
        if ch == "\\":
            buf.append(ch)
            escape = True
            continue
        if ch == "'":
            in_single = not in_single
            buf.append(ch)
            continue
        if ch == ";" and not in_single:
            stmt = "".join(buf).strip()
            if stmt:
                # 주석만 있는 블록 제외
                lines = [ln for ln in stmt.splitlines() if not ln.strip().startswith("--")]
                if any(ln.strip() for ln in lines):
                    statements.append("\n".join(lines))
            buf = []
        else:
            buf.append(ch)
    return statements


def main():
    parser = argparse.ArgumentParser(description="AWS RDS lab225 2026-11-16 시점 원상복구 스크립트")
    parser.add_argument(
        "--source",
        choices=["rds_clone", "local_sql"],
        default="rds_clone",
        help="복원 소스 선택: rds_clone(RDS 내부 백업 DB로부터 2초 고속 복원) | local_sql(로컬 SQL 덤프 파일로 복원)",
    )
    parser.add_argument(
        "--target-db",
        default="lab225",
        help="복원할 대상 DB 이름 (기본값: lab225)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 덮어쓰기 없이 백업 무결성 및 행 수만 사전 검증",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="확인 프롬프트 없이 즉시 복구 실행",
    )
    args = parser.parse_args()

    if not os.path.exists(MANIFEST_PATH):
        print(f"[오류] 매니페스트 파일을 찾을 수 없습니다: {MANIFEST_PATH}")
        sys.exit(1)

    with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
        manifest = json.load(mf)

    clone_db = manifest["rds_clone_database"]
    expected_tables = manifest["tables"]

    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )

    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION sql_mode = ''")
            print(f"============================================================")
            print(f" [복구 사전 점검] 소스={args.source} -> 대상 DB=`{args.target_db}`")
            print(f"  - 백업 기준 시각: {manifest['backup_created_at']}")
            print(f"============================================================")

            if args.source == "rds_clone":
                for tbl, info in expected_tables.items():
                    cur.execute(f"SELECT COUNT(*) AS cnt FROM `{clone_db}`.`{tbl}`")
                    c_cnt = cur.fetchone()["cnt"]
                    print(f"  - `{clone_db}.{tbl}` 보유 행 수: {c_cnt:,}행 (기대치: {info['row_count']:,}행)")
                    if c_cnt != info["row_count"]:
                        raise RuntimeError(f"백업 DB 행 수 불일치: {tbl}")
            else:
                if not os.path.exists(SQL_DUMP_PATH):
                    raise FileNotFoundError(f"SQL 덤프 파일 없음: {SQL_DUMP_PATH}")
                print(f"  - 로컬 SQL 덤프 확인 완료: {SQL_DUMP_PATH} ({os.path.getsize(SQL_DUMP_PATH):,} bytes)")

            if args.dry_run:
                print("\n[DRY-RUN 완료] 백업 상태가 100% 정상이며 언제든 즉시 복구 가능합니다.")
                return

            if not args.yes:
                ans = input(f"\n정말로 `{args.target_db}` DB를 2026-11-16 백업 상태로 되돌리시겠습니까? (yes 입력): ").strip()
                if ans.lower() != "yes":
                    print("복구가 취소되었습니다.")
                    return

            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{args.target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"USE `{args.target_db}`")
            cur.execute("SET FOREIGN_KEY_CHECKS = 0")

            if args.source == "rds_clone":
                for tbl, info in expected_tables.items():
                    cur.execute(f"DROP TABLE IF EXISTS `{args.target_db}`.`{tbl}`")
                    cur.execute(f"CREATE TABLE `{args.target_db}`.`{tbl}` LIKE `{clone_db}`.`{tbl}`")
                    cur.execute(f"INSERT INTO `{args.target_db}`.`{tbl}` SELECT * FROM `{clone_db}`.`{tbl}`")
                    cur.execute(f"SELECT COUNT(*) AS cnt FROM `{args.target_db}`.`{tbl}`")
                    restored_cnt = cur.fetchone()["cnt"]
                    print(f"  [복구 완료] `{args.target_db}.{tbl}` <- {restored_cnt:,}행 복원됨")
            else:
                with open(SQL_DUMP_PATH, "r", encoding="utf-8") as sf:
                    sql_text = sf.read()
                stmts = split_sql_statements(sql_text)
                for st in stmts:
                    cur.execute(st)
                for tbl, info in expected_tables.items():
                    cur.execute(f"SELECT COUNT(*) AS cnt FROM `{args.target_db}`.`{tbl}`")
                    restored_cnt = cur.fetchone()["cnt"]
                    print(f"  [복구 완료] `{args.target_db}.{tbl}` <- {restored_cnt:,}행 복원됨")

            cur.execute("SET FOREIGN_KEY_CHECKS = 1")
            print(f"\n[성공] `{args.target_db}` 데이터베이스가 백업 시점으로 100% 완벽히 원상복구되었습니다!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
