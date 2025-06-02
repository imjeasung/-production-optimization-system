# 🚀 Quick Start Example | 빠른 시작 예제

This example demonstrates how to set up and run a basic production optimization problem.
이 예제는 기본적인 생산 최적화 문제를 설정하고 실행하는 방법을 보여줍니다.

## 📋 Example Scenario | 예제 시나리오

A small electronics manufacturer with 2 production lines and 3 products:
2개의 생산 라인과 3개 제품을 가진 소규모 전자제품 제조업체:

- **Production Lines** | 생산 라인:
  - Assembly Line A: High capacity, medium cost | 조립라인 A: 고용량, 중간비용
  - Assembly Line B: Lower capacity, low cost | 조립라인 B: 저용량, 저비용

- **Products** | 제품:
  - Smartphone: High profit, high demand | 스마트폰: 고수익, 고수요
  - Tablet: Medium profit, medium demand | 태블릿: 중간수익, 중간수요
  - Earbuds: Low profit, high demand | 이어버드: 저수익, 고수요

## 🏃‍♂️ Running the Example | 예제 실행

### Method 1: Interactive Mode | 방법 1: 대화형 모드

```bash
python main.py
```

Select menu option 1 and follow the prompts with these values:
메뉴 옵션 1을 선택하고 다음 값들로 진행하세요:

```
=== Basic Settings ===
Number of production lines: 2
Number of products: 3
Optimization period: daily (1)
Optimization goal: maximize_profit (2)

=== Production Line 1 ===
Line ID: LINE_A
Line Name: Assembly Line A
Production capacity (units/hour): 50
Operating cost (won/hour): 30000
Max working hours per day: 16
Defect rate (0-1): 0.03
Investment cost: 0
Maintenance cost: 50000

=== Production Line 2 ===
Line ID: LINE_B
Line Name: Assembly Line B
Production capacity (units/hour): 30
Operating cost (won/hour): 20000
Max working hours per day: 20
Defect rate (0-1): 0.05
Investment cost: 0
Maintenance cost: 30000

=== Product 1 ===
Product ID: SMARTPHONE
Product Name: Smartphone
Material cost (won/unit): 150000
Selling price (won/unit): 300000
Target production: 200
Minimum demand: 100
Production time on LINE_A (min/unit): 8
Production time on LINE_B (min/unit): 12

=== Product 2 ===
Product ID: TABLET
Product Name: Tablet
Material cost (won/unit): 200000
Selling price (won/unit): 350000
Target production: 150
Minimum demand: 80
Production time on LINE_A (min/unit): 12
Production time on LINE_B (min/unit): 18

=== Product 3 ===
Product ID: EARBUDS
Product Name: Earbuds
Material cost (won/unit): 30000
Selling price (won/unit): 80000
Target production: 400
Minimum demand: 200
Production time on LINE_A (min/unit): 3
Production time on LINE_B (min/unit): 4
```

### Method 2: File Input | 방법 2: 파일 입력

Use the provided template file:
제공된 템플릿 파일 사용:

```bash
python main.py
# Select option 2: Load from file
# Enter filename: example_model.json
```

## 📊 Expected Results | 예상 결과

After optimization, you should see results similar to:
최적화 후 다음과 같은 결과를 볼 수 있습니다:

```
=== Optimization Results Summary ===
Total Cost: 15,480,000원
Total Revenue: 45,600,000원
Net Profit: 30,120,000원
Total Production: 684 units
Constraint Violations: 0
Feasibility: Yes

🏭 === Detailed Production Plan ===
📋 Production by Line:
  🏪 Assembly Line A:
     • Operating Hours: 15.2 hours
     • Utilization: 95.0%
     • Total Production: 456 units
     • Expected Revenue: 32,400,000원

  🏪 Assembly Line B:
     • Operating Hours: 18.5 hours
     • Utilization: 92.5%
     • Total Production: 228 units
     • Expected Revenue: 13,200,000원

📊 Product Achievement Rates:
    ✅ Smartphone: 187 units (93.5% achievement)
        Best Line: Assembly Line A
    ✅ Tablet: 134 units (89.3% achievement)
        Best Line: Assembly Line A
    ✅ Earbuds: 363 units (90.8% achievement)
        Best Line: Assembly Line B
```

## 🎯 Key Insights | 주요 인사이트

From this example, you can learn:
이 예제에서 배울 수 있는 것들:

1. **Resource Allocation** | 자원 배분: High-value products (smartphones, tablets) are optimally assigned to the more efficient line A
2. **Capacity Utilization** | 용량 활용: Both lines operate at near-maximum capacity for optimal efficiency
3. **Profit Optimization** | 수익 최적화: The system balances production volume with profit margins
4. **Constraint Handling** | 제약 조건 처리: All capacity and demand constraints are satisfied

## 🔄 Try Different Scenarios | 다양한 시나리오 시도

Experiment with different settings:
다양한 설정으로 실험해보세요:

- Change optimization goal to "minimize_cost" | 최적화 목표를 "비용 최소화"로 변경
- Adjust production capacities | 생산 능력 조정
- Modify product prices or costs | 제품 가격이나 비용 수정
- Add quality constraints | 품질 제약 조건 추가

## 📈 Next Steps | 다음 단계

1. Run optimization (menu option 4) | 최적화 실행 (메뉴 옵션 4)
2. Analyze results (menu option 5) | 결과 분석 (메뉴 옵션 5)
3. Generate reports (menu options 9-10) | 보고서 생성 (메뉴 옵션 9-10)
4. Try the Quick Insights feature (menu option 6) | 빠른 인사이트 기능 사용 (메뉴 옵션 6)