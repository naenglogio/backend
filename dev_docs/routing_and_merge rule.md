# AI 명령서 — 라우트 도메인 분리 + merge=union 적용

> 목적: 여러 명이 새 페이지를 추가할 때 `App.tsx`와 `pages/index.ts`에서 나는 merge 충돌을 없앤다.
> 대상 레포: naenglogio/frontend (React + TypeScript + Vite, **react-router v8**, 패키지 매니저 **yarn**)
> AI에게 이 문서를 그대로 주고 순서대로 수행시킨다. 각 단계 끝에서 사람이 검토 후 다음으로 넘어간다.

---

## 사전 확인 (이미 조사됨 — 참고용)
- react-router 버전: **^8.3.0** → `useRoutes`, `RouteObject` 사용 가능.
- 페이지 파일: 모두 별도 파일 (`src/components/pages/*.tsx`), barrel은 `src/components/pages/index.ts`.
- 인증 가드: `src/components/RequireAuth.tsx`, `RequireAuth({ children })` 형태.
- 현재 라우트(App.tsx)에 등록된 것: `/`(→/login 리다이렉트), `/login`, `/signup`, `/mainpage`, `/profile`(가드), `/ingredients`(가드).
- `.gitattributes` 없음 → 새로 만든다.

## 대전제 (지켜야 할 규칙)
- 기존 페이지 동작/경로를 바꾸지 마라. **구조만 옮긴다.** URL 경로는 그대로 유지.
- 이 레포는 **yarn**을 쓴다. npm 쓰지 마라. 검증은 `yarn build`(타입 포함) + `yarn dev`.
- **import 스타일은 기존 방식(barrel)을 그대로 유지한다.** 페이지는 `../components/pages`(barrel)에서 import한다.
  (import 스타일 변경은 팀 컨벤션 사안이라 이번 작업 범위가 아니다. 임의로 직접 경로로 바꾸지 마라.)

---

## STEP 1. 라우트 폴더/파일 생성 (도메인 분리)

`src/routes/` 폴더를 만들고 아래 파일들을 생성하라. 현재 App.tsx의 라우트를 도메인별로 옮긴다.
페이지 import는 **기존 barrel(`../components/pages`)** 을 사용한다.

### src/routes/auth.routes.tsx (로그인/회원가입 + 루트 리다이렉트)
```tsx
import { Navigate } from 'react-router';
import type { RouteObject } from 'react-router';
import { LoginPage, SignupPage } from '../components/pages';

export const authRoutes: RouteObject[] = [
  { path: '/', element: <Navigate to="/login" replace /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/signup', element: <SignupPage /> },
];
```

### src/routes/ingredient.routes.tsx (재성 담당 — 식재료/홈)
```tsx
import type { RouteObject } from 'react-router';
import { RequireAuth } from '../components/RequireAuth';
import { MainPage, IngredientListPage } from '../components/pages';

export const ingredientRoutes: RouteObject[] = [
  { path: '/mainpage', element: <MainPage /> },
  {
    path: '/ingredients',
    element: (
      <RequireAuth>
        <IngredientListPage />
      </RequireAuth>
    ),
  },
  // 새 라우트(상세/등록/스캔/3D 등)는 이 파일에만 추가한다.
];
```

### src/routes/user.routes.tsx (프로필 등)
```tsx
import type { RouteObject } from 'react-router';
import { RequireAuth } from '../components/RequireAuth';
import { ProfilePage } from '../components/pages';

export const userRoutes: RouteObject[] = [
  {
    path: '/profile',
    element: (
      <RequireAuth>
        <ProfilePage />
      </RequireAuth>
    ),
  },
];
```

### src/routes/index.tsx (합치기 — 이후 거의 안 바뀜)
```tsx
import type { RouteObject } from 'react-router';
import { authRoutes } from './auth.routes';
import { ingredientRoutes } from './ingredient.routes';
import { userRoutes } from './user.routes';

export const routes: RouteObject[] = [
  ...authRoutes,
  ...ingredientRoutes,
  ...userRoutes,
];
```

> 도메인 파일은 팀 합의에 따라 recipe.routes.tsx(선영), chat 관련 등으로 더 나눌 수 있다.
> 지금은 기존 라우트만 3개 파일로 옮긴다. 없는 페이지는 만들지 마라.

