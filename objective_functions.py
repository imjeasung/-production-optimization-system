"""
고도화된 목적 함수 모듈
다양한 최적화 목표와 복잡한 비즈니스 로직을 구현합니다.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

from config import OptimizationGoal
from production_model import ProductionModel

@dataclass
class ObjectiveComponents:
    """목적 함수 구성 요소"""
    material_cost: float = 0.0
    labor_cost: float = 0.0
    operating_cost: float = 0.0
    setup_cost: float = 0.0
    maintenance_cost: float = 0.0
    inventory_cost: float = 0.0
    quality_cost: float = 0.0
    opportunity_cost: float = 0.0
    
    revenue: float = 0.0
    production_volume: float = 0.0
    quality_score: float = 0.0
    efficiency_score: float = 0.0
    flexibility_score: float = 0.0
    
    total_cost: float = 0.0
    total_profit: float = 0.0
    
    def calculate_totals(self):
        """총계 계산"""
        self.total_cost = (self.material_cost + self.labor_cost + self.operating_cost + 
                          self.setup_cost + self.maintenance_cost + self.inventory_cost + 
                          self.quality_cost + self.opportunity_cost)
        self.total_profit = self.revenue - self.total_cost

class ObjectiveFunction(ABC):
    """목적 함수 추상 기본 클래스"""
    
    def __init__(self, production_model: ProductionModel):
        self.production_model = production_model
        self.weights = {}
        self.normalization_factors = {}
    
    @abstractmethod
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        """목적 함수 평가"""
        pass
    
    def set_weights(self, weights: Dict[str, float]):
        """가중치 설정"""
        self.weights = weights
    
    def calculate_normalization_factors(self, population: List):
        """정규화 인수 계산 - 안전한 버전"""
        try:
            # 개체군 기반으로 각 목적 함수의 최대/최소값 계산
            costs = []
            revenues = []
            productions = []
            
            for individual in population:
                try:
                    _, components = self.evaluate(individual)
                    costs.append(components.total_cost)
                    revenues.append(components.revenue)
                    productions.append(components.production_volume)
                except:
                    # 개별 개체 평가 실패 시 건너뛰기
                    continue
            
            if costs and revenues and productions:
                # 안전한 범위 계산
                cost_min, cost_max = min(costs), max(costs)
                revenue_min, revenue_max = min(revenues), max(revenues)
                production_min, production_max = min(productions), max(productions)
                
                self.normalization_factors = {
                    'cost_range': max(1.0, cost_max - cost_min),
                    'cost_min': cost_min,
                    'revenue_range': max(1.0, revenue_max - revenue_min),
                    'revenue_min': revenue_min,
                    'production_range': max(1.0, production_max - production_min),
                    'production_min': production_min
                }
            else:
                # 데이터가 없으면 기본값 설정
                self._set_default_normalization_factors()
                
        except Exception as e:
            print(f"정규화 인수 계산 중 오류: {e}")
            self._set_default_normalization_factors()
    
    def _set_default_normalization_factors(self):
        """기본 정규화 인수 설정"""
        self.normalization_factors = {
            'cost_range': 1000000.0,
            'cost_min': 0.0,
            'revenue_range': 1000000.0,
            'revenue_min': 0.0,
            'production_range': 10000.0,
            'production_min': 0.0
        }

class CostMinimizationObjective(ObjectiveFunction):
    """비용 최소화 목적 함수"""
    
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        components = ObjectiveComponents()
        
        # 1. 원자재 비용
        for product_id, product in self.production_model.products.items():
            total_production = individual.get_total_production(product_id)
            components.material_cost += total_production * product.material_cost
        
        # 2. 운영 비용 (라인별)
        for line_id, line in self.production_model.production_lines.items():
            utilization = individual.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            components.operating_cost += working_hours * line.operating_cost
        
        # 3. 인건비 (운영 시간 기반)
        total_working_hours = sum(
            individual.get_line_utilization(line_id) * line.max_working_hours
            for line_id, line in self.production_model.production_lines.items()
        )
        hourly_labor_cost = 30000  # 시간당 인건비 (원/시간)
        components.labor_cost = total_working_hours * hourly_labor_cost
        
        # 4. 셋업 비용
        for line_id, production_dict in individual.genes.items():
            setup_count = sum(1 for amount in production_dict.values() if amount > 0)
            if setup_count > 0:
                # 제품 전환 횟수 기반 셋업 비용
                base_setup_cost = 50000  # 기본 셋업 비용
                components.setup_cost += setup_count * base_setup_cost
        
        # 5. 유지보수 비용 (월간 비용을 일일로 환산)
        for line_id, line in self.production_model.production_lines.items():
            utilization = individual.get_line_utilization(line_id)
            if utilization > 0:  # 가동하는 라인만
                daily_maintenance = line.maintenance_cost / 30  # 월간을 일간으로
                components.maintenance_cost += daily_maintenance
        
        # 6. 품질 비용 (불량품 처리 비용)
        for line_id, line in self.production_model.production_lines.items():
            line_production = sum(individual.genes[line_id].values())
            defective_items = line_production * line.defect_rate
            if defective_items > 0:
                # 불량품당 처리 비용 (재작업 + 폐기)
                defect_handling_cost = 500  # 원/개
                components.quality_cost += defective_items * defect_handling_cost
        
        # 7. 재고 비용 (과잉 생산 시)
        for product_id, product in self.production_model.products.items():
            total_production = individual.get_total_production(product_id)
            excess_production = max(0, total_production - product.target_production)
            inventory_cost_rate = product.material_cost * 0.1  # 원자재 비용의 10%
            components.inventory_cost += excess_production * inventory_cost_rate
        
        # 8. 기회 비용 (목표 미달 시)
        for product_id, product in self.production_model.products.items():
            total_production = individual.get_total_production(product_id)
            shortage = max(0, product.target_production - total_production)
            if shortage > 0:
                # 미달분에 대한 기회 비용 (잠재 이익 손실)
                opportunity_cost_per_unit = product.calculate_unit_profit() * 0.5
                components.opportunity_cost += shortage * opportunity_cost_per_unit
        
        components.calculate_totals()
        
        # 비용 최소화이므로 음수로 반환 (높은 적합도 = 낮은 비용)
        fitness = -components.total_cost
        
        return fitness, components

class ProfitMaximizationObjective(ObjectiveFunction):
    """수익 최대화 목적 함수"""
    
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        # 먼저 비용 계산 (기존 비용 최소화 로직 활용)
        cost_objective = CostMinimizationObjective(self.production_model)
        _, components = cost_objective.evaluate(individual)
        
        # 수익 계산
        components.revenue = 0.0
        
        # 1. 기본 판매 수익
        for product_id, product in self.production_model.products.items():
            total_production = individual.get_total_production(product_id)
            effective_production = self._calculate_effective_production(individual, product_id)
            components.revenue += effective_production * product.selling_price
        
        # 2. 품질 프리미엄 (낮은 불량률 라인의 제품에 대해)
        for line_id, line in self.production_model.production_lines.items():
            if line.defect_rate < 0.03:  # 3% 미만 불량률
                line_production = sum(individual.genes[line_id].values())
                quality_premium = line_production * 100  # 개당 100원 프리미엄
                components.revenue += quality_premium
        
        # 3. 대량 생산 할인 효과 (규모의 경제)
        total_production = individual.calculate_total_production_amount()
        if total_production > 5000:  # 5000개 이상 생산 시
            volume_bonus = (total_production - 5000) * 50  # 초과분에 대해 개당 50원 보너스
            components.revenue += volume_bonus
        
        components.calculate_totals()
        
        # 수익 최대화
        fitness = components.total_profit
        
        return fitness, components
    
    def _calculate_effective_production(self, individual, product_id: str) -> float:
        """불량률을 고려한 유효 생산량 계산"""
        effective_production = 0.0
        
        for line_id, line in self.production_model.production_lines.items():
            line_production = individual.genes[line_id].get(product_id, 0.0)
            effective_production += line_production * (1 - line.defect_rate)
        
        return effective_production

class ProductionMaximizationObjective(ObjectiveFunction):
    """생산량 최대화 목적 함수"""
    
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        components = ObjectiveComponents()
        
        # 1. 총 생산량
        components.production_volume = individual.calculate_total_production_amount()
        
        # 2. 유효 생산량 (불량률 고려)
        effective_volume = 0.0
        for line_id, line in self.production_model.production_lines.items():
            line_production = sum(individual.genes[line_id].values())
            effective_volume += line_production * (1 - line.defect_rate)
        
        # 3. 목표 달성률 점수
        achievement_score = 0.0
        for product_id, product in self.production_model.products.items():
            total_production = individual.get_total_production(product_id)
            achievement_rate = min(1.0, total_production / product.target_production if product.target_production > 0 else 1.0)
            achievement_score += achievement_rate
        
        # 정규화된 달성률 점수
        achievement_score = achievement_score / len(self.production_model.products) if self.production_model.products else 0
        
        # 가중 합계
        fitness = (effective_volume * 0.7 + achievement_score * 1000 * 0.3)
        
        components.production_volume = components.production_volume
        components.efficiency_score = achievement_score
        
        return fitness, components

class QualityOptimizationObjective(ObjectiveFunction):
    """품질 최적화 목적 함수"""
    
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        components = ObjectiveComponents()
        
        # 1. 전체 품질 점수 계산
        total_weighted_quality = 0.0
        total_production = 0.0
        
        for line_id, line in self.production_model.production_lines.items():
            line_production = sum(individual.genes[line_id].values())
            if line_production > 0:
                quality_score = (1 - line.defect_rate)  # 높은 품질 = 낮은 불량률
                total_weighted_quality += line_production * quality_score
                total_production += line_production
        
        if total_production > 0:
            components.quality_score = total_weighted_quality / total_production
        else:
            components.quality_score = 0.0
        
        # 2. 일관성 점수 (라인 간 품질 편차 최소화)
        line_qualities = []
        for line_id, line in self.production_model.production_lines.items():
            line_production = sum(individual.genes[line_id].values())
            if line_production > 0:
                line_qualities.append(1 - line.defect_rate)
        
        if len(line_qualities) > 1:
            quality_std = np.std(line_qualities)
            consistency_score = max(0, 1 - quality_std)  # 편차가 작을수록 높은 점수
        else:
            consistency_score = 1.0
        
        # 3. 제품별 품질 요구사항 만족도
        quality_compliance = 0.0
        for product_id, product in self.production_model.products.items():
            product_quality = 0.0
            product_production = 0.0
            
            for line_id, line in self.production_model.production_lines.items():
                line_production = individual.genes[line_id].get(product_id, 0.0)
                if line_production > 0:
                    product_quality += line_production * (1 - line.defect_rate)
                    product_production += line_production
            
            if product_production > 0:
                avg_quality = product_quality / product_production
                # 제품의 최대 허용 불량률 대비 성능
                if avg_quality >= (1 - product.max_defect_rate):
                    quality_compliance += 1.0
                else:
                    quality_compliance += avg_quality / (1 - product.max_defect_rate)
        
        if self.production_model.products:
            quality_compliance = quality_compliance / len(self.production_model.products)
        
        # 최종 품질 점수 (가중 평균)
        fitness = (components.quality_score * 0.5 + 
                  consistency_score * 0.3 + 
                  quality_compliance * 0.2) * 1000
        
        components.efficiency_score = consistency_score
        components.flexibility_score = quality_compliance
        
        return fitness, components

class MultiObjectiveFunction(ObjectiveFunction):
    """다목적 최적화 함수"""
    
    def __init__(self, production_model: ProductionModel, weights: Dict[str, float]):
        super().__init__(production_model)
        self.weights = weights
        
        # 개별 목적 함수들
        self.cost_objective = CostMinimizationObjective(production_model)
        self.profit_objective = ProfitMaximizationObjective(production_model)
        self.production_objective = ProductionMaximizationObjective(production_model)
        self.quality_objective = QualityOptimizationObjective(production_model)
    
    def evaluate(self, individual) -> Tuple[float, ObjectiveComponents]:
        # 각 목적 함수별 평가
        cost_fitness, cost_components = self.cost_objective.evaluate(individual)
        profit_fitness, profit_components = self.profit_objective.evaluate(individual)
        production_fitness, production_components = self.production_objective.evaluate(individual)
        quality_fitness, quality_components = self.quality_objective.evaluate(individual)
        
        # 결합된 컴포넌트 생성
        combined_components = ObjectiveComponents()
        combined_components.material_cost = cost_components.material_cost
        combined_components.labor_cost = cost_components.labor_cost
        combined_components.operating_cost = cost_components.operating_cost
        combined_components.setup_cost = cost_components.setup_cost
        combined_components.maintenance_cost = cost_components.maintenance_cost
        combined_components.inventory_cost = cost_components.inventory_cost
        combined_components.quality_cost = cost_components.quality_cost
        combined_components.opportunity_cost = cost_components.opportunity_cost
        
        combined_components.revenue = profit_components.revenue
        combined_components.production_volume = production_components.production_volume
        combined_components.quality_score = quality_components.quality_score
        combined_components.efficiency_score = production_components.efficiency_score
        combined_components.flexibility_score = quality_components.flexibility_score
        
        combined_components.calculate_totals()
        
        # 정규화된 점수 계산
        try:
            normalized_scores = self._normalize_scores(
                cost_fitness, profit_fitness, production_fitness, quality_fitness
            )
        except Exception as e:
            # 정규화 실패 시 기본 가중치 사용
            print(f"정규화 실패: {e}, 기본 평가 사용")
            # 간단한 가중 합계로 대체
            fitness = (
                self.weights.get('cost_weight', 0.25) * (-cost_fitness / 1000000) +
                self.weights.get('profit_weight', 0.25) * (profit_fitness / 1000000) +
                self.weights.get('production_weight', 0.25) * (production_fitness / 10000) +
                self.weights.get('quality_weight', 0.25) * (quality_fitness / 1000)
            )
            return fitness, combined_components
        
        # 가중 합계
        fitness = (
            self.weights.get('cost_weight', 0.25) * normalized_scores['cost'] +
            self.weights.get('profit_weight', 0.25) * normalized_scores['profit'] +
            self.weights.get('production_weight', 0.25) * normalized_scores['production'] +
            self.weights.get('quality_weight', 0.25) * normalized_scores['quality']
        )
        
        return fitness, combined_components
    
    def _normalize_scores(self, cost_fitness: float, profit_fitness: float, 
                         production_fitness: float, quality_fitness: float) -> Dict[str, float]:
        """점수 정규화 - 안전한 버전"""
        
        # 항상 기본 정규화 사용 (가장 안전한 방법)
        # 실제 값의 범위를 추정하여 정규화
        
        try:
            # 비용 정규화 (음수 적합도이므로 절댓값 사용)
            cost_normalized = max(0, min(1, abs(cost_fitness) / 10000000))  # 1천만원 기준
            
            # 수익 정규화 (양수 적합도)
            profit_normalized = max(0, min(1, profit_fitness / 5000000))  # 500만원 기준
            
            # 생산량 정규화
            production_normalized = max(0, min(1, production_fitness / 100000))  # 10만개 기준
            
            # 품질 정규화
            quality_normalized = max(0, min(1, quality_fitness / 1000))  # 1000점 기준
            
            return {
                'cost': cost_normalized,
                'profit': profit_normalized,
                'production': production_normalized,
                'quality': quality_normalized
            }
            
        except Exception as e:
            print(f"정규화 중 오류 발생: {e}")
            # 모든 오류를 잡아서 기본값 반환
            return {
                'cost': 0.5,
                'profit': 0.5,
                'production': 0.5,
                'quality': 0.5
            }

class ObjectiveFunctionFactory:
    """목적 함수 팩토리 클래스"""
    
    @staticmethod
    def create_objective_function(optimization_goal: OptimizationGoal, 
                                 production_model: ProductionModel,
                                 weights: Optional[Dict[str, float]] = None) -> ObjectiveFunction:
        """최적화 목표에 따른 목적 함수 생성"""
        
        if optimization_goal == OptimizationGoal.MINIMIZE_COST:
            return CostMinimizationObjective(production_model)
        
        elif optimization_goal == OptimizationGoal.MAXIMIZE_PROFIT:
            return ProfitMaximizationObjective(production_model)
        
        elif optimization_goal == OptimizationGoal.MAXIMIZE_PRODUCTION:
            return ProductionMaximizationObjective(production_model)
        
        elif optimization_goal == OptimizationGoal.OPTIMIZE_QUALITY:
            return QualityOptimizationObjective(production_model)
        
        elif optimization_goal == OptimizationGoal.MULTI_OBJECTIVE:
            if not weights:
                weights = {'cost_weight': 0.25, 'profit_weight': 0.25, 
                          'production_weight': 0.25, 'quality_weight': 0.25}
            
            # 가중치 정규화 (합이 1이 되도록)
            total_weight = sum(weights.values())
            if total_weight != 1.0 and total_weight > 0:
                weights = {k: v/total_weight for k, v in weights.items()}
            
            return MultiObjectiveFunction(production_model, weights)
        
        else:
            raise ValueError(f"지원하지 않는 최적화 목표: {optimization_goal}")