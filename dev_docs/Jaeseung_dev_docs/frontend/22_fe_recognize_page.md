# FE-4. 카메라 인식 화면 + 등록 연결

## 선행
FE-1, FE-3 완료. (BE-7 완료면 실연동, 아니면 목업 선개발)

## 함께 읽을 문서
- `../shared/00_API_CONTRACT.md` (4. 카메라 인식)
- `../shared/01_STATUS_BOARD.md` (BE-7 상태)

## 지시
### 화면
`/ingredients/recognize` 라우트.
- 파일 업로드 + `getUserMedia` 카메라 프리뷰. 권한 거부 시 업로드로 폴백.
- 선택/촬영 이미지 미리보기.

### 인식 연동
- `recognize(image)` 호출 → `CameraRecognizeResponse.candidates`를 confidence 뱃지(%) 카드로 표시.
- 인식 중 로딩, 빈 결과/실패 상태 처리.

### 등록 연결
- 후보 카드 선택 시 `/ingredients/new`로 이동하면서 food_id/name/category 프리필(상태 전달). 사용자가 나머지 필드 보완 후 등록.

## 체크포인트
- [ ] 미리보기 표시, 권한 거부 폴백
- [ ] 모바일 뷰포트 정상
- [ ] confidence % 표기, 실패/빈 결과 처리
- [ ] 프리필 정확·수정 가능
- [ ] 인식 → 등록 → 상세까지 한 번에 연결

## 완료 후
`../shared/01_STATUS_BOARD.md`의 FE-4 → ✅.

---

## UI 명세 (와이어프레임 "스캔 (바코드/영수증)" 기준)
> 디자인은 `../shared/02_DESIGN_SYSTEM.md`를 따른다.
> ※ 와이어프레임은 바코드/영수증 탭 구조지만, 재성 담당(BE-7)은 **식재료 사진 인식**이다. 탭 구조는 유지하되 MVP는 사진 인식 흐름으로 구현하고, 바코드/영수증은 자리(placeholder)만 둬도 됨. 팀과 범위 협의.

**레이아웃 (위→아래)**
1. 상단: "스캔" 타이틀
2. **모드 탭**: SegmentedControl(바코드 / 영수증 / 사진) — MVP는 사진 인식 활성
3. **카메라 프리뷰** 영역: 점선 프레임 `rounded-card`, "카메라 프리뷰" 안내. 권한 거부 시 업로드 버튼 폴백.
4. **인식 결과 (검수)** 카드: 인식된 후보를 표시
   - 후보명 (예: 서울우유 900ml) + confidence %
   - `확인 후 추가`(primary) / `수정`(secondary) 버튼 (와이어프레임 그대로)
5. 하단: 5탭 네비게이션 (스캔 활성)

**흐름**: 프리뷰/업로드 → recognize() → 후보 카드 → 선택 시 등록 화면(FE-3)으로 프리필 이동.
**컴포넌트 재사용**: `atoms/SegmentedControl`, `atoms/Button`, 카드 컨테이너(`rounded-card shadow-soft`).

**UI 체크포인트**
- [ ] 카메라 프리뷰 프레임 + 권한 거부 시 업로드 폴백
- [ ] 후보 카드에 confidence % 표기
- [ ] 확인 후 추가=primary / 수정=secondary
- [ ] 선택 → 등록 화면 프리필 이동
- [ ] 하단 5탭 네비(스캔 활성), 기존 토큰만 사용
