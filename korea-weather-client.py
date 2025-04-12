import requests
import json
import sys

def test_korea_weather_mcp(city="서울"):
    """
    한국 날씨 MCP 서버를 테스트하는 함수
    """
    # MCP 서버 URL (로컬에서 실행 중인 경우)
    base_url = "http://localhost:8000"
    
    # 스키마 가져오기
    schema_response = requests.get(f"{base_url}/schema.json")
    print("\n===== MCP 스키마 정보 =====")
    print(json.dumps(schema_response.json(), indent=2, ensure_ascii=False))
    print("\n" + "-"*50)
    
    # 날씨 정보 요청
    weather_payload = {
        "parameters": {
            "city": city
        }
    }
    
    try:
        weather_response = requests.post(
            f"{base_url}/v1/functions/get_current_weather", 
            json=weather_payload
        )
        weather_response.raise_for_status()
        
        weather_data = weather_response.json()
        
        print(f"\n===== {city}의 현재 날씨 정보 =====")
        print(json.dumps(weather_data, indent=2, ensure_ascii=False))
        
        # 날씨 정보 간단하게 출력
        if "result" in weather_data and "error" not in weather_data["result"]:
            result = weather_data["result"]
            print("\n===== 날씨 요약 =====")
            print(f"위치: {result['location']}")
            print(f"기준 날짜/시간: {result['base_date']} {result['base_time']}")
            
            weather = result["weather"]
            print(f"기온: {weather.get('temperature', '정보 없음')}°C")
            print(f"강수량: {weather.get('rainfall', '정보 없음')}mm")
            print(f"습도: {weather.get('humidity', '정보 없음')}%")
            
            if "precipitation_type" in weather:
                print(f"강수 형태: {weather['precipitation_type'].get('name', '정보 없음')}")
            
            print(f"풍속: {weather.get('wind_speed', '정보 없음')}m/s")
        
    except requests.exceptions.RequestException as e:
        print(f"API 요청 오류: {str(e)}")

if __name__ == "__main__":
    # 명령줄 인자로 도시 이름을 받음
    city = "서울"  # 기본값
    
    if len(sys.argv) > 1:
        city = sys.argv[1]
    
    test_korea_weather_mcp(city)
