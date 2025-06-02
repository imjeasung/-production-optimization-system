"""
생산 최적화 시스템 설정 파일
기본 상수와 설정값들을 정의합니다.
"""

from enum import Enum
from typing import Dict, Any

class OptimizationGoal(Enum):
    """최적화 목표 열거형"""
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_PRODUCTION = "maximize_production"
    MAXIMIZE_PROFIT = "maximize_profit"
    MULTI_OBJECTIVE = "multi_objective"
    OPTIMIZE_QUALITY = "optimize_quality"

class SelectionMethod(Enum):
    """유전 알고리즘 선택 방법"""
    TOURNAMENT = "tournament"
    ROULETTE_WHEEL = "roulette_wheel"
    RANK_BASED = "rank_based"

class ConstraintHandling(Enum):
    """제약 조건 처리 방법"""
    PENALTY_FUNCTION = "penalty_function"
    REPAIR_ALGORITHM = "repair_algorithm"
    DEATH_PENALTY = "death_penalty"

# 기본 GA 파라미터
DEFAULT_GA_PARAMS = {
    'population_size': 100,
    'generations': 500,
    'crossover_rate': 0.8,
    'mutation_rate': 0.05,
    'elite_ratio': 0.1,
    'selection_method': SelectionMethod.TOURNAMENT,
    'tournament_size': 3,
    'constraint_handling': ConstraintHandling.PENALTY_FUNCTION
}

# 시스템 제한값
SYSTEM_LIMITS = {
    'max_production_lines': 20,
    'max_products': 10,
    'max_working_hours_per_day': 24,
    'max_defect_rate': 0.5,  # 50%
    'min_defect_rate': 0.0,   # 0%
}

# 최적화 목표별 기본 가중치
DEFAULT_WEIGHTS = {
    OptimizationGoal.MULTI_OBJECTIVE: {
        'cost_weight': 0.4,
        'production_weight': 0.4,
        'quality_weight': 0.2
    }
}

# 시각화 설정
VISUALIZATION_CONFIG = {
    'figure_size': (12, 8),
    'dpi': 100,
    'color_palette': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
    'font_size': 12
}

# 파일 경로 설정
FILE_PATHS = {
    'data_directory': 'data/',
    'results_directory': 'results/',
    'templates_directory': 'templates/',
    'config_file': 'production_config.json'
}

# 입력 데이터 유효성 검사 규칙
VALIDATION_RULES = {
    'production_capacity': {'min': 1, 'max': 10000},  # 개/시간
    'operating_cost': {'min': 0, 'max': 1000000},     # 원/시간
    'working_hours': {'min': 1, 'max': 24},           # 시간/일
    'defect_rate': {'min': 0.0, 'max': 0.5},          # 0-50%
    'material_cost': {'min': 0, 'max': 1000000},      # 원/개
    'selling_price': {'min': 0, 'max': 1000000},      # 원/개
    'target_production': {'min': 1, 'max': 1000000},  # 개
}

# 에러 메시지
ERROR_MESSAGES = {
    'invalid_input': "입력값이 유효하지 않습니다: {field}",
    'constraint_violation': "제약 조건 위반: {constraint}",
    'optimization_failed': "최적화 실행 중 오류가 발생했습니다: {error}",
    'file_not_found': "파일을 찾을 수 없습니다: {filename}",
    'data_format_error': "데이터 형식이 올바르지 않습니다: {details}"
}

# 성공 메시지
SUCCESS_MESSAGES = {
    'optimization_complete': "최적화가 성공적으로 완료되었습니다.",
    'data_loaded': "데이터가 성공적으로 로드되었습니다.",
    'results_saved': "결과가 저장되었습니다: {filename}"
}