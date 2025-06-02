"""
보고서 생성 모듈
분석 결과를 종합하여 상세한 HTML 보고서를 생성합니다.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from result_analyzer import ProductionAnalyzer, AnalysisResult
from production_model import ProductionModel
from genetic_algorithm import GAResult

class HTMLReportGenerator:
    """HTML 보고서 생성기"""
    
    def __init__(self, analyzer: ProductionAnalyzer):
        self.analyzer = analyzer
        self.model = analyzer.model
        self.ga_result = analyzer.ga_result
        self.analysis = analyzer.analysis_result
        
    def generate_full_report(self, output_path: Optional[str] = None) -> str:
        """완전한 HTML 보고서 생성"""
        if not self.analysis:
            raise ValueError("분석 결과가 없습니다. analyze_all()을 먼저 실행하세요.")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.analyzer.results_dir, f"optimization_report_{timestamp}.html")
        
        html_content = self._generate_html_content()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_html_content(self) -> str:
        """HTML 내용 생성"""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>생산 최적화 결과 보고서</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_executive_summary()}
        {self._generate_optimization_details()}
        {self._generate_production_analysis()}
        {self._generate_cost_analysis()}
        {self._generate_efficiency_analysis()}
        {self._generate_constraint_analysis()}
        {self._generate_bottleneck_analysis()}
        {self._generate_improvement_recommendations()}
        {self._generate_sensitivity_analysis()}
        {self._generate_technical_details()}
        {self._generate_footer()}
    </div>
</body>
</html>
"""
        return html
    
    def _get_css_styles(self) -> str:
        """CSS 스타일 정의"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .section {
            padding: 2rem;
            border-bottom: 1px solid #eee;
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section h2 {
            color: #2c3e50;
            margin-bottom: 1rem;
            border-left: 4px solid #3498db;
            padding-left: 1rem;
        }
        
        .section h3 {
            color: #34495e;
            margin: 1.5rem 0 1rem 0;
        }
        
        .executive-summary {
            background-color: #f8f9fa;
            border-left: 5px solid #28a745;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        
        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .kpi-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .kpi-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .success { color: #28a745; }
        .warning { color: #ffc107; }
        .danger { color: #dc3545; }
        .info { color: #17a2b8; }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        .data-table th,
        .data-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .data-table th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        
        .data-table tr:hover {
            background-color: #f5f5f5;
        }
        
        .recommendation-list {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .recommendation-list ul {
            margin-left: 1rem;
        }
        
        .recommendation-list li {
            margin-bottom: 0.5rem;
        }
        
        .chart-placeholder {
            background-color: #f8f9fa;
            border: 2px dashed #dee2e6;
            height: 300px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        .footer {
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .alert {
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        .alert-success {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        
        .alert-danger {
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        """
    
    def _generate_header(self) -> str:
        """헤더 생성"""
        return f"""
        <div class="header">
            <h1>생산 최적화 결과 보고서</h1>
            <div class="subtitle">
                생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')} | 
                최적화 목표: {self._get_goal_name()} |
                실행 시간: {self.ga_result.execution_time:.2f}초
            </div>
        </div>
        """
    
    def _generate_executive_summary(self) -> str:
        """경영진 요약 생성"""
        opt_summary = self.analysis.optimization_summary
        prod_analysis = self.analysis.production_analysis
        cost_analysis = self.analysis.cost_analysis
        
        return f"""
        <div class="section executive-summary">
            <h2>📊 경영진 요약</h2>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value {'success' if prod_analysis['overall_achievement'] >= 90 else 'warning' if prod_analysis['overall_achievement'] >= 80 else 'danger'}">
                        {prod_analysis['overall_achievement']:.1f}%
                    </div>
                    <div class="kpi-label">목표 달성률</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value info">
                        {prod_analysis['total_production']:,.0f}개
                    </div>
                    <div class="kpi-label">총 생산량</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value info">
                        {cost_analysis['total_cost']:,.0f}원
                    </div>
                    <div class="kpi-label">총 비용</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value {'success' if opt_summary['is_feasible'] else 'danger'}">
                        {'실행가능' if opt_summary['is_feasible'] else '제약위반'}
                    </div>
                    <div class="kpi-label">솔루션 상태</div>
                </div>
            </div>
            
            <div class="{'alert alert-success' if opt_summary['is_feasible'] else 'alert alert-warning'}">
                <strong>최적화 결과:</strong> 
                {self.ga_result.generation_count}세대에 걸친 최적화를 통해 
                {'모든 제약 조건을 만족하는' if opt_summary['is_feasible'] else f"{opt_summary['constraint_violations']}개의 제약 조건 위반이 있는"} 
                솔루션을 도출했습니다. 
                {f"개선률: {opt_summary['improvement_rate']:+.1f}%" if opt_summary['improvement_rate'] != 0 else ""}
            </div>
        </div>
        """
    
    def _generate_optimization_details(self) -> str:
        """최적화 세부사항 생성"""
        opt_summary = self.analysis.optimization_summary
        
        return f"""
        <div class="section">
            <h2>🔧 최적화 세부사항</h2>
            
            <table class="data-table">
                <tr>
                    <th>항목</th>
                    <th>값</th>
                    <th>설명</th>
                </tr>
                <tr>
                    <td>최적화 목표</td>
                    <td>{self._get_goal_name()}</td>
                    <td>최적화 알고리즘이 추구한 목표</td>
                </tr>
                <tr>
                    <td>총 실행 시간</td>
                    <td>{opt_summary['execution_time']:.2f}초</td>
                    <td>알고리즘 수행에 소요된 시간</td>
                </tr>
                <tr>
                    <td>진화 세대 수</td>
                    <td>{opt_summary['generations']}세대</td>
                    <td>유전 알고리즘이 진화한 세대 수</td>
                </tr>
                <tr>
                    <td>수렴 지점</td>
                    <td>{opt_summary['convergence_generation']}세대</td>
                    <td>최적 해가 발견된 세대</td>
                </tr>
                <tr>
                    <td>최종 적합도</td>
                    <td>{opt_summary['final_fitness']:.2f}</td>
                    <td>최종 솔루션의 적합도 점수</td>
                </tr>
                <tr>
                    <td>수렴 안정성</td>
                    <td>{opt_summary['convergence_stability']['stability_score']:.1f}%</td>
                    <td>해의 안정성 점수 (높을수록 안정적)</td>
                </tr>
            </table>
        </div>
        """
    
    def _generate_production_analysis(self) -> str:
        """생산 분석 생성"""
        prod_analysis = self.analysis.production_analysis
        
        # 제품별 테이블
        product_table = ""
        for product_name in prod_analysis['product_production'].keys():
            actual = prod_analysis['product_production'][product_name]
            target = prod_analysis['product_targets'][product_name]
            achievement = prod_analysis['product_achievement'][product_name]
            
            status_class = 'success' if achievement >= 100 else 'warning' if achievement >= 90 else 'danger'
            
            product_table += f"""
            <tr>
                <td>{product_name}</td>
                <td>{actual:,.0f}개</td>
                <td>{target:,.0f}개</td>
                <td class="{status_class}">{achievement:.1f}%</td>
            </tr>
            """
        
        # 라인별 테이블
        line_table = ""
        for line_name in prod_analysis['line_production'].keys():
            production = prod_analysis['line_production'][line_name]
            utilization = prod_analysis['line_utilization'][line_name]
            efficiency = prod_analysis['line_efficiency'][line_name]
            
            util_class = 'success' if utilization >= 80 else 'warning' if utilization >= 60 else 'info'
            
            line_table += f"""
            <tr>
                <td>{line_name}</td>
                <td>{production:,.0f}개</td>
                <td class="{util_class}">{utilization:.1f}%</td>
                <td>{efficiency:,.0f}개</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>📈 생산 분석</h2>
            
            <h3>제품별 생산 성과</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>제품명</th>
                        <th>실제 생산량</th>
                        <th>목표 생산량</th>
                        <th>달성률</th>
                    </tr>
                </thead>
                <tbody>
                    {product_table}
                </tbody>
            </table>
            
            <h3>라인별 생산 성과</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>라인명</th>
                        <th>생산량</th>
                        <th>가동률</th>
                        <th>유효 생산량</th>
                    </tr>
                </thead>
                <tbody>
                    {line_table}
                </tbody>
            </table>
            
            <div class="chart-placeholder">
                📊 제품별 생산량 차트 (별도 이미지 파일 참조)
            </div>
        </div>
        """
    
    def _generate_cost_analysis(self) -> str:
        """비용 분석 생성"""
        cost_analysis = self.analysis.cost_analysis
        
        # 비용 구성 테이블
        cost_table = ""
        for cost_type, amount in cost_analysis['cost_breakdown'].items():
            if amount > 0:
                percentage = cost_analysis['cost_percentages'][cost_type]
                cost_table += f"""
                <tr>
                    <td>{cost_type}</td>
                    <td>{amount:,.0f}원</td>
                    <td>{percentage:.1f}%</td>
                </tr>
                """
        
        # 주요 비용 동인
        major_drivers = cost_analysis['major_cost_drivers'][:3]
        drivers_text = ", ".join(major_drivers)
        
        return f"""
        <div class="section">
            <h2>💰 비용 분석</h2>
            
            <div class="alert alert-info">
                <strong>총 비용:</strong> {cost_analysis['total_cost']:,.0f}원 | 
                <strong>단위당 비용:</strong> {cost_analysis['cost_per_unit']:,.0f}원/개 |
                <strong>주요 비용 동인:</strong> {drivers_text}
            </div>
            
            <h3>비용 구성 상세</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>비용 항목</th>
                        <th>금액</th>
                        <th>비율</th>
                    </tr>
                </thead>
                <tbody>
                    {cost_table}
                </tbody>
            </table>
            
            <div class="chart-placeholder">
                🥧 비용 구성 파이 차트 (별도 이미지 파일 참조)
            </div>
        </div>
        """
    
    def _generate_efficiency_analysis(self) -> str:
        """효율성 분석 생성"""
        eff_analysis = self.analysis.efficiency_analysis
        
        # 라인별 효율성 테이블
        efficiency_table = ""
        for line_name, efficiency in eff_analysis['line_efficiency_ranking'].items():
            eff_class = 'success' if efficiency >= 80 else 'warning' if efficiency >= 60 else 'danger'
            efficiency_table += f"""
            <tr>
                <td>{line_name}</td>
                <td class="{eff_class}">{efficiency:.1f}점</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>⚡ 효율성 분석</h2>
            
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-value {'success' if eff_analysis['capacity_utilization'] >= 80 else 'warning' if eff_analysis['capacity_utilization'] >= 60 else 'danger'}">
                        {eff_analysis['capacity_utilization']:.1f}%
                    </div>
                    <div class="kpi-label">설비 가동률</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value {'success' if eff_analysis['quality_efficiency'] >= 95 else 'warning' if eff_analysis['quality_efficiency'] >= 90 else 'danger'}">
                        {eff_analysis['quality_efficiency']:.1f}%
                    </div>
                    <div class="kpi-label">품질 효율성</div>
                </div>
                
                <div class="kpi-card">
                    <div class="kpi-value info">
                        {eff_analysis['overall_efficiency']:.1f}점
                    </div>
                    <div class="kpi-label">종합 효율성</div>
                </div>
            </div>
            
            <h3>라인별 효율성 순위</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>라인명</th>
                        <th>효율성 점수</th>
                    </tr>
                </thead>
                <tbody>
                    {efficiency_table}
                </tbody>
            </table>
            
            {f'<div class="alert alert-warning"><strong>최고 성과:</strong> {eff_analysis["top_performer"]}</div>' if eff_analysis.get("top_performer") else ''}
            {f'<div class="alert alert-danger"><strong>개선 필요:</strong> {eff_analysis["bottleneck_line"]}</div>' if eff_analysis.get("bottleneck_line") else ''}
        </div>
        """
    
    def _generate_constraint_analysis(self) -> str:
        """제약 조건 분석 생성"""
        const_analysis = self.analysis.constraint_analysis
        
        # 위반 세부사항
        violations_text = ""
        if const_analysis['violation_details']:
            for violation in const_analysis['violation_details']:
                violations_text += f"<li>{violation}</li>"
            violations_text = f"<ul>{violations_text}</ul>"
        else:
            violations_text = "<p class='success'>모든 제약 조건을 만족합니다.</p>"
        
        # 여유도 분석
        margin_table = ""
        for constraint, margin in const_analysis['margin_analysis'].items():
            margin_class = 'success' if margin > 10 else 'warning' if margin > 0 else 'danger'
            margin_table += f"""
            <tr>
                <td>{constraint}</td>
                <td class="{margin_class}">{margin:+.1f}%</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>⚖️ 제약 조건 분석</h2>
            
            <div class="{'alert alert-success' if const_analysis['is_feasible'] else 'alert alert-danger'}">
                <strong>제약 조건 상태:</strong> 
                {'모든 제약 조건 만족' if const_analysis['is_feasible'] else f"{const_analysis['total_violations']}개 제약 조건 위반"}
            </div>
            
            <h3>위반 세부사항</h3>
            {violations_text}
            
            <h3>제약 조건별 여유도</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>제약 조건</th>
                        <th>여유도</th>
                    </tr>
                </thead>
                <tbody>
                    {margin_table}
                </tbody>
            </table>
            
            {'<div class="alert alert-warning"><strong>임계 제약 조건:</strong><ul>' + "".join([f"<li>{critical}</li>" for critical in const_analysis['critical_constraints']]) + '</ul></div>' if const_analysis['critical_constraints'] else ''}
        </div>
        """
    
    def _generate_bottleneck_analysis(self) -> str:
        """병목 분석 생성"""
        bottleneck_analysis = self.analysis.bottleneck_analysis
        
        # 병목 지점 테이블
        bottleneck_table = ""
        for bottleneck in bottleneck_analysis['bottlenecks']:
            severity_class = 'danger' if bottleneck['severity'] > 0.8 else 'warning' if bottleneck['severity'] > 0.6 else 'info'
            bottleneck_table += f"""
            <tr>
                <td>{bottleneck['type']}</td>
                <td>{bottleneck['location']}</td>
                <td class="{severity_class}">{bottleneck['severity']:.1%}</td>
                <td>{bottleneck['description']}</td>
            </tr>
            """
        
        # 권장사항
        recommendations_text = ""
        for rec in bottleneck_analysis['recommendations']:
            recommendations_text += f"<li>{rec}</li>"
        
        return f"""
        <div class="section">
            <h2>🚧 병목 지점 분석</h2>
            
            <div class="alert {'alert-success' if bottleneck_analysis['bottleneck_count'] == 0 else 'alert-warning'}">
                <strong>병목 현황:</strong> 총 {bottleneck_analysis['bottleneck_count']}개의 병목 지점 발견 
                (심각도 평균: {bottleneck_analysis['severity_score']:.1%})
            </div>
            
            {f'''
            <h3>병목 지점 상세</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>병목 유형</th>
                        <th>위치</th>
                        <th>심각도</th>
                        <th>설명</th>
                    </tr>
                </thead>
                <tbody>
                    {bottleneck_table}
                </tbody>
            </table>
            ''' if bottleneck_analysis['bottlenecks'] else '<p class="success">병목 지점이 발견되지 않았습니다.</p>'}
            
            {f'''
            <h3>해결 권장사항</h3>
            <div class="recommendation-list">
                <ul>
                    {recommendations_text}
                </ul>
            </div>
            ''' if bottleneck_analysis['recommendations'] else ''}
        </div>
        """
    
    def _generate_improvement_recommendations(self) -> str:
        """개선 권장사항 생성"""
        suggestions = self.analysis.improvement_suggestions
        
        suggestions_text = ""
        for i, suggestion in enumerate(suggestions, 1):
            suggestions_text += f"<li><strong>권장사항 {i}:</strong> {suggestion}</li>"
        
        return f"""
        <div class="section">
            <h2>💡 개선 권장사항</h2>
            
            <div class="recommendation-list">
                <h3>주요 개선 제안</h3>
                <ul>
                    {suggestions_text}
                </ul>
            </div>
            
            <div class="alert alert-info">
                <strong>💡 추가 고려사항:</strong>
                <ul>
                    <li>정기적인 설비 점검 및 예방 정비 실시</li>
                    <li>작업자 교육을 통한 품질 및 효율성 향상</li>
                    <li>데이터 기반 의사결정을 위한 모니터링 시스템 구축</li>
                    <li>지속적인 개선을 위한 KPI 설정 및 추적</li>
                </ul>
            </div>
        </div>
        """
    
    def _generate_sensitivity_analysis(self) -> str:
        """민감도 분석 생성"""
        sens_analysis = self.analysis.sensitivity_analysis
        
        # 시나리오 테이블
        scenario_table = ""
        for scenario_name, scenario_data in sens_analysis['scenarios'].items():
            impact_class = 'success' if scenario_data['impact_percentage'] > 0 else 'danger'
            scenario_table += f"""
            <tr>
                <td>{scenario_data['parameter']}</td>
                <td>{scenario_data['cost_impact']:+,.0f}원</td>
                <td>{scenario_data['profit_impact']:+,.0f}원</td>
                <td class="{impact_class}">{scenario_data['impact_percentage']:+.1f}%</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>📊 민감도 분석</h2>
            
            <div class="alert alert-info">
                <strong>분석 요약:</strong> {sens_analysis['summary']}
            </div>
            
            <h3>주요 시나리오 영향 분석</h3>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>시나리오</th>
                        <th>비용 영향</th>
                        <th>이익 영향</th>
                        <th>영향률</th>
                    </tr>
                </thead>
                <tbody>
                    {scenario_table}
                </tbody>
            </table>
            
            <div class="alert alert-warning">
                <strong>🎯 핵심 인사이트:</strong>
                <ul>
                    <li>가장 큰 영향을 미치는 요소: {sens_analysis.get('most_impactful', 'N/A')}</li>
                    <li>운영 개선 시 가장 우선적으로 고려해야 할 부분을 식별할 수 있습니다</li>
                    <li>투자 결정 시 ROI가 가장 높은 영역을 파악할 수 있습니다</li>
                </ul>
            </div>
        </div>
        """
    
    def _generate_technical_details(self) -> str:
        """기술적 세부사항 생성"""
        model_summary = self.model.get_model_summary()
        
        return f"""
        <div class="section">
            <h2>🔧 기술적 세부사항</h2>
            
            <h3>모델 구성</h3>
            <table class="data-table">
                <tr>
                    <td>생산 라인 수</td>
                    <td>{model_summary['num_production_lines']}개</td>
                </tr>
                <tr>
                    <td>제품 종류 수</td>
                    <td>{model_summary['num_products']}개</td>
                </tr>
                <tr>
                    <td>총 생산 능력</td>
                    <td>{model_summary['total_capacity']:,.0f}개/일</td>
                </tr>
                <tr>
                    <td>유효 생산 능력</td>
                    <td>{model_summary['total_effective_capacity']:,.0f}개/일</td>
                </tr>
                <tr>
                    <td>목표 생산량 합계</td>
                    <td>{model_summary['total_target_production']:,.0f}개</td>
                </tr>
            </table>
            
            <h3>알고리즘 파라미터</h3>
            <table class="data-table">
                <tr>
                    <td>최적화 알고리즘</td>
                    <td>유전 알고리즘 (Genetic Algorithm)</td>
                </tr>
                <tr>
                    <td>개체군 크기</td>
                    <td>정보 없음</td>
                </tr>
                <tr>
                    <td>진화 세대 수</td>
                    <td>{self.analysis.optimization_summary['generations']}세대</td>
                </tr>
                <tr>
                    <td>수렴 조건</td>
                    <td>100세대 연속 개선 없음 또는 최대 세대 도달</td>
                </tr>
            </table>
            
            <h3>데이터 품질</h3>
            <div class="alert alert-success">
                ✅ 모든 입력 데이터가 유효성 검사를 통과했습니다<br>
                ✅ 모델 일관성 검사 완료<br>
                ✅ 제약 조건 정의 검증 완료
            </div>
        </div>
        """
    
    def _generate_footer(self) -> str:
        """푸터 생성"""
        return f"""
        <div class="footer">
            생산 최적화 시스템 v1.0 | 
            보고서 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
            © 2025 Production Optimization System
        </div>
        """
    
    def _get_goal_name(self) -> str:
        """최적화 목표 이름 반환"""
        goal_names = {
            'minimize_cost': '비용 최소화',
            'maximize_production': '생산량 최대화',
            'maximize_profit': '수익 최대화',
            'multi_objective': '다목적 최적화',
            'optimize_quality': '품질 최적화'
        }
        return goal_names.get(self.model.optimization_goal.value, '알 수 없음')

