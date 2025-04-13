"""
기상청 API를 호출하고 날씨 데이터를 처리하는 모듈
"""
import traceback
import httpx
from config import KMA_API_KEY, KMA_API_URL
from utils import get_latest_base_time, find_location_by_name
from models import PTY_CODES

# 비동기 방식으로 초단기실황 데이터 가져오기
async def get_ultra_srt_ncst(city: str) -> dict:
    """
    기상청 API를 통해 초단기실황 데이터를 가져옵니다.
    
    Args:
        city (str): 도시 이름
        
    Returns:
        dict: 날씨 정보를 담은 딕셔너리
    """
    nx, ny, found_name = find_location_by_name(city)
    base_date, base_time = get_latest_base_time()
    
    # API 키 확인
    if not KMA_API_KEY:
        return {"error": "API 키가 설정되지 않았습니다. 환경 변수를 확인하세요."}
    
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
        async with httpx.AsyncClient(timeout=15) as client:  # 타임아웃 증가
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "response" not in data:
                return {"error": "기상청 API 응답 형식이 올바르지 않습니다.", "raw_response": str(data)[:300]}
            
            if data["response"]["header"]["resultCode"] != "00":
                error_msg = data["response"]["header"]["resultMsg"]
                return {"error": f"기상청 API 오류: {error_msg}"}

            if "items" not in data["response"]["body"] or "item" not in data["response"]["body"]["items"]:
                return {"error": "기상청 API에서 날씨 데이터를 찾을 수 없습니다.", "raw_response": str(data)[:300]}

            return parse_weather_data(data, found_name, base_date, base_time)

    except httpx.RequestError as e:
        return {"error": f"API 요청 오류: {str(e)}"}
    except Exception as e:
        error_trace = traceback.format_exc()
        return {"error": f"데이터 처리 오류: {str(e)}", "trace": error_trace[:500]}

def parse_weather_data(data: dict, location: str, base_date: str, base_time: str) -> dict:
    """
    기상청 API 응답을 파싱하여 날씨 정보 딕셔너리를 반환합니다.
    
    Args:
        data (dict): API 응답 데이터
        location (str): 위치 이름
        base_date (str): 기준 날짜
        base_time (str): 기준 시간
        
    Returns:
        dict: 날씨 정보를 담은 딕셔너리
    """
    items = data["response"]["body"]["items"]["item"]
    weather_data = {
        "location": location,
        "base_date": base_date,
        "base_time": base_time,
        "weather": {}
    }
    
    # 기본값 설정
    weather_data["weather"]["temperature"] = None
    weather_data["weather"]["rainfall"] = 0.0
    weather_data["weather"]["humidity"] = None
    weather_data["weather"]["precipitation_type"] = {"code": "0", "name": "없음"}
    weather_data["weather"]["wind_direction"] = None
    weather_data["weather"]["wind_speed"] = None
    
    for item in items:
        category = item["category"]
        value = item["obsrValue"]
        
        try:
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
        except (ValueError, TypeError) as e:
            print(f"데이터 변환 오류 ({category}): {e}")
    
    # 데이터 검증
    if weather_data["weather"]["temperature"] is None:
        print(f"경고: {location}의 기온 데이터가 없습니다.")
    
    return weather_data