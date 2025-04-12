from fastmcp import FastMCP
import os
from dotenv import load_dotenv
import httpx
from datetime import datetime, timedelta

# 환경변수 로딩
load_dotenv(override=True)

# 기상청 API 관련 설정
KMA_API_KEY = os.environ.get("KMA_API_KEY", "")
KMA_API_URL = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0"

# 날씨 코드 설명 매핑
PTY_CODES = {
    "0": "없음",
    "1": "비",
    "2": "비/눈",
    "3": "눈",
    "5": "빗방울",
    "6": "빗방울눈날림",
    "7": "눈날림"
}

SKY_CODES = {
    "1": "맑음",
    "3": "구름많음",
    "4": "흐림"
}

# 지역 정보 데이터 (필요에 따라 추가)
CAPITAL_LOCATION = [
    {
        "administrativeArea": "Seoul",
        "administrativeAreaKorean": "서울특별시",
        "capitalNX": 60,
        "capitalNY": 127,
        "koreanName": "서울",
        "midAreaNumber": "11B00000",
    },
    {
        "administrativeArea": "Busan",
        "administrativeAreaKorean": "부산광역시",
        "capitalNX": 98,
        "capitalNY": 76,
        "koreanName": "부산",
        "midAreaNumber": "11H20000",
    },
    {
        "administrativeArea": "Daegu",
        "administrativeAreaKorean": "대구광역시",
        "capitalNX": 89,
        "capitalNY": 90,
        "koreanName": "대구",
        "midAreaNumber": "11H10000",
    },
    {
        "administrativeArea": "Incheon",
        "administrativeAreaKorean": "인천광역시",
        "capitalNX": 55,
        "capitalNY": 124,
        "koreanName": "인천",
        "midAreaNumber": "11B00000",
    },
    {
        "administrativeArea": "Gwangju",
        "administrativeAreaKorean": "광주광역시",
        "capitalNX": 58,
        "capitalNY": 74,
        "koreanName": "광주",
        "midAreaNumber": "11F20000",
    },
    {
        "administrativeArea": "Daejeon",
        "administrativeAreaKorean": "대전광역시",
        "capitalNX": 67,
        "capitalNY": 100,
        "koreanName": "대전",
        "midAreaNumber": "11C20000",
    },
    {
        "administrativeArea": "Ulsan",
        "administrativeAreaKorean": "울산광역시",
        "capitalNX": 102,
        "capitalNY": 84,
        "koreanName": "울산",
        "midAreaNumber": "11H20000",
    },
    {
        "administrativeArea": "Sejong-si",
        "administrativeAreaKorean": "세종특별자치시",
        "capitalNX": 66,
        "capitalNY": 103,
        "koreanName": "세종",
        "midAreaNumber": "11C20000",
    },
    {
        "administrativeArea": "Gyeonggi-do",
        "administrativeAreaKorean": "경기도",
        "capitalNX": 60,
        "capitalNY": 120,
        "koreanName": "경기도",
        "midAreaNumber": "11B00000",
    },
    {
        "administrativeArea": "Gangwon-do",
        "administrativeAreaKorean": "강원특별자치도",
        "capitalNX": 73,
        "capitalNY": 134,
        "koreanName": "강원도",
        "midAreaNumber": "11D10000",
    },
    {
        "administrativeArea": "Chungcheongbuk-do",
        "administrativeAreaKorean": "충청북도",
        "capitalNX": 69,
        "capitalNY": 107,
        "koreanName": "충청북도",
        "midAreaNumber": "11C10000",
    },
    {
        "administrativeArea": "Chungcheongnam-do",
        "administrativeAreaKorean": "충청남도",
        "capitalNX": 68,
        "capitalNY": 100,
        "koreanName": "충청남도",
        "midAreaNumber": "11C20000",
    },
    {
        "administrativeArea": "Jeollabuk-do",
        "administrativeAreaKorean": "전북특별자치도",
        "capitalNX": 63,
        "capitalNY": 89,
        "koreanName": "전라북도",
        "midAreaNumber": "11F10000",
    },
    {
        "administrativeArea": "Jeollanam-do",
        "administrativeAreaKorean": "전라남도",
        "capitalNX": 51,
        "capitalNY": 67,
        "koreanName": "전라남도",
        "midAreaNumber": "11F20000",
    },
    {
        "administrativeArea": "Gyeongsangbuk-do",
        "administrativeAreaKorean": "경상북도",
        "capitalNX": 89,
        "capitalNY": 91,
        "koreanName": "경상북도",
        "midAreaNumber": "11H10000",
    },
    {
        "administrativeArea": "Gyeongsangnam-do",
        "administrativeAreaKorean": "경상남도",
        "capitalNX": 91,
        "capitalNY": 77,
        "koreanName": "경상남도",
        "midAreaNumber": "11H20000",
    },
    {
        "administrativeArea": "Jeju-do",
        "administrativeAreaKorean": "제주특별자치도",
        "capitalNX": 52,
        "capitalNY": 38,
        "koreanName": "제주",
        "midAreaNumber": "11G00000",
    },
]

# 현재 시간 기준 최신 발표시간 계산
def get_latest_base_time():
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
    # 찾지 못하면 기본값으로 서울 반환
    return 60, 127, "서울"

# 비동기 방식으로 초단기실황 데이터 가져오기
async def get_ultra_srt_ncst(city: str) -> dict:
    nx, ny, found_name = find_location_by_name(city)
    base_date, base_time = get_latest_base_time()
    url = f"{KMA_API_URL}/getUltraSrtNcst"
    params = {
        "authKey": KMA_API_KEY,
        "dataType": "JSON",
        "numOfRows": 10,
        "pageNo": 1,
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if data["response"]["header"]["resultCode"] != "00":
                error_msg = data["response"]["header"]["resultMsg"]
                return {"error": f"기상청 API 오류: {error_msg}"}

            items = data["response"]["body"]["items"]["item"]
            weather_data = {
                "location": found_name,
                "base_date": base_date,
                "base_time": base_time,
                "weather": {}
            }
            for item in items:
                category = item["category"]
                value = item["obsrValue"]
                if category == "T1H":  # 기온
                    weather_data["weather"]["temperature"] = float(value)
                elif category == "RN1":  # 1시간 강수량
                    weather_data["weather"]["rainfall"] = float(value)
                elif category == "REH":  # 습도
                    weather_data["weather"]["humidity"] = float(value)
                elif category == "PTY":  # 강수형태
                    weather_data["weather"]["precipitation_type"] = {
                        "code": value,
                        "name": PTY_CODES.get(value, "알 수 없음")
                    }
                elif category == "VEC":  # 풍향
                    weather_data["weather"]["wind_direction"] = float(value)
                elif category == "WSD":  # 풍속
                    weather_data["weather"]["wind_speed"] = float(value)
            return weather_data

    except httpx.RequestError as e:
        return {"error": f"API 요청 오류: {str(e)}"}
    except Exception as e:
        return {"error": f"데이터 처리 오류: {str(e)}"}

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Korea Weather MCP")

# MCP 도구(tool) 정의: 특정 도시의 현재 날씨 정보를 가져옵니다.
@mcp.tool()
async def get_current_weather(city: str = "서울") -> dict:
    """
    특정 한국 지역의 현재 날씨 정보를 가져옵니다.
    예: get_current_weather("부산")
    """
    return await get_ultra_srt_ncst(city)

if __name__ == "__main__":
    # 개발 또는 배포 시 "fastmcp dev server.py" 혹은 "fastmcp install server.py" 명령으로 실행
    mcp.run()
