import asyncpg
import asyncio

async def test_asyncpg_connection():
    try:
        conn = await asyncpg.connect(
            user='hwi',
            password='1234',
            host='localhost',
            port=5432,
            database='voca'
        )
        print("Connection successful!")
        await conn.close()
    except Exception as e:
        print("Connection failed:", e)

asyncio.run(test_asyncpg_connection())