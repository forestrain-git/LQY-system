"""
智慧调度服务 / Intelligent Dispatch Services

包含排队算法、泊位分配、路径优化等核心调度逻辑
Includes queue algorithm, berth allocation, route optimization

Author: AI Sprint
Date: 2026-04-07
"""

import heapq
import random
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple

from app.modules.dispatch.models import (
    Vehicle, VehicleStatus,
    Berth, BerthStatus, BerthType,
    Schedule, ScheduleStatus
)


class QueuePriority(Enum):
    """
    排队优先级 / Queue Priority

    车辆排队优先级规则
    Vehicle queue priority rules
    """
    EMERGENCY = 0     # 紧急车辆 / Emergency vehicle
    APPOINTMENT = 1   # 预约车辆 / Scheduled appointment
    STANDARD = 2      # 标准车辆 / Standard
    WAITING = 3       # 等待中 / Waiting


class DispatchRecommendation:
    """
    调度建议 / Dispatch Recommendation

    系统生成的调度决策建议
    System-generated dispatch decision recommendation
    """

    def __init__(
        self,
        vehicle_id: int,
        recommended_berth_id: Optional[int],
        estimated_wait_minutes: float,
        priority_score: float,
        reason: str
    ):
        self.vehicle_id = vehicle_id
        self.recommended_berth_id = recommended_berth_id
        self.estimated_wait_minutes = estimated_wait_minutes
        self.priority_score = priority_score
        self.reason = reason


class QueueManager:
    """
    队列管理器 / Queue Manager

    管理车辆排队系统，实现智能排队算法
    Manages vehicle queuing system with intelligent algorithm

    业务规则 / Business Rules:
    - 预约车辆优先 / Scheduled vehicles have priority
    - 同类型垃圾优先分配到对应泊位 / Same waste type → matching berth
    - FIFO基础上考虑等待时间和优先级 / FIFO with wait time and priority
    """

    def __init__(self):
        self._queue: List[Tuple[float, datetime, int, Schedule]] = []
        self._counter = 0  # 用于稳定排序 / For stable sorting

    def add_to_queue(self, schedule: Schedule, priority: QueuePriority = QueuePriority.STANDARD) -> int:
        """
        添加车辆到队列 / Add vehicle to queue

        Args:
            schedule: 调度记录 / Schedule record
            priority: 优先级 / Priority level

        Returns:
            分配的排队号 / Assigned queue number
        """
        self._counter += 1
        # 优先级数值越小越优先 / Lower number = higher priority
        heapq.heappush(
            self._queue,
            (priority.value, schedule.appointment_time, self._counter, schedule)
        )
        return self._counter

    def get_next_vehicle(self, berth_type: Optional[BerthType] = None) -> Optional[Schedule]:
        """
        获取下一个待调度车辆 / Get next vehicle to dispatch

        Args:
            berth_type: 期望泊位类型 / Desired berth type

        Returns:
            下一条调度记录或None / Next schedule or None
        """
        if not self._queue:
            return None

        # 找到最适合的车辆 / Find best matching vehicle
        candidates = []
        for item in self._queue:
            _, _, _, schedule = item
            # 简单匹配逻辑：如果没有指定类型或匹配成功
            # Simple matching: no type specified or type matches
            match_score = 0
            if berth_type and schedule.expected_waste_type == berth_type.value:
                match_score = 1
            candidates.append((match_score, item))

        if not candidates:
            return None

        # 按匹配度和优先级排序 / Sort by match and priority
        candidates.sort(key=lambda x: (x[0], x[1][0], x[1][1]), reverse=True)
        best_match = candidates[0][1]

        # 从队列中移除 / Remove from queue
        self._queue.remove(best_match)
        heapq.heapify(self._queue)

        return best_match[3]

    def get_queue_position(self, schedule_id: int) -> Optional[int]:
        """
        获取车辆排队位置 / Get vehicle queue position

        Args:
            schedule_id: 调度ID / Schedule ID

        Returns:
            当前位置(1-based)或None / Position (1-based) or None
        """
        sorted_queue = sorted(self._queue)
        for idx, (_, _, _, schedule) in enumerate(sorted_queue, 1):
            if schedule.id == schedule_id:
                return idx
        return None

    def estimate_wait_time(self, position: int, avg_service_minutes: float = 15.0) -> float:
        """
        预估等待时间 / Estimate wait time

        Args:
            position: 排队位置 / Queue position
            avg_service_minutes: 平均服务时间 / Average service time

        Returns:
            预估等待分钟数 / Estimated wait minutes
        """
        return position * avg_service_minutes


