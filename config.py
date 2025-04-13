import os
from dotenv import load_dotenv

# 환경변수 로딩
load_dotenv(override=True)

# 기상청 API 관련 설정
KMA_API_KEY = os.environ.get("KMA_API_KEY", "")
if not KMA_API_KEY:
    print("경고: KMA_API_KEY가 설정되지 않았습니다. 환경 변수를 확인하세요.")

KMA_API_URL = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0"