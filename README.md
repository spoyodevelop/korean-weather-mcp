# 한국 지역 날씨 MCP (Model Context Protocol) 서버

이 프로젝트는 한국 지역의 실시간 날씨 정보를 제공하는 Model Context Protocol(MCP) 서버입니다. 기상청의 초단기실황 API를 활용하여 가장 최신의 기상 데이터를 제공합니다.

## 주요 기능

- **실시간 날씨 정보 제공:**  
  한국의 모든 광역시/도에 대한 기온, 강수량, 습도, 강수 형태, 풍향, 풍속 등의 정보를 자동으로 최신 발표 데이터를 기준으로 제공합니다.
- **다양한 도시 명칭 지원:**  
  한글 및 영어 도시 이름(예: 서울, Seoul, 부산, Busan 등) 모두를 지원하여 검색 편의성을 높였습니다.
- **자동 최신 데이터 사용:**  
  기상청 API의 시간 규칙에 따라 10분 미만 시 이전 정시 데이터 또는 전날 데이터(00시 10분 이전)를 자동으로 선택하여 사용합니다.

## 설치 방법

1. **필요한 패키지 설치**

   가상환경(venv) 내에서 FastMCP, uv, httpx, python-dotenv 등 필요한 의존성을 설치합니다.

   ```bash
   pip install fastmcp uv httpx python-dotenv
   ```

2. **환경 변수 설정**

   프로젝트 루트에 `.env` 파일을 생성하고, 기상청에서 발급받은 API 키를 설정합니다.
   해당 키는 https://apihub.kma.go.kr/ 에서 회원가입후 발급 받을수 있으며,
   한달에 2만회 호출이 가능합니다.

   추가적으로, 초단기예보에 api 활용신청이 필요합니다. 예특보 탭에서 단기예보, 초단기예보쪽에
   API 활용 신청을 하시면 정상적으로 이용이 가능합니다.

   ```env
   KMA_API_KEY="기상청에서_발급받은_API_키"
   ```

3. **서버 설치**

   Claude Desktop에 설치할 경우, 다음 명령어를 실행하세요:

   ```bash
   fastmcp install server.py
   ```

   개발 모드에서 테스트하려면 다음과 같이 실행할 수도 있습니다:

   ```bash
   fastmcp dev server.py
   ```

## 사용 방법

### 서버 실행

서버는 기본적으로 `http://localhost:8000`에서 실행됩니다.

### API 엔드포인트

- **스키마 정보:**  
  `GET /schema.json`
- **날씨 정보 요청:**  
  `POST /v1/functions/get_current_weather`

> **참고:** FastMCP를 사용할 경우 도구(tool) 기능이 등록된 엔드포인트를 사용하여 요청할 수 있습니다. 만약 엔드포인트 경로가 변경되었다면 스키마 파일에서 최신 정보를 확인하세요.

## 지원하는 지역

다음과 같은 한국의 주요 행정구역이 지원됩니다:

| 영문명            | 한글명         | 검색 키워드 예시          |
| ----------------- | -------------- | ------------------------- |
| Seoul             | 서울특별시     | Seoul, 서울, 서울특별시   |
| Busan             | 부산광역시     | Busan, 부산, 부산광역시   |
| Daegu             | 대구광역시     | Daegu, 대구, 대구광역시   |
| Incheon           | 인천광역시     | Incheon, 인천, 인천광역시 |
| Gwangju           | 광주광역시     | Gwangju, 광주, 광주광역시 |
| Daejeon           | 대전광역시     | Daejeon, 대전, 대전광역시 |
| Ulsan             | 울산광역시     | Ulsan, 울산, 울산광역시   |
| Sejong-si         | 세종특별자치시 | Sejong, 세종, 세종시      |
| Gyeonggi-do       | 경기도         | Gyeonggi, 경기, 경기도    |
| Gangwon-do        | 강원특별자치도 | Gangwon, 강원, 강원도     |
| Chungcheongbuk-do | 충청북도       | Chungbuk, 충북, 충청북도  |
| Chungcheongnam-do | 충청남도       | Chungnam, 충남, 충청남도  |
| Jeollabuk-do      | 전북특별자치도 | Jeonbuk, 전북, 전라북도   |
| Jeollanam-do      | 전라남도       | Jeonnam, 전남, 전라남도   |
| Gyeongsangbuk-do  | 경상북도       | Gyeongbuk, 경북, 경상북도 |
| Gyeongsangnam-do  | 경상남도       | Gyeongnam, 경남, 경상남도 |
| Jeju-do           | 제주특별자치도 | Jeju, 제주, 제주도        |

## API 응답 예시

```json
{
  "result": {
    "location": "서울",
    "base_date": "20250413",
    "base_time": "1500",
    "weather": {
      "temperature": 18.5,
      "rainfall": 0.0,
      "humidity": 45.0,
      "precipitation_type": {
        "code": "0",
        "name": "없음"
      },
      "wind_direction": 250.0,
      "wind_speed": 2.3
    }
  }
}
```

## 중요 코드 설명

### 시간 처리 로직

- **데이터 발표 기준:**  
  기상청 API는 매 정시에 데이터를 생성하고 10분 후에 제공합니다.
- **로직 설명:**
  1. 현재 시간이 정시 후 10분 미만이면 이전 정시의 데이터를 요청합니다.
  2. 만약 현재 시간이 00시이고 10분 미만이면 전날 23시 데이터를 요청합니다.
  3. 그 외의 경우, 현재 시간의 정시 데이터를 요청합니다.

### 지역 검색 로직

도시 이름 검색은 다음과 같이 진행됩니다:

1. **정확한 이름 일치:**  
   (영문명, 한글명, 행정구역명)

2. **부분 일치 검색:**  
   검색어가 포함된 경우를 판단하여 유연하게 처리합니다.

3. **기본값 반환:**  
   검색 결과가 없으면 기본값으로 서울의 정보를 반환합니다.

### 기상청 API 코드 의미

- **강수형태(PTY) 코드:**

  - 0: 없음
  - 1: 비
  - 2: 비/눈
  - 3: 눈
  - 5: 빗방울
  - 6: 빗방울눈날림
  - 7: 눈날림

- **하늘상태(SKY) 코드:**
  - 1: 맑음
  - 3: 구름많음
  - 4: 흐림

## 참고 자료

- [Model Context Protocol 문서](https://modelcontextprotocol.io/)
- [기상청 단기예보 API 문서](https://apihub.kma.go.kr/)

---
