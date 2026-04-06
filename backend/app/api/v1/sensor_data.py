"""传感器数据API路由

提供传感器数据的批量写入和导出功能
"""

import csv
import io
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.database import get_session
from app.models import Device, DeviceStatus, SensorData
from app.schemas import ResponseBase, SensorDataCreate

router = APIRouter(prefix="/sensor-data", tags=["sensor-data"])


@router.post("", response_model=ResponseBase[dict])
async def create_sensor_data(
    data: SensorDataCreate | List[SensorDataCreate],
    session: AsyncSession = Depends(get_session),
) -> ResponseBase[dict]:
    """创建传感器数据

    支持单条或批量创建，最多100条
    验证设备存在且状态不为disabled
    """
    # 统一转换为列表
    if isinstance(data, SensorDataCreate):
        data_list = [data]
    else:
        data_list = data

    # 检查数量限制
    if len(data_list) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次最多提交100条数据",
        )

    if len(data_list) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数据不能为空",
        )

    # 收集所有device_id
    device_ids = {item.device_id for item in data_list}

    # 验证设备存在且可用
    device_result = await session.execute(
        select(Device).where(
            Device.id.in_(device_ids),
            Device.status != DeviceStatus.DISABLED,
        )
    )
    valid_devices = {d.id: d for d in device_result.scalars().all()}

    # 检查是否有无效设备
    invalid_ids = device_ids - set(valid_devices.keys())
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备不存在或已禁用: {invalid_ids}",
        )

    # 批量创建
    sensor_data_list = [SensorData(**item.model_dump()) for item in data_list]
    session.add_all(sensor_data_list)
    await session.commit()

    # 刷新获取ID
    for item in sensor_data_list:
        await session.refresh(item)

    return ResponseBase(
        code=0,
        message="success",
        data={
            "ids": [item.id for item in sensor_data_list],
            "count": len(sensor_data_list),
        },
    )


@router.get("/export")
async def export_sensor_data(
    device_id: int = Query(..., description="设备ID"),
    start: datetime | None = Query(None, description="开始时间（ISO8601）"),
    end: datetime | None = Query(None, description="结束时间（ISO8601）"),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """导出传感器数据为CSV

    返回CSV文件流，包含timestamp,device_name,temperature,vibration,current列
    """
    # 获取设备信息
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
    query = query.order_by(SensorData.timestamp.asc())

    result = await session.execute(query)
    data_list = result.scalars().all()

    # 生成CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "device_name", "temperature", "vibration", "current"])

    for data in data_list:
        writer.writerow([
            data.timestamp.isoformat(),
            device.name,
            data.temperature,
            data.vibration,
            data.current,
        ])

    output.seek(0)

    # 返回文件流
    filename = f"sensor_data_{device.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
