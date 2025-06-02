"""
생산 시스템 모델링 모듈
생산 라인, 제품, 전체 생산 시스템을 모델링하는 클래스들을 정의합니다.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from config import OptimizationGoal, VALIDATION_RULES

@dataclass
class ProductionLine:
    """생산 라인 클래스"""
    line_id: str
    line_name: str
    production_capacity: float  # 개/시간
    operating_cost: float      # 원/시간
    max_working_hours: float   # 시간/일
    defect_rate: float         # 불량률 (0-1)
    investment_cost: float = 0.0     # 설비 투자 비용
    maintenance_cost: float = 0.0    # 월간 유지보수 비용
    compatible_products: List[str] = field(default_factory=list)  # 생산 가능한 제품 ID 목록
    
    def __post_init__(self):
        """데이터 유효성 검사"""
        self._validate_parameters()
    
    def _validate_parameters(self):
        """파라미터 유효성 검사"""
        if not (VALIDATION_RULES['production_capacity']['min'] <= 
                self.production_capacity <= 
                VALIDATION_RULES['production_capacity']['max']):
            raise ValueError(f"생산 능력이 유효 범위를 벗어났습니다: {self.production_capacity}")
        
        if not (VALIDATION_RULES['operating_cost']['min'] <= 
                self.operating_cost <= 
                VALIDATION_RULES['operating_cost']['max']):
            raise ValueError(f"운영 비용이 유효 범위를 벗어났습니다: {self.operating_cost}")
        
        if not (VALIDATION_RULES['working_hours']['min'] <= 
                self.max_working_hours <= 
                VALIDATION_RULES['working_hours']['max']):
            raise ValueError(f"작업 시간이 유효 범위를 벗어났습니다: {self.max_working_hours}")
        
        if not (VALIDATION_RULES['defect_rate']['min'] <= 
                self.defect_rate <= 
                VALIDATION_RULES['defect_rate']['max']):
            raise ValueError(f"불량률이 유효 범위를 벗어났습니다: {self.defect_rate}")
    
    def calculate_daily_capacity(self) -> float:
        """일일 최대 생산 능력 계산"""
        return self.production_capacity * self.max_working_hours
    
    def calculate_effective_capacity(self) -> float:
        """불량률을 고려한 유효 생산 능력 계산"""
        return self.calculate_daily_capacity() * (1 - self.defect_rate)
    
    def calculate_daily_operating_cost(self, working_hours: float) -> float:
        """일일 운영 비용 계산"""
        if working_hours > self.max_working_hours:
            raise ValueError(f"작업 시간이 최대 가동 시간을 초과했습니다: {working_hours}")
        return self.operating_cost * working_hours

@dataclass
class Product:
    """제품 클래스"""
    product_id: str
    product_name: str
    material_cost: float       # 원/개
    selling_price: float       # 원/개
    target_production: float   # 목표 생산량
    min_demand: float = 0.0    # 최소 수요량
    max_defect_rate: float = 0.1  # 최대 허용 불량률
    material_supply_limit: float = float('inf')  # 원자재 공급 제한
    production_times: Dict[str, float] = field(default_factory=dict)  # 라인별 생산 시간 (분/개)
    setup_times: Dict[str, float] = field(default_factory=dict)       # 라인별 셋업 시간 (분)
    setup_costs: Dict[str, float] = field(default_factory=dict)       # 라인별 셋업 비용 (원)
    
    def __post_init__(self):
        """데이터 유효성 검사"""
        self._validate_parameters()
    
    def _validate_parameters(self):
        """파라미터 유효성 검사"""
        if not (VALIDATION_RULES['material_cost']['min'] <= 
                self.material_cost <= 
                VALIDATION_RULES['material_cost']['max']):
            raise ValueError(f"원자재 비용이 유효 범위를 벗어났습니다: {self.material_cost}")
        
        if not (VALIDATION_RULES['selling_price']['min'] <= 
                self.selling_price <= 
                VALIDATION_RULES['selling_price']['max']):
            raise ValueError(f"판매 가격이 유효 범위를 벗어났습니다: {self.selling_price}")
        
        if self.selling_price <= self.material_cost:
            raise ValueError(f"판매 가격이 원자재 비용보다 낮습니다: {self.selling_price} <= {self.material_cost}")
    
    def calculate_unit_profit(self) -> float:
        """단위 이익 계산"""
        return self.selling_price - self.material_cost
    
    def get_production_time(self, line_id: str) -> float:
        """특정 라인에서의 생산 시간 반환 (분/개)"""
        return self.production_times.get(line_id, 0.0)
    
    def get_setup_time(self, line_id: str) -> float:
        """특정 라인에서의 셋업 시간 반환 (분)"""
        return self.setup_times.get(line_id, 0.0)
    
    def get_setup_cost(self, line_id: str) -> float:
        """특정 라인에서의 셋업 비용 반환 (원)"""
        return self.setup_costs.get(line_id, 0.0)

@dataclass
class ProductionConstraints:
    """생산 제약 조건 클래스"""
    total_budget: float = float('inf')        # 총 예산 제한
    labor_limit: int = float('inf')           # 인력 제약
    daily_material_limits: Dict[str, float] = field(default_factory=dict)  # 제품별 일일 원자재 제한
    line_product_compatibility: Dict[str, List[str]] = field(default_factory=dict)  # 라인별 생산 가능 제품
    min_production_requirements: Dict[str, float] = field(default_factory=dict)     # 제품별 최소 생산 요구량

class ProductionModel:
    """전체 생산 시스템 모델 클래스"""
    
    def __init__(self):
        self.production_lines: Dict[str, ProductionLine] = {}
        self.products: Dict[str, Product] = {}
        self.constraints: ProductionConstraints = ProductionConstraints()
        self.optimization_goal: OptimizationGoal = OptimizationGoal.MAXIMIZE_PROFIT
        self.optimization_weights: Dict[str, float] = {}
    
    def add_production_line(self, line: ProductionLine):
        """생산 라인 추가"""
        self.production_lines[line.line_id] = line
    
    def add_product(self, product: Product):
        """제품 추가"""
        self.products[product.product_id] = product
    
    def set_constraints(self, constraints: ProductionConstraints):
        """제약 조건 설정"""
        self.constraints = constraints
    
    def set_optimization_goal(self, goal: OptimizationGoal, weights: Optional[Dict[str, float]] = None):
        """최적화 목표 설정"""
        self.optimization_goal = goal
        if weights:
            self.optimization_weights = weights
    
    def validate_model(self) -> Tuple[bool, List[str]]:
        """모델 유효성 검사"""
        errors = []
        
        # 기본 검사
        if not self.production_lines:
            errors.append("생산 라인이 정의되지 않았습니다.")
        
        if not self.products:
            errors.append("제품이 정의되지 않았습니다.")
        
        # 호환성 검사
        for product_id, product in self.products.items():
            compatible_lines = []
            for line_id, line in self.production_lines.items():
                if product_id in line.compatible_products:
                    compatible_lines.append(line_id)
            
            if not compatible_lines:
                errors.append(f"제품 {product_id}를 생산할 수 있는 라인이 없습니다.")
        
        # 생산 시간 정의 검사
        for product_id, product in self.products.items():
            for line_id in self.production_lines.keys():
                if (line_id in self.production_lines[line_id].compatible_products and 
                    product_id not in product.production_times):
                    errors.append(f"제품 {product_id}의 라인 {line_id}에 대한 생산 시간이 정의되지 않았습니다.")
        
        return len(errors) == 0, errors
    
    def get_model_summary(self) -> Dict[str, Any]:
        """모델 요약 정보 반환"""
        summary = {
            'num_production_lines': len(self.production_lines),
            'num_products': len(self.products),
            'optimization_goal': self.optimization_goal.value,
            'total_capacity': sum(line.calculate_daily_capacity() for line in self.production_lines.values()),
            'total_effective_capacity': sum(line.calculate_effective_capacity() for line in self.production_lines.values()),
            'total_target_production': sum(product.target_production for product in self.products.values()),
            'compatibility_matrix': self._build_compatibility_matrix()
        }
        return summary
    
    def _build_compatibility_matrix(self) -> pd.DataFrame:
        """라인-제품 호환성 매트릭스 생성"""
        lines = list(self.production_lines.keys())
        products = list(self.products.keys())
        
        matrix = pd.DataFrame(0, index=lines, columns=products)
        
        for line_id, line in self.production_lines.items():
            for product_id in line.compatible_products:
                if product_id in products:
                    matrix.loc[line_id, product_id] = 1
        
        return matrix
    
    def calculate_theoretical_max_profit(self) -> float:
        """이론적 최대 이익 계산 (제약 조건 무시)"""
        total_profit = 0
        for product in self.products.values():
            total_profit += product.calculate_unit_profit() * product.target_production
        return total_profit
    
    def calculate_theoretical_min_cost(self) -> float:
        """이론적 최소 비용 계산"""
        total_cost = 0
        for product in self.products.values():
            total_cost += product.material_cost * product.target_production
        
        # 최소 운영 비용 추가 (가장 효율적인 라인 사용 가정)
        for product in self.products.values():
            min_operating_cost = float('inf')
            for line_id, line in self.production_lines.items():
                if product.product_id in line.compatible_products:
                    production_time = product.get_production_time(line_id) / 60  # 시간 단위로 변환
                    cost = line.operating_cost * production_time * product.target_production
                    min_operating_cost = min(min_operating_cost, cost)
            
            if min_operating_cost != float('inf'):
                total_cost += min_operating_cost
        
        return total_cost