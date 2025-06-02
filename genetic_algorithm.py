"""
유전 알고리즘 엔진 모듈
생산 최적화를 위한 유전 알고리즘을 구현합니다.
웹버전의 구체적인 분석 기능을 반영하여 개선된 버전입니다.
"""

import numpy as np
import random
from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy

from config import DEFAULT_GA_PARAMS, SelectionMethod, OptimizationGoal, ConstraintHandling
from production_model import ProductionModel, ProductionLine, Product
from objective_functions import ObjectiveFunctionFactory, ObjectiveComponents
from constraint_handler import AdvancedConstraintHandler

@dataclass
class GAResult:
    """유전 알고리즘 실행 결과"""
    best_solution: 'Individual'
    best_fitness: float
    fitness_history: List[float]
    generation_count: int
    convergence_generation: int
    execution_time: float
    success: bool
    error_message: str = ""
    detailed_analysis: Optional[Dict[str, Any]] = None

class Individual:
    """유전 알고리즘의 개체(염색체) 클래스"""
    
    def __init__(self, production_model: ProductionModel):
        self.production_model = production_model
        self.genes: Dict[str, Dict[str, float]] = {}  # {line_id: {product_id: production_amount}}
        self.fitness: float = 0.0
        self.fitness_components: Dict[str, float] = {}
        self.is_feasible: bool = True
        self.constraint_violations: List[str] = []
        
        # 염색체 초기화
        self._initialize_genes()
    
    def _initialize_genes(self):
        """염색체 초기화 - 랜덤하게 생산량 할당"""
        for line_id, line in self.production_model.production_lines.items():
            self.genes[line_id] = {}
            for product_id in line.compatible_products:
                if product_id in self.production_model.products:
                    # 0과 라인 최대 생산능력 사이의 랜덤 값
                    max_capacity = line.calculate_effective_capacity()
                    self.genes[line_id][product_id] = random.uniform(0, max_capacity * 0.1)
    
    def get_total_production(self, product_id: str) -> float:
        """특정 제품의 총 생산량 계산"""
        total = 0.0
        for line_id, production_dict in self.genes.items():
            total += production_dict.get(product_id, 0.0)
        return total
    
    def get_line_utilization(self, line_id: str) -> float:
        """특정 라인의 가동률 계산"""
        line = self.production_model.production_lines[line_id]
        total_time_needed = 0.0
        
        for product_id, production_amount in self.genes[line_id].items():
            if product_id in self.production_model.products:
                product = self.production_model.products[product_id]
                production_time_per_unit = product.get_production_time(line_id) / 60  # 시간 단위
                total_time_needed += production_amount * production_time_per_unit
        
        return min(total_time_needed / line.max_working_hours, 1.0)
    
    def calculate_total_cost(self) -> float:
        """총 비용 계산"""
        total_cost = 0.0
        
        # 원자재 비용
        for product_id, product in self.production_model.products.items():
            total_production = self.get_total_production(product_id)
            total_cost += total_production * product.material_cost
        
        # 운영 비용
        for line_id, line in self.production_model.production_lines.items():
            utilization = self.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            total_cost += working_hours * line.operating_cost
        
        # 셋업 비용 (간소화 - 제품이 생산되면 셋업 비용 발생)
        for line_id, production_dict in self.genes.items():
            for product_id, production_amount in production_dict.items():
                if production_amount > 0:
                    product = self.production_model.products[product_id]
                    total_cost += product.get_setup_cost(line_id)
        
        return total_cost
    
    def calculate_total_revenue(self) -> float:
        """총 수익 계산"""
        total_revenue = 0.0
        for product_id, product in self.production_model.products.items():
            total_production = self.get_total_production(product_id)
            total_revenue += total_production * product.selling_price
        return total_revenue
    
    def calculate_total_production_amount(self) -> float:
        """총 생산량 계산"""
        total = 0.0
        for product_id in self.production_model.products.keys():
            total += self.get_total_production(product_id)
        return total
    
    def check_constraints(self) -> Tuple[bool, List[str]]:
        """제약 조건 검사 (호환성을 위해 유지, 실제로는 AdvancedConstraintHandler 사용)"""
        # 이 메서드는 호환성을 위해 유지하지만, 실제 제약 조건 검사는 
        # FitnessEvaluator의 AdvancedConstraintHandler에서 수행됩니다.
        return self.is_feasible, self.constraint_violations
    
    # ==============================================
    # 🎯 새로운 구체적인 분석 메서드들 (웹버전에서 이식)
    # ==============================================
    
    def get_detailed_production_plan(self) -> Dict[str, Any]:
        """구체적인 생산 계획 생성 - 어디서 무엇을 얼마나"""
        plan = {
            "line_by_line": {},  # 라인별 상세 계획
            "product_by_product": {},  # 제품별 상세 계획
            "summary": {}  # 요약
        }
        
        # 1. 라인별 상세 계획
        for line_id, line in self.production_model.production_lines.items():
            line_plan = {
                "line_name": line.line_name,
                "line_id": line_id,
                "products": {},
                "total_working_time": 0,
                "total_production": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "utilization_rate": 0
            }
            
            if line_id in self.genes:
                total_time = 0
                total_production = 0
                total_revenue = 0
                
                for product_id, production_amount in self.genes[line_id].items():
                    if production_amount > 0 and product_id in self.production_model.products:
                        product = self.production_model.products[product_id]
                        production_time_per_unit = product.get_production_time(line_id) / 60  # 분->시간
                        
                        product_info = {
                            "product_name": product.product_name,
                            "product_id": product_id,
                            "production_amount": round(production_amount, 1),
                            "time_per_unit_minutes": product.get_production_time(line_id),
                            "total_time_hours": round(production_amount * production_time_per_unit, 2),
                            "revenue": round(production_amount * product.selling_price, 0),
                            "material_cost": round(production_amount * product.material_cost, 0),
                            "profit": round(production_amount * (product.selling_price - product.material_cost), 0)
                        }
                        
                        line_plan["products"][product.product_name] = product_info
                        total_time += product_info["total_time_hours"]
                        total_production += production_amount
                        total_revenue += product_info["revenue"]
                
                line_plan["total_working_time"] = round(total_time, 2)
                line_plan["total_production"] = round(total_production, 1)
                line_plan["total_revenue"] = round(total_revenue, 0)
                line_plan["total_cost"] = round(total_time * line.operating_cost, 0)
                line_plan["utilization_rate"] = round((total_time / line.max_working_hours) * 100, 1) if line.max_working_hours > 0 else 0
            
            plan["line_by_line"][line.line_name] = line_plan
        
        # 2. 제품별 상세 계획
        for product_id, product in self.production_model.products.items():
            product_plan = {
                "product_name": product.product_name,
                "product_id": product_id,
                "target_production": product.target_production,
                "lines": {},
                "total_production": 0,
                "achievement_rate": 0,
                "total_revenue": 0,
                "total_profit": 0,
                "best_line": None
            }
            
            total_production = 0
            line_productions = []
            
            for line_id, line in self.production_model.production_lines.items():
                if line_id in self.genes and product_id in self.genes[line_id]:
                    production = self.genes[line_id][product_id]
                    if production > 0:
                        line_info = {
                            "line_name": line.line_name,
                            "line_id": line_id,
                            "production_amount": round(production, 1),
                            "time_per_unit_minutes": product.get_production_time(line_id),
                            "total_time_hours": round(production * product.get_production_time(line_id) / 60, 2),
                            "efficiency_score": round(production / (product.get_production_time(line_id) / 60), 1)
                        }
                        product_plan["lines"][line.line_name] = line_info
                        total_production += production
                        line_productions.append((line.line_name, production))
            
            product_plan["total_production"] = round(total_production, 1)
            product_plan["achievement_rate"] = round((total_production / product.target_production) * 100, 1) if product.target_production > 0 else 0
            product_plan["total_revenue"] = round(total_production * product.selling_price, 0)
            product_plan["total_profit"] = round(total_production * (product.selling_price - product.material_cost), 0)
            
            # 최고 생산 라인 찾기
            if line_productions:
                product_plan["best_line"] = max(line_productions, key=lambda x: x[1])[0]
            
            plan["product_by_product"][product.product_name] = product_plan
        
        return plan
    
    def get_production_schedule(self) -> Dict[str, Any]:
        """생산 스케줄 생성 - 언제 무엇을 만들지"""
        schedule = {
            "daily_schedule": {},
            "production_sequence": {},
            "bottlenecks": []
        }
        
        # 각 라인별 일일 스케줄
        for line_id, line in self.production_model.production_lines.items():
            if line_id not in self.genes:
                continue
                
            line_schedule = {
                "line_name": line.line_name,
                "line_id": line_id,
                "max_hours": line.max_working_hours,
                "products_sequence": [],
                "total_scheduled_hours": 0,
                "idle_time": 0
            }
            
            # 수익성 순으로 제품 정렬 (높은 마진 제품 먼저)
            products_in_line = []
            for product_id, production_amount in self.genes[line_id].items():
                if production_amount > 0 and product_id in self.production_model.products:
                    product = self.production_model.products[product_id]
                    unit_profit = product.selling_price - product.material_cost
                    products_in_line.append((product, production_amount, unit_profit))
            
            # 수익성 높은 순으로 정렬
            products_in_line.sort(key=lambda x: x[2], reverse=True)
            
            current_hour = 0
            for product, production_amount, unit_profit in products_in_line:
                time_per_unit = product.get_production_time(line_id) / 60
                total_time = production_amount * time_per_unit
                
                if current_hour + total_time <= line.max_working_hours:
                    line_schedule["products_sequence"].append({
                        "product_name": product.product_name,
                        "start_hour": round(current_hour, 1),
                        "end_hour": round(current_hour + total_time, 1),
                        "production_amount": round(production_amount, 1),
                        "unit_profit": round(unit_profit, 0)
                    })
                    current_hour += total_time
            
            line_schedule["total_scheduled_hours"] = round(current_hour, 1)
            line_schedule["idle_time"] = round(line.max_working_hours - current_hour, 1)
            
            # 병목 감지 (가동률 90% 이상)
            utilization = (current_hour / line.max_working_hours) * 100
            if utilization >= 90:
                schedule["bottlenecks"].append({
                    "line_name": line.line_name,
                    "utilization": round(utilization, 1),
                    "issue": "고가동률 병목"
                })
            
            schedule["daily_schedule"][line.line_name] = line_schedule
        
        return schedule
    
    def get_resource_utilization_analysis(self) -> Dict[str, Any]:
        """자원 활용도 분석"""
        analysis = {
            "efficiency_scores": {},
            "capacity_analysis": {},
            "recommendations": []
        }
        
        # 라인별 효율성 분석
        for line_id, line in self.production_model.production_lines.items():
            utilization = self.get_line_utilization(line_id) * 100
            
            # 수익성 계산
            line_revenue = 0
            line_cost = (utilization / 100) * line.max_working_hours * line.operating_cost
            
            if line_id in self.genes:
                for product_id, production_amount in self.genes[line_id].items():
                    if product_id in self.production_model.products:
                        product = self.production_model.products[product_id]
                        line_revenue += production_amount * product.selling_price
            
            efficiency_score = (line_revenue - line_cost) / line_cost * 100 if line_cost > 0 else 0
            
            status = "개선필요"
            if utilization >= 80 and efficiency_score >= 150:
                status = "효율적"
            elif utilization >= 60 and efficiency_score >= 100:
                status = "양호"
            elif utilization >= 40 or efficiency_score >= 50:
                status = "보통"
            
            analysis["efficiency_scores"][line.line_name] = {
                "utilization_rate": round(utilization, 1),
                "efficiency_score": round(efficiency_score, 1),
                "revenue_per_hour": round(line_revenue / (utilization / 100 * line.max_working_hours), 0) if utilization > 0 else 0,
                "status": status
            }
            
            # 추천 사항 생성
            if utilization < 50:
                analysis["recommendations"].append(f"📈 {line.line_name}: 낮은 가동률({utilization:.1f}%) - 생산량 증대 가능")
            elif utilization > 95:
                analysis["recommendations"].append(f"⚡ {line.line_name}: 고가동률({utilization:.1f}%) - 용량 확장 검토 필요")
            
            if efficiency_score < 100:
                analysis["recommendations"].append(f"💰 {line.line_name}: 낮은 효율성({efficiency_score:.1f}%) - 수익성 높은 제품 집중 권장")
        
        return analysis
    
    def get_profitability_analysis(self) -> Dict[str, Any]:
        """수익성 분석"""
        analysis = {
            "product_profitability": {},
            "line_profitability": {},
            "optimization_insights": []
        }
        
        # 제품별 수익성
        product_profits = []
        
        for product_id, product in self.production_model.products.items():
            total_production = self.get_total_production(product_id)
            unit_profit = product.selling_price - product.material_cost
            total_profit = total_production * unit_profit
            
            product_data = {
                "unit_profit": round(unit_profit, 0),
                "total_production": round(total_production, 1),
                "total_profit": round(total_profit, 0),
                "profit_margin": round((unit_profit / product.selling_price) * 100, 1),
                "ranking": 0
            }
            
            analysis["product_profitability"][product.product_name] = product_data
            product_profits.append((product.product_name, total_profit))
        
        # 수익성 랭킹
        product_profits.sort(key=lambda x: x[1], reverse=True)
        for i, (product_name, _) in enumerate(product_profits):
            analysis["product_profitability"][product_name]["ranking"] = i + 1
        
        # 라인별 수익성
        for line_id, line in self.production_model.production_lines.items():
            line_revenue = 0
            line_cost = self.get_line_utilization(line_id) * line.max_working_hours * line.operating_cost
            
            if line_id in self.genes:
                for product_id, production_amount in self.genes[line_id].items():
                    if product_id in self.production_model.products:
                        product = self.production_model.products[product_id]
                        line_revenue += production_amount * product.selling_price
            
            analysis["line_profitability"][line.line_name] = {
                "revenue": round(line_revenue, 0),
                "cost": round(line_cost, 0),
                "profit": round(line_revenue - line_cost, 0)
            }
        
        # 인사이트 생성
        if product_profits:
            best_product = product_profits[0][0]
            worst_product = product_profits[-1][0]
            
            analysis["optimization_insights"].append(f"🏆 최고 수익 제품: {best_product}")
            analysis["optimization_insights"].append(f"🔧 개선 필요 제품: {worst_product}")
            
            total_profit = sum(p[1] for p in product_profits)
            best_profit = product_profits[0][1]
            
            if best_profit / total_profit > 0.5:
                analysis["optimization_insights"].append(f"🎯 {best_product}에 생산 집중 권장")
            else:
                analysis["optimization_insights"].append("📊 다양한 제품 포트폴리오 전략")
        
        return analysis

