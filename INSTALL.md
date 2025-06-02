# 🏗️ Setup and Installation Guide | 설치 및 설정 가이드

## 📋 Quick Installation | 빠른 설치

### Method 1: Using pip (Recommended) | pip 사용 (권장)
```bash
# Clone repository | 리포지토리 클론
git clone https://github.com/imjeasung/-production-optimization-system.git
cd -production-optimization-system

# Install dependencies | 의존성 설치
pip install -r requirements.txt

# Run the system | 시스템 실행
python main.py
```

### Method 2: Using conda | conda 사용
```bash
# Create conda environment | conda 환경 생성
conda create -n prod-opt python=3.8
conda activate prod-opt

# Install dependencies | 의존성 설치
pip install -r requirements.txt

# Run the system | 시스템 실행
python main.py
```

## 🎯 Quick Demo | 빠른 데모
```bash
# Run automated demo | 자동 데모 실행
cd examples
python optimization_demo.py

# Or load example scenario | 또는 예시 시나리오 로드
python ../main.py
# Select option 2, then load "examples/manufacturing_scenario.json"
```

## 🔧 System Requirements | 시스템 요구사항

- **Python**: 3.8 or higher | 3.8 이상
- **RAM**: 4GB minimum, 8GB recommended | 최소 4GB, 권장 8GB
- **Storage**: 500MB free space | 여유 공간 500MB
- **OS**: Windows, macOS, Linux | 윈도우, 맥OS, 리눅스

## 📊 Expected Performance | 예상 성능

- **Small problems** (2-3 lines, 3-4 products): < 30 seconds
- **소규모 문제** (2-3 라인, 3-4 제품): 30초 미만
- **Medium problems** (5-8 lines, 5-10 products): 1-5 minutes  
- **중규모 문제** (5-8 라인, 5-10 제품): 1-5분
- **Large problems** (10+ lines, 10+ products): 5-30 minutes
- **대규모 문제** (10+ 라인, 10+ 제품): 5-30분

## 🆘 Troubleshooting | 문제 해결

### Common Issues | 일반적인 문제

#### 1. ImportError: No module named 'matplotlib'
```bash
# Solution | 해결책
pip install matplotlib seaborn
```

#### 2. Permission Error on Windows | 윈도우 권한 오류
```bash
# Solution | 해결책
pip install --user -r requirements.txt
```

#### 3. Korean Font Issues | 한글 폰트 문제
The system automatically handles Korean fonts. If charts show boxes instead of Korean characters:
시스템이 자동으로 한글 폰트를 처리합니다. 차트에서 한글이 박스로 표시되면:

- **Windows**: Install "Malgun Gothic" font (usually pre-installed)
- **윈도우**: "맑은 고딕" 폰트 설치 (일반적으로 기본 설치)
- **macOS**: Install "Nanum Gothic" font
- **맥OS**: "나눔고딕" 폰트 설치
- **Linux**: Install Korean font packages
- **리눅스**: 한글 폰트 패키지 설치

#### 4. Memory Issues with Large Problems | 대규모 문제의 메모리 이슈
```python
# Reduce GA parameters in config.py | config.py에서 GA 파라미터 감소
DEFAULT_GA_PARAMS = {
    'population_size': 50,  # Reduce from 100
    'generations': 200,     # Reduce from 500
    # ...
}
```

## 📞 Support | 지원

- **GitHub Issues**: [Report bugs](https://github.com/imjeasung/-production-optimization-system/issues)
- **Email**: jeasunglim39@gmail.com
- **Documentation**: Check examples/ folder

---

🎉 **Ready to optimize your production!** | **생산 최적화를 시작할 준비가 되었습니다!**
