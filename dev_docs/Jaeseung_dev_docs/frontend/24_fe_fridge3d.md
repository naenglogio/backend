# FE-6. 메인 3D 냉장고

## 선행
FE-1 완료 + 3D 기술 스파이크(@react-three/fiber, drei 설치 검증) 완료. (BE-3 완료면 실데이터)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (2. 목록)
- `../shared/01_STATUS_BOARD.md` (BE-3 상태)
- 현재 `src/components/pages/MainPage.tsx`, `src/components/organisms/FridgeCard.tsx`

## 목표 수준
**레벨 2(드래그 이동) + 상세 이동 인터랙션.** soft delete 연동은 범위 밖(여유 시 레벨 3).
스파이크 실패 시 → 2.5D 폴백.

## 지시 (하위 단계)
### 6-1. 씬 세팅
MainPage의 FridgeCard 자리에 3D 냉장고 컴포넌트 임베드. 냉장(0)/냉동(1) 칸 구분, 조명, OrbitControls.

### 6-2. 오브젝트 배치 (실데이터)
`listIngredients`(소유분, is_deleted=false, `Fridge3DItem[]`)로 식재료를 storage_type별 칸에 배치. expiration_status/expiration_date 기준 임박·만료 색상 강조. 배치 좌표는 프론트 그리드 규칙.

### 6-3. 드래그 이동 (레벨 2)
raycasting + 드래그로 냉장고 안 이동, 냉장/냉동 칸 간 이동 허용(화면 동작까지, 저장 X). 터치·마우스 지원.

### 6-4. 상세 이동 인터랙션 (제스처 분기)
- 판정: 다운 후 이동 > 8px = 드래그 / 정지 + 500ms = 롱프레스. 상호배타.
- **모바일 롱프레스 → "상세화면으로 이동하시겠습니까?" 확인 팝업 → `/ingredients/:id`**
- **웹 더블클릭 → 상세 이동**

## 체크포인트
- [ ] 대시보드에 자연스럽게 임베드, 부드러운 렌더
- [ ] 냉장/냉동 칸 분리 배치, 10건+ 안 겹침
- [ ] 임박 시각 구분
- [ ] 드래그 이동(터치·마우스), 칸 경계 처리
- [ ] 드래그 중 상세 오발동 없음
- [ ] 롱프레스 팝업→이동 / 더블클릭 이동 / 대상 id 정확

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-6 → ✅.

---

## UI 명세 (와이어프레임 "홈 · 3D 냉장고" 기준)
> 디자인은 `../shared/02_DESIGN_SYSTEM.md`를 따른다. 기존 MainPage 레이아웃(사이드바/탑바/카드) 안에 3D 냉장고를 임베드한다.

**홈 화면 구성 (기존 MainPage 유지 + 냉장고만 3D화)**
1. 상단: "오늘의 요약 (날짜)" + `자세히 보기 >`
2. **3D 냉장고 카드** (FridgeCard 자리): `rounded-card` 안에 3D 씬
   - 안내 텍스트 "드래그하여 냉장고 내부 확인"
   - 냉장 칸(위)/냉동 칸(아래) 2단 구획 — storage_type 0/1 대응
   - 각 칸에 식재료 수 뱃지(예: 18, 6), 임박 개수는 danger 뱃지(예: 3)
3. "오늘 만들 수 있는 레시피" 섹션 (RecipeSection, 선영 담당 — 건드리지 않음)
4. 하단: 5탭 네비게이션 (홈 활성)

**3D 씬 UI**
- 냉장고 외형: 2칸 구획이 시각적으로 구분(냉장/냉동).
- 식재료 오브젝트: 임박·만료는 상태색(warning/danger) 강조.
- 인터랙션 피드백: hover/드래그 중 하이라이트, 롱프레스 진행 표시(모바일).

**컴포넌트/토큰**
- 카드 컨테이너는 기존 `rounded-card shadow-soft bg-surface`.
- 상태색은 `fresh/warning/danger` 토큰 재사용(3D 머티리얼 색도 이 값에 맞춤).
- 상세 이동 확인 팝업은 `atoms/Modal` 재사용.

**UI 체크포인트**
- [ ] 기존 MainPage 레이아웃 안에 자연스럽게 임베드(사이드바/탑바/네비 유지)
- [ ] 냉장/냉동 2칸 구획 시각 구분 + 칸별 개수 뱃지
- [ ] 임박 개수 danger 뱃지
- [ ] 상태색이 토큰(fresh/warning/danger)과 일치
- [ ] 롱프레스 확인 팝업은 Modal 재사용
- [ ] RecipeSection(선영) 미변경