class FitnessEvaluator:
    """적합도 평가 클래스"""
    
    def __init__(self, production_model: ProductionModel, constraint_handling: ConstraintHandling = ConstraintHandling.PENALTY_FUNCTION):
        self.production_model = production_model
        self.constraint_handling = constraint_handling
        
        # 고급 목적 함수 생성
        self.objective_function = ObjectiveFunctionFactory.create_objective_function(
            production_model.optimization_goal,
            production_model,
            production_model.optimization_weights
        )
        
        # 고급 제약 조건 처리기 생성
        self.constraint_handler = AdvancedConstraintHandler(production_model, constraint_handling)
    
    def evaluate(self, individual: Individual) -> float:
        """개체의 적합도 평가"""
        # 고급 목적 함수로 기본 적합도 계산
        objective_fitness, objective_components = self.objective_function.evaluate(individual)
        
        # 고급 제약 조건 검사
        is_feasible, violations, total_penalty = self.constraint_handler.check_all_constraints(individual)
        
        # 제약 조건 처리 방법에 따른 적합도 조정
        if self.constraint_handling == ConstraintHandling.DEATH_PENALTY:
            # 제약 조건 위반 시 매우 낮은 적합도
            if not is_feasible:
                fitness = -1e6
            else:
                fitness = objective_fitness
        
        elif self.constraint_handling == ConstraintHandling.REPAIR_ALGORITHM:
            # 제약 조건 위반 시 복구 시도
            if not is_feasible:
                self.constraint_handler.repair_violations(individual, violations)
                # 복구 후 재평가
                is_feasible, violations, total_penalty = self.constraint_handler.check_all_constraints(individual)
                objective_fitness, objective_components = self.objective_function.evaluate(individual)
            
            fitness = objective_fitness - total_penalty * 0.1  # 적은 페널티
        
        else:  # PENALTY_FUNCTION (기본값)
            # 페널티 함수 방법
            fitness = objective_fitness - total_penalty
        
        # Individual 객체 업데이트
        individual.fitness = fitness
        individual.is_feasible = is_feasible
        individual.constraint_violations = [v.description for v in violations]
        individual.fitness_components = self._convert_components_to_dict(objective_components, violations)
        
        return fitness
    
    def _convert_components_to_dict(self, components: ObjectiveComponents, violations: List) -> Dict[str, float]:
        """ObjectiveComponents를 딕셔너리로 변환"""
        return {
            'material_cost': components.material_cost,
            'labor_cost': components.labor_cost,
            'operating_cost': components.operating_cost,
            'setup_cost': components.setup_cost,
            'maintenance_cost': components.maintenance_cost,
            'inventory_cost': components.inventory_cost,
            'quality_cost': components.quality_cost,
            'opportunity_cost': components.opportunity_cost,
            'total_cost': components.total_cost,
            'revenue': components.revenue,
            'total_profit': components.total_profit,
            'production_volume': components.production_volume,
            'quality_score': components.quality_score,
            'efficiency_score': components.efficiency_score,
            'flexibility_score': components.flexibility_score,
            'constraint_violations': len(violations),
            'is_feasible': len(violations) == 0
        }
    
    def update_normalization_factors(self, population: List[Individual]):
        """정규화 인수 업데이트 (다목적 최적화용)"""
        if hasattr(self.objective_function, 'calculate_normalization_factors'):
            self.objective_function.calculate_normalization_factors(population)

