"""
Initial migration with dispatch and workflow models

Initial migration including vehicle, berth, schedule, staff, department, work order models

Revision ID: initial_migration_2026
Revises:
Create Date: 2026-04-07 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'initial_migration_2026'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema / 升级数据库结构"""

    # ============== 部门表 / Departments ==============
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_departments_code', 'departments', ['code'], unique=True)

    # ============== 人员表 / Staff ==============
    op.create_table(
        'staff',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('employee_no', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('role', sa.String(30), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(100), nullable=True),
        sa.Column('department_id', sa.Integer(), nullable=True),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('gps_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('badge_id', sa.String(50), nullable=True, unique=True),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_staff_employee_no', 'staff', ['employee_no'], unique=True)
    op.create_index('ix_staff_status', 'staff', ['status'])
    op.create_index('ix_staff_badge_id', 'staff', ['badge_id'], unique=True)

    # ============== 车辆表 / Vehicles ==============
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('license_plate', sa.String(20), nullable=False, unique=True),
        sa.Column('vehicle_type', sa.String(20), nullable=False),
        sa.Column('brand', sa.String(50), nullable=True),
        sa.Column('model', sa.String(50), nullable=True),
        sa.Column('max_capacity', sa.Float(), nullable=False, default=5.0),
        sa.Column('current_load', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('gps_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_mileage', sa.Float(), nullable=False, default=0.0),
        sa.Column('engine_hours', sa.Float(), nullable=False, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehicles_license_plate', 'vehicles', ['license_plate'], unique=True)
    op.create_index('ix_vehicles_status', 'vehicles', ['status'])

    # ============== 泊位表 / Berths ==============
    op.create_table(
        'berths',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('berth_type', sa.String(20), nullable=False),
        sa.Column('location_x', sa.Float(), nullable=True),
        sa.Column('location_y', sa.Float(), nullable=True),
        sa.Column('capacity_tons', sa.Float(), nullable=False, default=10.0),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('current_vehicle_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['current_vehicle_id'], ['vehicles.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_berths_code', 'berths', ['code'], unique=True)
    op.create_index('ix_berths_status', 'berths', ['status'])

    # ============== 调度表 / Schedules ==============
    op.create_table(
        'schedules',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('berth_id', sa.Integer(), nullable=True),
        sa.Column('appointment_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('expected_waste_type', sa.String(20), nullable=True),
        sa.Column('expected_weight', sa.Float(), nullable=True),
        sa.Column('queue_number', sa.Integer(), nullable=True),
        sa.Column('queue_entered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('checked_in_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('unloading_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('unloading_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('gross_weight', sa.Float(), nullable=True),
        sa.Column('tare_weight', sa.Float(), nullable=True),
        sa.Column('net_weight', sa.Float(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id']),
        sa.ForeignKeyConstraint(['berth_id'], ['berths.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_schedules_status', 'schedules', ['status'])
    op.create_index('ix_schedules_vehicle_id', 'schedules', ['vehicle_id'])

    # ============== 工单表 / Work Orders ==============
    # 注意: equipment_id 外键暂时注释，等待设备模块完成后添加
    # Note: equipment_id FK temporarily disabled until equipment module is ready
    op.create_table(
        'work_orders',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('order_no', sa.String(30), nullable=False, unique=True),
        sa.Column('order_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('planned_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('planned_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, index=True),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('satisfaction', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        # sa.ForeignKeyConstraint(['equipment_id'], ['devices.id']),  # 暂时禁用 / Temporarily disabled
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id']),
        sa.ForeignKeyConstraint(['creator_id'], ['staff.id']),
        sa.ForeignKeyConstraint(['assignee_id'], ['staff.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_work_orders_order_no', 'work_orders', ['order_no'], unique=True)
    op.create_index('ix_work_orders_status', 'work_orders', ['status'])

    # ============== 工单任务表 / Work Order Tasks ==============
    op.create_table(
        'work_order_tasks',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('work_order_id', sa.Integer(), nullable=False),
        sa.Column('task_no', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(200), nullable=False),
        sa.Column('assignee_id', sa.Integer(), nullable=True),
        sa.Column('standard_time_minutes', sa.Integer(), nullable=True),
        sa.Column('actual_time_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('result_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['work_order_id'], ['work_orders.id']),
        sa.ForeignKeyConstraint(['assignee_id'], ['staff.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema / 降级数据库结构"""

    # 按依赖关系逆序删除 / Delete in reverse dependency order
    op.drop_table('work_order_tasks')
    op.drop_table('work_orders')
    op.drop_table('schedules')
    op.drop_table('berths')
    op.drop_table('vehicles')
    op.drop_table('staff')
    op.drop_table('departments')
