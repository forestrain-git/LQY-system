"""
预测服务 / Prediction Service

提供时间序列分析和预测功能，用于：
1. 垃圾量趋势预测 - 支持运营调度决策
2. 设备故障趋势预测 - 支持预防性维护

算法说明 / Algorithm Notes:
- 移动平均(MA): 平滑短期波动，显示长期趋势
- 指数平滑(EMA): 对近期数据赋予更高权重，响应更快

Author: AI Sprint
Date: 2026-04-07
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class PredictionResult:
    """
    预测结果数据类 / Prediction Result Data Class

    Attributes:
        timestamp: 预测时间点 / Prediction timestamp
        value: 预测值 / Predicted value
        confidence_lower: 置信区间下限 / Lower confidence bound
        confidence_upper: 置信区间上限 / Upper confidence bound
        method: 使用的预测方法 / Prediction method used
    """
    timestamp: datetime
    value: float
    confidence_lower: float
    confidence_upper: float
    method: str


class TimeSeriesPredictor:
    """
    时间序列预测器 / Time Series Predictor

    基于历史数据进行趋势预测，支持多种算法
    Supports multiple algorithms for trend prediction based on historical data

    使用示例 / Usage Example:
        predictor = TimeSeriesPredictor(historical_data)
        results = predictor.predict_next_days(days=7, method='ema')
    """

    def __init__(self, historical_data: List[Dict]):
        """
        初始化预测器 / Initialize predictor

        Args:
            historical_data: 历史数据列表，每项包含'timestamp'和'value'
                            List of historical data with 'timestamp' and 'value'
        """
        self.data = sorted(historical_data, key=lambda x: x['timestamp'])
        self.values = [d['value'] for d in self.data]

    def moving_average(self, window: int = 7) -> List[float]:
        """
        简单移动平均算法 / Simple Moving Average (SMA)

        计算方式：MA_n = (V_1 + V_2 + ... + V_n) / n
        用于平滑短期波动，显示长期趋势

        Args:
            window: 移动窗口大小 / Moving window size (default: 7 days)

        Returns:
            移动平均序列 / Moving average sequence
        """
        if len(self.values) < window:
            window = len(self.values)

        ma_values = []
        for i in range(len(self.values)):
            if i < window - 1:
                # 前window-1个点使用可用数据的平均
                # Use available data average for first window-1 points
                ma_values.append(sum(self.values[:i+1]) / (i+1))
            else:
                # 标准移动平均计算
                window_data = self.values[i-window+1:i+1]
                ma_values.append(sum(window_data) / window)

        return ma_values

    def exponential_smoothing(self, alpha: float = 0.3) -> List[float]:
        """
        指数平滑算法 / Exponential Smoothing (EMA)

        计算方式：S_t = α * Y_t + (1-α) * S_{t-1}
        - α (alpha): 平滑因子，0-1之间，越大对近期数据越敏感
        - 适合有明显趋势变化的数据

        Args:
            alpha: 平滑因子 / Smoothing factor (0-1, default: 0.3)
                  0.1=平滑, 0.5=敏感 / 0.1=smooth, 0.5=responsive

        Returns:
            指数平滑序列 / Exponentially smoothed sequence
        """
        if not self.values:
            return []

        ema_values = [self.values[0]]  # 第一个点初始化 / Initialize with first point

        for i in range(1, len(self.values)):
            # EMA公式: 新值 = α*当前值 + (1-α)*上一期平滑值
            # EMA formula: new = α*current + (1-α)*previous_smoothed
            ema = alpha * self.values[i] + (1 - alpha) * ema_values[i-1]
            ema_values.append(ema)

        return ema_values

    def calculate_trend(self) -> float:
        """
        计算线性趋势 / Calculate Linear Trend

        使用最小二乘法计算趋势斜率
        Uses least squares method to calculate trend slope

        Returns:
            趋势斜率 / Trend slope (正=上升趋势, 负=下降趋势)
                     Positive = upward trend, Negative = downward trend
        """
        n = len(self.values)
        if n < 2:
            return 0.0

        # 最小二乘法 / Least squares method
        x_values = list(range(n))
        sum_x = sum(x_values)
        sum_y = sum(self.values)
        sum_xy = sum(x * y for x, y in zip(x_values, self.values))
        sum_x2 = sum(x * x for x in x_values)

        # 斜率公式: (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
        # Slope formula
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def predict_next_days(
        self,
        days: int = 7,
        method: str = 'ema',
        alpha: float = 0.3,
        confidence: float = 0.95
    ) -> List[PredictionResult]:
        """
        预测未来N天的数值 / Predict values for next N days

        Args:
            days: 预测天数 / Number of days to predict (default: 7)
            method: 预测方法 / Prediction method ('ma', 'ema', 'trend')
            alpha: EMA平滑因子 / EMA smoothing factor
            confidence: 置信水平 / Confidence level (default: 0.95)

        Returns:
            预测结果列表 / List of prediction results
        """
        if not self.values:
            return []

        # 计算历史标准差用于置信区间
        # Calculate historical std dev for confidence intervals
        mean_val = sum(self.values) / len(self.values)
        variance = sum((v - mean_val) ** 2 for v in self.values) / len(self.values)
        std_dev = math.sqrt(variance)

        # 根据方法选择基础预测值 / Select base prediction by method
        if method == 'ma':
            ma_series = self.moving_average()
            last_trend = ma_series[-1] if ma_series else mean_val
            trend_slope = self.calculate_trend()
        elif method == 'ema':
            ema_series = self.exponential_smoothing(alpha)
            last_trend = ema_series[-1] if ema_series else mean_val
            trend_slope = self.calculate_trend()
        else:  # trend method
            trend_slope = self.calculate_trend()
            last_trend = self.values[-1]

        # 生成预测结果 / Generate predictions
        results = []
        last_timestamp = self.data[-1]['timestamp']

        for i in range(1, days + 1):
            # 预测时间点 / Prediction timestamp
            future_time = last_timestamp + timedelta(days=i)

            # 预测值 = 最后趋势 + 趋势斜率 * 天数
            # Predicted value = last trend + slope * days
            predicted = last_trend + trend_slope * i

            # 确保预测值非负 / Ensure non-negative predictions
            predicted = max(0, predicted)

            # 置信区间（使用正态分布近似）/ Confidence intervals
            # Z值: 95% = 1.96, 90% = 1.645
            z_score = 1.96 if confidence >= 0.95 else 1.645
            margin = z_score * std_dev * math.sqrt(i)  # 随时间扩大 / Widen over time

            lower = max(0, predicted - margin)
            upper = predicted + margin

            results.append(PredictionResult(
                timestamp=future_time,
                value=round(predicted, 2),
                confidence_lower=round(lower, 2),
                confidence_upper=round(upper, 2),
                method=method
            ))

        return results


class WasteVolumePredictor:
    """
    垃圾量预测器 / Waste Volume Predictor

    专门用于预测垃圾转运站的垃圾进站量
    Specialized for predicting waste intake at transfer stations

    业务场景 / Business Scenarios:
    - 日常运营调度 / Daily operation scheduling
    - 高峰期预警 / Peak period warning
    - 运力规划 / Capacity planning
    """

    def __init__(self, db_session=None):
        """
        初始化 / Initialize

        Args:
            db_session: 数据库会话 / Database session (optional)
        """
        self.db = db_session

    async def predict_daily_volume(
        self,
        station_id: str,
        days_ahead: int = 7
    ) -> Dict:
        """
        预测指定站点未来N天的垃圾量 / Predict waste volume for station

        Args:
            station_id: 站点ID / Station identifier
            days_ahead: 预测天数 / Days to predict ahead (default: 7)

        Returns:
            预测结果字典 / Prediction result dictionary
            {
                'station_id': 站点ID,
                'predictions': [PredictionResult列表],
                'trend': 趋势描述,
                'confidence': 平均置信度
            }
        """
        # TODO: 从数据库获取历史数据
        # TODO: Fetch historical data from database

        # 模拟数据（实际应从数据库获取）/ Mock data (replace with DB query)
        mock_historical = self._generate_mock_historical_data(days=30)

        predictor = TimeSeriesPredictor(mock_historical)
        predictions = predictor.predict_next_days(
            days=days_ahead,
            method='ema',
            alpha=0.3
        )

        # 分析趋势 / Analyze trend
        trend_slope = predictor.calculate_trend()
        if trend_slope > 0.1:
            trend_desc = "上升趋势 / Upward trend"
        elif trend_slope < -0.1:
            trend_desc = "下降趋势 / Downward trend"
        else:
            trend_desc = "平稳 / Stable"

        # 计算平均置信区间宽度 / Calculate avg confidence interval width
        avg_confidence = sum(
            (p.confidence_upper - p.confidence_lower) / p.value
            for p in predictions if p.value > 0
        ) / len(predictions) if predictions else 0

        return {
            'station_id': station_id,
            'predictions': [
                {
                    'date': p.timestamp.isoformat(),
                    'predicted_volume': p.value,
                    'confidence_range': [p.confidence_lower, p.confidence_upper],
                    'unit': '吨 / tons'
                }
                for p in predictions
            ],
            'trend': trend_desc,
            'trend_slope': round(trend_slope, 4),
            'avg_confidence_width': round(avg_confidence * 100, 2),
            'method': 'EMA (α=0.3)',
            'generated_at': datetime.now().isoformat()
        }

    def _generate_mock_historical_data(self, days: int = 30) -> List[Dict]:
        """
        生成模拟历史数据 / Generate mock historical data

        模拟真实垃圾量的周期性变化:
        - 工作日较多，周末较少
        - 存在一定的随机波动

        Args:
            days: 历史天数 / Number of days of history

        Returns:
            历史数据列表 / List of historical data
        """
        import random

        data = []
        base_time = datetime.now() - timedelta(days=days)

        for i in range(days):
            timestamp = base_time + timedelta(days=i)

            # 基础量 ~200吨/日 / Base volume ~200 tons/day
            base_volume = 200

            # 周末因子 / Weekend factor (weekends have less waste)
            weekday = timestamp.weekday()
            if weekday >= 5:  # 周六日 / Saturday, Sunday
                weekend_factor = 0.7
            else:
                weekend_factor = 1.0

            # 随机波动 ±15% / Random fluctuation ±15%
            random_factor = random.uniform(0.85, 1.15)

            # 轻微趋势（模拟增长）/ Slight growth trend
            trend_factor = 1 + (i * 0.005)

            volume = base_volume * weekend_factor * random_factor * trend_factor

            data.append({
                'timestamp': timestamp,
                'value': round(volume, 2)
            })

        return data


class EquipmentFailurePredictor:
    """
    设备故障预测器 / Equipment Failure Predictor

    基于设备运行参数预测故障概率
    Predicts failure probability based on equipment operation parameters

    预测维度 / Prediction Dimensions:
    - 振动异常 / Vibration anomalies
    - 温度升高 / Temperature rise
    - 电流波动 / Current fluctuations
    """

    def __init__(self, db_session=None):
        self.db = db_session

    async def predict_failure_risk(
        self,
        equipment_id: str,
        look_ahead_days: int = 7
    ) -> Dict:
        """
        预测设备故障风险 / Predict equipment failure risk

        Args:
            equipment_id: 设备ID / Equipment identifier
            look_ahead_days: 预测提前天数 / Days to look ahead (default: 7)

        Returns:
            风险评估结果 / Risk assessment result
            {
                'equipment_id': 设备ID,
                'risk_level': 风险等级 (low/medium/high),
                'failure_probability': 故障概率,
                'predicted_failure_date': 预计故障日期,
                'recommendations': [建议措施列表]
            }
        """
        # TODO: 从数据库获取设备传感器历史数据
        # TODO: Fetch sensor historical data from database

        # 模拟分析结果 / Mock analysis results
        import random

        # 模拟故障概率 / Mock failure probability (0-1)
        failure_prob = random.uniform(0.1, 0.8)

        # 风险等级划分 / Risk level classification
        if failure_prob < 0.3:
            risk_level = "low"
            risk_desc = "低风险 / Low risk"
        elif failure_prob < 0.6:
            risk_level = "medium"
            risk_desc = "中风险 / Medium risk"
        else:
            risk_level = "high"
            risk_desc = "高风险 / High risk"

        # 生成建议 / Generate recommendations
        recommendations = self._generate_recommendations(risk_level)

        # 预计故障日期（如果风险高）/ Predicted failure date
        if failure_prob > 0.5:
            predicted_date = (datetime.now() + timedelta(
                days=int((1 - failure_prob) * look_ahead_days)
            )).isoformat()
        else:
            predicted_date = None

        return {
            'equipment_id': equipment_id,
            'risk_level': risk_level,
            'risk_description': risk_desc,
            'failure_probability': round(failure_prob * 100, 2),
            'predicted_failure_date': predicted_date,
            'look_ahead_days': look_ahead_days,
            'recommendations': recommendations,
            'monitored_parameters': [
                'vibration',      # 振动 / Vibration
                'temperature',    # 温度 / Temperature
                'current',        # 电流 / Current
                'running_hours'   # 运行时长 / Running hours
            ],
            'generated_at': datetime.now().isoformat()
        }

    def _generate_recommendations(self, risk_level: str) -> List[str]:
        """
        根据风险等级生成维护建议 / Generate maintenance recommendations

        Args:
            risk_level: 风险等级 / Risk level (low/medium/high)

        Returns:
            建议列表 / List of recommendations
        """
        recommendations = {
            'low': [
                "继续常规监测 / Continue routine monitoring",
                "按计划进行保养 / Follow scheduled maintenance",
                "记录运行参数 / Record operation parameters"
            ],
            'medium': [
                "增加监测频率 / Increase monitoring frequency",
                "准备备用设备 / Prepare backup equipment",
                "预约维护检查 / Schedule maintenance inspection",
                "检查易损件状态 / Check wear parts condition"
            ],
            'high': [
                "立即安排维护 / Arrange immediate maintenance",
                "启用备用设备 / Activate backup equipment",
                "减少设备负载 / Reduce equipment load",
                "通知相关人员 / Notify relevant personnel",
                "准备停机计划 / Prepare shutdown plan"
            ]
        }

        return recommendations.get(risk_level, recommendations['low'])
