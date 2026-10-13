import toml
import pymysql
import sys

sys.stdout.reconfigure(encoding='utf-8')

secrets = toml.load('Final_Experiment/4_APC_Coldchain_Dashboard/.streamlit/secrets.toml')
cfg = secrets['MySQL']

conn = pymysql.connect(
    host=cfg['MYSQL_HOST'], port=cfg['MYSQL_PORT'], user=cfg['MYSQL_USER'],
    password=cfg['MYSQL_PASSWORD'], database=cfg['MYSQL_DATABASE'],
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as c:
    c.execute("""
        SHOW VARIABLES WHERE Variable_name IN (
            'version_comment', 'innodb_buffer_pool_size', 'max_connections',
            'hostname', 'port'
        )
    """)
    vars_dict = {r['Variable_name']: r['Value'] for r in c.fetchall()}
    
    # DB 크기 계산
    c.execute("""
        SELECT SUM(data_length + index_length) / 1024 / 1024 as size_mb
        FROM information_schema.tables
        WHERE table_schema = %s
    """, (cfg['MYSQL_DATABASE'],))
    db_size = c.fetchone()['size_mb']
    
conn.close()

buffer_pool_mb = int(vars_dict.get('innodb_buffer_pool_size', 0)) / (1024 * 1024)
max_conn = int(vars_dict.get('max_connections', 0))

print("=== AWS RDS 상세 사양 및 요금 분석 ===")
print(f"호스트: {cfg['MYSQL_HOST']}")
print(f"버퍼 풀: {buffer_pool_mb:.1f} MB")
print(f"최대 연결 수: {max_conn}")
print(f"실제 데이터 저장량: {db_size:.2f} MB")

# 인스턴스 타입 추정
# db.t3.micro: RAM 1GB -> buffer_pool 약 300~500MB, max_connections 약 60~90
# db.t4g.micro: RAM 1GB -> buffer_pool 약 300~500MB, max_connections 약 60~90
# db.t3.small: RAM 2GB -> buffer_pool 약 1000~1300MB
if buffer_pool_mb < 700:
    instance_type = "db.t3.micro 또는 db.t4g.micro (1 vCPU, 1 GiB RAM)"
    free_tier_eligible = True
    estimated_cost_usd = 0.0 if free_tier_eligible else 18.0  # 프리티어 시 0원, 만료 시 월 약 18~20달러 (시간당 $0.026)
elif buffer_pool_mb < 1500:
    instance_type = "db.t3.small 또는 db.t4g.small (2 vCPU, 2 GiB RAM)"
    free_tier_eligible = False
    estimated_cost_usd = 36.0 # 월 약 35~40달러
else:
    instance_type = f"상위 인스턴스 (버퍼풀 {buffer_pool_mb:.0f}MB)"
    free_tier_eligible = False
    estimated_cost_usd = 70.0

print(f"추정 인스턴스 타입: {instance_type}")
print(f"프리티어(Free Tier) 대상 여부: {free_tier_eligible}")
