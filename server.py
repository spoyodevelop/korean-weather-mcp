"""
날씨 정보 제공을 위한 FastMCP 서버
"""
from fastmcp import FastMCP
from api import get_ultra_srt_ncst

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("Korea Weather MCP")

# MCP 도구(tool) 정의: 특정 도시의 현재 날씨 정보를 가져옵니다.
@mcp.tool()
async def get_current_weather(city: str = "서울") -> dict:
    """
    특정 한국 지역의 현재 날씨 정보를 가져옵니다.
    예: get_current_weather("부산")
    
    Args:
        city (str): 날씨를 조회할 도시 이름 (기본값: "서울")
        
    Returns:
        dict: 날씨 정보를 담은 딕셔너리
    """
    result = await get_ultra_srt_ncst(city)
    
    # 오류 발생 시 로그 기록
    if "error" in result:
        print(f"오류 발생 ({city}): {result['error']}")
    
    return result

if __name__ == "__main__":
    # 개발 또는 배포 시 "fastmcp dev server.py" 혹은 "fastmcp install server.py" 명령으로 실행
    mcp.run()