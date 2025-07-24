# 메뉴 추천 프로젝트

이 프로젝트는 최근 3번의 식사에서 섭취한 영양소 정보를 바탕으로 다음 식사로 추천할 메뉴를 제안합니다.

## 사용 방법
1. `meal_history.json` 파일에 최근 3번의 식사 정보를 입력합니다.
2. `menus.json` 파일에는 추천 가능한 메뉴의 영양 정보를 기록합니다.
3. `python3 recommend_menu.py` 명령을 실행하면 가장 적절한 메뉴가 출력됩니다.

### 예시
```
$ python3 recommend_menu.py
Recommended menu: Chicken Salad
```
