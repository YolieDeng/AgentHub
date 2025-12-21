"""测试数据库连接"""
import psycopg2
from app.core.config import settings

try:
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        database=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
    )
    print("✅ 数据库连接成功！")

    # 测试 pgvector
    cur = conn.cursor()
    cur.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
    if cur.fetchone():
        print("✅ pgvector 扩展已启用！")
    else:
        print("❌ pgvector 扩展未启用，请在 Supabase SQL Editor 中执行: CREATE EXTENSION vector;")

    cur.close()
    conn.close()
except Exception as e:
    print(f"❌ 连接失败: {e}")