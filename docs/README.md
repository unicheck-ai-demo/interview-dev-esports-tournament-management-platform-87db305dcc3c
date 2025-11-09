# Esports Tournament Management Platform

A platform to streamline the organization of esports tournaments by empowering organizers to create and manage tournaments, register participants and teams, schedule brackets, track results in real time, and automatically update player and team rankings.

## Data Model Overview

### Tournament
- `id, name, description, start_date, end_date, status, max_participants, archived, created_at, updated_at`
- Status: upcoming, active, completed, archived

### Player
- Linked to `User`
- `nickname, elo_rating, created_at, updated_at`

### Team
- `name (unique), members (m2m Player), elo_rating, created_at, updated_at`

### Registration
- `tournament, player or team, registered_at`
- Ensures a user or team is not registered for the same tournament twice

### Match
- `tournament, round_number, player1, player2, team1, team2, scheduled_at, completed, winner_player, winner_team, created_at, updated_at`

## Key Features

### Tournament Management
- Versioned REST API (/api/v1/tournaments) for CRUD, listing, archiving, and filtering

### Participant Registration
- APIs for individual/player and team tournament registration
- Capacity validation with PostgreSQL row-level locking for concurrency

### Match Scheduling, Bracket Generation
- Seed participants and generate brackets using optimized SQL (window functions/CTEs via Django DB API)
- API for fetching bracket data

### Leaderboard & Stats
- Leaderboards and statistics for tournaments, filterable by player/team
- Paginated and leveraging optimized SQL queries for performance

### ELO Rating Calculation
- Background recalculation with Celery (triggered at match completion)
- Multi-step transaction with rollback on error for integrity

### Authentication
- DRF TokenAuthentication (set in `settings.py`)
- POST/PUT/DELETE require authentication, GET is public

## Architecture
- **Layered:** API Layer (DRF ViewSets), Service Layer (business logic in services.py), Data Layer (Django ORM models)
- **Patterns:** Service Object Pattern, Repository hints via custom managers, Asynchronous Task Queue (Celery)
- **Tests:** pytest, pytest-django for core features, service logic, auth, and async tasks

## Running and Development

- See the project's Makefile and top-level README for setup
- Migration: `make makemigrations && make migrate`
- Worker: `make worker` (for celery tasks)
- Run/test: `make run`, `make test`

## Important Notes
- Heavily indexed columns on foreign keys and filter fields for speed
- Strict SOLID separation of concerns
- Avoids n+1 queries in leaderboard/seeding with raw SQL when needed, never for business logic
- No business logic in models or views; use services
- No Pydantic, dataclasses, or Django admin

---
Contact: info@unicheck.ai
