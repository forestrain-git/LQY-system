#!/usr/bin/env python3
"""
初始化数据库脚本
Init Database Script

使用SQLite创建所有表
"""

import asyncio
import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db, close_db

# 导入所有模型以确保创建表
from app.modules.equipment.models import Equipment
from app.modules.workflow.models import WorkOrder
from app.modules.dispatch.models import Vehicle, Berth, Schedule
from app.modules.safety.models import SafetyAlert
from app.modules.ai.models import Conversation, Message


async def main():
    """初始化数据库"""
    print("正在初始化数据库...")

    try:
        await init_db()
        print("✅ 数据库初始化成功！")

        # 列出所有表
        from app.database import engine
        from sqlalchemy import inspect

        async with engine.connect() as conn:
            def get_tables(sync_conn):
                inspector = inspect(sync_conn)
                return inspector.get_table_names()

            tables = await conn.run_sync(get_tables)
            print(f"\n已创建 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
