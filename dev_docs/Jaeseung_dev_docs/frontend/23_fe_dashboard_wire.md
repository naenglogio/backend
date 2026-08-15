# FE-5. MainPage 대시보드 실API 연동

## 선행
FE-1 완료. (BE-5, BE-6 완료면 실데이터, 아니면 목업)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (5. 집계)
- `../shared/01_STATUS_BOARD.md` (BE-5 상태)
- 현재 `src/components/pages/MainPage.tsx`, `src/mock/home.ts`

## 지시
현재 MainPage는 `mock/home.ts` 하드코딩으로 동작 중. 이를 실API로 전환.
- `services/homeApi.ts` 작성 or `ingredientApi.getSummary()` 사용 → `IngredientSummaryResponse`.
- `StatStrip`(total/expiring/fresh), `FridgeCard`(냉장/냉동/임박 수), `ExpiringCard`(임박 목록)를 실데이터로.
- storage_type 라벨은 `utils/storage.ts` 사용.
- 로딩·에러 상태 처리. `mock/home.ts` 의존 제거.

## 주의
- `RecipeSection`은 **선영 담당** 레시피 영역 → 이번엔 건드리지 말고 협의.

## 체크포인트
- [ ] 통계/냉장고/임박이 실API로
- [ ] seed 데이터 숫자와 화면 일치
- [ ] `mock/home.ts` 의존 제거
- [ ] 로딩·에러 상태

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-5 → ✅.

---

## UI 명세 (와이어프레임 "내 프로필 / 홈 요약" 기준)
> 기존 MainPage의 StatStrip/FridgeCard/ExpiringCard 컴포넌트를 그대로 쓰고 데이터만 실API로 교체. UI 구조 변경 없음.
- 냉장고 현황: 총 식재료 수 / 만료 임박 수 (와이어프레임 "24 / 3" 형태)
- 임박 목록: ExpiringItem 재사용, D-day 표시.
- 새 컴포넌트 만들지 말 것 — 데이터 소스만 `getSummary()`로.