class BerthAllocator:
    """
    泊位分配器 / Berth Allocator

    智能分配泊位，优化场地利用率
    Intelligent berth allocation to optimize yard utilization

    分配策略 / Allocation Strategy:
    1. 垃圾类型匹配 / Waste type matching
    2. 最短等待时间 / Shortest wait time
    3. 负载均衡 / Load balancing
    """

    # 垃圾类型到泊位类型的映射 / Waste type to berth type mapping
    TYPE_MAPPING = {
        "domestic": BerthType.DOMESTIC,
        "kitchen": BerthType.KITCHEN,
        "recyclable": BerthType.RECYCLABLE,
        "hazardous": BerthType.HAZARDOUS,
        "bulky": BerthType.BULKY,
        "green": BerthType.GREEN,
    }

    def __init__(self, berths: List[Berth]):
        self.berths = berths

    def find_best_berth(
        self,
        vehicle: Vehicle,
        waste_type: Optional[str] = None,
        strategy: str = "balanced"
    ) -> Optional[Berth]:
        """
        找到最佳泊位 / Find best berth

        Args:
            vehicle: 车辆 / Vehicle
            waste_type: 垃圾类型 / Waste type
            strategy: 分配策略 / Allocation strategy

        Returns:
            最佳泊位或None / Best berth or None
        """
        available_berths = [b for b in self.berths if b.status == BerthStatus.AVAILABLE]

        if not available_berths:
            return None

        # 评分函数 / Scoring function
        def score_berth(berth: Berth) -> float:
            score = 0.0

            # 类型匹配得分 / Type matching score (0-40)
            if waste_type:
                expected_type = self.TYPE_MAPPING.get(waste_type)
                if expected_type and berth.berth_type == expected_type:
                    score += 40.0
                elif berth.berth_type == BerthType.EMERGENCY:
                    score += 20.0  # 应急泊位通用 / Emergency berth universal

            # 容量匹配得分 / Capacity matching (0-30)
            if vehicle.max_capacity <= berth.capacity_tons * 1.2:
                score += 30.0
            elif vehicle.max_capacity <= berth.capacity_tons * 1.5:
                score += 15.0

            # 负载均衡得分 / Load balancing (0-30)
            # 假设使用历史使用频率
            score += 30.0 * random.random()

            return score

        random.seed(vehicle.id)  # 可复现 / Reproducible

        # 评分并选择最佳 / Score and select best
        scored = [(score_berth(b), b) for b in available_berths]
        scored.sort(key=lambda x: x[0], reverse=True)

        return scored[0][1] if scored else None

    def allocate(self, vehicle: Vehicle, berth: Berth) -> bool:
        """
        分配泊位 / Allocate berth

        Args:
            vehicle: 车辆 / Vehicle
            berth: 泊位 / Berth

        Returns:
            是否成功 / Success flag
        """
        if berth.status != BerthStatus.AVAILABLE:
            return False

        berth.status = BerthStatus.OCCUPIED
        berth.current_vehicle_id = vehicle.id
        vehicle.status = VehicleStatus.UNLOADING
        return True

    def release(self, berth: Berth) -> None:
        """
        释放泊位 / Release berth

        Args:
            berth: 泊位 / Berth
        """
        berth.status = BerthStatus.AVAILABLE
        berth.current_vehicle_id = None


class DispatchOptimizer:
    """
    调度优化器 / Dispatch Optimizer

    提供全局调度优化建议
    Provides global dispatch optimization recommendations
    """

    def __init__(self, queue_manager: QueueManager, berth_allocator: BerthAllocator):
        self.queue_manager = queue_manager
        self.berth_allocator = berth_allocator

    def generate_recommendations(
        self,
        pending_schedules: List[Schedule],
        vehicles: List[Vehicle]
    ) -> List[DispatchRecommendation]:
        """
        生成调度建议 / Generate dispatch recommendations

        Args:
            pending_schedules: 待处理调度 / Pending schedules
            vehicles: 所有车辆 / All vehicles

        Returns:
            调度建议列表 / List of recommendations
        """
        recommendations = []
        vehicle_map = {v.id: v for v in vehicles}

        for schedule in pending_schedules:
            vehicle = vehicle_map.get(schedule.vehicle_id)
            if not vehicle:
                continue

            # 找到最佳泊位 / Find best berth
            best_berth = self.berth_allocator.find_best_berth(
                vehicle,
                schedule.expected_waste_type
            )

            # 计算优先级分数 / Calculate priority score
            priority_score = self._calculate_priority(schedule, vehicle)

            # 预估等待时间 / Estimate wait time
            queue_pos = self.queue_manager.get_queue_position(schedule.id)
            wait_minutes = self.queue_manager.estimate_wait_time(queue_pos or 1)

            # 生成原因说明 / Generate reason
            reason = self._generate_reason(schedule, best_berth, priority_score)

            rec = DispatchRecommendation(
                vehicle_id=vehicle.id,
                recommended_berth_id=best_berth.id if best_berth else None,
                estimated_wait_minutes=wait_minutes,
                priority_score=priority_score,
                reason=reason
            )
            recommendations.append(rec)

        # 按优先级分数排序 / Sort by priority score
        recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        return recommendations

    def _calculate_priority(self, schedule: Schedule, vehicle: Vehicle) -> float:
        """
        计算调度优先级分数 / Calculate dispatch priority score

        Returns:
            0-100 优先级分数 / Priority score 0-100
        """
        score = 50.0  # 基础分 / Base score

        # 预约准时性 / Appointment punctuality
        if schedule.appointment_time:
            time_diff = (datetime.now() - schedule.appointment_time).total_seconds() / 60
            if time_diff > 0:  # 已迟到 / Late
                score += min(30, time_diff / 10)

        # 车辆负载 / Vehicle load
        load_ratio = vehicle.current_load / vehicle.max_capacity if vehicle.max_capacity > 0 else 0
        score += load_ratio * 20  # 满载加分 / Full load bonus

        return min(100, score)

    def _generate_reason(
        self,
        schedule: Schedule,
        berth: Optional[Berth],
        priority: float
    ) -> str:
        """生成调度原因 / Generate dispatch reason"""
        if berth:
            return f"推荐泊位{berth.code}，匹配度{priority:.0f}%"
        return "暂无可用泊位，建议等待"


