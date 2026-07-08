# ShopPilot Architecture

## Overview

ShopPilot is a cross-platform commerce intelligence platform with a Next.js frontend, FastAPI backend, pluggable marketplace adapters, and optional Codex engineering agents.

## Data Flow

```
User Input → Frontend → FastAPI → Adapter → Bright Data → Normalized Listings
    → Analysis Engine → AI Agents → Recommendations → Dashboard
```

## Layers

### Frontend (`frontend/`)
- Next.js App Router dashboard
- Typed API client in `lib/api.ts`
- shadcn/ui components

### Backend (`backend/app/`)
- **API routes** — REST endpoints for analyses, search, Codex
- **Services** — Bright Data, ingestion, normalization, AI orchestration
- **Adapters** — Platform-specific extraction (Etsy, Google Shopping, generic, stubs)
- **Analysis** — Pricing, keywords, competitors, listing audit, trends
- **Agents** — OpenAI product intelligence (listing advisor, expansion, research)
- **Codex Agents** — Optional developer tooling for adapter maintenance

### Database
- SQLite for local development via SQLAlchemy
- Alembic for migrations

## Adapter Pattern

All adapters inherit from `BaseMarketplaceAdapter`:

- `build_search_url()` — construct marketplace search URL
- `parse_listings()` — parse HTML into `ProductListingSchema`
- `normalize_listing()` — normalize raw dict to schema

Register new adapters in `adapters/__init__.py`.

## Mock Fallback

When Bright Data is unavailable or parsing fails, `MockAdapter` loads seed data from `seed/sample_marketplace_data.json`.
