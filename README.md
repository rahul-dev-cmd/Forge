# Forge – AI-Native Project Operating System

Forge is an AI-native project operating system designed to help software teams understand, collaborate on, and evolve software projects faster.

## Monorepo Layout

- `apps/`
  - `web/`: Next.js 15 Web Application frontend
  - `api/`: FastAPI Backend API
- `packages/`
  - `config/`: Shared configurations (ESLint, Prettier, TypeScript)
  - `types/`: Shared TypeScript typings
  - `ui/`: Shared components package
  - `utils/`: Shared helper functions

## Scripts

Execute commands using `pnpm` in the workspace root:

- `pnpm dev`: Start all apps in development mode.
- `pnpm build`: Build all workspace projects.
- `pnpm lint`: Run ESLint check for all code.
- `pnpm typecheck`: Run TypeScript type validations.