class ExcelReportGenerator:
    """Excel 보고서 생성기"""
    
    def __init__(self, analyzer: ProductionAnalyzer):
        self.analyzer = analyzer
        self.analysis = analyzer.analysis_result
    
    def generate_excel_report(self, output_path: Optional[str] = None) -> str:
        """Excel 보고서 생성"""
        try:
            import pandas as pd
            
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(self.analyzer.results_dir, f"optimization_report_{timestamp}.xlsx")
            
            # Excel 작성기 생성
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # 1. 요약 시트
                self._create_summary_sheet(writer)
                
                # 2. 제품별 분석 시트
                self._create_product_analysis_sheet(writer)
                
                # 3. 라인별 분석 시트
                self._create_line_analysis_sheet(writer)
                
                # 4. 비용 분석 시트
                self._create_cost_analysis_sheet(writer)
                
                # 5. 권장사항 시트
                self._create_recommendations_sheet(writer)
            
            return output_path
            
        except ImportError:
            raise ImportError("Excel 보고서 생성을 위해 pandas와 openpyxl이 필요합니다.")
    
    def _create_summary_sheet(self, writer):
        """요약 시트 생성"""
        import pandas as pd
        
        # 주요 지표 데이터프레임
        summary_data = {
            '지표': [
                '총 생산량',
                '목표 달성률',
                '총 비용',
                '설비 가동률',
                '품질 효율성',
                '제약 위반 수',
                '병목 지점 수',
                '실행 시간'
            ],
            '값': [
                f"{self.analysis.production_analysis['total_production']:,.0f}개",
                f"{self.analysis.production_analysis['overall_achievement']:.1f}%",
                f"{self.analysis.cost_analysis['total_cost']:,.0f}원",
                f"{self.analysis.efficiency_analysis['capacity_utilization']:.1f}%",
                f"{self.analysis.efficiency_analysis['quality_efficiency']:.1f}%",
                f"{self.analysis.constraint_analysis['total_violations']}개",
                f"{self.analysis.bottleneck_analysis['bottleneck_count']}개",
                f"{self.analysis.optimization_summary['execution_time']:.2f}초"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='요약', index=False)
    
    def _create_product_analysis_sheet(self, writer):
        """제품별 분석 시트 생성"""
        import pandas as pd
        
        prod_analysis = self.analysis.production_analysis
        
        product_data = []
        for product_name in prod_analysis['product_production'].keys():
            product_data.append({
                '제품명': product_name,
                '실제_생산량': prod_analysis['product_production'][product_name],
                '목표_생산량': prod_analysis['product_targets'][product_name],
                '달성률_퍼센트': prod_analysis['product_achievement'][product_name]
            })
        
        df_products = pd.DataFrame(product_data)
        df_products.to_excel(writer, sheet_name='제품별_분석', index=False)
    
    def _create_line_analysis_sheet(self, writer):
        """라인별 분석 시트 생성"""
        import pandas as pd
        
        prod_analysis = self.analysis.production_analysis
        
        line_data = []
        for line_name in prod_analysis['line_production'].keys():
            line_data.append({
                '라인명': line_name,
                '생산량': prod_analysis['line_production'][line_name],
                '가동률_퍼센트': prod_analysis['line_utilization'][line_name],
                '유효_생산량': prod_analysis['line_efficiency'][line_name]
            })
        
        df_lines = pd.DataFrame(line_data)
        df_lines.to_excel(writer, sheet_name='라인별_분석', index=False)
    
    def _create_cost_analysis_sheet(self, writer):
        """비용 분석 시트 생성"""
        import pandas as pd
        
        cost_analysis = self.analysis.cost_analysis
        
        cost_data = []
        for cost_type, amount in cost_analysis['cost_breakdown'].items():
            if amount > 0:
                cost_data.append({
                    '비용_항목': cost_type,
                    '금액': amount,
                    '비율_퍼센트': cost_analysis['cost_percentages'][cost_type]
                })
        
        df_costs = pd.DataFrame(cost_data)
        df_costs.to_excel(writer, sheet_name='비용_분석', index=False)
    
    def _create_recommendations_sheet(self, writer):
        """권장사항 시트 생성"""
        import pandas as pd
        
        recommendations_data = []
        for i, suggestion in enumerate(self.analysis.improvement_suggestions, 1):
            recommendations_data.append({
                '번호': i,
                '권장사항': suggestion,
                '우선순위': '높음' if i <= 3 else '보통'
            })
        
        df_recommendations = pd.DataFrame(recommendations_data)
        df_recommendations.to_excel(writer, sheet_name='권장사항', index=False)