# 메뉴 추천 웹 서비스

최근 3끼 식사와 개인 정보를 입력하면 부족한 영양소를 채워 줄 다음 메뉴를 추천하는 간단한 웹 서비스입니다. 라이트/다크 모드를 지원하고 TailwindCSS를 이용해 반응형으로 동작합니다.

## 사용 방법
1. `menus.json` 파일에 음식 데이터를 추가합니다.
2. `python3 web_service.py` 를 실행하고 브라우저에서 `http://localhost:8000` 에 접속합니다.
3. 성별, 연령, 알레르기 정보와 최근 식사 3가지를 입력하면 추천 결과가 표시됩니다.

### 예시
```bash
$ python3 web_service.py
Serving on http://localhost:8000
```
