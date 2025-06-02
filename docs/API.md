# 📚 API Documentation | API 문서

This document provides detailed information about the core classes and methods in the Production Optimization System.
이 문서는 생산 최적화 시스템의 핵심 클래스와 메소드에 대한 상세 정보를 제공합니다.

## 🏗️ Core Classes | 핵심 클래스

### ProductionLine Class

Represents a production line in the manufacturing system.
제조 시스템의 생산 라인을 나타냅니다.

```python
from production_model import ProductionLine

line = ProductionLine(
    line_id="LINE_001",           # Unique identifier | 고유 식별자
    line_name="Assembly Line 1",  # Display name | 표시 이름
    production_capacity=100.0,    # Units per hour | 시간당 생산량
    operating_cost=50000.0,       # Cost per hour (KRW) | 시간당 비용(원)
    max_working_hours=16.0,       # Hours per day | 일일 최대 시간
    defect_rate=0.05,            # Defect rate (0-1) | 불량률 (0-1)
    investment_cost=0.0,         # Equipment cost | 설비 비용
    maintenance_cost=100000.0    # Monthly maintenance | 월간 유지비
)
```

**Key Methods:**
- `calculate_daily_capacity()`: Returns maximum daily production capacity
- `calculate_effective_capacity()`: Returns capacity considering defect rate
- `calculate_daily_operating_cost(hours)`: Calculates operating cost for given hours

### Product Class

Represents a product to be manufactured.
제조할 제품을 나타냅니다.

```python
from production_model import Product

product = Product(
    product_id="PROD_001",
    product_name="Smartphone",
    material_cost=150000.0,      # Cost per unit | 단위당 원자재 비용
    selling_price=300000.0,      # Price per unit | 단위당 판매 가격
    target_production=200.0,     # Production target | 생산 목표
    min_demand=100.0,           # Minimum demand | 최소 수요
    production_times={          # Production time per line | 라인별 생산 시간
        "LINE_001": 8.0         # Minutes per unit | 분/개
    }
)
```

**Key Methods:**
- `calculate_unit_profit()`: Returns profit per unit
- `get_production_time(line_id)`: Returns production time for specific line
- `get_setup_time(line_id)`: Returns setup time for specific line

### GeneticAlgorithm Class

Main optimization engine using genetic algorithms.
유전 알고리즘을 사용하는 메인 최적화 엔진입니다.

```python
from genetic_algorithm import GeneticAlgorithm

# Custom GA parameters | 사용자 정의 GA 파라미터
ga_params = {
    'population_size': 100,
    'generations': 500,
    'crossover_rate': 0.8,
    'mutation_rate': 0.05,
    'elite_ratio': 0.1
}

ga = GeneticAlgorithm(production_model, ga_params)
result = ga.run()
```

**Key Methods:**
- `run()`: Execute the optimization process
- `initialize_population()`: Create initial population
- `selection()`: Perform parent selection
- `crossover()`: Generate offspring through crossover
- `mutation()`: Apply mutation operators

### ProductionAnalyzer Class

Analyzes optimization results and generates insights.
최적화 결과를 분석하고 인사이트를 생성합니다.

```python
from result_analyzer import ProductionAnalyzer

analyzer = ProductionAnalyzer(production_model, ga_result)
analysis_result = analyzer.analyze_all()
```

**Key Methods:**
- `analyze_all()`: Perform comprehensive analysis
- `save_analysis_report()`: Save analysis to JSON file
- `_analyze_production()`: Analyze production metrics
- `_analyze_costs()`: Analyze cost breakdown
- `_analyze_efficiency()`: Analyze efficiency metrics

## 🎯 Optimization Goals | 최적화 목표

The system supports five optimization objectives:
시스템은 5가지 최적화 목표를 지원합니다:

```python
from config import OptimizationGoal

# Available goals | 사용 가능한 목표들
OptimizationGoal.MINIMIZE_COST      # 비용 최소화
OptimizationGoal.MAXIMIZE_PROFIT    # 수익 최대화
OptimizationGoal.MAXIMIZE_PRODUCTION # 생산량 최대화
OptimizationGoal.OPTIMIZE_QUALITY   # 품질 최적화
OptimizationGoal.MULTI_OBJECTIVE    # 다목적 최적화
```

## ⚖️ Constraint Types | 제약 조건 유형

### Capacity Constraints | 용량 제약
Ensures production doesn't exceed line capacity.
생산량이 라인 용량을 초과하지 않도록 보장합니다.

### Demand Constraints | 수요 제약
Ensures minimum demand requirements are met.
최소 수요 요구사항이 충족되도록 보장합니다.

### Quality Constraints | 품질 제약
Maintains overall defect rate below specified threshold.
전체 불량률을 지정된 임계값 이하로 유지합니다.

### Budget Constraints | 예산 제약
Keeps total costs within budget limits.
총 비용을 예산 한도 내로 유지합니다.

## 📊 Analysis Components | 분석 구성 요소

### Production Analysis | 생산 분석
- Total production vs targets | 총 생산량 대 목표
- Line utilization rates | 라인 가동률
- Product achievement rates | 제품 달성률

