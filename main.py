"""
생산 최적화 시스템 메인 프로그램
전체 시스템의 실행 흐름을 관리합니다.
"""

import sys
import os
import time
from typing import Optional

from config import SUCCESS_MESSAGES, ERROR_MESSAGES, OptimizationGoal
from production_model import ProductionModel
from user_interface import DataInputHandler, FileIOHandler
from genetic_algorithm import GeneticAlgorithm, GAResult
from result_analyzer import ProductionAnalyzer, ProductionVisualizer
from report_generator import HTMLReportGenerator, ExcelReportGenerator

class ProductionOptimizer:
    """생산 최적화 시스템 메인 클래스"""
    
    def __init__(self):
        self.model: Optional[ProductionModel] = None
        self.input_handler = DataInputHandler()
        self.file_handler = FileIOHandler()= None
    
    def display_welcome_message(self):
        """환영 메시지 출력"""
        print("=" * 60)
        print("   생산 최적화 시스템 v1.0")
        print("   유전 알고리즘 기반 생산 계획 최적화")
        print("=" * 60)
        print()
    
    def display_main_menu(self):
        """메인 메뉴 출력"""
        print("\n=== 메인 메뉴 ===")
        print("1. 새로운 최적화 문제 설정")
        print("2. 파일에서 문제 로드")
        print("3. 현재 문제 정보 확인")
        print("4. 최적화 실행")
        print("5. 결과 분석")
        print("6. 🔥 빠른 인사이트 (NEW!)")
        print("7. 시각화 대시보드 생성")
        print("8. 상세 차트 생성")
        print("9. HTML 보고서 생성")
        print("10. Excel 보고서 생성")
        print("11. 모델 저장")
        print("12. 입력 템플릿 생성")
        print("13. 종료")
        print()
    
    def setup_new_problem(self):
        """새로운 최적화 문제 설정"""
        print("\n새로운 최적화 문제를 설정합니다.")
        
        try:
            # 1. 기본 설정
            settings = self.input_handler.get_basic_settings()
            
            # 2. ProductionModel 초기화
            self.model = ProductionModel()
            
            # 3. 생산 라인 정보 입력
            production_lines = self.input_handler.get_production_line_data(settings['line_count'])
            for line in production_lines:
                self.model.add_production_line(line)
            
            # 4. 제품 정보 입력
            products = self.input_handler.get_product_data(settings['product_count'], production_lines)
            for product in products:
                self.model.add_product(product)
            
            # 5. 최적화 목표 설정
            weights = settings.get('weights', {})
            self.model.set_optimization_goal(settings['optimization_goal'], weights)
            
            # 6. 모델 유효성 검사
            is_valid, errors = self.model.validate_model()
            if not is_valid:
                print("\n모델 유효성 검사 실패:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print(f"\n{SUCCESS_MESSAGES['data_loaded']}")
            self._display_model_summary()
            
            return True
        
        except Exception as e:
            print(f"{ERROR_MESSAGES['data_format_error'].format(details=str(e))}")
            return False
    
    def load_problem_from_file(self):
        """파일에서 문제 로드"""
        filename = input("로드할 파일명을 입력하세요: ").strip()
        
        if not os.path.exists(filename):
            print(ERROR_MESSAGES['file_not_found'].format(filename=filename))
            return False
        
        model = self.file_handler.load_model_from_json(filename)
        if model is None:
            print("파일 로드에 실패했습니다.")
            return False
        
        self.model = model
        print(f"{SUCCESS_MESSAGES['data_loaded']}")
        self._display_model_summary()
        return True
    
    def display_problem_info(self):
        """현재 문제 정보 출력"""
        if self.model is None:
            print("설정된 문제가 없습니다. 먼저 문제를 설정하거나 로드해주세요.")
            return
        
        self._display_model_summary()
    
    def run_optimization(self):
        """최적화 실행"""
        if self.model is None:
            print("설정된 문제가 없습니다. 먼저 문제를 설정하거나 로드해주세요.")
            return
        
        print("\n최적화를 실행합니다...")
        
        # GA 파라미터 설정
        print("\nGA 파라미터를 설정하시겠습니까? (y/n):")
        if input().strip().lower() == 'y':
            ga_params = self.input_handler.get_ga_parameters()
        else:
            ga_params = None
        
        # 유전 알고리즘 초기화 및 실행
        self.ga = GeneticAlgorithm(self.model, ga_params)
        
        print("\n최적화 실행 중...")
        print("(진행률은 콘솔에서 확인하세요)")
        
        start_time = time.time()
        result = self.ga.run()
        end_time = time.time()
        
        self.last_result = result
        
        if result.success:
            print(f"\n{SUCCESS_MESSAGES['optimization_complete']}")
            print(f"실행 시간: {result.execution_time:.2f}초")
            print(f"수렴 세대: {result.convergence_generation}")
            print(f"최종 적합도: {result.best_fitness:.2f}")
            
            self._display_optimization_result(result)
            
            # 분석기 초기화
            self._initialize_analyzer()
        else:
            print(f"\n{ERROR_MESSAGES['optimization_failed'].format(error=result.error_message)}")
    
    def analyze_results(self):
        """결과 분석 - 구체적인 인사이트 제공"""
        if not self._check_analysis_ready():
            return
        
        try:
            print("\n종합적인 결과 분석을 수행합니다...")
            
            # 기존 분석 실행
            analysis_result = self.analyzer.analyze_all()
            
            # 🎆 새로운 구체적인 분석 추가
            detailed_analysis = self.last_result.detailed_analysis if self.last_result else {}
            
            print(f"\n📊 === 종합 결과 분석 ===")
            
            # 📋 구체적인 생산 계획 표시
            if detailed_analysis:
                self._display_detailed_production_plan(detailed_analysis)
                self._display_resource_efficiency_analysis(detailed_analysis)
                self._display_profitability_insights(detailed_analysis)
            
            # 기존 분석 결과도 표시
            print(f"\n📈 === 기본 통계 ===")
            print(f"   • 총 비용: {analysis_result.cost_analysis['total_cost']:,.0f}원")
            print(f"   • 총 생산량: {analysis_result.production_analysis['total_production']:,.0f}개")
            print(f"   • 목표 달성률: {analysis_result.production_analysis['overall_achievement']:.1f}%")
            print(f"   • 전체 가동률: {analysis_result.efficiency_analysis['capacity_utilization']:.1f}%")
            
            # 제약 조건 비중 요약 체크
            print(f"\n⚠️ === 제약 조건 검사 ===")
            if analysis_result.constraint_analysis['is_feasible']:
                print("   ✅ 모든 제약 조건을 만족합니다.")
            else:
                print("   ❌ 제약 조건 위반:")
                for violation in analysis_result.constraint_analysis['violation_details']:
                    print(f"     - {violation}")
            
            # 분석 결과 저장
            report_file = self.analyzer.save_analysis_report()
            print(f"\n📁 상세 분석 결과가 저장되었습니다: {report_file}")
            
        except Exception as e:
            print(f"결과 분석 중 오류가 발생했습니다: {e}")
    
    def _display_resource_efficiency_analysis(self, detailed_analysis: dict[str, any]):
        """자원 효율성 분석 표시"""
        resource_analysis = detailed_analysis.get('resource_utilization', {})
        if not resource_analysis:
            return
            
        print(f"\n⚡ === 자원 효율성 분석 ===")
        
        efficiency_scores = resource_analysis.get('efficiency_scores', {})
        if efficiency_scores:
            print(f"\n🏆 라인별 효율성:")
            for line_name, metrics in efficiency_scores.items():
                status = metrics.get('status', '보통')
                utilization = metrics.get('utilization_rate', 0)
                efficiency = metrics.get('efficiency_score', 0)
                revenue_per_hour = metrics.get('revenue_per_hour', 0)
                
                status_emoji = {
                    '효율적': '🎉',
                    '양호': '😊', 
                    '보통': '😐',
                    '개선필요': '😰'
                }.get(status, '😐')
                
                print(f"   {status_emoji} {line_name} ({status}):")
                print(f"      - 가동률: {utilization:.1f}%")
                print(f"      - 효율성: {efficiency:.1f}%")
                print(f"      - 시간당 수익: {revenue_per_hour:,.0f}원")
        
        # 추천사항
        recommendations = resource_analysis.get('recommendations', [])
        if recommendations:
            print(f"\n💡 자원 최적화 추천사항:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"   {i}. {rec}")
    
    def _display_profitability_insights(self, detailed_analysis: dict[str, any]):
        """수익성 인사이트 표시"""
        profitability = detailed_analysis.get('profitability_analysis', {})
        if not profitability:
            return
            
        print(f"\n💰 === 수익성 분석 ===")
        
        # 제품별 수익성 랭킹
        product_profitability = profitability.get('product_profitability', {})
        if product_profitability:
            print(f"\n🏆 제품별 수익성 랭킹:")
            
            # 랭킹순으로 정렬
            sorted_products = sorted(product_profitability.items(), 
                                   key=lambda x: x[1].get('ranking', 999))
            
            for product_name, metrics in sorted_products[:5]:  # 상위 5개만
                ranking = metrics.get('ranking', 0)
                total_profit = metrics.get('total_profit', 0)
                profit_margin = metrics.get('profit_margin', 0)
                total_production = metrics.get('total_production', 0)
                
                medal = ['🥇', '🥈', '🥉'][ranking-1] if ranking <= 3 else f'{ranking}위'
                print(f"   {medal} {product_name}:")
                print(f"      - 총 수익: {total_profit:,.0f}원")
                print(f"      - 수익률: {profit_margin:.1f}%")
                print(f"      - 생산량: {total_production:.0f}개")
        
        # 최적화 인사이트
        insights = profitability.get('optimization_insights', [])
        if insights:
            print(f"\n🎯 전략적 인사이트:")
            for i, insight in enumerate(insights, 1):
                print(f"   {i}. {insight}")
    
    def display_quick_insights_menu(self):
        """빠른 인사이트 메뉴 추가"""
        if not self._check_analysis_ready():
            return
            
        detailed_analysis = self.last_result.detailed_analysis if self.last_result else {}
        if not detailed_analysis:
            print("구체적인 분석 데이터가 없습니다.")
            return
            
        print(f"\n🔥 === 빠른 인사이트 ===")
        
        while True:
            print(f"\n1. 라인별 생산 스케줄 보기")
            print(f"2. 수익성 분석 자세히 보기")
            print(f"3. 자원 효율성 자세히 보기")
            print(f"4. 경영진 요약 보기")
            print(f"5. 메인 메뉴로 돌아가기")
            
            choice = input("\n선택하세요 (1-5): ").strip()
            
            if choice == '1':
                self._display_production_schedule(detailed_analysis)
            elif choice == '2':
                self._display_profitability_insights(detailed_analysis)
            elif choice == '3':
                self._display_resource_efficiency_analysis(detailed_analysis)
            elif choice == '4':
                self._display_executive_summary(detailed_analysis)
            elif choice == '5':
                break
            else:
                print("올바른 메뉴 번호를 선택해주세요.")
    
    def _display_production_schedule(self, detailed_analysis: dict[str, any]):
        """생산 스케줄 상세 표시"""
        schedule = detailed_analysis.get('production_schedule', {})
        if not schedule:
            print("생산 스케줄 데이터가 없습니다.")
            return
            
        print(f"\n🗓️ === 라인별 생산 스케줄 ===")
        
        daily_schedule = schedule.get('daily_schedule', {})
        for line_name, line_schedule in daily_schedule.items():
            print(f"\n🏪 {line_name}:")
            print(f"   최대 가동시간: {line_schedule.get('max_hours', 0)}시간")
            print(f"   실제 가동시간: {line_schedule.get('total_scheduled_hours', 0)}시간")
            print(f"   유휴시간: {line_schedule.get('idle_time', 0)}시간")
            
            products_sequence = line_schedule.get('products_sequence', [])
            if products_sequence:
                print(f"   \n   📅 생산 순서 (수익성 높은 순):")
                for seq in products_sequence:
                    start = seq.get('start_hour', 0)
                    end = seq.get('end_hour', 0)
                    product = seq.get('product_name', '')
                    amount = seq.get('production_amount', 0)
                    profit = seq.get('unit_profit', 0)
                    print(f"     {start:.1f}-{end:.1f}시: {product} {amount:.0f}개 (단가수익 {profit:,.0f}원)")
        
        # 병목 지점
        bottlenecks = schedule.get('bottlenecks', [])
        if bottlenecks:
            print(f"\n⚠️ 병목 지점:")
            for bottleneck in bottlenecks:
                line_name = bottleneck.get('line_name', '')
                utilization = bottleneck.get('utilization', 0)
                issue = bottleneck.get('issue', '')
                print(f"   • {line_name}: {utilization:.1f}% - {issue}")

    def create_dashboard(self):
        """시각화 대시보드 생성"""
        if not self._check_analysis_ready():
            return
            
        try:
            print("\n시각화 대시보드를 생성합니다...")
            
            # 분석이 안 되어 있으면 실행
            if not self.analyzer.analysis_result:
                self.analyzer.analyze_all()
            
            # 대시보드 생성
            dashboard_file = self.visualizer.create_production_dashboard()
            print(f"대시보드가 생성되었습니다: {dashboard_file}")
            
            # 운영체제에 따른 파일 열기 안내
            print("\n💡 생성된 대시보드를 확인하려면:")
            print(f"   파일 탐색기에서 {dashboard_file}를 열어보세요.")
            
        except Exception as e:
            print(f"대시보드 생성 중 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()
    
    def create_detailed_charts(self):
        """상세 차트 생성"""
        if not self._check_analysis_ready():
            return
            
        try:
            print("\n상세 차트를 생성합니다...")
            
            # 분석이 안 되어 있으면 실행
            if not self.analyzer.analysis_result:
                self.analyzer.analyze_all()
            
            # 상세 차트 생성
            chart_files = self.visualizer.create_detailed_charts()
            
            print("상세 차트가 생성되었습니다:")
            for chart_file in chart_files:
                print(f"   - {chart_file}")
            
        except Exception as e:
            print(f"상세 차트 생성 중 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_html_report(self):
        """HTML 보고서 생성"""
        if not self._check_analysis_ready():
            return
            
        try:
            print("\nHTML 보고서를 생성합니다...")
            
            # 분석이 안 되어 있으면 실행
            if not self.analyzer.analysis_result:
                self.analyzer.analyze_all()
            
            # HTML 보고서 생성
            html_generator = HTMLReportGenerator(self.analyzer)
            report_file = html_generator.generate_full_report()
            
            print(f"HTML 보고서가 생성되었습니다: {report_file}")
            print("\n💡 보고서를 확인하려면:")
            print(f"   웹 브라우저에서 {report_file}를 열어보세요.")
            
        except Exception as e:
            print(f"HTML 보고서 생성 중 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()
    
    def generate_excel_report(self):
        """Excel 보고서 생성"""
        if not self._check_analysis_ready():
            return
            
        try:
            print("\nExcel 보고서를 생성합니다...")
            
            # 분석이 안 되어 있으면 실행
            if not self.analyzer.analysis_result:
                self.analyzer.analyze_all()
            
            # Excel 보고서 생성
            excel_generator = ExcelReportGenerator(self.analyzer)
            report_file = excel_generator.generate_excel_report()
            
            print(f"Excel 보고서가 생성되었습니다: {report_file}")
            print("\n💡 보고서를 확인하려면:")
            print(f"   Microsoft Excel에서 {report_file}를 열어보세요.")
            
        except ImportError:
            print("Excel 보고서 생성을 위해 pandas와 openpyxl 라이브러리가 필요합니다.")
            print("설치 명령: pip install pandas openpyxl")
        except Exception as e:
            print(f"Excel 보고서 생성 중 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()
    
    def _check_analysis_ready(self) -> bool:
        """분석 준비 상태 확인"""
        if self.model is None:
            print("설정된 모델이 없습니다. 먼저 문제를 설정하거나 로드해주세요.")
            return False
            
        if self.last_result is None or not self.last_result.success:
            print("분석할 최적화 결과가 없습니다. 먼저 최적화를 실행해주세요.")
            return False
        
        # 분석기가 없으면 초기화
        if self.analyzer is None:
            self._initialize_analyzer()
            
        return True
    
    def _initialize_analyzer(self):
        """분석기 초기화"""
        if self.model and self.last_result and self.last_result.success:
            self.analyzer = ProductionAnalyzer(self.model, self.last_result)
            self.visualizer = ProductionVisualizer(self.analyzer)
    
    def save_model(self):
        """모델 저장"""
        if self.model is None:
            print("저장할 모델이 없습니다.")
            return
        
        filename = input("저장할 파일명을 입력하세요 (예: my_model.json): ").strip()
        if not filename:
            print("파일명을 입력해주세요.")
            return
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        if self.file_handler.save_model_to_json(self.model, filename):
            print(SUCCESS_MESSAGES['results_saved'].format(filename=filename))
        else:
            print("모델 저장에 실패했습니다.")
    
    def create_template(self):
        """입력 템플릿 생성"""
        filename = self.file_handler.create_input_template()
        if filename:
            print(f"입력 템플릿이 생성되었습니다: {filename}")
            print("이 파일을 수정하여 데이터를 입력하고 '파일에서 문제 로드' 메뉴를 사용하세요.")
        else:
            print("템플릿 생성에 실패했습니다.")
    
    def _display_model_summary(self):
        """모델 요약 정보 출력"""
        if self.model is None:
            return
        
        summary = self.model.get_model_summary()
        
        print(f"\n=== 모델 요약 ===")
        print(f"생산 라인 수: {summary['num_production_lines']}개")
        print(f"제품 종류 수: {summary['num_products']}개")
        print(f"최적화 목표: {summary['optimization_goal']}")
        print(f"총 생산 능력: {summary['total_capacity']:,.0f}개/일")
        print(f"유효 생산 능력: {summary['total_effective_capacity']:,.0f}개/일")
        print(f"목표 생산량: {summary['total_target_production']:,.0f}개")
        
        # 호환성 매트릭스 출력
        print(f"\n라인-제품 호환성:")
        compatibility_matrix = summary['compatibility_matrix']
        print(compatibility_matrix.to_string())
    
    def _display_optimization_result(self, result: GAResult):
        """최적화 결과 상세 출력 - 구체적인 생산 계획 포함"""
        if not result.success:
            return
        
        solution = result.best_solution
        components = solution.fitness_components
        
        print(f"\n=== 최적화 결과 요약 ===")
        print(f"총 비용: {components['total_cost']:,.0f}원")
        print(f"총 수익: {components['revenue']:,.0f}원")
        print(f"순이익: {components['total_profit']:,.0f}원")
        print(f"총 생산량: {components['production_volume']:,.0f}개")
        print(f"제약 조건 위반: {components['constraint_violations']}개")
        print(f"실행 가능성: {'예' if components['is_feasible'] else '아니오'}")
        
        # 🎯 새로운 구체적인 분석 결과 표시
        if result.detailed_analysis:
            self._display_detailed_production_plan(result.detailed_analysis)
            self._display_executive_summary(result.detailed_analysis)
    
    def _display_detailed_production_plan(self, detailed_analysis: dict[str, any]):
        """구체적인 생산 계획 표시 - 어디서 무엇을 얼마나"""
        if not detailed_analysis:
            return
            
        print(f"\n🏭 === 구체적인 생산 계획 ===")
        
        # 1. 라인별 상세 계획
        production_plan = detailed_analysis.get('detailed_production_plan', {})
        line_by_line = production_plan.get('line_by_line', {})
        
        if line_by_line:
            print(f"\n📋 라인별 생산 계획:")
            for line_name, line_plan in line_by_line.items():
                print(f"\n  🏪 {line_name}:")
                print(f"     • 가동시간: {line_plan.get('total_working_time', 0):.1f}시간")
                print(f"     • 가동률: {line_plan.get('utilization_rate', 0):.1f}%")
                print(f"     • 총 생산량: {line_plan.get('total_production', 0):.0f}개")
                print(f"     • 예상 수익: {line_plan.get('total_revenue', 0):,.0f}원")
                
                products = line_plan.get('products', {})
                if products:
                    print(f"     📦 생산 제품:")
                    for product_name, product_info in products.items():
                        amount = product_info.get('production_amount', 0)
                        time_hours = product_info.get('total_time_hours', 0)
                        profit = product_info.get('profit', 0)
                        print(f"       - {product_name}: {amount:.0f}개 ({time_hours:.1f}시간, 수익 {profit:,.0f}원)")
        
        # 2. 제품별 달성률
        product_by_product = production_plan.get('product_by_product', {})
        if product_by_product:
            print(f"\n📊 제품별 목표 달성률:")
            for product_name, product_plan in product_by_product.items():
                total_production = product_plan.get('total_production', 0)
                achievement_rate = product_plan.get('achievement_rate', 0)
                best_line = product_plan.get('best_line', 'N/A')
                
                status = "✅" if achievement_rate >= 100 else "📈" if achievement_rate >= 80 else "⚠️"
                print(f"    {status} {product_name}: {total_production:.0f}개 (달성률 {achievement_rate:.1f}%)")
                if best_line != 'N/A':
                    print(f"        최고 생산 라인: {best_line}")
    
    def _display_executive_summary(self, detailed_analysis: dict[str, any]):
        """경영진용 요약 정보 표시"""
        executive_summary = detailed_analysis.get('executive_summary', {})
        if not executive_summary:
            return
            
        print(f"\n💼 === 경영진 요약 ===")
        
        # 핵심 지표
        key_metrics = executive_summary.get('key_metrics', {})
        if key_metrics:
            print(f"\n📈 핵심 성과 지표:")
            for metric, value in key_metrics.items():
                print(f"   • {metric}: {value}")
        
        # 최우선 과제
        top_priorities = executive_summary.get('top_priorities', [])
        if top_priorities:
            print(f"\n🎯 최우선 과제:")
            for i, priority in enumerate(top_priorities[:3], 1):
                print(f"   {i}. {priority}")
        
        # 빠른 개선 방안
        quick_wins = executive_summary.get('quick_wins', [])
        if quick_wins:
            print(f"\n⚡ 빠른 개선 방안:")
            for i, win in enumerate(quick_wins[:3], 1):
                print(f"   {i}. {win}")
        
        # 추천사항
        recommendations = detailed_analysis.get('recommendations', [])
        if recommendations:
            print(f"\n💡 주요 추천사항:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"   {i}. {rec}")
    
    def run(self):
        """메인 실행 루프"""
        self.display_welcome_message()
        
        while True:
            self.display_main_menu()
            
            try:
                choice = input("메뉴를 선택하세요 (1-13): ").strip()
                
                if choice == '1':
                    self.setup_new_problem()
                
                elif choice == '2':
                    self.load_problem_from_file()
                
                elif choice == '3':
                    self.display_problem_info()
                
                elif choice == '4':
                    self.run_optimization()
                
                elif choice == '5':
                    self.analyze_results()
                
                elif choice == '6':  # 🔥 새로운 빠른 인사이트 메뉴!
                    self.display_quick_insights_menu()
                
                elif choice == '7':
                    self.create_dashboard()
                
                elif choice == '8':
                    self.create_detailed_charts()
                
                elif choice == '9':
                    self.generate_html_report()
                
                elif choice == '10':
                    self.generate_excel_report()
                
                elif choice == '11':
                    self.save_model()
                
                elif choice == '12':
                    self.create_template()
                
                elif choice == '13':
                    print("\n프로그램을 종료합니다.")
                    break
                
                else:
                    print("올바른 메뉴 번호를 선택해주세요.")
            
            except KeyboardInterrupt:
                print("\n\n프로그램이 중단되었습니다.")
                break
            
            except Exception as e:
                print(f"\n오류가 발생했습니다: {e}")
                print("계속 진행하려면 Enter를 누르세요...")
                input()

def main():
    """메인 함수"""
    try:
        optimizer = ProductionOptimizer()
        optimizer.run()
    
    except Exception as e:
        print(f"치명적 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())