# studio

Web console (React + TypeScript + Vite). M0 has first-run setup, sign-in and an empty home
screen; authoring arrives in M3.

`src/App.tsx` decides the screen (setup → sign-in → app) from `/api/setup/status` and
`/api/auth/me`. `src/api.ts` is the only place that calls the API.

Built output is copied into the backend image and served by the API, so a self-hoster deploys
one container.

## Develop

Run from `code/` (the npm workspace root), with the backend running on :8000:

```bash
npm install
npm run dev --workspace studio        # http://localhost:5173, proxies /api to :8000
```

## Check

```bash
npm run check                          # Biome lint + format check (from code/); `npm run format` fixes
npm run typecheck --workspace studio
npm test --workspace studio            # Vitest; one file: npx vitest run src/App.test.tsx (in studio/)
npm run build --workspace studio       # → studio/dist
```