### Cost Analysis | 비용 분석
- Material costs | 원자재 비용
- Operating costs | 운영 비용
- Setup costs | 셋업 비용
- Quality costs | 품질 비용

### Efficiency Analysis | 효율성 분석
- Capacity utilization | 용량 활용률
- Quality efficiency | 품질 효율성
- Overall efficiency score | 전체 효율성 점수

## 🔧 Configuration Options | 설정 옵션

### GA Parameters | 유전 알고리즘 파라미터

```python
DEFAULT_GA_PARAMS = {
    'population_size': 100,      # Population size | 개체군 크기
    'generations': 500,          # Number of generations | 세대 수
    'crossover_rate': 0.8,       # Crossover probability | 교차 확률
    'mutation_rate': 0.05,       # Mutation probability | 돌연변이 확률
    'elite_ratio': 0.1,          # Elite preservation ratio | 엘리트 보존 비율
    'selection_method': 'tournament',  # Selection method | 선택 방법
    'tournament_size': 3,        # Tournament size | 토너먼트 크기
    'constraint_handling': 'penalty_function'  # Constraint handling | 제약 처리
}
```

### Validation Rules | 검증 규칙

```python
VALIDATION_RULES = {
    'production_capacity': {'min': 1, 'max': 10000},
    'operating_cost': {'min': 0, 'max': 1000000},
    'working_hours': {'min': 1, 'max': 24},
    'defect_rate': {'min': 0.0, 'max': 0.5},
    'material_cost': {'min': 0, 'max': 1000000},
    'selling_price': {'min': 0, 'max': 1000000},
    'target_production': {'min': 1, 'max': 1000000}
}
```

## 📈 Result Structure | 결과 구조

### GAResult Class
Contains optimization results and metadata.
최적화 결과와 메타데이터를 포함합니다.

```python
result = GAResult(
    best_solution=individual,        # Best solution found | 최적 해
    best_fitness=fitness_value,      # Best fitness value | 최적 적합도
    fitness_history=history,         # Fitness evolution | 적합도 변화
    generation_count=generations,    # Total generations | 총 세대 수
    convergence_generation=conv_gen, # Convergence point | 수렴 지점
    execution_time=time_taken,       # Runtime in seconds | 실행 시간
    success=True,                    # Success flag | 성공 여부
    detailed_analysis=analysis       # Detailed insights | 상세 분석
)
```

### Individual Class
Represents a solution candidate.
해 후보를 나타냅니다.

```python
# Access production allocation | 생산 할당 접근
individual.genes[line_id][product_id]  # Production amount | 생산량

# Calculate metrics | 메트릭 계산
individual.get_total_production(product_id)    # Total production | 총 생산량
individual.get_line_utilization(line_id)       # Line utilization | 라인 가동률
individual.calculate_total_cost()               # Total cost | 총 비용
individual.calculate_total_revenue()            # Total revenue | 총 수익
```

## 🛠️ Usage Examples | 사용 예제

### Basic Setup | 기본 설정

```python
from production_model import ProductionModel, ProductionLine, Product
from genetic_algorithm import GeneticAlgorithm

# Create model | 모델 생성
model = ProductionModel()

# Add production line | 생산 라인 추가
line = ProductionLine(
    line_id="LINE_001",
    line_name="Assembly Line",
    production_capacity=50.0,
    operating_cost=30000.0,
    max_working_hours=16.0,
    defect_rate=0.03
)
model.add_production_line(line)

# Add product | 제품 추가
product = Product(
    product_id="PRODUCT_001",
    product_name="Smartphone",
    material_cost=150000.0,
    selling_price=300000.0,
    target_production=200.0,
    production_times={"LINE_001": 8.0}
)
model.add_product(product)

# Set optimization goal | 최적화 목표 설정
model.set_optimization_goal(OptimizationGoal.MAXIMIZE_PROFIT)

# Run optimization | 최적화 실행
ga = GeneticAlgorithm(model)
result = ga.run()
```

### Advanced Configuration | 고급 설정

```python
# Custom GA parameters | 사용자 정의 GA 파라미터
custom_params = {
    'population_size': 150,
    'generations': 1000,
    'crossover_rate': 0.9,
    'mutation_rate': 0.02,
    'elite_ratio': 0.15
}

# Multi-objective optimization | 다목적 최적화
weights = {
    'cost_weight': 0.3,
    'profit_weight': 0.4,
    'production_weight': 0.2,
    'quality_weight': 0.1
}

model.set_optimization_goal(OptimizationGoal.MULTI_OBJECTIVE, weights)
ga = GeneticAlgorithm(model, custom_params)
result = ga.run()
```

## 🔍 Error Handling | 오류 처리

Common errors and solutions:
일반적인 오류와 해결책:

### ValidationError
**Cause**: Invalid input parameters
**Solution**: Check parameter ranges in VALIDATION_RULES

### ModelError  
**Cause**: Inconsistent model configuration
**Solution**: Ensure all products have compatible production lines

### OptimizationError
**Cause**: Optimization failure
**Solution**: Adjust GA parameters or relax constraints