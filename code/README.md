# code

All source code. Each folder is one deployable or library with its own toolchain, tests and
README.

| Folder | What | Stack |
|---|---|---|
| [`backend/`](backend/) | API: management API for Studio, SDK API, event ingestion. Serves built Studio and `/sdk.js` | Python, FastAPI, SQLAlchemy 2, Alembic, Postgres |
| [`studio/`](studio/) | Web console: author, target, publish, analyse | React, TypeScript, Vite |
| [`sdk/`](sdk/) | Browser SDK loaded on the host app's pages | TypeScript, no runtime deps |
| [`shared/`](shared/) | Contracts shared across parts (JSON Schemas, generated types) | JSON Schema |
| [`builder-extension/`](builder-extension/) | Chrome extension for building steps on the live page (phase 2) | TypeScript, Manifest V3 |
| [`demo/`](demo/) | Plain host page that loads the SDK, for local testing | HTML |

The JavaScript packages (`studio`, `sdk`, `shared`, `builder-extension`, `demo`) form one pnpm
workspace rooted in this folder, so the repository root stays free of JS tooling files.