**STEP 1 체크포인트**
- [ ] 기존 App.tsx의 모든 경로가 새 파일들에 1:1로 옮겨졌는가(누락 없음)
- [ ] 가드가 필요한 경로(/profile, /ingredients)에 RequireAuth가 유지됐는가
- [ ] 페이지 import가 전부 기존 barrel(`../components/pages`)을 사용하는가

---

## STEP 2. App.tsx 교체

App.tsx를 아래로 교체하라. 라우트 목록은 전부 STEP 1로 이동했으므로 여기선 routes를 렌더만 한다.

```tsx
import { BrowserRouter, useRoutes } from 'react-router';
import { routes } from './routes';

function AppRoutes() {
  return useRoutes(routes);
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
```

**STEP 2 체크포인트**
- [ ] App.tsx에 더 이상 개별 `<Route>`가 없다
- [ ] `useRoutes(routes)`가 `<BrowserRouter>` 안쪽에서 호출된다
- [ ] `yarn dev`로 기존 5개 경로가 전부 정상 렌더된다(/login, /signup, /mainpage, /profile, /ingredients)

---

## STEP 3. .gitattributes에 merge=union 적용

레포 루트에 `.gitattributes`가 없으므로 새로 만들고 아래 내용을 넣어라.
`pages/index.ts` 같은 barrel 파일은 계속 쓰이므로, 그 충돌은 union으로 자동 병합되게 한다.

```
# 한 줄 = 한 export 인 순수 barrel 파일에만 union 적용.
# 두 브랜치가 서로 다른 줄을 추가하면 충돌 마커 없이 자동 병합된다.
src/components/pages/index.ts merge=union
```

> **적용 범위는 `pages/index.ts` 하나뿐이다.** 가장 충돌이 잦은 파일에만 최소로 건다.
> atoms/molecules/organisms의 index.ts는 이번엔 걸지 않는다(충돌 빈도가 낮고, union은 최소 범위로 쓰는 게 안전). 필요해지면 나중에 같은 형식으로 추가한다.

### 절대 하지 말 것 (중요)
- `types/index.ts`, `App.tsx`, `src/routes/*` 등 **여러 줄 블록/JSX 파일에는 union을 걸지 마라.**
  여러 줄을 union으로 합치면 문법이 깨진 결과가 충돌 마커 없이 조용히 커밋될 수 있다.
- `pages/index.ts`가 "한 줄 = 한 export" 형태임을 확인하고 적용하라.

### 주의 (팀 공지 사항)
- union은 "서로 다른 줄 추가"는 자동 합치지만, **같은 export를 두 사람이 각자 추가하면 중복 줄**이 조용히 들어갈 수 있다.
  → barrel에 export 추가 시 알파벳 위치를 지키고, 리뷰에서 중복 여부를 한 번 확인한다.

**STEP 3 체크포인트**
- [ ] `.gitattributes`가 레포 루트에 생성됐다
- [ ] union 대상이 `src/components/pages/index.ts` **하나뿐이다** (types/index.ts·App.tsx·routes·다른 barrel 제외)
- [ ] 해당 파일이 실제로 "한 줄=한 export" 형태다

---

## STEP 4. 최종 검증 & 보고

- `yarn build`가 타입 에러 0으로 통과하는가
- `yarn dev`로 기존 5개 경로가 정상 동작하는가
- 무엇을 만들었는지(생성/수정 파일 목록), 각 STEP 체크포인트 통과 여부를 보고하라

---

## 커밋 제안
1. `refactor(routing): split routes into domain files + useRoutes`
2. `chore(git): add merge=union for barrel index files`

## 팀 공지용 한 줄 요약
- 새 페이지 라우트는 **자기 도메인의 `src/routes/*.routes.tsx`에만** 추가한다(App.tsx 수정 금지).
- 페이지 import는 **기존처럼 barrel** 사용(import 스타일 변경 없음).
- barrel(index.ts)에 export 추가 시 **알파벳 위치 유지**(union 중복 방지).

---

## 참고: 이번 범위에서 제외한 것
- **직접 import 전환**은 하지 않는다. import 스타일은 팀 컨벤션 사안이라, 필요하면 별도 안건으로 논의한다.
  (pages/index.ts 충돌은 이번 STEP 3의 merge=union으로 이미 처리된다.)