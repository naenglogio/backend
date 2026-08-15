# 디자인 시스템 참조 (SHARED · 프론트 UI 공통)

> 재성 담당 화면은 **기존 디자인 시스템을 그대로 따른다.** 새 색·새 컴포넌트를 임의로 만들지 말고, 아래 토큰과 기존 컴포넌트를 재사용한다.
> 와이어프레임 하단 명시: "기존 UI 스타일과 하단 내비게이션 유지".

## 스타일 방식
- **Tailwind CSS v4** + `src/index.css`의 `@theme` 토큰. styled-components 등 별도 CSS-in-JS 없음.
- atomic 구조: `atoms → molecules → organisms → pages`.

## 테마 토큰 (src/index.css)
- 색 (brand): `primary-50` ~ `primary-900` (하늘색 #6cb4ee 계열)
- 배경/선: `surface`(#fff), `surface-muted`(#f7f8fc), `line`(#e3e6f0)
- 텍스트: `ink`(#1a1d29), `ink-soft`, `ink-muted`
- 상태색: `fresh`(초록), `warning`(주황), `danger`(빨강) — 신선도/에러 공용
- 모양: `rounded-card`(20px), `rounded-input`(14px), `shadow-soft`
- 폰트: 시스템 한글 스택(`--font-sans`)
- 클래스 예: `bg-primary-500 text-white`, `rounded-card shadow-soft`, `text-danger`, `bg-surface-muted`

## 재사용 가능한 기존 컴포넌트
**atoms**: Button(primary/secondary, loading), Input(label/error/action), Checkbox, Modal, Badge, SegmentedControl(제네릭 탭), ToggleSwitch, NavIcon, StatCard, RecipeCard, FridgeIllustration, DDayTag(⚠️ 아래 주의)
**molecules**: NavItem, SearchInput, SortFilter, StorageTabs, ExpiringItem, StatCard
**organisms**: Sidebar, TopBar, FridgeCard, IngredientCard, IngredientList, ExpiringCard, StatStrip, LoginForm, SignupForm, ProfileSettingsForm, RecipeSection

## 주의: DDayTag
- 현재 `DDayTag`는 `mock/home`의 `DDay`(0/1/3 고정 리터럴)에 묶여 있다.
- 재성 상세/목록은 실제 `expiration_date`로 D-day를 계산해야 하므로 그대로 쓸 수 없다.
- **방침**: 실제 날짜(`expiration_date`)를 받아 D-day를 계산해 색/라벨을 정하는 확장 버전을 만든다.
  기존 파일을 덮지 말고 `atoms/ExpiryTag.tsx`(신규)로 만들어 재성 화면에서 사용. (기존 DDayTag는 선영·우희 홈이 쓰므로 유지)
  색 규칙: 지남/오늘 = danger, 임박(N일 이내) = warning, 여유 = fresh 또는 primary.

## 레이아웃/네비게이션
- 하단 5탭 내비게이션: **홈 · 냉장고 · 스캔 · 알림 · 마트** (와이어프레임 공통). 기존 NavItem/NavIcon 사용.
- 상세/등록 등 진입 화면은 상단에 뒤로가기 + 타이틀.
- 모바일 우선 레이아웃. 카드형 컨테이너(`rounded-card shadow-soft bg-surface`).

## storage_type 표시
- 데이터는 int(0/1). 표시는 `utils/storage.ts`의 `storageLabel`/`STORAGE_OPTIONS`.
- 상세/등록의 저장위치 탭은 SegmentedControl 사용 가능(단, value가 int라 문자열 제네릭과 맞게 매핑 필요 — 라벨은 냉장/냉동).
  ※ 와이어프레임엔 "냉장/냉동/실온" 3탭이 보이나, **노션 정본은 냉장/냉동 2종(실온 없음)**. 2탭으로 구현하고 팀에 공유.
