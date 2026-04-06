"""设备API路由

提供设备的CRUD操作和查询功能
"""

from datetime import date, datetime, time, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Device, DeviceStatus, SensorData
from app.schemas import (
    DeviceCreate,
    DeviceResponse,
    DeviceUpdate,
    ListResponse,
    Pagination,
    ResponseBase,
    SensorDataResponse,
)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("", response_model=ResponseBase[DeviceResponse], status_code=status.HTTP_201_CREATED)
async def create_device(
    data: DeviceCreate,
    session: AsyncSession = Depends(get_session),
) -> ResponseBase[DeviceResponse]:
    """创建设备

    检查名称是否已存在，存在则返回409 Conflict
    """
    # 检查名称是否已存在
    result = await session.execute(select(Device).where(Device.name == data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="设备名称已存在",
        )

    device = Device(**data.model_dump())
    session.add(device)
    await session.commit()
    await session.refresh(device)

    return ResponseBase(code=0, message="success", data=DeviceResponse.model_validate(device))


@router.get("", response_model=ListResponse[List[DeviceResponse]])
async def list_devices(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    status: str | None = Query(None, description="状态过滤，逗号分隔多个状态"),
    type: str | None = Query(None, description="类型过滤，逗号分隔多个类型"),
    name: str | None = Query(None, description="名称模糊搜索"),
    session: AsyncSession = Depends(get_session),
) -> ListResponse[List[DeviceResponse]]:
    """获取设备列表

    支持分页、状态过滤、类型过滤和名称搜索
    """
    # 构建查询
    query = select(Device).where(Device.status != DeviceStatus.DISABLED)

    # 状态过滤
    if status:
        status_list = [s.strip() for s in status.split(",")]
        query = query.where(Device.status.in_(status_list))

    # 类型过滤
    if type:
        type_list = [t.strip() for t in type.split(",")]
        query = query.where(Device.type.in_(type_list))

    # 名称模糊搜索
    if name:
        query = query.where(Device.name.ilike(f"%{name}%"))

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # 排序和分页
    query = query.order_by(Device.updated_at.desc()).offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    devices = result.scalars().all()

    pages = (total + size - 1) // size

    return ListResponse(
        code=0,
        message="success",
        data=[DeviceResponse.model_validate(d) for d in devices],
        pagination=Pagination(page=page, size=size, total=total, pages=pages),
    )


@router.get("/{device_id}", response_model=ResponseBase[DeviceResponse])
async def get_device(
    device_id: int,
    session: AsyncSession = Depends(get_session),
) -> ResponseBase[DeviceResponse]:
    """获取单个设备详情

    包含最新的传感器数据
    """
    result = await session.execute(
        select(Device).where(Device.id == device_id, Device.status != DeviceStatus.DISABLED)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在",
        )

    # 获取最新传感器数据
    sensor_result = await session.execute(
        select(SensorData)
        .where(SensorData.device_id == device_id)
        .order_by(SensorData.timestamp.desc())
        .limit(1)
    )
    latest_sensor_data = sensor_result.scalar_one_or_none()

    response_data = DeviceResponse.model_validate(device)
    if latest_sensor_data:
        response_data.latest_sensor_data = SensorDataResponse(
            id=latest_sensor_data.id,
            device_id=latest_sensor_data.device_id,
            temperature=latest_sensor_data.temperature,
            vibration=latest_sensor_data.vibration,
            current=latest_sensor_data.current,
            timestamp=latest_sensor_data.timestamp,
            device_name=device.name,
        )

    return ResponseBase(code=0, message="success", data=response_data)


@router.put("/{device_id}", response_model=ResponseBase[DeviceResponse])
async def update_device(
    device_id: int,
    data: DeviceUpdate,
    session: AsyncSession = Depends(get_session),
) -> ResponseBase[DeviceResponse]:
    """更新设备信息"""
    result = await session.execute(
        select(Device).where(Device.id == device_id, Device.status != DeviceStatus.DISABLED)
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在",
        )

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(device, key, value)

    await session.commit()
    await session.refresh(device)

    return ResponseBase(code=0, message="success", data=DeviceResponse.model_validate(device))


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """删除设备（软删除）

    将设备状态设置为disabled
    """
    result = await session.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        return  # 幂等，不存在也返回204

    # 已经是disabled则直接返回
    if device.status == DeviceStatus.DISABLED:
        return

    device.status = DeviceStatus.DISABLED
    await session.commit()


@router.get("/{device_id}/data", response_model=ListResponse[List[SensorDataResponse]])
async def get_device_data(
    device_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    start: datetime | None = Query(None, description="开始时间（ISO8601）"),
    end: datetime | None = Query(None, description="结束时间（ISO8601）"),
    session: AsyncSession = Depends(get_session),
) -> ListResponse[List[SensorDataResponse]]:
    """获取设备传感器数据"""
    # 验证设备存在
    device_result = await session.execute(
        select(Device).where(Device.id == device_id, Device.status != DeviceStatus.DISABLED)
    )
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在",
        )

    # 构建查询
    query = select(SensorData).where(SensorData.device_id == device_id)

    if start:
        query = query.where(SensorData.timestamp >= start)
    if end:
        query = query.where(SensorData.timestamp <= end)

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # 排序和分页
    query = query.order_by(SensorData.timestamp.desc()).offset((page - 1) * size).limit(size)

    result = await session.execute(query)
    data_list = result.scalars().all()

    pages = (total + size - 1) // size

    return ListResponse(
        code=0,
        message="success",
        data=[
            SensorDataResponse(
                id=d.id,
                device_id=d.device_id,
                temperature=d.temperature,
                vibration=d.vibration,
                current=d.current,
                timestamp=d.timestamp,
                device_name=device.name,
            )
            for d in data_list
        ],
        pagination=Pagination(page=page, size=size, total=total, pages=pages),
    )


@router.get("/{device_id}/stats", response_model=ResponseBase[dict])
async def get_device_stats(
    device_id: int,
    session: AsyncSession = Depends(get_session),
) -> ResponseBase[dict]:
    """获取设备今日统计数据"""
    # 验证设备存在
    device_result = await session.execute(
        select(Device).where(Device.id == device_id, Device.status != DeviceStatus.DISABLED)
    )
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设备不存在",
        )

    # 今日时间范围
    today = date.today()
    today_start = datetime.combine(today, time.min, tzinfo=timezone.utc)
    today_end = datetime.combine(today, time.max, tzinfo=timezone.utc)

    # 查询统计
    stats_result = await session.execute(
        select(
            func.count().label("total_records"),
            func.avg(SensorData.temperature).label("avg_temperature"),
            func.avg(SensorData.vibration).label("avg_vibration"),
            func.avg(SensorData.current).label("avg_current"),
            func.max(SensorData.timestamp).label("latest_timestamp"),
        ).where(
            SensorData.device_id == device_id,
            SensorData.timestamp >= today_start,
            SensorData.timestamp <= today_end,
        )
    )
    stats = stats_result.one()

    return ResponseBase(
        code=0,
        message="success",
        data={
            "total_records": stats.total_records or 0,
            "avg_temperature": round(stats.avg_temperature, 2) if stats.avg_temperature else None,
            "avg_vibration": round(stats.avg_vibration, 2) if stats.avg_vibration else None,
            "avg_current": round(stats.avg_current, 2) if stats.avg_current else None,
            "latest_timestamp": stats.latest_timestamp.isoformat() if stats.latest_timestamp else None,
        },
    )