class SmartDispatchService:
    """
    智慧调度服务 / Smart Dispatch Service

    整合队列管理、泊位分配、优化建议的完整调度服务
    Complete dispatch service integrating queue, allocation, and optimization
    """

    def __init__(self, berths: List[Berth]):
        self.queue_manager = QueueManager()
        self.berth_allocator = BerthAllocator(berths)
        self.optimizer = DispatchOptimizer(self.queue_manager, self.berth_allocator)

    def schedule_arrival(
        self,
        vehicle: Vehicle,
        expected_waste_type: Optional[str] = None,
        expected_weight: Optional[float] = None,
        appointment_time: Optional[datetime] = None
    ) -> Schedule:
        """
        登记车辆到达 / Register vehicle arrival

        Args:
            vehicle: 车辆 / Vehicle
            expected_waste_type: 预期垃圾类型 / Expected waste type
            expected_weight: 预期重量 / Expected weight
            appointment_time: 预约时间 / Appointment time

        Returns:
            创建的调度记录 / Created schedule record
        """
        # 尝试立即分配泊位 / Try immediate berth allocation
        best_berth = self.berth_allocator.find_best_berth(vehicle, expected_waste_type)

        schedule = Schedule(
            vehicle_id=vehicle.id,
            berth_id=best_berth.id if best_berth else None,
            appointment_time=appointment_time or datetime.now(),
            expected_waste_type=expected_waste_type,
            expected_weight=expected_weight,
            status=ScheduleStatus.CHECKED_IN if best_berth else ScheduleStatus.QUEUED,
            checked_in_at=datetime.now(),
        )

        if not best_berth:
            # 加入队列 / Add to queue
            queue_no = self.queue_manager.add_to_queue(schedule)
            schedule.queue_number = queue_no
            schedule.queue_entered_at = datetime.now()

        return schedule

    def process_queue(self) -> List[Schedule]:
        """
        处理队列，分配可用泊位 / Process queue, allocate available berths

        Returns:
            本次处理的调度列表 / List of processed schedules
        """
        processed = []

        while True:
            next_schedule = self.queue_manager.get_next_vehicle()
            if not next_schedule:
                break

            # 尝试分配泊位 / Try allocate berth
            # 这里简化处理，实际应从数据库查询车辆
            # Simplified - actual should query DB for vehicle
            available_berth = self.berth_allocator.find_best_berth(
                Vehicle(id=next_schedule.vehicle_id),  # 简化 / Simplified
                next_schedule.expected_waste_type
            )

            if available_berth:
                next_schedule.berth_id = available_berth.id
                next_schedule.status = ScheduleStatus.CHECKED_IN
                processed.append(next_schedule)
            else:
                # 没有可用泊位，放回队列 / No berth, put back
                self.queue_manager.add_to_queue(next_schedule)
                break

        return processed

    def complete_unloading(
        self,
        schedule: Schedule,
        gross_weight: float,
        tare_weight: float
    ) -> Schedule:
        """
        完成卸货 / Complete unloading

        Args:
            schedule: 调度记录 / Schedule record
            gross_weight: 毛重 / Gross weight
            tare_weight: 皮重 / Tare weight

        Returns:
            更新后的调度记录 / Updated schedule
        """
        schedule.gross_weight = gross_weight
        schedule.tare_weight = tare_weight
        schedule.net_weight = gross_weight - tare_weight
        schedule.status = ScheduleStatus.COMPLETED
        schedule.completed_at = datetime.now()

        # 释放泊位 / Release berth
        if schedule.berth_id:
            berth = next(
                (b for b in self.berth_allocator.berths if b.id == schedule.berth_id),
                None
            )
            if berth:
                self.berth_allocator.release(berth)

        return schedule
