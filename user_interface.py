"""
사용자 인터페이스 모듈
사용자 입력 처리 및 대화형 인터페이스를 제공합니다.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import asdict

from config import (
    OptimizationGoal, SelectionMethod, DEFAULT_GA_PARAMS, 
    VALIDATION_RULES, ERROR_MESSAGES, SUCCESS_MESSAGES, SYSTEM_LIMITS
)
from production_model import ProductionModel, ProductionLine, Product, ProductionConstraints

class InputValidator:
    """입력 데이터 유효성 검사 클래스"""
    
    @staticmethod
    def validate_numeric_input(value: str, field_name: str, min_val: float = None, max_val: float = None) -> Tuple[bool, float, str]:
        """숫자 입력 유효성 검사"""
        try:
            numeric_value = float(value)
            
            if min_val is not None and numeric_value < min_val:
                return False, 0, f"{field_name}: 최소값 {min_val} 이상이어야 합니다."
            
            if max_val is not None and numeric_value > max_val:
                return False, 0, f"{field_name}: 최대값 {max_val} 이하여야 합니다."
            
            return True, numeric_value, ""
        
        except ValueError:
            return False, 0, f"{field_name}: 유효한 숫자를 입력해주세요."
    
    @staticmethod
    def validate_string_input(value: str, field_name: str, min_length: int = 1) -> Tuple[bool, str, str]:
        """문자열 입력 유효성 검사"""
        if len(value.strip()) < min_length:
            return False, "", f"{field_name}: 최소 {min_length}자 이상 입력해주세요."
        
        return True, value.strip(), ""
    
    @staticmethod
    def validate_production_line_data(line_data: Dict) -> Tuple[bool, List[str]]:
        """생산 라인 데이터 유효성 검사"""
        errors = []
        required_fields = ['line_id', 'line_name', 'production_capacity', 'operating_cost', 'max_working_hours', 'defect_rate']
        
        for field in required_fields:
            if field not in line_data:
                errors.append(f"필수 필드 누락: {field}")
        
        if errors:
            return False, errors
        
        # 숫자 필드 검사
        numeric_fields = {
            'production_capacity': VALIDATION_RULES['production_capacity'],
            'operating_cost': VALIDATION_RULES['operating_cost'],
            'max_working_hours': VALIDATION_RULES['working_hours'],
            'defect_rate': VALIDATION_RULES['defect_rate']
        }
        
        for field, rules in numeric_fields.items():
            try:
                value = float(line_data[field])
                if not (rules['min'] <= value <= rules['max']):
                    errors.append(f"{field}: {rules['min']} ~ {rules['max']} 범위의 값이어야 합니다.")
            except (ValueError, TypeError):
                errors.append(f"{field}: 유효한 숫자여야 합니다.")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_product_data(product_data: Dict) -> Tuple[bool, List[str]]:
        """제품 데이터 유효성 검사"""
        errors = []
        required_fields = ['product_id', 'product_name', 'material_cost', 'selling_price', 'target_production']
        
        for field in required_fields:
            if field not in product_data:
                errors.append(f"필수 필드 누락: {field}")
        
        if errors:
            return False, errors
        
        # 숫자 필드 검사
        numeric_fields = {
            'material_cost': VALIDATION_RULES['material_cost'],
            'selling_price': VALIDATION_RULES['selling_price'],
            'target_production': VALIDATION_RULES['target_production']
        }
        
        for field, rules in numeric_fields.items():
            try:
                value = float(product_data[field])
                if not (rules['min'] <= value <= rules['max']):
                    errors.append(f"{field}: {rules['min']} ~ {rules['max']} 범위의 값이어야 합니다.")
            except (ValueError, TypeError):
                errors.append(f"{field}: 유효한 숫자여야 합니다.")
        
        # 판매가격이 원자재 비용보다 높은지 확인
        try:
            if float(product_data['selling_price']) <= float(product_data['material_cost']):
                errors.append("판매 가격이 원자재 비용보다 높아야 합니다.")
        except (ValueError, TypeError):
            pass  # 이미 위에서 숫자 형식 오류 검사함
        
        return len(errors) == 0, errors

class DataInputHandler:
    """데이터 입력 처리 클래스"""
    
    def __init__(self):
        self.validator = InputValidator()
    
    def get_basic_settings(self) -> Dict[str, Any]:
        """기본 설정 입력 받기"""
        print("\n=== 생산 최적화 시스템 기본 설정 ===")
        
        settings = {}
        
        # 생산 라인 수
        while True:
            try:
                line_count = int(input(f"생산 라인 수 (1-{SYSTEM_LIMITS['max_production_lines']}): "))
                if 1 <= line_count <= SYSTEM_LIMITS['max_production_lines']:
                    settings['line_count'] = line_count
                    break
                else:
                    print(f"1부터 {SYSTEM_LIMITS['max_production_lines']} 사이의 값을 입력해주세요.")
            except ValueError:
                print("유효한 정수를 입력해주세요.")
        
        # 제품 종류 수
        while True:
            try:
                product_count = int(input(f"제품 종류 수 (1-{SYSTEM_LIMITS['max_products']}): "))
                if 1 <= product_count <= SYSTEM_LIMITS['max_products']:
                    settings['product_count'] = product_count
                    break
                else:
                    print(f"1부터 {SYSTEM_LIMITS['max_products']} 사이의 값을 입력해주세요.")
            except ValueError:
                print("유효한 정수를 입력해주세요.")
        
        # 최적화 기간
        print("\n최적화 기간을 선택하세요:")
        print("1. 일간")
        print("2. 주간")
        print("3. 월간")
        
        while True:
            try:
                period_choice = int(input("선택 (1-3): "))
                if period_choice == 1:
                    settings['optimization_period'] = 'daily'
                    break
                elif period_choice == 2:
                    settings['optimization_period'] = 'weekly'
                    break
                elif period_choice == 3:
                    settings['optimization_period'] = 'monthly'
                    break
                else:
                    print("1, 2, 3 중에서 선택해주세요.")
            except ValueError:
                print("유효한 숫자를 입력해주세요.")
        
        # 최적화 목표
        print("\n최적화 목표를 선택하세요:")
        goals = list(OptimizationGoal)
        for i, goal in enumerate(goals, 1):
            goal_name = {
                OptimizationGoal.MINIMIZE_COST: "비용 최소화",
                OptimizationGoal.MAXIMIZE_PRODUCTION: "생산량 최대화",
                OptimizationGoal.MAXIMIZE_PROFIT: "수익 최대화",
                OptimizationGoal.MULTI_OBJECTIVE: "복합 목표",
                OptimizationGoal.OPTIMIZE_QUALITY: "품질 최적화"
            }[goal]
            print(f"{i}. {goal_name}")
        
        while True:
            try:
                goal_choice = int(input(f"선택 (1-{len(goals)}): "))
                if 1 <= goal_choice <= len(goals):
                    settings['optimization_goal'] = goals[goal_choice - 1]
                    break
                else:
                    print(f"1부터 {len(goals)} 사이의 값을 입력해주세요.")
            except ValueError:
                print("유효한 숫자를 입력해주세요.")
        
        # 복합 목표인 경우 가중치 설정
        if settings['optimization_goal'] == OptimizationGoal.MULTI_OBJECTIVE:
            print("\n가중치를 설정하세요 (총합이 1이 되도록):")
            
            while True:
                try:
                    cost_weight = float(input("비용 가중치 (0-1): "))
                    production_weight = float(input("생산량 가중치 (0-1): "))
                    quality_weight = float(input("품질 가중치 (0-1): "))
                    
                    total = cost_weight + production_weight + quality_weight
                    if abs(total - 1.0) < 0.01:  # 부동소수점 오차 허용
                        settings['weights'] = {
                            'cost_weight': cost_weight,
                            'production_weight': production_weight,
                            'quality_weight': quality_weight
                        }
                        break
                    else:
                        print(f"가중치의 합이 1이 되어야 합니다. 현재 합계: {total:.3f}")
                except ValueError:
                    print("유효한 숫자를 입력해주세요.")
        
        return settings
    
    def get_production_line_data(self, line_count: int) -> List[ProductionLine]:
        """생산 라인 데이터 입력 받기"""
        print(f"\n=== 생산 라인 정보 입력 ({line_count}개) ===")
        
        production_lines = []
        
        for i in range(line_count):
            print(f"\n--- 라인 {i+1} ---")
            
            while True:
                line_data = {}
                
                # 라인 ID
                line_data['line_id'] = input("라인 ID: ").strip()
                if not line_data['line_id']:
                    print("라인 ID를 입력해주세요.")
                    continue
                
                # 라인 이름
                line_data['line_name'] = input("라인 이름: ").strip()
                if not line_data['line_name']:
                    print("라인 이름을 입력해주세요.")
                    continue
                
                # 시간당 생산 능력
                capacity_input = input("시간당 생산 능력 (개/시간): ")
                is_valid, capacity, error = self.validator.validate_numeric_input(
                    capacity_input, "생산 능력", 
                    VALIDATION_RULES['production_capacity']['min'],
                    VALIDATION_RULES['production_capacity']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                line_data['production_capacity'] = capacity
                
                # 시간당 운영 비용
                cost_input = input("시간당 운영 비용 (원/시간): ")
                is_valid, cost, error = self.validator.validate_numeric_input(
                    cost_input, "운영 비용",
                    VALIDATION_RULES['operating_cost']['min'],
                    VALIDATION_RULES['operating_cost']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                line_data['operating_cost'] = cost
                
                # 일일 최대 가동 시간
                hours_input = input("일일 최대 가동 시간: ")
                is_valid, hours, error = self.validator.validate_numeric_input(
                    hours_input, "가동 시간",
                    VALIDATION_RULES['working_hours']['min'],
                    VALIDATION_RULES['working_hours']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                line_data['max_working_hours'] = hours
                
                # 불량률
                defect_input = input("불량률 (0-1 또는 0-100%): ")
                is_valid, defect, error = self.validator.validate_numeric_input(
                    defect_input, "불량률", 0, 100
                )
                if not is_valid:
                    print(error)
                    continue
                
                # 100보다 큰 값이면 백분율로 가정하고 소수점으로 변환
                if defect > 1:
                    defect = defect / 100
                line_data['defect_rate'] = defect
                
                # 선택적 필드들
                investment_input = input("설비 투자 비용 (원, 선택사항): ").strip()
                if investment_input:
                    is_valid, investment, error = self.validator.validate_numeric_input(
                        investment_input, "투자 비용", 0
                    )
                    if is_valid:
                        line_data['investment_cost'] = investment
                    else:
                        print(error)
                        continue
                else:
                    line_data['investment_cost'] = 0.0
                
                maintenance_input = input("월간 유지보수 비용 (원, 선택사항): ").strip()
                if maintenance_input:
                    is_valid, maintenance, error = self.validator.validate_numeric_input(
                        maintenance_input, "유지보수 비용", 0
                    )
                    if is_valid:
                        line_data['maintenance_cost'] = maintenance
                    else:
                        print(error)
                        continue
                else:
                    line_data['maintenance_cost'] = 0.0
                
                # 데이터 유효성 검사
                is_valid, errors = self.validator.validate_production_line_data(line_data)
                if not is_valid:
                    print("입력 오류:")
                    for error in errors:
                        print(f"  - {error}")
                    continue
                
                # ProductionLine 객체 생성
                try:
                    production_line = ProductionLine(
                        line_id=line_data['line_id'],
                        line_name=line_data['line_name'],
                        production_capacity=line_data['production_capacity'],
                        operating_cost=line_data['operating_cost'],
                        max_working_hours=line_data['max_working_hours'],
                        defect_rate=line_data['defect_rate'],
                        investment_cost=line_data['investment_cost'],
                        maintenance_cost=line_data['maintenance_cost']
                    )
                    production_lines.append(production_line)
                    break
                
                except ValueError as e:
                    print(f"데이터 생성 오류: {e}")
                    continue
        
        return production_lines
    
    def get_product_data(self, product_count: int, production_lines: List[ProductionLine]) -> List[Product]:
        """제품 데이터 입력 받기"""
        print(f"\n=== 제품 정보 입력 ({product_count}개) ===")
        
        products = []
        line_ids = [line.line_id for line in production_lines]
        
        for i in range(product_count):
            print(f"\n--- 제품 {i+1} ---")
            
            while True:
                product_data = {}
                
                # 제품 ID
                product_data['product_id'] = input("제품 ID: ").strip()
                if not product_data['product_id']:
                    print("제품 ID를 입력해주세요.")
                    continue
                
                # 제품 이름
                product_data['product_name'] = input("제품 이름: ").strip()
                if not product_data['product_name']:
                    print("제품 이름을 입력해주세요.")
                    continue
                
                # 단위당 원자재 비용
                material_input = input("단위당 원자재 비용 (원/개): ")
                is_valid, material_cost, error = self.validator.validate_numeric_input(
                    material_input, "원자재 비용",
                    VALIDATION_RULES['material_cost']['min'],
                    VALIDATION_RULES['material_cost']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                product_data['material_cost'] = material_cost
                
                # 단위당 판매 가격
                price_input = input("단위당 판매 가격 (원/개): ")
                is_valid, selling_price, error = self.validator.validate_numeric_input(
                    price_input, "판매 가격",
                    VALIDATION_RULES['selling_price']['min'],
                    VALIDATION_RULES['selling_price']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                product_data['selling_price'] = selling_price
                
                # 목표 생산량
                target_input = input("목표 생산량 (개): ")
                is_valid, target_production, error = self.validator.validate_numeric_input(
                    target_input, "목표 생산량",
                    VALIDATION_RULES['target_production']['min'],
                    VALIDATION_RULES['target_production']['max']
                )
                if not is_valid:
                    print(error)
                    continue
                product_data['target_production'] = target_production
                
                # 최소 수요량 (선택사항)
                min_demand_input = input("최소 수요량 (개, 선택사항): ").strip()
                if min_demand_input:
                    is_valid, min_demand, error = self.validator.validate_numeric_input(
                        min_demand_input, "최소 수요량", 0
                    )
                    if is_valid:
                        product_data['min_demand'] = min_demand
                    else:
                        print(error)
                        continue
                else:
                    product_data['min_demand'] = 0.0
                
                # 데이터 유효성 검사
                is_valid, errors = self.validator.validate_product_data(product_data)
                if not is_valid:
                    print("입력 오류:")
                    for error in errors:
                        print(f"  - {error}")
                    continue
                
                # 라인별 생산 시간 입력
                print(f"\n라인별 생산 시간 설정 (제품: {product_data['product_name']}):")
                production_times = {}
                compatible_lines = []
                
                for line in production_lines:
                    while True:
                        time_input = input(f"{line.line_name} ({line.line_id})에서의 생산 시간 (분/개, 0=생산불가): ")
                        is_valid, prod_time, error = self.validator.validate_numeric_input(
                            time_input, "생산 시간", 0
                        )
                        if not is_valid:
                            print(error)
                            continue
                        
                        production_times[line.line_id] = prod_time
                        if prod_time > 0:
                            compatible_lines.append(line.line_id)
                        break
                
                if not compatible_lines:
                    print("최소 하나의 라인에서는 생산 가능해야 합니다.")
                    continue
                
                # ProductionLine의 compatible_products 업데이트
                for line in production_lines:
                    if line.line_id in compatible_lines:
                        if product_data['product_id'] not in line.compatible_products:
                            line.compatible_products.append(product_data['product_id'])
                
                # Product 객체 생성
                try:
                    product = Product(
                        product_id=product_data['product_id'],
                        product_name=product_data['product_name'],
                        material_cost=product_data['material_cost'],
                        selling_price=product_data['selling_price'],
                        target_production=product_data['target_production'],
                        min_demand=product_data['min_demand'],
                        production_times=production_times
                    )
                    products.append(product)
                    break
                
                except ValueError as e:
                    print(f"데이터 생성 오류: {e}")
                    continue
        
        return products
    
    def get_ga_parameters(self) -> Dict[str, Any]:
        """유전 알고리즘 파라미터 입력 받기"""
        print("\n=== 유전 알고리즘 파라미터 설정 ===")
        print("기본값을 사용하려면 Enter를 누르세요.")
        
        params = DEFAULT_GA_PARAMS.copy()
        
        # 개체군 크기
        pop_input = input(f"개체군 크기 (기본값: {params['population_size']}): ").strip()
        if pop_input:
            is_valid, pop_size, error = self.validator.validate_numeric_input(
                pop_input, "개체군 크기", 10, 1000
            )
            if is_valid:
                params['population_size'] = int(pop_size)
            else:
                print(f"오류: {error}. 기본값을 사용합니다.")
        
        # 세대 수
        gen_input = input(f"세대 수 (기본값: {params['generations']}): ").strip()
        if gen_input:
            is_valid, generations, error = self.validator.validate_numeric_input(
                gen_input, "세대 수", 10, 10000
            )
            if is_valid:
                params['generations'] = int(generations)
            else:
                print(f"오류: {error}. 기본값을 사용합니다.")
        
        # 교차율
        cross_input = input(f"교차율 (기본값: {params['crossover_rate']}): ").strip()
        if cross_input:
            is_valid, crossover_rate, error = self.validator.validate_numeric_input(
                cross_input, "교차율", 0.0, 1.0
            )
            if is_valid:
                params['crossover_rate'] = crossover_rate
            else:
                print(f"오류: {error}. 기본값을 사용합니다.")
        
        # 돌연변이율
        mut_input = input(f"돌연변이율 (기본값: {params['mutation_rate']}): ").strip()
        if mut_input:
            is_valid, mutation_rate, error = self.validator.validate_numeric_input(
                mut_input, "돌연변이율", 0.0, 1.0
            )
            if is_valid:
                params['mutation_rate'] = mutation_rate
            else:
                print(f"오류: {error}. 기본값을 사용합니다.")
        
        return params

class FileIOHandler:
    """파일 입출력 처리 클래스"""
    
    @staticmethod
    def save_model_to_json(model: ProductionModel, filename: str) -> bool:
        """모델을 JSON 파일로 저장"""
        try:
            model_dict = {
                'production_lines': {
                    line_id: asdict(line) for line_id, line in model.production_lines.items()
                },
                'products': {
                    product_id: asdict(product) for product_id, product in model.products.items()
                },
                'constraints': asdict(model.constraints),
                'optimization_goal': model.optimization_goal.value,
                'optimization_weights': model.optimization_weights
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(model_dict, f, ensure_ascii=False, indent=2)
            
            return True
        
        except Exception as e:
            print(f"파일 저장 오류: {e}")
            return False
    
    @staticmethod
    def load_model_from_json(filename: str) -> Optional[ProductionModel]:
        """JSON 파일에서 모델 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                model_dict = json.load(f)
            
            model = ProductionModel()
            
            # 생산 라인 로드
            for line_id, line_data in model_dict['production_lines'].items():
                line = ProductionLine(**line_data)
                model.add_production_line(line)
            
            # 제품 로드
            for product_id, product_data in model_dict['products'].items():
                product = Product(**product_data)
                model.add_product(product)
            
            # 제약 조건 로드
            constraints = ProductionConstraints(**model_dict['constraints'])
            model.set_constraints(constraints)
            
            # 최적화 목표 로드
            goal = OptimizationGoal(model_dict['optimization_goal'])
            weights = model_dict.get('optimization_weights', {})
            model.set_optimization_goal(goal, weights)
            
            return model
        
        except Exception as e:
            print(f"파일 로드 오류: {e}")
            return None
    
    @staticmethod
    def create_input_template() -> str:
        """입력 템플릿 파일 생성"""
        template_data = {
            "생산_라인": [
                {
                    "line_id": "LINE_001",
                    "line_name": "조립라인1",
                    "production_capacity": 100.0,
                    "operating_cost": 50000.0,
                    "max_working_hours": 16.0,
                    "defect_rate": 0.05,
                    "investment_cost": 0.0,
                    "maintenance_cost": 100000.0
                }
            ],
            "제품": [
                {
                    "product_id": "PROD_001",
                    "product_name": "제품A",
                    "material_cost": 1000.0,
                    "selling_price": 2000.0,
                    "target_production": 1000.0,
                    "min_demand": 500.0,
                    "production_times": {
                        "LINE_001": 5.0
                    }
                }
            ]
        }
        
        filename = "input_template.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            return filename
        except Exception as e:
            print(f"템플릿 생성 오류: {e}")
            return ""