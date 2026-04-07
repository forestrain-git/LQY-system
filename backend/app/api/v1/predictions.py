"""
预测API路由 / Prediction API Routes

提供垃圾量预测和设备故障预测的RESTful API接口
Provides RESTful API endpoints for waste volume and equipment failure predictions

路由前缀 / Route prefix: /api/v1/predictions

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.prediction_service import (
    WasteVolumePredictor,
    EquipmentFailurePredictor
)

# 创建路由 / Create router
router = APIRouter(
    prefix="/predictions",
    tags=["predictions"],  # API文档标签 / API doc tag
    responses={404: {"description": "未找到 / Not found"}}
)


# ============== Pydantic模型 / Pydantic Models ==============

class WasteVolumePredictionRequest(BaseModel):
    """
    垃圾量预测请求模型 / Waste Volume Prediction Request
    """
    station_id: str = Field(
        ...,
        description="站点ID / Station identifier",
        example="lqy_station_01"
    )
    days_ahead: int = Field(
        default=7,
        ge=1,
        le=30,
        description="预测天数 / Days to predict ahead (1-30)",
        example=7
    )

    class Config:
        json_schema_extra = {
            "example": {
                "station_id": "lqy_station_01",
                "days_ahead": 7
            }
        }


class WasteVolumePredictionItem(BaseModel):
    """
    单日垃圾量预测结果 / Single Day Waste Volume Prediction
    """
    date: str = Field(..., description="日期 / Date (ISO format)")
    predicted_volume: float = Field(..., description="预测量(吨) / Predicted volume (tons)")
    confidence_range: List[float] = Field(
        ...,
        description="置信区间[下限,上限] / Confidence range [lower, upper]"
    )
    unit: str = Field(default="吨 / tons", description="单位 / Unit")


class WasteVolumePredictionResponse(BaseModel):
    """
    垃圾量预测响应模型 / Waste Volume Prediction Response
    """
    station_id: str = Field(..., description="站点ID / Station identifier")
    predictions: List[WasteVolumePredictionItem] = Field(
        ...,
        description="预测结果列表 / List of predictions"
    )
    trend: str = Field(..., description="趋势描述 / Trend description")
    trend_slope: float = Field(..., description="趋势斜率 / Trend slope")
    avg_confidence_width: float = Field(
        ...,
        description="平均置信区间宽度(%) / Average confidence interval width (%)"
    )
    method: str = Field(..., description="预测方法 / Prediction method")
    generated_at: str = Field(..., description="生成时间 / Generation time")


class EquipmentFailurePredictionRequest(BaseModel):
    """
    设备故障预测请求模型 / Equipment Failure Prediction Request
    """
    equipment_id: str = Field(
        ...,
        description="设备ID / Equipment identifier",
        example="compressor_01"
    )
    look_ahead_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="预测提前天数 / Days to look ahead",
        example=7
    )

    class Config:
        json_schema_extra = {
            "example": {
                "equipment_id": "compressor_01",
                "look_ahead_days": 7
            }
        }


class EquipmentFailurePredictionResponse(BaseModel):
    """
    设备故障预测响应模型 / Equipment Failure Prediction Response
    """
    equipment_id: str = Field(..., description="设备ID / Equipment identifier")
    risk_level: str = Field(
        ...,
        description="风险等级(low/medium/high) / Risk level",
        pattern="^(low|medium|high)$"
    )
    risk_description: str = Field(..., description="风险描述 / Risk description")
    failure_probability: float = Field(
        ...,
        ge=0,
        le=100,
        description="故障概率(%) / Failure probability (%)"
    )
    predicted_failure_date: Optional[str] = Field(
        None,
        description="预计故障日期 / Predicted failure date"
    )
    look_ahead_days: int = Field(..., description="预测天数 / Look ahead days")
    recommendations: List[str] = Field(
        ...,
        description="建议措施列表 / List of recommendations"
    )
    monitored_parameters: List[str] = Field(
        ...,
        description="监测参数列表 / List of monitored parameters"
    )
    generated_at: str = Field(..., description="生成时间 / Generation time")


# ============== API端点 / API Endpoints ==============

@router.post(
    "/waste-volume",
    response_model=WasteVolumePredictionResponse,
    summary="垃圾量预测 / Waste Volume Prediction",
    description="""
    预测指定站点未来N天的垃圾进站量
    Predict waste intake volume for a station for the next N days

    使用指数平滑算法(EMA)，考虑历史数据的周期性变化
    Uses Exponential Moving Average (EMA) algorithm with seasonal adjustments
    """
)
async def predict_waste_volume(
    request: WasteVolumePredictionRequest
) -> WasteVolumePredictionResponse:
    """
    垃圾量预测端点 / Waste volume prediction endpoint

    Args:
        request: 预测请求参数 / Prediction request parameters

    Returns:
        预测结果 / Prediction results

    Raises:
        HTTPException: 当预测失败时 / When prediction fails
    """
    try:
        predictor = WasteVolumePredictor()
        result = await predictor.predict_daily_volume(
            station_id=request.station_id,
            days_ahead=request.days_ahead
        )

        # 转换为Pydantic模型 / Convert to Pydantic model
        return WasteVolumePredictionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"预测失败 / Prediction failed: {str(e)}"
        )


@router.get(
    "/waste-volume/{station_id}",
    response_model=WasteVolumePredictionResponse,
    summary="垃圾量预测(简版) / Waste Volume Prediction (Simple)",
    description="通过URL参数快速获取垃圾量预测 / Quick waste volume prediction via URL params"
)
async def predict_waste_volume_simple(
    station_id: str,
    days: int = Query(default=7, ge=1, le=30, description="预测天数 / Days to predict")
) -> WasteVolumePredictionResponse:
    """
    垃圾量预测简版端点 / Simple waste volume prediction endpoint

    Args:
        station_id: 站点ID / Station identifier
        days: 预测天数 / Days to predict

    Returns:
        预测结果 / Prediction results
    """
    request = WasteVolumePredictionRequest(
        station_id=station_id,
        days_ahead=days
    )
    return await predict_waste_volume(request)


@router.post(
    "/equipment-failure",
    response_model=EquipmentFailurePredictionResponse,
    summary="设备故障预测 / Equipment Failure Prediction",
    description="""
    预测指定设备在未来一段时间内的故障风险
    Predict failure risk for equipment within a future time period

    基于振动、温度、电流等传感器数据分析
    Based on vibration, temperature, current and other sensor data
    """
)
async def predict_equipment_failure(
    request: EquipmentFailurePredictionRequest
) -> EquipmentFailurePredictionResponse:
    """
    设备故障预测端点 / Equipment failure prediction endpoint

    Args:
        request: 预测请求参数 / Prediction request parameters

    Returns:
        风险评估结果 / Risk assessment results

    Raises:
        HTTPException: 当预测失败时 / When prediction fails
    """
    try:
        predictor = EquipmentFailurePredictor()
        result = await predictor.predict_failure_risk(
            equipment_id=request.equipment_id,
            look_ahead_days=request.look_ahead_days
        )

        return EquipmentFailurePredictionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"预测失败 / Prediction failed: {str(e)}"
        )


@router.get(
    "/equipment-failure/{equipment_id}",
    response_model=EquipmentFailurePredictionResponse,
    summary="设备故障预测(简版) / Equipment Failure Prediction (Simple)",
    description="通过URL参数快速获取设备故障预测 / Quick equipment failure prediction via URL params"
)
async def predict_equipment_failure_simple(
    equipment_id: str,
    days: int = Query(default=7, ge=1, le=30, description="预测天数 / Look ahead days")
) -> EquipmentFailurePredictionResponse:
    """
    设备故障预测简版端点 / Simple equipment failure prediction endpoint

    Args:
        equipment_id: 设备ID / Equipment identifier
        days: 预测天数 / Days to look ahead

    Returns:
        风险评估结果 / Risk assessment results
    """
    request = EquipmentFailurePredictionRequest(
        equipment_id=equipment_id,
        look_ahead_days=days
    )
    return await predict_equipment_failure(request)


@router.get(
    "/methods",
    summary="获取预测方法说明 / Get Prediction Methods",
    description="获取支持的预测方法及其说明 / Get supported prediction methods and descriptions"
)
async def get_prediction_methods():
    """
    获取预测方法说明 / Get prediction method descriptions

    Returns:
        方法列表 / List of methods
    """
    return {
        "methods": [
            {
                "id": "ma",
                "name": "移动平均 / Moving Average",
                "description": "平滑短期波动，显示长期趋势 / Smooth short-term fluctuations, show long-term trend",
                "best_for": "稳定趋势的数据 / Data with stable trends",
                "parameters": {
                    "window": "窗口大小(默认7天) / Window size (default 7 days)"
                }
            },
            {
                "id": "ema",
                "name": "指数平滑 / Exponential Moving Average",
                "description": "对近期数据赋予更高权重 / Give higher weight to recent data",
                "best_for": "有趋势变化的数据 / Data with trend changes",
                "parameters": {
                    "alpha": "平滑因子0-1(默认0.3) / Smoothing factor 0-1 (default 0.3)"
                }
            },
            {
                "id": "trend",
                "name": "线性趋势 / Linear Trend",
                "description": "基于最小二乘法的线性拟合 / Linear fitting based on least squares",
                "best_for": "有明显线性趋势的数据 / Data with clear linear trends",
                "parameters": {}
            }
        ],
        "default_method": "ema",
        "confidence_levels": {
            "0.95": "95%置信区间(标准) / 95% confidence interval (standard)",
            "0.90": "90%置信区间 / 90% confidence interval"
        }
    }
