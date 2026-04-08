"""
Add equipment foreign key constraint

Revision ID: 2026_04_08_0900
Revises: 2026_04_07_2000
Create Date: 2026-04-08 09:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026_04_08_0900'
down_revision = '2026_04_07_2000'
branch_labels = None
depends_on = None


def upgrade():
    """
    升级：添加equipment外键约束
    """
    # 检查外键约束是否已存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 获取work_orders表的外键
    foreign_keys = inspector.get_foreign_keys('work_orders')
    fk_names = [fk['name'] for fk in foreign_keys]

    # 添加外键约束（如果不存在）
    if 'fk_work_orders_equipment_id' not in fk_names:
        with op.batch_alter_table('work_orders', schema=None) as batch_op:
            batch_op.create_foreign_key(
                'fk_work_orders_equipment_id',
                'equipment',
                ['equipment_id'],
                ['id'],
                ondelete='SET NULL'
            )
        print("✅ 已添加equipment外键约束")
    else:
        print("⚠️ 外键约束已存在，跳过")


def downgrade():
    """
    降级：移除equipment外键约束
    """
    with op.batch_alter_table('work_orders', schema=None) as batch_op:
        batch_op.drop_constraint('fk_work_orders_equipment_id', type_='foreignkey')

    print("✅ 已移除equipment外键约束")
