"""
결과 분석 및 시각화 모듈
최적화 결과를 종합적으로 분석하고 시각화합니다.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime
import os

from production_model import ProductionModel
from genetic_algorithm import GAResult, Individual
from config import VISUALIZATION_CONFIG



@dataclass
class AnalysisResult:
    """분석 결과 데이터 클래스"""
    optimization_summary: Dict[str, Any]
    production_analysis: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    efficiency_analysis: Dict[str, Any]
    constraint_analysis: Dict[str, Any]
    bottleneck_analysis: Dict[str, Any]
    improvement_suggestions: List[str]
    sensitivity_analysis: Dict[str, Any]
    comparison_analysis: Optional[Dict[str, Any]] = None

class ProductionAnalyzer:
    """생산 최적화 결과 분석기"""
    plt.rcParams['font.family'] = 'Malgun Gothic'
    def __init__(self, production_model: ProductionModel, ga_result: GAResult):
        self.model = production_model
        self.ga_result = ga_result
        self.solution = ga_result.best_solution if ga_result.success else None
        self.analysis_result: Optional[AnalysisResult] = None
        
        # 시각화 설정
        self.figure_size = VISUALIZATION_CONFIG['figure_size']
        self.dpi = VISUALIZATION_CONFIG['dpi']
        self.colors = VISUALIZATION_CONFIG['color_palette']
        
        # 결과 저장 디렉토리
        self.results_dir = "analysis_results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def analyze_all(self) -> AnalysisResult:
        """종합적인 결과 분석"""
        if not self.solution:
            raise ValueError("유효한 최적화 결과가 없습니다.")
        
        print("결과 분석 중...")
        
        # 각 분석 수행
        optimization_summary = self._analyze_optimization_summary()
        production_analysis = self._analyze_production()
        cost_analysis = self._analyze_costs()
        efficiency_analysis = self._analyze_efficiency()
        constraint_analysis = self._analyze_constraints()
        bottleneck_analysis = self._analyze_bottlenecks()
        improvement_suggestions = self._generate_improvement_suggestions()
        sensitivity_analysis = self._perform_sensitivity_analysis()
        
        self.analysis_result = AnalysisResult(
            optimization_summary=optimization_summary,
            production_analysis=production_analysis,
            cost_analysis=cost_analysis,
            efficiency_analysis=efficiency_analysis,
            constraint_analysis=constraint_analysis,
            bottleneck_analysis=bottleneck_analysis,
            improvement_suggestions=improvement_suggestions,
            sensitivity_analysis=sensitivity_analysis
        )
        
        print("결과 분석 완료!")
        return self.analysis_result
    
    def _analyze_optimization_summary(self) -> Dict[str, Any]:
        """최적화 요약 분석"""
        components = self.solution.fitness_components
        
        return {
            'execution_time': self.ga_result.execution_time,
            'generations': self.ga_result.generation_count,
            'convergence_generation': self.ga_result.convergence_generation,
            'final_fitness': self.ga_result.best_fitness,
            'is_feasible': components['is_feasible'],
            'constraint_violations': components['constraint_violations'],
            'optimization_goal': self.model.optimization_goal.value,
            'improvement_rate': self._calculate_improvement_rate(),
            'convergence_stability': self._analyze_convergence_stability()
        }
    
    def _analyze_production(self) -> Dict[str, Any]:
        """생산 분석"""
        production_data = {}
        
        # 제품별 생산량
        product_production = {}
        product_targets = {}
        product_achievement = {}
        
        for product_id, product in self.model.products.items():
            actual = self.solution.get_total_production(product_id)
            target = product.target_production
            
            product_production[product.product_name] = actual
            product_targets[product.product_name] = target
            product_achievement[product.product_name] = (actual / target * 100) if target > 0 else 0
        
        # 라인별 생산량 및 가동률
        line_production = {}
        line_utilization = {}
        line_efficiency = {}
        
        for line_id, line in self.model.production_lines.items():
            production = sum(self.solution.genes[line_id].values())
            utilization = self.solution.get_line_utilization(line_id)
            efficiency = production * (1 - line.defect_rate)  # 유효 생산량
            
            line_production[line.line_name] = production
            line_utilization[line.line_name] = utilization * 100
            line_efficiency[line.line_name] = efficiency
        
        return {
            'total_production': sum(product_production.values()),
            'total_target': sum(product_targets.values()),
            'overall_achievement': sum(product_production.values()) / sum(product_targets.values()) * 100 if sum(product_targets.values()) > 0 else 0,
            'product_production': product_production,
            'product_targets': product_targets,
            'product_achievement': product_achievement,
            'line_production': line_production,
            'line_utilization': line_utilization,
            'line_efficiency': line_efficiency,
            'production_balance': self._calculate_production_balance()
        }
    
    def _analyze_costs(self) -> Dict[str, Any]:
        """비용 분석"""
        components = self.solution.fitness_components
        
        cost_breakdown = {
            '원자재비': components.get('material_cost', 0),
            '인건비': components.get('labor_cost', 0),
            '운영비': components.get('operating_cost', 0),
            '셋업비': components.get('setup_cost', 0),
            '유지보수비': components.get('maintenance_cost', 0),
            '재고비': components.get('inventory_cost', 0),
            '품질비': components.get('quality_cost', 0),
            '기회비용': components.get('opportunity_cost', 0)
        }
        
        total_cost = sum(cost_breakdown.values())
        cost_percentages = {k: (v / total_cost * 100) if total_cost > 0 else 0 for k, v in cost_breakdown.items()}
        
        # 라인별 비용 효율성
        line_cost_efficiency = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            line_cost = working_hours * line.operating_cost
            line_production = sum(self.solution.genes[line_id].values())
            
            if line_production > 0:
                cost_per_unit = line_cost / line_production
                line_cost_efficiency[line.line_name] = cost_per_unit
            else:
                line_cost_efficiency[line.line_name] = 0
        
        return {
            'total_cost': total_cost,
            'cost_breakdown': cost_breakdown,
            'cost_percentages': cost_percentages,
            'line_cost_efficiency': line_cost_efficiency,
            'cost_per_unit': total_cost / self.solution.calculate_total_production_amount() if self.solution.calculate_total_production_amount() > 0 else 0,
            'major_cost_drivers': self._identify_major_cost_drivers(cost_breakdown)
        }
    
    def _analyze_efficiency(self) -> Dict[str, Any]:
        """효율성 분석"""
        # 전체 효율성 지표
        total_capacity = sum(line.calculate_daily_capacity() for line in self.model.production_lines.values())
        total_production = self.solution.calculate_total_production_amount()
        capacity_utilization = (total_production / total_capacity * 100) if total_capacity > 0 else 0
        
        # 품질 효율성
        total_effective_production = 0
        for line_id, line in self.model.production_lines.items():
            line_production = sum(self.solution.genes[line_id].values())
            total_effective_production += line_production * (1 - line.defect_rate)
        
        quality_efficiency = (total_effective_production / total_production * 100) if total_production > 0 else 0
        
        # 라인별 효율성 순위
        line_efficiency_ranking = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            quality_factor = 1 - line.defect_rate
            efficiency_score = utilization * quality_factor * 100
            line_efficiency_ranking[line.line_name] = efficiency_score
        
        # 효율성 순위 정렬
        sorted_efficiency = dict(sorted(line_efficiency_ranking.items(), key=lambda x: x[1], reverse=True))
        
        return {
            'capacity_utilization': capacity_utilization,
            'quality_efficiency': quality_efficiency,
            'overall_efficiency': (capacity_utilization + quality_efficiency) / 2,
            'line_efficiency_ranking': sorted_efficiency,
            'efficiency_variance': np.var(list(line_efficiency_ranking.values())),
            'top_performer': max(sorted_efficiency.keys(), key=lambda x: sorted_efficiency[x]) if sorted_efficiency else None,
            'bottleneck_line': min(sorted_efficiency.keys(), key=lambda x: sorted_efficiency[x]) if sorted_efficiency else None
        }
    
    def _analyze_constraints(self) -> Dict[str, Any]:
        """제약 조건 분석"""
        violations = self.solution.constraint_violations
        
        constraint_status = {
            'total_violations': len(violations),
            'is_feasible': self.solution.is_feasible,
            'violation_details': violations
        }
        
        # 제약 조건별 여유도 분석
        margin_analysis = {}
        
        # 용량 여유도
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            margin_analysis[f"{line.line_name}_용량여유도"] = (1 - utilization) * 100
        
        # 수요 충족도
        for product_id, product in self.model.products.items():
            actual = self.solution.get_total_production(product_id)
            target = product.target_production
            margin_analysis[f"{product.product_name}_수요여유도"] = (actual - target) / target * 100 if target > 0 else 0
        
        return {
            **constraint_status,
            'margin_analysis': margin_analysis,
            'critical_constraints': self._identify_critical_constraints(margin_analysis)
        }
    
    def _analyze_bottlenecks(self) -> Dict[str, Any]:
        """병목 지점 분석"""
        bottlenecks = []
        
        # 용량 병목
        max_utilization = 0
        capacity_bottleneck = None
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            if utilization > max_utilization:
                max_utilization = utilization
                capacity_bottleneck = line.line_name
        
        if max_utilization > 0.9:  # 90% 이상 가동률
            bottlenecks.append({
                'type': '용량 병목',
                'location': capacity_bottleneck,
                'severity': max_utilization,
                'description': f"{capacity_bottleneck}의 가동률이 {max_utilization:.1%}로 높음"
            })
        
        # 품질 병목
        quality_issues = []
        for line_id, line in self.model.production_lines.items():
            if line.defect_rate > 0.05:  # 5% 이상 불량률
                line_production = sum(self.solution.genes[line_id].values())
                if line_production > 0:
                    quality_issues.append({
                        'line': line.line_name,
                        'defect_rate': line.defect_rate,
                        'impact': line_production * line.defect_rate
                    })
        
        if quality_issues:
            worst_quality = max(quality_issues, key=lambda x: x['impact'])
            bottlenecks.append({
                'type': '품질 병목',
                'location': worst_quality['line'],
                'severity': worst_quality['defect_rate'],
                'description': f"{worst_quality['line']}의 불량률이 {worst_quality['defect_rate']:.1%}로 높음"
            })
        
        # 비용 병목
        line_costs = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            line_costs[line.line_name] = working_hours * line.operating_cost
        
        if line_costs:
            max_cost_line = max(line_costs.keys(), key=lambda x: line_costs[x])
            total_operating_cost = sum(line_costs.values())
            cost_ratio = line_costs[max_cost_line] / total_operating_cost if total_operating_cost > 0 else 0
            
            if cost_ratio > 0.4:  # 40% 이상 비용 점유
                bottlenecks.append({
                    'type': '비용 병목',
                    'location': max_cost_line,
                    'severity': cost_ratio,
                    'description': f"{max_cost_line}이 총 운영비의 {cost_ratio:.1%}를 차지함"
                })
        
        return {
            'bottlenecks': bottlenecks,
            'bottleneck_count': len(bottlenecks),
            'severity_score': sum(b['severity'] for b in bottlenecks) / len(bottlenecks) if bottlenecks else 0,
            'recommendations': self._generate_bottleneck_recommendations(bottlenecks)
        }
    
    def _generate_improvement_suggestions(self) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        if not self.analysis_result:
            # 임시로 필요한 분석 수행
            production_analysis = self._analyze_production()
            efficiency_analysis = self._analyze_efficiency()
            cost_analysis = self._analyze_costs()
        else:
            production_analysis = self.analysis_result.production_analysis
            efficiency_analysis = self.analysis_result.efficiency_analysis
            cost_analysis = self.analysis_result.cost_analysis
        
        # 생산량 관련 제안
        if production_analysis['overall_achievement'] < 90:
            suggestions.append("전체 목표 달성률이 90% 미만입니다. 고효율 라인의 가동률을 높이거나 추가 설비 투자를 검토하세요.")
        
        # 효율성 관련 제안
        if efficiency_analysis['capacity_utilization'] < 70:
            suggestions.append("전체 설비 가동률이 70% 미만입니다. 생산 계획을 재검토하거나 유휴 설비 활용 방안을 모색하세요.")
        
        if efficiency_analysis['quality_efficiency'] < 95:
            suggestions.append("품질 효율성이 95% 미만입니다. 고불량률 라인의 품질 개선이나 정비가 필요합니다.")
        
        # 비용 관련 제안
        major_costs = cost_analysis['major_cost_drivers']
        if '운영비' in major_costs[:2]:
            suggestions.append("운영비가 주요 비용 요인입니다. 에너지 효율 개선이나 자동화 투자를 고려하세요.")
        
        if '품질비' in major_costs[:3]:
            suggestions.append("품질 비용이 높습니다. 예방적 품질관리 시스템 도입을 검토하세요.")
        
        # 라인별 제안
        line_efficiency = efficiency_analysis['line_efficiency_ranking']
        if line_efficiency:
            lowest_line = min(line_efficiency.keys(), key=lambda x: line_efficiency[x])
            if line_efficiency[lowest_line] < 50:
                suggestions.append(f"{lowest_line}의 효율성이 매우 낮습니다. 설비 점검이나 교체를 고려하세요.")
        
        # 균형 관련 제안
        if production_analysis.get('production_balance', 1.0) > 1.5:
            suggestions.append("라인 간 생산량 불균형이 심합니다. 작업 부하를 재분배하여 균형을 맞추세요.")
        
        return suggestions
    
    def _perform_sensitivity_analysis(self) -> Dict[str, Any]:
        """민감도 분석"""
        # 주요 파라미터 변화에 따른 영향 분석 (시뮬레이션)
        sensitivity_results = {}
        
        # 현재 성과 지표
        current_profit = self.solution.fitness_components.get('total_profit', 0)
        current_cost = self.solution.fitness_components.get('total_cost', 0)
        current_production = self.solution.calculate_total_production_amount()
        
        # 가상의 민감도 분석 (실제로는 파라미터를 변경해서 재실행해야 함)
        # 여기서는 추정치를 사용
        
        # 불량률 개선 시나리오
        defect_rate_impact = 0
        for line_id, line in self.model.production_lines.items():
            line_production = sum(self.solution.genes[line_id].values())
            if line.defect_rate > 0.03:  # 3% 이상 불량률
                # 불량률을 절반으로 줄였을 때의 예상 효과
                current_defects = line_production * line.defect_rate
                improved_defects = line_production * (line.defect_rate / 2)
                defect_rate_impact += (current_defects - improved_defects) * 500  # 불량품당 500원 절약
        
        sensitivity_results['defect_rate_improvement'] = {
            'parameter': '불량률 50% 개선',
            'cost_impact': -defect_rate_impact,  # 비용 절약
            'profit_impact': defect_rate_impact,
            'impact_percentage': (defect_rate_impact / current_profit * 100) if current_profit > 0 else 0
        }
        
        # 운영비 변화 시나리오
        operating_cost_impact = self.solution.fitness_components.get('operating_cost', 0) * 0.1  # 10% 변화 가정
        sensitivity_results['operating_cost_change'] = {
            'parameter': '운영비 10% 증가',
            'cost_impact': operating_cost_impact,
            'profit_impact': -operating_cost_impact,
            'impact_percentage': (operating_cost_impact / current_profit * 100) if current_profit > 0 else 0
        }
        
        # 생산능력 증가 시나리오
        capacity_impact = current_production * 0.2 * 1000  # 20% 증가, 제품당 1000원 이익 가정
        sensitivity_results['capacity_increase'] = {
            'parameter': '생산능력 20% 증가',
            'cost_impact': capacity_impact * 0.3,  # 비용도 30% 정도 증가
            'profit_impact': capacity_impact * 0.7,  # 순이익은 70%
            'impact_percentage': (capacity_impact * 0.7 / current_profit * 100) if current_profit > 0 else 0
        }
        
        return {
            'scenarios': sensitivity_results,
            'most_impactful': max(sensitivity_results.keys(), key=lambda x: abs(sensitivity_results[x]['impact_percentage'])) if sensitivity_results else None,
            'summary': self._summarize_sensitivity(sensitivity_results)
        }
    
    def _calculate_improvement_rate(self) -> float:
        """개선률 계산 (초기 대비)"""
        if len(self.ga_result.fitness_history) < 2:
            return 0.0
        
        initial_fitness = self.ga_result.fitness_history[0]
        final_fitness = self.ga_result.fitness_history[-1]
        
        if initial_fitness == 0:
            return 0.0
        
        return ((final_fitness - initial_fitness) / abs(initial_fitness)) * 100
    
    def _analyze_convergence_stability(self) -> Dict[str, float]:
        """수렴 안정성 분석"""
        history = self.ga_result.fitness_history
        if len(history) < 10:
            return {'stability_score': 0.0, 'convergence_rate': 0.0}
        
        # 마지막 10% 구간의 변동성 분석
        last_10_percent = history[-len(history)//10:]
        stability_score = 100 - (np.std(last_10_percent) / np.mean(last_10_percent) * 100) if np.mean(last_10_percent) != 0 else 0
        
        # 수렴 속도 (50% 개선까지 걸린 세대)
        target_improvement = (history[-1] - history[0]) * 0.5 + history[0]
        convergence_gen = 0
        for i, fitness in enumerate(history):
            if fitness >= target_improvement:
                convergence_gen = i
                break
        
        convergence_rate = (convergence_gen / len(history) * 100) if len(history) > 0 else 0
        
        return {
            'stability_score': max(0, stability_score),
            'convergence_rate': convergence_rate
        }
    
    def _calculate_production_balance(self) -> float:
        """생산량 균형 지수 계산"""
        line_productions = []
        for line_id, line in self.model.production_lines.items():
            line_productions.append(sum(self.solution.genes[line_id].values()))
        
        if not line_productions or max(line_productions) == 0:
            return 1.0
        
        # 변동계수 (CV)를 사용한 균형 지수
        cv = np.std(line_productions) / np.mean(line_productions)
        return cv
    
    def _identify_major_cost_drivers(self, cost_breakdown: Dict[str, float]) -> List[str]:
        """주요 비용 동인 식별"""
        sorted_costs = sorted(cost_breakdown.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_costs if item[1] > 0]
    
    def _identify_critical_constraints(self, margin_analysis: Dict[str, float]) -> List[str]:
        """임계 제약 조건 식별"""
        critical = []
        for constraint, margin in margin_analysis.items():
            if '용량여유도' in constraint and margin < 10:  # 10% 미만 여유도
                critical.append(f"{constraint}: {margin:.1f}% 여유도")
            elif '수요여유도' in constraint and margin < -5:  # 5% 이상 부족
                critical.append(f"{constraint}: {margin:.1f}% 부족")
        return critical
    
    def _generate_bottleneck_recommendations(self, bottlenecks: List[Dict]) -> List[str]:
        """병목 해결 권장사항 생성"""
        recommendations = []
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == '용량 병목':
                recommendations.append(f"{bottleneck['location']}: 추가 설비 투자 또는 작업시간 연장 검토")
            elif bottleneck['type'] == '품질 병목':
                recommendations.append(f"{bottleneck['location']}: 품질 개선 프로그램 도입 또는 설비 정비")
            elif bottleneck['type'] == '비용 병목':
                recommendations.append(f"{bottleneck['location']}: 운영 효율성 개선 또는 에너지 절약 방안 검토")
        
        return recommendations
    
    def _summarize_sensitivity(self, sensitivity_results: Dict) -> str:
        """민감도 분석 요약"""
        if not sensitivity_results:
            return "민감도 분석 데이터가 없습니다."
        
        max_impact = max(sensitivity_results.values(), key=lambda x: abs(x['impact_percentage']))
        return f"가장 큰 영향: {max_impact['parameter']} (이익 {max_impact['impact_percentage']:+.1f}%)"
    
    def save_analysis_report(self, filename: Optional[str] = None) -> str:
        """분석 결과를 JSON 파일로 저장"""
        if not self.analysis_result:
            raise ValueError("분석 결과가 없습니다. analyze_all()을 먼저 실행하세요.")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.json"
        
        filepath = os.path.join(self.results_dir, filename)
        
        # 분석 결과를 딕셔너리로 변환
        report_data = asdict(self.analysis_result)
        report_data['metadata'] = {
            'analysis_timestamp': datetime.now().isoformat(),
            'model_summary': self.model.get_model_summary(),
            'optimization_parameters': {
                'goal': self.model.optimization_goal.value,
                'weights': self.model.optimization_weights
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)
        
        return filepath

class ProductionVisualizer:
    """생산 최적화 결과 시각화 클래스"""
    plt.rcParams['font.family'] = 'Malgun Gothic'
    def __init__(self, analyzer: ProductionAnalyzer):
        self.analyzer = analyzer
        self.model = analyzer.model
        self.solution = analyzer.solution
        self.analysis = analyzer.analysis_result
        self.colors = VISUALIZATION_CONFIG['color_palette']
        
        # 한글 폰트 설정 강화
        self._setup_korean_font()
        
        # 시각화 설정
        plt.style.use('seaborn-v0_8')
        sns.set_palette(self.colors)
    
    # result_analyzer.py 파일의 ProductionVisualizer 클래스 내 _setup_korean_font 메서드를 아래 코드로 교체하세요.

    def _setup_korean_font(self):
        """한글 폰트를 'Malgun Gothic'으로 직접 설정합니다."""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        print("✅ 한글 폰트: 'Malgun Gothic' 설정 시도 완료.") # 확인용 print문
        print("   (주의: 'Malgun Gothic' 폰트가 시스템에 설치되어 있고 Matplotlib에서 인식 가능해야 합니다.)") # 확인용 print문
        # Matplotlib이 현재 사용하려는 폰트 패밀리 확인
        print(f"ℹ️ Matplotlib 현재 설정된 폰트: {plt.rcParams['font.family']}")
        # Matplotlib이 인식하는 실제 폰트 파일 경로 확인 (특정 폰트 이름으로)
        import matplotlib.font_manager as fm
        try:
            font_path = fm.findfont('Malgun Gothic')
            print(f"✅ 'Malgun Gothic' 폰트 파일 경로: {font_path}")
        except Exception as e:
            print(f"❌ 'Malgun Gothic' 폰트를 찾을 수 없음: {e}")

        # 만약 Arial로 계속 나온다면, Arial 폰트 정보도 확인
        try:
            arial_path = fm.findfont('Arial')
            print(f"ℹ️ 'Arial' 폰트 파일 경로 (참고용): {arial_path}")
        except:
            pass # Arial 못찾아도 일단 진행
    
    def create_production_dashboard(self, save_path: Optional[str] = None) -> str:
        """생산 대시보드 생성"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        if not self.analysis:
            raise ValueError("분석 결과가 없습니다.")
        
        # 대시보드 레이아웃 설정 (2x3 그리드)
        fig = plt.figure(figsize=(20, 15))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 제품별 생산량 vs 목표
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_production_vs_target(ax1)
        
        # 2. 라인별 가동률
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_line_utilization(ax2)
        
        # 3. 비용 구성
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_cost_breakdown(ax3)
        
        # 4. GA 수렴 과정
        ax4 = fig.add_subplot(gs[1, :2])
        self._plot_ga_convergence(ax4)
        
        # 5. 라인별 효율성 히트맵
        ax5 = fig.add_subplot(gs[1, 2])
        self._plot_efficiency_heatmap(ax5)
        
        # 6. 종합 성과 지표
        ax6 = fig.add_subplot(gs[2, :])
        self._plot_performance_summary(ax6)
        
        plt.suptitle('생산 최적화 결과 대시보드', fontsize=20, fontweight='bold')
        
        # 저장
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.analyzer.results_dir, f"dashboard_{timestamp}.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path
    
    def _plot_production_vs_target(self, ax):
        """제품별 생산량 vs 목표 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        production_data = self.analysis.production_analysis
        
        products = list(production_data['product_production'].keys())
        actual = list(production_data['product_production'].values())
        target = list(production_data['product_targets'].values())
        
        x = np.arange(len(products))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, actual, width, label='실제 생산량', alpha=0.8)
        bars2 = ax.bar(x + width/2, target, width, label='목표 생산량', alpha=0.8)
        
        ax.set_xlabel('제품')
        ax.set_ylabel('생산량 (개)')
        ax.set_title('제품별 생산량 vs 목표')
        ax.set_xticks(x)
        ax.set_xticklabels(products, rotation=45, ha='right')
        ax.legend()
        
        # 값 표시
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)
    
    def _plot_line_utilization(self, ax):
        """라인별 가동률 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        utilization_data = self.analysis.production_analysis['line_utilization']
        
        lines = list(utilization_data.keys())
        utilization = list(utilization_data.values())
        
        bars = ax.barh(lines, utilization, alpha=0.8)
        
        # 색상 구분 (가동률에 따라)
        for i, (bar, util) in enumerate(zip(bars, utilization)):
            if util > 90:
                bar.set_color('#ff6b6b')  # 높은 가동률 - 빨간색
            elif util > 70:
                bar.set_color('#feca57')  # 중간 가동률 - 노란색
            else:
                bar.set_color('#48dbfb')  # 낮은 가동률 - 파란색
        
        ax.set_xlabel('가동률 (%)')
        ax.set_title('라인별 가동률')
        ax.set_xlim(0, 100)
        
        # 기준선 추가
        ax.axvline(x=80, color='red', linestyle=':', alpha=0.6, linewidth=1, label='목표 80%')
        ax.legend(loc='lower right', bbox_to_anchor=(0.3, 1))
        
        # 값 표시
        for i, v in enumerate(utilization):
            ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=9)
    
    def _plot_cost_breakdown(self, ax):
        """비용 구성 파이 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        cost_data = self.analysis.cost_analysis['cost_breakdown']
        
        # 0이 아닌 비용만 표시
        non_zero_costs = {k: v for k, v in cost_data.items() if v > 0}
        
        if non_zero_costs:
            labels = list(non_zero_costs.keys())
            sizes = list(non_zero_costs.values())
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                             startangle=90, textprops={'fontsize': 8})
            
            # 작은 항목들은 라벨을 바깥으로
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
        ax.set_title('비용 구성')
    
    def _plot_ga_convergence(self, ax):
        """GA 수렴 과정 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        history = self.analyzer.ga_result.fitness_history
        generations = range(len(history))
        
        ax.plot(generations, history, linewidth=2, alpha=0.8)
        ax.set_xlabel('세대')
        ax.set_ylabel('적합도')
        ax.set_title('유전 알고리즘 수렴 과정')
        ax.grid(True, alpha=0.3)
        
        # 수렴 지점 표시
        convergence_gen = self.analyzer.ga_result.convergence_generation
        if convergence_gen < len(history):
            ax.axvline(x=convergence_gen, color='red', linestyle='--', 
                      label=f'수렴 지점 (세대 {convergence_gen})')
            ax.legend()
        
        # 최종 적합도 표시
        final_fitness = history[-1]
        ax.annotate(f'최종: {final_fitness:.2f}',
                   xy=(len(history)-1, final_fitness),
                   xytext=(10, 10), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
    
    def _plot_efficiency_heatmap(self, ax):
        """라인별 효율성 히트맵"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        # 라인별 다양한 지표들을 히트맵으로 표시
        lines = list(self.model.production_lines.keys())
        metrics = ['가동률', '품질', '비용효율성']
        
        data = []
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id) * 100
            quality = (1 - line.defect_rate) * 100
            
            # 비용 효율성 (역수 사용)
            line_production = sum(self.solution.genes[line_id].values())
            if line_production > 0:
                cost_per_unit = (line.operating_cost * self.solution.get_line_utilization(line_id) * line.max_working_hours) / line_production
                cost_efficiency = 100 / (1 + cost_per_unit / 1000)  # 정규화
            else:
                cost_efficiency = 0
            
            data.append([utilization, quality, cost_efficiency])
        
        # 라인 이름으로 변환
        line_names = [self.model.production_lines[line_id].line_name for line_id in lines]
        
        im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        
        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(metrics)
        ax.set_yticks(range(len(line_names)))
        ax.set_yticklabels(line_names)
        ax.set_title('라인별 효율성 히트맵')
        
        # 값 표시
        for i in range(len(line_names)):
            for j in range(len(metrics)):
                text = ax.text(j, i, f'{data[i][j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        # 컬러바
        plt.colorbar(im, ax=ax, shrink=0.8)
    
    def _plot_performance_summary(self, ax):
        """종합 성과 지표 표"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        # 테이블 형태로 주요 지표 표시
        ax.axis('tight')
        ax.axis('off')
        
        # 성과 지표 데이터
        summary_data = [
            ['지표', '값', '평가'],
            ['총 생산량', f"{self.analysis.production_analysis['total_production']:,.0f}개", 
             self._get_rating(self.analysis.production_analysis['overall_achievement'], [80, 90, 95])],
            ['목표 달성률', f"{self.analysis.production_analysis['overall_achievement']:.1f}%",
             self._get_rating(self.analysis.production_analysis['overall_achievement'], [80, 90, 95])],
            ['총 비용', f"{self.analysis.cost_analysis['total_cost']:,.0f}원", '-'],
            ['전체 가동률', f"{self.analysis.efficiency_analysis['capacity_utilization']:.1f}%",
             self._get_rating(self.analysis.efficiency_analysis['capacity_utilization'], [60, 75, 85])],
            ['품질 효율성', f"{self.analysis.efficiency_analysis['quality_efficiency']:.1f}%",
             self._get_rating(self.analysis.efficiency_analysis['quality_efficiency'], [90, 95, 98])],
            ['제약 위반', f"{self.analysis.constraint_analysis['total_violations']}개",
             '우수' if self.analysis.constraint_analysis['total_violations'] == 0 else '개선필요'],
            ['병목 지점', f"{self.analysis.bottleneck_analysis['bottleneck_count']}개",
             self._get_rating(5 - self.analysis.bottleneck_analysis['bottleneck_count'], [1, 3, 5])]
        ]
        
        # 테이블 생성
        table = ax.table(cellText=summary_data[1:], colLabels=summary_data[0],
                        cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2)
        
        # 헤더 스타일
        for i in range(3):
            table[(0, i)].set_facecolor('#4ECDC4')
            table[(0, i)].set_text_props(weight='bold')
        
        # 평가에 따른 색상 설정
        for i in range(1, len(summary_data)):
            rating = summary_data[i][2]
            if rating == '우수':
                table[(i, 2)].set_facecolor('#90EE90')  # 연한 초록색
            elif rating == '양호':
                table[(i, 2)].set_facecolor('#FFE4B5')  # 연한 주황색
            elif rating == '개선필요':
                table[(i, 2)].set_facecolor('#FFB6C1')  # 연한 빨간색
        
        ax.set_title('종합 성과 지표', fontsize=14, fontweight='bold', pad=20)
    
    def _get_rating(self, value: float, thresholds: List[float]) -> str:
        """값에 따른 평가 등급 반환"""
        if value >= thresholds[2]:
            return '우수'
        elif value >= thresholds[1]:
            return '양호'
        elif value >= thresholds[0]:
            return '보통'
        else:
            return '개선필요'
    
    def create_detailed_charts(self, save_dir: Optional[str] = None) -> List[str]:
        """상세 차트들을 개별 파일로 생성"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        if not save_dir:
            save_dir = self.analyzer.results_dir
        
        chart_files = []
        
        # 1. 제품별 상세 분석 차트
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 제품별 생산량 및 달성률
        self._plot_product_detailed_analysis(ax1, ax2, ax3, ax4)
        
        plt.tight_layout()
        chart_file = os.path.join(save_dir, f"product_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(chart_file)
        
        # 2. 라인별 상세 분석 차트
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 라인별 세부 지표
        self._plot_line_detailed_analysis(ax1, ax2, ax3, ax4)
        
        plt.tight_layout()
        chart_file = os.path.join(save_dir, f"line_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        chart_files.append(chart_file)
        
        return chart_files
    
    def _plot_product_detailed_analysis(self, ax1, ax2, ax3, ax4):
        """제품별 상세 분석 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        production_data = self.analysis.production_analysis
        
        # ax1: 달성률
        products = list(production_data['product_achievement'].keys())
        achievement = list(production_data['product_achievement'].values())
        
        bars = ax1.bar(products, achievement, alpha=0.8)
        ax1.axhline(y=100, color='red', linestyle='--', alpha=0.7, label='목표선')
        ax1.set_ylabel('달성률 (%)')
        ax1.set_title('제품별 목표 달성률')
        ax1.legend()
        
        for i, v in enumerate(achievement):
            color = 'green' if v >= 100 else 'red'
            ax1.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom', color=color, fontweight='bold')
        
        # ax2: 제품별 수익성 (단위당 이익 × 생산량)
        product_profits = {}
        for product_id, product in self.model.products.items():
            unit_profit = product.calculate_unit_profit()
            production = self.solution.get_total_production(product_id)
            product_profits[product.product_name] = unit_profit * production
        
        ax2.bar(product_profits.keys(), product_profits.values(), alpha=0.8, color='gold')
        ax2.set_ylabel('총 이익 (원)')
        ax2.set_title('제품별 총 이익 기여도')
        
        # ax3: 제품별 라인 배정 현황
        product_line_data = []
        for product_id, product in self.model.products.items():
            for line_id, line in self.model.production_lines.items():
                production = self.solution.genes[line_id].get(product_id, 0)
                if production > 0:
                    product_line_data.append({
                        'Product': product.product_name,
                        'Line': line.line_name,
                        'Production': production
                    })
        
        if product_line_data:
            df = pd.DataFrame(product_line_data)
            pivot_df = df.pivot(index='Product', columns='Line', values='Production').fillna(0)
            
            im = ax3.imshow(pivot_df.values, cmap='Blues', aspect='auto')
            ax3.set_xticks(range(len(pivot_df.columns)))
            ax3.set_xticklabels(pivot_df.columns, rotation=45, ha='right')
            ax3.set_yticks(range(len(pivot_df.index)))
            ax3.set_yticklabels(pivot_df.index)
            ax3.set_title('제품-라인 배정 현황')
            
            # 값 표시
            for i in range(len(pivot_df.index)):
                for j in range(len(pivot_df.columns)):
                    value = pivot_df.iloc[i, j]
                    if value > 0:
                        ax3.text(j, i, f'{value:.0f}', ha="center", va="center", 
                                color="white" if value > pivot_df.values.max()/2 else "black")
        
        # ax4: 제품별 품질 성과
        product_quality = {}
        for product_id, product in self.model.products.items():
            total_production = 0
            effective_production = 0
            for line_id, line in self.model.production_lines.items():
                production = self.solution.genes[line_id].get(product_id, 0)
                total_production += production
                effective_production += production * (1 - line.defect_rate)
            
            quality_rate = (effective_production / total_production * 100) if total_production > 0 else 0
            product_quality[product.product_name] = quality_rate
        
        ax4.bar(product_quality.keys(), product_quality.values(), alpha=0.8, color='lightgreen')
        ax4.axhline(y=95, color='red', linestyle='--', alpha=0.7, label='품질 목표')
        ax4.set_ylabel('품질률 (%)')
        ax4.set_title('제품별 품질 성과')
        ax4.set_ylim(90, 100)
        ax4.legend()
    
    def _plot_line_detailed_analysis(self, ax1, ax2, ax3, ax4):
        """라인별 상세 분석 차트"""
        plt.rcParams['font.family'] = 'Malgun Gothic'
        # ax1: 라인별 시간당 생산량
        line_hourly_production = {}
        for line_id, line in self.model.production_lines.items():
            total_production = sum(self.solution.genes[line_id].values())
            working_hours = self.solution.get_line_utilization(line_id) * line.max_working_hours
            hourly_production = total_production / working_hours if working_hours > 0 else 0
            line_hourly_production[line.line_name] = hourly_production
        
        ax1.bar(line_hourly_production.keys(), line_hourly_production.values(), alpha=0.8)
        ax1.set_ylabel('시간당 생산량 (개/시간)')
        ax1.set_title('라인별 시간당 생산량')
        
        # ax2: 라인별 비용 구성
        line_costs = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            
            operating_cost = working_hours * line.operating_cost
            maintenance_cost = line.maintenance_cost / 30  # 일간 유지보수비
            
            line_costs[line.line_name] = {
                '운영비': operating_cost,
                '유지보수비': maintenance_cost
            }
        
        # 스택 바 차트
        lines = list(line_costs.keys())
        operating_costs = [line_costs[line]['운영비'] for line in lines]
        maintenance_costs = [line_costs[line]['유지보수비'] for line in lines]
        
        ax2.bar(lines, operating_costs, label='운영비', alpha=0.8)
        ax2.bar(lines, maintenance_costs, bottom=operating_costs, label='유지보수비', alpha=0.8)
        ax2.set_ylabel('비용 (원)')
        ax2.set_title('라인별 비용 구성')
        ax2.legend()
        
        # ax3: 라인별 효율성 레이더 차트 (간단한 막대로 대체)
        efficiency_metrics = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id) * 100
            quality = (1 - line.defect_rate) * 100
            
            # 생산성 (시간당 생산량 대비)
            max_hourly = max(line_hourly_production.values()) if line_hourly_production.values() else 1
            productivity = (line_hourly_production[line.line_name] / max_hourly * 100) if max_hourly > 0 else 0
            
            efficiency_metrics[line.line_name] = (utilization + quality + productivity) / 3
        
        ax3.bar(efficiency_metrics.keys(), efficiency_metrics.values(), alpha=0.8, color='orange')
        ax3.set_ylabel('종합 효율성 점수')
        ax3.set_title('라인별 종합 효율성')
        ax3.set_ylim(0, 100)
        
        # ax4: 라인별 가동 시간 분석
        line_hours = {}
        for line_id, line in self.model.production_lines.items():
            utilization = self.solution.get_line_utilization(line_id)
            working_hours = utilization * line.max_working_hours
            idle_hours = line.max_working_hours - working_hours
            
            line_hours[line.line_name] = {
                '가동시간': working_hours,
                '유휴시간': idle_hours
            }
        
        lines = list(line_hours.keys())
        working_hours = [line_hours[line]['가동시간'] for line in lines]
        idle_hours = [line_hours[line]['유휴시간'] for line in lines]
        
        ax4.bar(lines, working_hours, label='가동시간', alpha=0.8)
        ax4.bar(lines, idle_hours, bottom=working_hours, label='유휴시간', alpha=0.8)
        ax4.set_ylabel('시간')
        ax4.set_title('라인별 가동/유휴 시간')
        ax4.legend()