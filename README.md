# 🏭 Production Optimization System | 생산 최적화 시스템

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Contributors](https://img.shields.io/badge/Contributors-Welcome-orange.svg)](CONTRIBUTING.md)

**A sophisticated production planning optimization system using genetic algorithms** 
유전 알고리즘을 활용한 고도화된 생산 계획 최적화 시스템

---

## 🌟 Features | 주요 기능

### 🎯 Multi-Objective Optimization | 다목적 최적화
- **Cost Minimization** | 비용 최소화
- **Profit Maximization** | 수익 최대화  
- **Production Volume Maximization** | 생산량 최대화
- **Quality Optimization** | 품질 최적화
- **Multi-Objective Weighted Optimization** | 가중치 기반 복합 최적화

### 🧬 Advanced Genetic Algorithm | 고도화된 유전 알고리즘
- Tournament, Roulette Wheel, and Rank-based Selection | 토너먼트, 룰렛휠, 순위 기반 선택
- Adaptive Mutation and Crossover | 적응형 돌연변이 및 교차
- Constraint Handling (Penalty, Repair, Death Penalty) | 제약 조건 처리
- Real-time Convergence Analysis | 실시간 수렴 분석

### 📊 Comprehensive Analysis & Reporting | 종합 분석 및 보고
- **Production Schedule Analysis** | 생산 스케줄 분석
- **Resource Utilization Insights** | 자원 활용도 인사이트
- **Profitability Analysis** | 수익성 분석
- **Bottleneck Identification** | 병목 지점 식별
- **Interactive HTML Reports** | 인터랙티브 HTML 보고서
- **Excel Export Capabilities** | Excel 내보내기 기능

### 📈 Data Visualization | 데이터 시각화
- Production Dashboard | 생산 대시보드
- Performance Charts | 성과 차트
- Efficiency Heatmaps | 효율성 히트맵
- Convergence Graphs | 수렴 그래프

---

## 🚀 Quick Start | 빠른 시작

### Prerequisites | 필수 조건
```bash
Python 3.8+
numpy
pandas
matplotlib
seaborn
openpyxl (for Excel reports)
```

### Installation | 설치
```bash
# Clone the repository | 리포지토리 클론
git clone https://github.com/imjeasung/-production-optimization-system.git
cd production-optimization-system

# Install dependencies | 의존성 설치
pip install numpy pandas matplotlib seaborn openpyxl

# Run the system | 시스템 실행
python main.py
```

### Example Usage | 사용 예시
```bash
$ python main.py

============================================================
   Production Optimization System v1.0
   Genetic Algorithm-based Production Planning Optimization
============================================================

=== Main Menu ===
1. Setup New Optimization Problem
2. Load Problem from File
3. View Current Problem Info
4. Run Optimization
5. Analyze Results
6. 🔥 Quick Insights (NEW!)
7. Generate Visualization Dashboard
8. Create Detailed Charts
9. Generate HTML Report
10. Generate Excel Report
11. Save Model
12. Create Input Template
13. Exit
```

---

## 📁 Project Structure | 프로젝트 구조

```
production-optimization-system/
├── 📄 main.py                    # Main application entry point | 메인 애플리케이션
├── ⚙️ config.py                  # System configuration | 시스템 설정
├── 🏭 production_model.py        # Production line & product models | 생산 모델
├── 🖥️ user_interface.py          # User input/output handling | 사용자 인터페이스
├── 🧬 genetic_algorithm.py       # GA optimization engine | 유전 알고리즘 엔진
├── 📊 result_analyzer.py         # Results analysis & visualization | 결과 분석
├── 📋 report_generator.py        # HTML/Excel report generation | 보고서 생성
├── 🎯 objective_functions.py     # Multi-objective functions | 목적 함수
├── ⚖️ constraint_handler.py      # Advanced constraint management | 제약 조건 처리
└── 📂 analysis_results/          # Generated reports & charts | 생성된 결과물
```

---

## 📱 Example Scenario | 가상 시나리오

### 🏭 **Smart Electronics Manufacturing Company**
**스마트 전자제품 제조업체 최적화 사례**

#### Problem Statement | 문제 상황
- **3 Production Lines** | 3개 생산 라인
- **4 Product Types** | 4가지 제품

#### Step-by-Step Parameter Input | 단계별 파라미터 입력

**🏭 Production Line Setup | 생산 라인 설정**
```
=== Line 1 ===
라인 ID: LINE_001
라인 이름: 스마트폰 조립라인 A
시간당 생산 능력 (개/시간): 120
시간당 운영 비용 (원/시간): 75000
일일 최대 가동 시간: 16
불량률 (0-1 또는 0-100%): 3
설비 투자 비용 (원, 선택사항): 50000000
월간 유지보수 비용 (원, 선택사항): 300000

=== Line 2 ===
라인 ID: LINE_002
라인 이름: 스마트폰 조립라인 B  
시간당 생산 능력 (개/시간): 100
시간당 운영 비용 (원/시간): 60000
일일 최대 가동 시간: 20
불량률 (0-1 또는 0-100%): 5
설비 투자 비용 (원, 선택사항): 30000000
월간 유지보수 비용 (원, 선택사항): 250000

=== Line 3 ===
라인 ID: LINE_003
라인 이름: 액세서리 제조라인
시간당 생산 능력 (개/시간): 200
시간당 운영 비용 (원/시간): 45000
일일 최대 가동 시간: 18
불량률 (0-1 또는 0-100%): 2
설비 투자 비용 (원, 선택사항): 25000000
월간 유지보수 비용 (원, 선택사항): 200000
```

**📱 Product Configuration | 제품 설정**
```
=== Product 1 ===
제품 ID: PHONE_PREMIUM
제품 이름: 프리미엄 스마트폰
단위당 원자재 비용 (원/개): 350000
단위당 판매 가격 (원/개): 800000
목표 생산량 (개): 500
최소 수요량 (개, 선택사항): 400

=== Product 2 ===
제품 ID: PHONE_STANDARD
제품 이름: 표준 스마트폰
단위당 원자재 비용 (원/개): 200000
단위당 판매 가격 (원/개): 450000
목표 생산량 (개): 800
최소 수요량 (개, 선택사항): 600

=== Product 3 ===
제품 ID: ACCESSORY_CASE
제품 이름: 휴대폰 케이스
단위당 원자재 비용 (원/개): 5000
단위당 판매 가격 (원/개): 25000
목표 생산량 (개): 2000
최소 수요량 (개, 선택사항): 1500

=== Product 4 ===
제품 ID: ACCESSORY_CHARGER
제품 이름: 무선충전기
단위당 원자재 비용 (원/개): 15000
단위당 판매 가격 (원/개): 50000
목표 생산량 (개): 1200
최소 수요량 (개, 선택사항): 1000
```

**⚙️ Line-Product Compatibility | 라인-제품 호환성**
```
LINE_001에서 생산 가능: PHONE_PREMIUM, PHONE_STANDARD
LINE_002에서 생산 가능: PHONE_PREMIUM, PHONE_STANDARD  
LINE_003에서 생산 가능: ACCESSORY_CASE, ACCESSORY_CHARGER

각 제품별 생산 시간 (분/개):
- PHONE_PREMIUM: LINE_001(25분), LINE_002(30분)
- PHONE_STANDARD: LINE_001(20분), LINE_002(22분)
- ACCESSORY_CASE: LINE_003(3분)
- ACCESSORY_CHARGER: LINE_003(8분)
```

### 🚀 Try This Scenario | 이 시나리오 체험하기

#### Method 1: Quick Demo | 빠른 데모
```bash
cd examples
python optimization_demo.py
```

#### Method 2: Manual Input Practice | 수동 입력 연습
```bash
python main.py
# Select "1. 새로운 최적화 문제 설정"
# Follow the prompts with the parameters shown above
# 위에 표시된 파라미터들을 프롬프트에 따라 입력하세요
```

#### Method 3: Load Pre-configured Scenario | 사전 설정된 시나리오 로드
```bash
python main.py
# Select "2. 파일에서 문제 로드"
# Load: examples/manufacturing_scenario.json
```

**Expected runtime**: 30-60 seconds | **예상 실행시간**: 30-60초  
**Output files**: Dashboard, charts, HTML report | **출력 파일**: 대시보드, 차트, HTML 보고서

---

## 🎯 System Architecture | 시스템 아키텍처

### Core Components | 핵심 구성요소

#### 1. **Production Model** | 생산 모델
```python
# Define production lines | 생산 라인 정의
production_line = ProductionLine(
    line_id="LINE_001",
    production_capacity=100.0,    # units/hour | 개/시간
    operating_cost=50000.0,       # cost/hour | 원/시간
    max_working_hours=16.0,       # hours/day | 시간/일
    defect_rate=0.05              # 5% defect rate | 5% 불량률
)

# Define products | 제품 정의
product = Product(
    product_id="PROD_001",
    material_cost=1000.0,         # cost/unit | 원/개
    selling_price=2000.0,         # price/unit | 원/개
    target_production=1000.0      # target units | 목표 개수
)
```

#### 2. **Genetic Algorithm Engine** | 유전 알고리즘 엔진
- **Population-based Search** | 개체군 기반 탐색
- **Multi-point Crossover** | 다점 교차
- **Gaussian Mutation** | 가우시안 돌연변이
- **Elite Preservation** | 엘리트 보존

#### 3. **Advanced Constraint Handling** | 고도화된 제약 조건 처리
- **Capacity Constraints** | 용량 제약
- **Demand Satisfaction** | 수요 충족
- **Quality Requirements** | 품질 요구사항
- **Budget Limitations** | 예산 제한

---

## 📈 Optimization Results | 최적화 결과

### Sample Output | 샘플 출력
```
=== Optimization Results Summary ===
Total Cost: 2,450,000원
Total Revenue: 3,200,000원
Net Profit: 750,000원
Total Production: 1,850 units
Constraint Violations: 0
Feasibility: Yes

🏭 === Detailed Production Plan ===
📋 Production by Line:
  🏪 Assembly Line 1:
     • Operating Hours: 14.2 hours
     • Utilization: 88.8%
     • Total Production: 1,420 units
     • Expected Revenue: 2,840,000원
```

---

## 🔧 Configuration | 설정

### Optimization Goals | 최적화 목표
```python
OptimizationGoal.MINIMIZE_COST      # 비용 최소화
OptimizationGoal.MAXIMIZE_PROFIT    # 수익 최대화
OptimizationGoal.MAXIMIZE_PRODUCTION # 생산량 최대화
OptimizationGoal.OPTIMIZE_QUALITY   # 품질 최적화
OptimizationGoal.MULTI_OBJECTIVE    # 다목적 최적화
```

### GA Parameters | 유전 알고리즘 파라미터
```python
ga_params = {
    'population_size': 100,          # 개체군 크기
    'generations': 500,              # 세대 수
    'crossover_rate': 0.8,           # 교차율
    'mutation_rate': 0.05,           # 돌연변이율
    'elite_ratio': 0.1               # 엘리트 비율
}
```

---

## 📊 Analysis Features | 분석 기능

### 1. Executive Dashboard | 경영진 대시보드
- Key Performance Indicators (KPIs) | 핵심 성과 지표
- Cost Breakdown Analysis | 비용 구성 분석
- Production Achievement Rates | 생산 달성률

### 2. Resource Efficiency Analysis | 자원 효율성 분석
- Line Utilization Rates | 라인 가동률
- Quality Performance Metrics | 품질 성과 지표
- Bottleneck Identification | 병목 지점 식별

### 3. Profitability Insights | 수익성 인사이트
- Product Profitability Ranking | 제품 수익성 순위
- Revenue per Hour Analysis | 시간당 수익 분석
- Strategic Recommendations | 전략적 권장사항

---

## 🎨 Visualization Examples | 시각화 예시

The system generates comprehensive visual reports including:
시스템은 다음과 같은 종합적인 시각화 보고서를 생성합니다:

- **Production vs Target Charts** | 생산량 vs 목표 차트
- **Line Utilization Dashboards** | 라인 가동률 대시보드
- **Cost Breakdown Pie Charts** | 비용 구성 파이 차트
- **GA Convergence Graphs** | 유전 알고리즘 수렴 그래프
- **Efficiency Heatmaps** | 효율성 히트맵

---

## 🤝 Contributing | 기여하기

We welcome contributions! | 기여를 환영합니다!

1. Fork the repository | 리포지토리 포크
2. Create a feature branch | 기능 브랜치 생성
3. Commit your changes | 변경사항 커밋
4. Push to the branch | 브랜치에 푸시
5. Open a Pull Request | 풀 리퀘스트 열기

---

## 📄 License | 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
이 프로젝트는 MIT 라이선스 하에 있습니다.

---

## 👨‍💻 Author | 개발자

**[LimJaeSung]** | **[임재성]**
- GitHub: [@imjeasung](https://github.com/imjeasung)
- Email: jeasunglim39@gmail.com

---

## 🔮 Future Enhancements | 향후 개선사항

- [ ] Machine Learning-based Parameter Tuning | 머신러닝 기반 파라미터 튜닝
- [ ] Real-time Data Integration | 실시간 데이터 통합
- [ ] Multi-site Optimization | 다중 사이트 최적화
- [ ] Advanced Visualization with Plotly | Plotly를 활용한 고급 시각화
- [ ] REST API Development | REST API 개발

---

⭐ **Star this repository if you found it helpful!** | **도움이 되셨다면 스타를 눌러주세요!**
