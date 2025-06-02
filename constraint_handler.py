"""
고도화된 제약 조건 처리 모듈
다양한 제약 조건과 처리 방법을 구현합니다.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import copy

from config import ConstraintHandling
from production_model import ProductionModel

class ConstraintType(Enum):
    """제약 조건 유형"""
    HARD = "hard"           # 절대 위반 불가능한 제약
    SOFT = "soft"           # 위반 시 페널티가 있는 제약
    FLEXIBLE = "flexible"   # 상황에 따라 조정 가능한 제약

class ConstraintPriority(Enum):
    """제약 조건 우선순위"""
    CRITICAL = 1    # 최고 우선순위
    HIGH = 2        # 높은 우선순위
    MEDIUM = 3      # 중간 우선순위
    LOW = 4         # 낮은 우선순위

@dataclass
class ConstraintViolation:
    """제약 조건 위반 정보"""
    constraint_name: str
    constraint_type: ConstraintType
    priority: ConstraintPriority
    violation_amount: float
    violation_percentage: float
    penalty_value: float
    description: str
    suggested_fix: str = ""

class Constraint(ABC):
    """제약 조건 추상 기본 클래스"""
    
    def __init__(self, name: str, constraint_type: ConstraintType, 
                 priority: ConstraintPriority, penalty_weight: float = 1.0):
        self.name = name
        self.constraint_type = constraint_type
        self.priority = priority
        self.penalty_weight = penalty_weight
        self.enabled = True
    
    @abstractmethod
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        """제약 조건 위반 검사"""
        pass
    
    @abstractmethod
    def repair(self, individual, production_model: ProductionModel):
        """제약 조건 위반 시 복구"""
        pass

class CapacityConstraint(Constraint):
    """생산 능력 제약"""
    
    def __init__(self, safety_margin: float = 0.05):
        super().__init__("생산능력제약", ConstraintType.HARD, ConstraintPriority.CRITICAL, 10000.0)
        self.safety_margin = safety_margin  # 안전 여유율
    
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        max_violation = 0.0
        violated_lines = []
        
        for line_id, line in production_model.production_lines.items():
            utilization = individual.get_line_utilization(line_id)
            max_utilization = 1.0 - self.safety_margin
            
            if utilization > max_utilization:
                violation = utilization - max_utilization
                max_violation = max(max_violation, violation)
                violated_lines.append(f"{line.line_name}({utilization:.1%})")
        
        if max_violation > 0:
            return ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                priority=self.priority,
                violation_amount=max_violation,
                violation_percentage=max_violation * 100,
                penalty_value=max_violation * self.penalty_weight,
                description=f"라인 용량 초과: {', '.join(violated_lines)}",
                suggested_fix="생산량을 줄이거나 작업 시간을 조정하세요"
            )
        
        return None
    
    def repair(self, individual, production_model: ProductionModel):
        """용량 초과 시 생산량 비례 감소"""
        for line_id, line in production_model.production_lines.items():
            utilization = individual.get_line_utilization(line_id)
            max_utilization = 1.0 - self.safety_margin
            
            if utilization > max_utilization:
                # 모든 제품의 생산량을 비례적으로 감소
                reduction_ratio = max_utilization / utilization
                for product_id in individual.genes[line_id]:
                    individual.genes[line_id][product_id] *= reduction_ratio

class DemandConstraint(Constraint):
    """수요 제약"""
    
    def __init__(self, min_satisfaction_rate: float = 0.8):
        super().__init__("수요제약", ConstraintType.SOFT, ConstraintPriority.HIGH, 5000.0)
        self.min_satisfaction_rate = min_satisfaction_rate
    
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        total_shortage = 0.0
        total_demand = 0.0
        violated_products = []
        
        for product_id, product in production_model.products.items():
            total_production = individual.get_total_production(product_id)
            required_production = max(product.min_demand, product.target_production * self.min_satisfaction_rate)
            
            if total_production < required_production:
                shortage = required_production - total_production
                total_shortage += shortage
                violated_products.append(f"{product.product_name}({shortage:.0f}개 부족)")
            
            total_demand += required_production
        
        if total_shortage > 0:
            violation_percentage = (total_shortage / total_demand * 100) if total_demand > 0 else 0
            
            return ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                priority=self.priority,
                violation_amount=total_shortage,
                violation_percentage=violation_percentage,
                penalty_value=total_shortage * self.penalty_weight,
                description=f"수요 미달: {', '.join(violated_products)}",
                suggested_fix="생산량을 늘리거나 효율적인 라인에 배정하세요"
            )
        
        return None
    
    def repair(self, individual, production_model: ProductionModel):
        """수요 부족 시 생산량 증가"""
        for product_id, product in production_model.products.items():
            total_production = individual.get_total_production(product_id)
            required_production = max(product.min_demand, product.target_production * self.min_satisfaction_rate)
            
            if total_production < required_production:
                shortage = required_production - total_production
                
                # 가장 효율적인 라인에 추가 생산 할당
                best_line_id = self._find_best_line_for_product(product_id, production_model, individual)
                if best_line_id:
                    individual.genes[best_line_id][product_id] += shortage
    
    def _find_best_line_for_product(self, product_id: str, production_model: ProductionModel, individual) -> Optional[str]:
        """제품에 가장 적합한 라인 찾기"""
        best_line_id = None
        best_efficiency = 0
        
        for line_id, line in production_model.production_lines.items():
            if product_id in line.compatible_products:
                # 현재 가동률이 낮고 불량률이 낮은 라인 선호
                current_utilization = individual.get_line_utilization(line_id)
                if current_utilization < 0.9:  # 90% 미만 가동률
                    efficiency = (1 - line.defect_rate) * (1 - current_utilization)
                    if efficiency > best_efficiency:
                        best_efficiency = efficiency
                        best_line_id = line_id
        
        return best_line_id

class BudgetConstraint(Constraint):
    """예산 제약"""
    
    def __init__(self, budget_limit: float):
        super().__init__("예산제약", ConstraintType.HARD, ConstraintPriority.CRITICAL, 8000.0)
        self.budget_limit = budget_limit
    
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        total_cost = individual.calculate_total_cost()
        
        if total_cost > self.budget_limit:
            violation = total_cost - self.budget_limit
            violation_percentage = (violation / self.budget_limit * 100)
            
            return ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                priority=self.priority,
                violation_amount=violation,
                violation_percentage=violation_percentage,
                penalty_value=violation * self.penalty_weight,
                description=f"예산 초과: {total_cost:,.0f}원 > {self.budget_limit:,.0f}원",
                suggested_fix="고비용 라인의 생산량을 줄이거나 저비용 제품을 늘리세요"
            )
        
        return None
    
    def repair(self, individual, production_model: ProductionModel):
        """예산 초과 시 고비용 라인 생산량 감소"""
        total_cost = individual.calculate_total_cost()
        
        if total_cost > self.budget_limit:
            # 라인별 비용 효율성 계산
            line_costs = {}
            for line_id, line in production_model.production_lines.items():
                utilization = individual.get_line_utilization(line_id)
                working_hours = utilization * line.max_working_hours
                line_costs[line_id] = line.operating_cost * working_hours
            
            # 비용이 높은 라인부터 생산량 감소
            sorted_lines = sorted(line_costs.items(), key=lambda x: x[1], reverse=True)
            
            for line_id, cost in sorted_lines:
                if individual.calculate_total_cost() <= self.budget_limit:
                    break
                
                # 해당 라인의 생산량을 10%씩 감소
                for product_id in individual.genes[line_id]:
                    individual.genes[line_id][product_id] *= 0.9

class QualityConstraint(Constraint):
    """품질 제약"""
    
    def __init__(self, max_overall_defect_rate: float = 0.05):
        super().__init__("품질제약", ConstraintType.SOFT, ConstraintPriority.HIGH, 3000.0)
        self.max_overall_defect_rate = max_overall_defect_rate
    
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        total_production = 0.0
        total_defects = 0.0
        
        for line_id, line in production_model.production_lines.items():
            line_production = sum(individual.genes[line_id].values())
            total_production += line_production
            total_defects += line_production * line.defect_rate
        
        if total_production > 0:
            overall_defect_rate = total_defects / total_production
            
            if overall_defect_rate > self.max_overall_defect_rate:
                violation = overall_defect_rate - self.max_overall_defect_rate
                violation_percentage = violation * 100
                
                return ConstraintViolation(
                    constraint_name=self.name,
                    constraint_type=self.constraint_type,
                    priority=self.priority,
                    violation_amount=violation,
                    violation_percentage=violation_percentage,
                    penalty_value=violation * total_production * self.penalty_weight,
                    description=f"전체 불량률 초과: {overall_defect_rate:.2%} > {self.max_overall_defect_rate:.2%}",
                    suggested_fix="고품질 라인의 생산량을 늘리고 저품질 라인을 줄이세요"
                )
        
        return None
    
    def repair(self, individual, production_model: ProductionModel):
        """품질 위반 시 고품질 라인으로 생산 이동"""
        # 라인별 품질 순서 정렬 (낮은 불량률이 높은 품질)
        sorted_lines = sorted(
            production_model.production_lines.items(),
            key=lambda x: x[1].defect_rate
        )
        
        # 저품질 라인에서 고품질 라인으로 생산량 이동
        for i in range(len(sorted_lines) - 1, 0, -1):  # 역순으로 (저품질부터)
            low_quality_line_id = sorted_lines[i][0]
            low_quality_line = sorted_lines[i][1]
            
            for j in range(i):  # 더 높은 품질의 라인들
                high_quality_line_id = sorted_lines[j][0]
                high_quality_line = sorted_lines[j][1]
                
                # 공통 제품에 대해 생산량 이동
                for product_id in individual.genes[low_quality_line_id]:
                    if (product_id in high_quality_line.compatible_products and
                        individual.genes[low_quality_line_id][product_id] > 0):
                        
                        # 고품질 라인의 여유 용량 확인
                        high_utilization = individual.get_line_utilization(high_quality_line_id)
                        if high_utilization < 0.8:  # 80% 미만 가동률
                            # 생산량의 일부를 이동
                            move_amount = individual.genes[low_quality_line_id][product_id] * 0.3
                            individual.genes[low_quality_line_id][product_id] -= move_amount
                            individual.genes[high_quality_line_id][product_id] += move_amount

class MaterialSupplyConstraint(Constraint):
    """원자재 공급 제약"""
    
    def __init__(self):
        super().__init__("원자재공급제약", ConstraintType.HARD, ConstraintPriority.CRITICAL, 7000.0)
    
    def check_violation(self, individual, production_model: ProductionModel) -> Optional[ConstraintViolation]:
        violated_products = []
        max_violation = 0.0
        
        for product_id, product in production_model.products.items():
            total_production = individual.get_total_production(product_id)
            
            if total_production > product.material_supply_limit:
                violation = total_production - product.material_supply_limit
                max_violation = max(max_violation, violation)
                violated_products.append(f"{product.product_name}({violation:.0f}개 초과)")
        
        if max_violation > 0:
            return ConstraintViolation(
                constraint_name=self.name,
                constraint_type=self.constraint_type,
                priority=self.priority,
                violation_amount=max_violation,
                violation_percentage=(max_violation / product.material_supply_limit * 100) if product.material_supply_limit > 0 else 0,
                penalty_value=max_violation * self.penalty_weight,
                description=f"원자재 공급 한계 초과: {', '.join(violated_products)}",
                suggested_fix="해당 제품의 생산량을 공급 한계 내로 조정하세요"
            )
        
        return None
    
    def repair(self, individual, production_model: ProductionModel):
        """원자재 공급 한계 초과 시 생산량 조정"""
        for product_id, product in production_model.products.items():
            total_production = individual.get_total_production(product_id)
            
            if total_production > product.material_supply_limit:
                # 각 라인의 생산량을 비례적으로 감소
                reduction_ratio = product.material_supply_limit / total_production
                
                for line_id in individual.genes:
                    if product_id in individual.genes[line_id]:
                        individual.genes[line_id][product_id] *= reduction_ratio

class AdvancedConstraintHandler:
    """고급 제약 조건 처리기"""
    
    def __init__(self, production_model: ProductionModel, handling_method: ConstraintHandling = ConstraintHandling.PENALTY_FUNCTION):
        self.production_model = production_model
        self.handling_method = handling_method
        self.constraints: List[Constraint] = []
        self.violation_history: List[List[ConstraintViolation]] = []
        self.adaptive_penalties = {}
        
        # 기본 제약 조건들 추가
        self._initialize_default_constraints()
    
    def _initialize_default_constraints(self):
        """기본 제약 조건들 초기화"""
        self.constraints = [
            CapacityConstraint(),
            DemandConstraint(),
            QualityConstraint(),
            MaterialSupplyConstraint()
        ]
        
        # 예산 제약이 설정되어 있으면 추가
        if hasattr(self.production_model.constraints, 'total_budget') and self.production_model.constraints.total_budget < float('inf'):
            self.constraints.append(BudgetConstraint(self.production_model.constraints.total_budget))
    
    def add_constraint(self, constraint: Constraint):
        """제약 조건 추가"""
        self.constraints.append(constraint)
    
    def remove_constraint(self, constraint_name: str):
        """제약 조건 제거"""
        self.constraints = [c for c in self.constraints if c.name != constraint_name]
    
    def check_all_constraints(self, individual) -> Tuple[bool, List[ConstraintViolation], float]:
        """모든 제약 조건 검사"""
        violations = []
        total_penalty = 0.0
        
        for constraint in self.constraints:
            if constraint.enabled:
                violation = constraint.check_violation(individual, self.production_model)
                if violation:
                    violations.append(violation)
                    
                    # 적응적 페널티 적용
                    adaptive_penalty = self._calculate_adaptive_penalty(constraint.name, violation.penalty_value)
                    total_penalty += adaptive_penalty
        
        is_feasible = len(violations) == 0
        
        # 위반 이력 저장
        self.violation_history.append(violations)
        if len(self.violation_history) > 100:  # 최근 100개만 유지
            self.violation_history.pop(0)
        
        return is_feasible, violations, total_penalty
    
    def repair_violations(self, individual, violations: List[ConstraintViolation]):
        """제약 조건 위반 복구"""
        if self.handling_method == ConstraintHandling.REPAIR_ALGORITHM:
            # 우선순위에 따라 정렬
            sorted_violations = sorted(violations, key=lambda v: v.priority.value)
            
            for violation in sorted_violations:
                # 해당 제약 조건 찾기
                constraint = next((c for c in self.constraints if c.name == violation.constraint_name), None)
                if constraint:
                    constraint.repair(individual, self.production_model)
    
    def _calculate_adaptive_penalty(self, constraint_name: str, base_penalty: float) -> float:
        """적응적 페널티 계산"""
        # 위반 빈도 기반 페널티 조정
        if constraint_name not in self.adaptive_penalties:
            self.adaptive_penalties[constraint_name] = {
                'base_penalty': base_penalty,
                'violation_count': 0,
                'multiplier': 1.0
            }
        
        penalty_info = self.adaptive_penalties[constraint_name]
        penalty_info['violation_count'] += 1
        
        # 위반 빈도가 높을수록 페널티 증가
        if penalty_info['violation_count'] > 10:
            penalty_info['multiplier'] = min(5.0, penalty_info['multiplier'] * 1.1)
        
        return base_penalty * penalty_info['multiplier']
    
    def get_constraint_statistics(self) -> Dict[str, Any]:
        """제약 조건 통계 정보"""
        stats = {}
        
        if not self.violation_history:
            return stats
        
        # 각 제약 조건별 위반 통계
        for constraint in self.constraints:
            constraint_violations = []
            for violations in self.violation_history:
                for violation in violations:
                    if violation.constraint_name == constraint.name:
                        constraint_violations.append(violation)
            
            if constraint_violations:
                stats[constraint.name] = {
                    'violation_frequency': len(constraint_violations) / len(self.violation_history),
                    'average_violation': np.mean([v.violation_amount for v in constraint_violations]),
                    'max_violation': max([v.violation_amount for v in constraint_violations]),
                    'average_penalty': np.mean([v.penalty_value for v in constraint_violations])
                }
            else:
                stats[constraint.name] = {
                    'violation_frequency': 0.0,
                    'average_violation': 0.0,
                    'max_violation': 0.0,
                    'average_penalty': 0.0
                }
        
        return stats
    
    def suggest_parameter_adjustments(self) -> List[str]:
        """파라미터 조정 제안"""
        suggestions = []
        stats = self.get_constraint_statistics()
        
        for constraint_name, stat in stats.items():
            if stat['violation_frequency'] > 0.7:  # 70% 이상 위반
                if constraint_name == "생산능력제약":
                    suggestions.append("생산 능력이 부족합니다. 라인 수를 늘리거나 가동 시간을 증가시키세요.")
                elif constraint_name == "수요제약":
                    suggestions.append("수요 목표가 너무 높습니다. 목표 생산량을 조정하거나 라인 효율성을 개선하세요.")
                elif constraint_name == "예산제약":
                    suggestions.append("예산이 부족합니다. 예산을 늘리거나 저비용 운영 방안을 고려하세요.")
                elif constraint_name == "품질제약":
                    suggestions.append("품질 기준이 엄격합니다. 고품질 라인을 늘리거나 품질 개선 투자를 고려하세요.")
        
        return suggestions

class ConstraintRelaxation:
    """제약 조건 완화 관리"""
    
    def __init__(self, constraint_handler: AdvancedConstraintHandler):
        self.constraint_handler = constraint_handler
        self.relaxation_levels = {}
    
    def relax_constraint(self, constraint_name: str, relaxation_factor: float):
        """제약 조건 완화"""
        self.relaxation_levels[constraint_name] = relaxation_factor
        
        # 해당 제약 조건의 페널티 가중치 감소
        for constraint in self.constraint_handler.constraints:
            if constraint.name == constraint_name:
                constraint.penalty_weight *= (1 - relaxation_factor)
    
    def tighten_constraint(self, constraint_name: str, tightening_factor: float):
        """제약 조건 강화"""
        # 해당 제약 조건의 페널티 가중치 증가
        for constraint in self.constraint_handler.constraints:
            if constraint.name == constraint_name:
                constraint.penalty_weight *= (1 + tightening_factor)
    
    def auto_adjust_constraints(self):
        """자동 제약 조건 조정"""
        stats = self.constraint_handler.get_constraint_statistics()
        
        for constraint_name, stat in stats.items():
            # 위반 빈도가 너무 높으면 완화, 너무 낮으면 강화
            if stat['violation_frequency'] > 0.8:
                self.relax_constraint(constraint_name, 0.1)  # 10% 완화
            elif stat['violation_frequency'] < 0.1:
                self.tighten_constraint(constraint_name, 0.1)  # 10% 강화