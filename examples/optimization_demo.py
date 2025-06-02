#!/usr/bin/env python3
"""
생산 최적화 시스템 데모 스크립트
Production Optimization System Demo Script

이 스크립트는 시스템의 주요 기능을 자동으로 실행하여 보여줍니다.
This script automatically demonstrates the key features of the system.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import OptimizationGoal
from production_model import ProductionModel, ProductionLine, Product
from genetic_algorithm import GeneticAlgorithm
from result_analyzer import ProductionAnalyzer, ProductionVisualizer
from report_generator import HTMLReportGenerator

def create_demo_scenario():
    """데모용 시나리오 생성 | Create demo scenario"""
    print("🏭 Creating demo manufacturing scenario...")
    print("🏭 데모 제조업 시나리오 생성 중...")
    
    # Initialize model
    model = ProductionModel()
    
    # Add production lines
    lines = [
        ProductionLine(
            line_id="DEMO_LINE_1",
            line_name="High-Tech Assembly Line",
            production_capacity=100.0,
            operating_cost=50000.0,
            max_working_hours=16.0,
            defect_rate=0.03,
            investment_cost=10000000.0,
            maintenance_cost=200000.0,
            compatible_products=["PRODUCT_A", "PRODUCT_B"]
        ),
        ProductionLine(
            line_id="DEMO_LINE_2", 
            line_name="Standard Assembly Line",
            production_capacity=80.0,
            operating_cost=35000.0,
            max_working_hours=20.0,
            defect_rate=0.05,
            investment_cost=5000000.0,
            maintenance_cost=150000.0,
            compatible_products=["PRODUCT_B", "PRODUCT_C"]
        )
    ]
    
    for line in lines:
        model.add_production_line(line)
    
    # Add products
    products = [
        Product(
            product_id="PRODUCT_A",
            product_name="Premium Widget",
            material_cost=1000.0,
            selling_price=3000.0,
            target_production=500.0,
            min_demand=400.0,
            production_times={"DEMO_LINE_1": 30.0, "DEMO_LINE_2": 0.0},
            setup_times={"DEMO_LINE_1": 60.0, "DEMO_LINE_2": 0.0},
            setup_costs={"DEMO_LINE_1": 50000.0, "DEMO_LINE_2": 0.0}
        ),
        Product(
            product_id="PRODUCT_B",
            product_name="Standard Widget", 
            material_cost=500.0,
            selling_price=1500.0,
            target_production=800.0,
            min_demand=600.0,
            production_times={"DEMO_LINE_1": 20.0, "DEMO_LINE_2": 25.0},
            setup_times={"DEMO_LINE_1": 45.0, "DEMO_LINE_2": 60.0},
            setup_costs={"DEMO_LINE_1": 30000.0, "DEMO_LINE_2": 40000.0}
        ),
        Product(
            product_id="PRODUCT_C",
            product_name="Economy Widget",
            material_cost=200.0,
            selling_price=600.0,
            target_production=1200.0,
            min_demand=1000.0,
            production_times={"DEMO_LINE_1": 0.0, "DEMO_LINE_2": 15.0},
            setup_times={"DEMO_LINE_1": 0.0, "DEMO_LINE_2": 30.0},
            setup_costs={"DEMO_LINE_1": 0.0, "DEMO_LINE_2": 20000.0}
        )
    ]
    
    for product in products:
        model.add_product(product)
    
    # Set optimization goal
    model.set_optimization_goal(OptimizationGoal.MAXIMIZE_PROFIT)
    
    return model

def run_optimization_demo(model):
    """최적화 실행 데모 | Run optimization demo"""
    print("\n🧬 Running genetic algorithm optimization...")
    print("🧬 유전 알고리즘 최적화 실행 중...")
    
    # Configure GA parameters for demo (smaller for faster execution)
    ga_params = {
        'population_size': 50,
        'generations': 100,
        'crossover_rate': 0.8,
        'mutation_rate': 0.05,
        'elite_ratio': 0.1
    }
    
    # Initialize and run GA
    ga = GeneticAlgorithm(model, ga_params)
    result = ga.run()
    
    if result.success:
        print(f"\n✅ Optimization completed successfully!")
        print(f"✅ 최적화가 성공적으로 완료되었습니다!")
        print(f"   • Execution time: {result.execution_time:.2f} seconds")
        print(f"   • 실행 시간: {result.execution_time:.2f}초")
        print(f"   • Generations: {result.generation_count}")
        print(f"   • 세대 수: {result.generation_count}")
        print(f"   • Final fitness: {result.best_fitness:.2f}")
        print(f"   • 최종 적합도: {result.best_fitness:.2f}")
        
        return result
    else:
        print(f"❌ Optimization failed: {result.error_message}")
        print(f"❌ 최적화 실패: {result.error_message}")
        return None

def analyze_results_demo(model, result):
    """결과 분석 데모 | Results analysis demo"""
    print("\n📊 Analyzing optimization results...")
    print("📊 최적화 결과 분석 중...")
    
    # Initialize analyzer
    analyzer = ProductionAnalyzer(model, result)
    analysis_result = analyzer.analyze_all()
    
    # Display key insights
    print(f"\n🎯 Key Results | 주요 결과:")
    print(f"   • Total Cost: {analysis_result.cost_analysis['total_cost']:,.0f} KRW")
    print(f"   • 총 비용: {analysis_result.cost_analysis['total_cost']:,.0f}원")
    print(f"   • Total Production: {analysis_result.production_analysis['total_production']:,.0f} units")
    print(f"   • 총 생산량: {analysis_result.production_analysis['total_production']:,.0f}개")
    print(f"   • Achievement Rate: {analysis_result.production_analysis['overall_achievement']:.1f}%")
    print(f"   • 목표 달성률: {analysis_result.production_analysis['overall_achievement']:.1f}%")
    print(f"   • Capacity Utilization: {analysis_result.efficiency_analysis['capacity_utilization']:.1f}%")
    print(f"   • 설비 가동률: {analysis_result.efficiency_analysis['capacity_utilization']:.1f}%")
    
    # Create visualizations
    visualizer = ProductionVisualizer(analyzer)
    
    try:
        print(f"\n📈 Creating visualizations...")
        print(f"📈 시각화 생성 중...")
        
        dashboard_file = visualizer.create_production_dashboard()
        print(f"   • Dashboard created: {dashboard_file}")
        print(f"   • 대시보드 생성: {dashboard_file}")
        
        chart_files = visualizer.create_detailed_charts()
        print(f"   • Charts created: {len(chart_files)} files")
        print(f"   • 차트 생성: {len(chart_files)}개 파일")
        
    except Exception as e:
        print(f"   ⚠️ Visualization creation failed: {e}")
        print(f"   ⚠️ 시각화 생성 실패: {e}")
    
    # Generate HTML report
    try:
        print(f"\n📋 Generating HTML report...")
        print(f"📋 HTML 보고서 생성 중...")
        
        html_generator = HTMLReportGenerator(analyzer)
        report_file = html_generator.generate_full_report()
        print(f"   • Report created: {report_file}")
        print(f"   • 보고서 생성: {report_file}")
        
    except Exception as e:
        print(f"   ⚠️ Report generation failed: {e}")
        print(f"   ⚠️ 보고서 생성 실패: {e}")
    
    return analyzer

def main():
    """메인 데모 함수 | Main demo function"""
    print("=" * 60)
    print("🚀 PRODUCTION OPTIMIZATION SYSTEM DEMO")
    print("🚀 생산 최적화 시스템 데모")
    print("=" * 60)
    
    try:
        # Step 1: Create scenario
        model = create_demo_scenario()
        
        # Step 2: Run optimization
        result = run_optimization_demo(model)
        
        if result and result.success:
            # Step 3: Analyze results
            analyzer = analyze_results_demo(model, result)
            
            print("\n🎉 Demo completed successfully!")
            print("🎉 데모가 성공적으로 완료되었습니다!")
            print("\nCheck the 'analysis_results' folder for generated files.")
            print("생성된 파일들을 확인하려면 'analysis_results' 폴더를 확인하세요.")
            
        else:
            print("\n❌ Demo failed during optimization.")
            print("❌ 최적화 중 데모가 실패했습니다.")
            
    except Exception as e:
        print(f"\n💥 Demo failed with error: {e}")
        print(f"💥 오류로 인해 데모가 실패했습니다: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
