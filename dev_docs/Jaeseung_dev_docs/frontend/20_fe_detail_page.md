# FE-2. 상세 화면

## 선행
FE-1 완료. (BE-3 완료면 실연동, 아니면 계약서 기준 목업으로 선개발)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (1. 상세)
- `../shared/01_STATUS_BOARD.md` (BE-3 상태 확인)

## 지시
`/ingredients/:id` 라우트 신설(App.tsx, `RequireAuth`로 보호).
- `getIngredient(id)` 연동, `IngredientDetailResponse` 사용.
- 재사용: `atoms/DDayTag`, `utils/dday.ts`, `utils/storage.ts`.
- 표시: name, storage_type(라벨), quantity+unit, purchase_date, expiration_date D-day, **expiration_status(CONFIRMED=확정 / ESTIMATED=예상 시각 구분)**, memo, image_url. 상품기반이면 참고 상품/프로필도.
- 삭제·수정 버튼(동작은 다음 단계 또는 여력 시).
- 로딩 스피너, 404 처리.

## 체크포인트
- [ ] RequireAuth 보호
- [ ] CONFIRMED/ESTIMATED 시각 구분
- [ ] D-day 정확(지난 경우 D+N)
- [ ] 로딩·404
- [ ] 피그마 시안 정합

## BE 연동 상태에 따라
- BE-3 ✅ → 실서버 연동
- BE-3 ⬜ → 계약서 기준 목업 응답으로 화면 완성, base URL만 나중에 전환

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-2 → ✅.

---

## UI 명세 (와이어프레임 "식재료 상세 / 편집" 기준)
> 디자인은 `../shared/02_DESIGN_SYSTEM.md`의 토큰·컴포넌트를 따른다.

**레이아웃 (위→아래)**
1. 상단: 뒤로가기(‹) + 화면 타이틀
2. 식재료 이미지 영역 (image_url, 없으면 placeholder) — `rounded-card`
3. 이름 (name) — 큰 굵은 텍스트 (`text-ink` 강조)
4. **저장 위치**: SegmentedControl(냉장/냉동) — storage_type(int)와 매핑. 편집 시 변경.
5. **수량**: `-` / 값+unit / `+` 스테퍼 (예: 900ml). 편집 가능.
6. **유통기한**: 날짜 + D-day. `expiration_status`에 따라:
   - CONFIRMED → 일반 표시
   - ESTIMATED → "예상" 뱃지 + 테두리 강조(warning 계열)
   - 지난 경우 danger 색 테두리 (와이어프레임의 빨간 박스 "2025.06.12 (D-1)")
7. memo (있으면)
8. 하단: **저장** 버튼(primary, full-width) + **삭제**(danger 텍스트 버튼)

**컴포넌트 재사용**: `atoms/Button`, `atoms/Input`, `atoms/SegmentedControl`, 신규 `atoms/ExpiryTag`(D-day 계산형).
**상태**: 조회 모드 ↔ 편집 모드 구분(와이어프레임 제목이 "상세 / 편집"). 처음엔 조회, 수정 버튼으로 편집 전환하거나 인라인 편집.

**UI 체크포인트**
- [ ] 저장위치 탭이 냉장/냉동 2종(실온 없음, 노션 정본)
- [ ] 수량 스테퍼 동작(+/-), unit 표기
- [ ] 유통기한이 status별로 시각 구분(확정/예상/지남)
- [ ] 저장=primary / 삭제=danger, 하단 배치
- [ ] 기존 토큰만 사용(임의 색 금지)
