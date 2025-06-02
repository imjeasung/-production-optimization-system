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

## 🙏 Acknowledgments | 감사의 말

- Inspired by modern production optimization challenges | 현대 생산 최적화 과제에서 영감을 받음
- Built with love for efficient manufacturing | 효율적인 제조업을 위한 애정으로 제작
- Thanks to the open-source community | 오픈소스 커뮤니티에 감사

---

## 📚 Documentation | 문서

For detailed documentation, please visit our [Wiki](https://github.com/yourusername/production-optimization-system/wiki).
자세한 문서는 [위키](https://github.com/yourusername/production-optimization-system/wiki)를 참조하세요.

---

## 🔮 Future Enhancements | 향후 개선사항

- [ ] Machine Learning-based Parameter Tuning | 머신러닝 기반 파라미터 튜닝
- [ ] Real-time Data Integration | 실시간 데이터 통합
- [ ] Multi-site Optimization | 다중 사이트 최적화
- [ ] Advanced Visualization with Plotly | Plotly를 활용한 고급 시각화
- [ ] REST API Development | REST API 개발

---

⭐ **Star this repository if you found it helpful!** | **도움이 되셨다면 스타를 눌러주세요!**
