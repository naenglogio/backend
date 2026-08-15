# FE-3. 등록 화면

## 선행
FE-1 완료. (BE-4 완료면 실연동, 아니면 목업 선개발)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (3. 등록)
- `../shared/01_STATUS_BOARD.md` (BE-4 상태)

## 지시
`/ingredients/new` 라우트 신설.
- 폼: name, storage_type select(`STORAGE_OPTIONS`), quantity+unit, purchase_date(date picker), expiration_date(date picker), memo.
- `createIngredient(body)` 연동. `IngredientCreateRequest` 사용. **storage_type은 int로 전송.**
- 성공 시 상세 화면(`/ingredients/:id`)으로 이동.
- 서버 422 에러를 필드별로 표시(클라이언트 검증 + 서버 검증).

## 체크포인트
- [ ] storage_type int 전송
- [ ] 클라 검증 + 서버 422 필드별 표시
- [ ] 등록 성공 → 상세 이동
- [ ] date picker 동작

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-3 → ✅.
> FE-4(카메라)에서 이 화면으로 프리필 이동하므로, name/category/food_id를 외부에서 주입받을 수 있게 설계.

---

## UI 명세 (와이어프레임 "식재료 등록" 기준)
> 디자인은 `../shared/02_DESIGN_SYSTEM.md`를 따른다.

**레이아웃 (위→아래)**
1. 상단: 뒤로가기(‹) + "식재료 등록" 타이틀
2. **사진 추가** 영역: 점선 박스 `+ 사진 추가` (image_url용, 선택). 우측에 식재료명/카테고리 입력.
   - 식재료명(name) 입력 — `atoms/Input`
   - 카테고리 선택 (food 연결 or 표시용)
3. **보관 위치**: SegmentedControl(냉장/냉동) — 기본 냉장 선택
4. **수량 · 단위**: quantity 입력 + unit 입력(예: 1 / 개) — 2열
5. **구매일 · 유통기한**: purchase_date / expiration_date date picker — 2열
6. 알림 시점 표시(예: "만료 3일 전") — 참고 UI (알림은 선영 담당, 값 표시만)
7. 하단: **등록하기** 버튼(primary, full-width)

**컴포넌트 재사용**: `atoms/Input`, `atoms/Button`, `atoms/SegmentedControl`, date input.
**카메라 프리필 대응**: FE-4에서 name/category/food_id를 주입받으면 해당 필드가 채워진 상태로 진입.

**UI 체크포인트**
- [ ] 보관위치 냉장/냉동 2종(실온 없음)
- [ ] 수량+단위 2열, 구매일+유통기한 2열 배치
- [ ] 사진 추가 점선 박스(선택 입력)
- [ ] 등록하기 primary full-width
- [ ] 검증 에러가 Input error prop으로 필드 아래 표시
- [ ] 기존 토큰만 사용
