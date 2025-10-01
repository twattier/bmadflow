# Unified Project Structure

```
bmadflow/
├── .github/workflows/         # CI/CD (ci.yaml, lint.yaml, deploy.yaml)
├── apps/
│   ├── web/                   # React SPA
│   │   ├── src/               # Components, pages, hooks, services
│   │   ├── public/
│   │   ├── tests/
│   │   └── package.json
│   └── api/                   # FastAPI backend
│       ├── src/               # Routes, services, repositories, models
│       ├── tests/
│       ├── alembic/           # Database migrations
│       └── requirements.txt
├── packages/
│   ├── shared/                # Shared TypeScript types
│   └── config/                # Shared ESLint, TypeScript configs
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx.conf
├── scripts/                   # setup.sh, dev.sh, test.sh
├── docs/                      # prd.md, front-end-spec.md, architecture.md
├── .env.example
├── package.json               # npm workspaces
└── README.md
```

---