class GeneticAlgorithm:
    """유전 알고리즘 메인 클래스"""
    
    def __init__(self, production_model: ProductionModel, ga_params: Optional[Dict] = None):
        self.production_model = production_model
        self.params = {**DEFAULT_GA_PARAMS, **(ga_params or {})}
        
        # 제약 조건 처리 방법 설정
        constraint_handling = self.params.get('constraint_handling', ConstraintHandling.PENALTY_FUNCTION)
        self.fitness_evaluator = FitnessEvaluator(production_model, constraint_handling)
        
        self.population: List[Individual] = []
        self.fitness_history: List[float] = []
        self.best_individual: Optional[Individual] = None
    
    def initialize_population(self):
        """초기 개체군 생성"""
        self.population = []
        for _ in range(self.params['population_size']):
            individual = Individual(self.production_model)
            self.fitness_evaluator.evaluate(individual)
            self.population.append(individual)
        
        # 최적 개체 찾기
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.best_individual = copy.deepcopy(self.population[0])
        
        # 다목적 최적화의 경우 정규화 인수 업데이트
        if self.production_model.optimization_goal == OptimizationGoal.MULTI_OBJECTIVE:
            self.fitness_evaluator.update_normalization_factors(self.population)
    
    def selection(self, population: List[Individual]) -> List[Individual]:
        """선택 연산"""
        method = self.params['selection_method']
        selected = []
        
        if method == SelectionMethod.TOURNAMENT:
            tournament_size = self.params.get('tournament_size', 3)
            for _ in range(len(population)):
                tournament = random.sample(population, min(tournament_size, len(population)))
                winner = max(tournament, key=lambda x: x.fitness)
                selected.append(copy.deepcopy(winner))
        
        elif method == SelectionMethod.ROULETTE_WHEEL:
            # 적합도가 음수일 수 있으므로 최소값을 0으로 조정
            fitnesses = [ind.fitness for ind in population]
            min_fitness = min(fitnesses)
            adjusted_fitnesses = [f - min_fitness + 1 for f in fitnesses]
            total_fitness = sum(adjusted_fitnesses)
            
            for _ in range(len(population)):
                pick = random.uniform(0, total_fitness)
                current = 0
                for i, fitness in enumerate(adjusted_fitnesses):
                    current += fitness
                    if current >= pick:
                        selected.append(copy.deepcopy(population[i]))
                        break
        
        else:  # RANK_BASED
            sorted_pop = sorted(population, key=lambda x: x.fitness)
            ranks = list(range(1, len(population) + 1))
            total_rank = sum(ranks)
            
            for _ in range(len(population)):
                pick = random.uniform(0, total_rank)
                current = 0
                for i, rank in enumerate(ranks):
                    current += rank
                    if current >= pick:
                        selected.append(copy.deepcopy(sorted_pop[i]))
                        break
        
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """교차 연산"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # 단순 산술 교차
        alpha = random.uniform(0.3, 0.7)
        
        for line_id in child1.genes:
            for product_id in child1.genes[line_id]:
                val1 = parent1.genes[line_id][product_id]
                val2 = parent2.genes[line_id][product_id]
                
                child1.genes[line_id][product_id] = alpha * val1 + (1 - alpha) * val2
                child2.genes[line_id][product_id] = (1 - alpha) * val1 + alpha * val2
        
        return child1, child2
    
    def mutation(self, individual: Individual) -> Individual:
        """돌연변이 연산"""
        mutated = copy.deepcopy(individual)
        mutation_rate = self.params['mutation_rate']
        
        for line_id in mutated.genes:
            for product_id in mutated.genes[line_id]:
                if random.random() < mutation_rate:
                    # 가우시안 돌연변이
                    current_value = mutated.genes[line_id][product_id]
                    line = self.production_model.production_lines[line_id]
                    max_capacity = line.calculate_effective_capacity()
                    
                    # 표준편차는 최대 용량의 10%
                    sigma = max_capacity * 0.1
                    new_value = current_value + random.gauss(0, sigma)
                    
                    # 값의 범위 제한 (0 이상, 최대 용량 이하)
                    mutated.genes[line_id][product_id] = max(0, min(new_value, max_capacity))
        
        return mutated
    
    def _create_detailed_analysis(self) -> Dict[str, Any]:
        """상세 분석 데이터 생성 - 웹버전 스타일로 개선"""
        if not self.best_individual:
            return {}
        
        # 🚀 구체적인 분석 정보 생성
        analysis = {
            "detailed_production_plan": self.best_individual.get_detailed_production_plan(),
            "production_schedule": self.best_individual.get_production_schedule(),
            "resource_utilization": self.best_individual.get_resource_utilization_analysis(),
            "profitability_analysis": self.best_individual.get_profitability_analysis(),
            "recommendations": self._generate_comprehensive_recommendations(),
            "executive_summary": self._generate_executive_summary()
        }
        
        return analysis
    
    def _generate_comprehensive_recommendations(self) -> List[str]:
        """종합적인 개선 추천사항 생성"""
        recommendations = []
        
        if not self.best_individual:
            return recommendations
        
        # 1. 제약 조건 위반 처리
        if not self.best_individual.is_feasible:
            recommendations.append("⚠️ 제약 조건 위반 해결 우선")
            for violation in self.best_individual.constraint_violations[:3]:  # 상위 3개만
                recommendations.append(f"   • {violation}")
        
        # 2. 생산량 분석
        total_target = sum(p.target_production for p in self.production_model.products.values())
        total_actual = self.best_individual.calculate_total_production_amount()
        
        if total_actual < total_target * 0.8:
            recommendations.append("📈 전체 생산량이 목표 대비 80% 미만 - 생산 능력 확장 검토")
        
        # 3. 라인별 추천사항
        resource_analysis = self.best_individual.get_resource_utilization_analysis()
        recommendations.extend(resource_analysis.get("recommendations", []))
        
        # 4. 제품별 추천사항
        profitability = self.best_individual.get_profitability_analysis()
        recommendations.extend(profitability.get("optimization_insights", []))
        
        return recommendations
    
    def _generate_executive_summary(self) -> Dict[str, Any]:
        """경영진을 위한 요약 정보"""
        if not self.best_individual:
            return {}
        
        total_revenue = self.best_individual.calculate_total_revenue()
        total_cost = self.best_individual.calculate_total_cost()
        total_profit = total_revenue - total_cost
        
        # 주요 성과 지표
        summary = {
            "key_metrics": {
                "total_profit": f"{total_profit:,.0f}원",
                "profit_margin": f"{(total_profit/total_revenue*100):.1f}%" if total_revenue > 0 else "0%",
                "total_production": f"{self.best_individual.calculate_total_production_amount():.0f}개",
                "feasibility": "실행 가능" if self.best_individual.is_feasible else "제약 조건 위반"
            },
            "top_priorities": [],
            "quick_wins": []
        }
        
        # 최우선 과제
        if not self.best_individual.is_feasible:
            summary["top_priorities"].append("제약 조건 위반 해결")
        
        # 수익성 분석에서 우선순위 추출
        profitability = self.best_individual.get_profitability_analysis()
        if profitability.get("optimization_insights"):
            summary["top_priorities"].extend(profitability["optimization_insights"][:2])
        
        # 빠른 개선 방안
        resource_analysis = self.best_individual.get_resource_utilization_analysis()
        for line_name, metrics in resource_analysis.get("efficiency_scores", {}).items():
            if metrics["utilization_rate"] < 50:
                summary["quick_wins"].append(f"{line_name} 라인 가동률 향상")
        
        return summary
    
    def run(self) -> GAResult:
        """유전 알고리즘 실행"""
        import time
        start_time = time.time()
        
        try:
            # 초기화
            self.initialize_population()
            self.fitness_history = [self.best_individual.fitness]
            
            convergence_generation = 0
            no_improvement_count = 0
            
            for generation in range(self.params['generations']):
                # 선택
                selected = self.selection(self.population)
                
                # 교차 및 돌연변이
                new_population = []
                
                # 엘리트 보존
                elite_count = int(len(self.population) * self.params['elite_ratio'])
                elite = sorted(self.population, key=lambda x: x.fitness, reverse=True)[:elite_count]
                new_population.extend(elite)
                
                # 나머지 개체 생성
                while len(new_population) < self.params['population_size']:
                    parent1 = random.choice(selected)
                    parent2 = random.choice(selected)
                    
                    if random.random() < self.params['crossover_rate']:
                        child1, child2 = self.crossover(parent1, parent2)
                    else:
                        child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
                    
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    
                    self.fitness_evaluator.evaluate(child1)
                    self.fitness_evaluator.evaluate(child2)
                    
                    new_population.extend([child1, child2])
                
                # 개체수 조정
                new_population = new_population[:self.params['population_size']]
                self.population = new_population
                
                # 최적 개체 업데이트
                current_best = max(self.population, key=lambda x: x.fitness)
                if current_best.fitness > self.best_individual.fitness:
                    self.best_individual = copy.deepcopy(current_best)
                    convergence_generation = generation
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1
                
                self.fitness_history.append(self.best_individual.fitness)
                
                # 조기 종료 조건 (100세대 동안 개선 없음)
                if no_improvement_count >= 100:
                    break
            
            execution_time = time.time() - start_time
            
            return GAResult(
                best_solution=self.best_individual,
                best_fitness=self.best_individual.fitness,
                fitness_history=self.fitness_history,
                generation_count=generation + 1,
                convergence_generation=convergence_generation,
                execution_time=execution_time,
                success=True,
                detailed_analysis=self._create_detailed_analysis()
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return GAResult(
                best_solution=None,
                best_fitness=float('-inf'),
                fitness_history=self.fitness_history,
                generation_count=0,
                convergence_generation=0,
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
