"""
날씨 정보 처리를 위한 유틸리티 함수들
"""
from datetime import datetime, timedelta
from models import CAPITAL_LOCATION

# 현재 시간 기준 최신 발표시간 계산
def get_latest_base_time():
    """
    기상청 API 호출을 위한 최신 base_date와 base_time을 계산합니다.
    현재 시간 기준으로 가장 최근의 발표 시간을 반환합니다.
    
    Returns:
        tuple: (base_date, base_time) 형식의 튜플
    """
    now = datetime.now()
    # 현재 시간이 00:10 이전이면 전날 23시 데이터를 사용
    if now.hour == 0 and now.minute < 10:
        yesterday = now - timedelta(days=1)
        base_date = yesterday.strftime("%Y%m%d")
        base_time = "2300"
    else:
        if now.minute < 10:
            now = now - timedelta(hours=1)
        base_date = now.strftime("%Y%m%d")
        base_time = now.strftime("%H00")
    return base_date, base_time

# 지역명으로 좌표(nx, ny) 찾기
def find_location_by_name(city_name: str):
    """
    도시 이름으로 기상청 좌표(nx, ny)를 찾습니다.
    
    Args:
        city_name (str): 도시 이름 (한글 또는 영문)
        
    Returns:
        tuple: (nx, ny, 한글이름) 형식의 튜플
    """
    # 입력값 정규화
    city_name = city_name.strip()
    
    # 완전 일치 검색
    for location in CAPITAL_LOCATION:
        if (city_name.lower() == location["administrativeArea"].lower() or
            city_name == location["administrativeAreaKorean"] or
            city_name == location["koreanName"]):
            return location["capitalNX"], location["capitalNY"], location["koreanName"]
    
    # 부분 일치 검색 (더 유연한 검색)
    for location in CAPITAL_LOCATION:
        if (city_name.lower() in location["administrativeArea"].lower() or
            city_name in location["administrativeAreaKorean"] or
            city_name in location["koreanName"]):
            return location["capitalNX"], location["capitalNY"], location["koreanName"]
            
    # 별도의 예외 케이스 처리
    if "충남" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "충청남도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "충북" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "충청북도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "경남" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "경상남도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "경북" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "경상북도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "전남" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "전라남도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "전북" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "전라북도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    elif "강원" in city_name:
        for location in CAPITAL_LOCATION:
            if location["koreanName"] == "강원도":
                return location["capitalNX"], location["capitalNY"], location["koreanName"]
    
    # 찾지 못한 경우
    print(f"경고: '{city_name}' 지역을 찾을 수 없어 서울 정보를 반환합니다.")
    for location in CAPITAL_LOCATION:
        if location["koreanName"] == "서울":
            return location["capitalNX"], location["capitalNY"], "서울"