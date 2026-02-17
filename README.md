# NutriTrack

**AI-powered personal nutrition and health tracking platform**

---

## What Is NutriTrack

NutriTrack is a self-hosted nutrition and health tracking application designed to work hand-in-hand with AI agents. You talk to your AI assistant, it logs your meals, exercise, weight, and vitals through NutriTrack's REST API, and a real-time dashboard visualizes everything. A built-in gamification system awards XP, tracks streaks, and grants badges to keep you motivated. NutriTrack is LLM-agnostic -- any agent that can make HTTP calls can serve as your personal nutrition assistant.

The platform runs locally on the user's machine -- no cloud accounts or external services required. Users can optionally expose it via reverse proxy or tunnels if they want remote access, but this is entirely optional -- the default is localhost-only.

## Screenshots

<!-- Add screenshots here -->

## Features

- Calorie and macro tracking with personalized daily goals calculated using the Mifflin-St Jeor equation
- Weight trend tracking with historical charts
- Exercise logging with dynamic calorie adjustment (exercise calories feed back into your daily budget)
- Health vitals monitoring: blood pressure, blood sugar, SpO2, and heart rate
- Gamification system with streaks, XP points, elite status, and achievement badges
- Dark-theme dashboard built with Chart.js for all visualizations
- REST API with auto-generated Swagger documentation at `/docs`
- AI agent integration -- any LLM can log and query data via standard HTTP requests
- Zero-configuration SQLite database (no external database server required)
- Docker and bare-metal deployment options
- Food search across past entries and CSV data export

## Quick Start

### Path A: Docker (Recommended)

```bash
git clone https://github.com/BenZenTuna/Nutritrack.git
cd Nutritrack
docker compose up -d
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

### Path B: Direct Install

```bash
git clone https://github.com/BenZenTuna/Nutritrack.git
cd Nutritrack
chmod +x install.sh
./install.sh
```

The installer checks for Python 3.10+, creates a virtual environment, installs dependencies, initializes the database, and starts the server.

## Load Demo Data

Seed 30 days of realistic sample data to explore the dashboard immediately.

**Docker:**

```bash
docker compose exec nutritrack python3 seed.py
```

**Direct install:**

```bash
python3 seed.py
```

## Connect Your AI Agent

NutriTrack exposes a full REST API that any LLM-based agent can call. Point your agent at `http://localhost:8000` and give it instructions like:

> You are a nutrition tracking assistant. When the user tells you what they ate, log it by calling POST /api/food with the meal name, estimated calories, protein, carbs, fat, and meal type. When they ask for a summary, call GET /api/daily-summary. Use the NutriTrack API at http://localhost:8000.

For detailed agent setup instructions, prompt templates, and endpoint examples, see [docs/AGENT_README.md](docs/AGENT_README.md).

## API Reference

All endpoints are served under `http://localhost:8000`. Interactive Swagger documentation is available at `/docs`.

### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get the current user profile |
| PUT | `/api/profile` | Create or update the user profile |

### Food

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/food` | Log a food entry |
| GET | `/api/food` | Get food entries for a date (default: today) |
| GET | `/api/food/range` | Get food entries for a date range |
| GET | `/api/food/search` | Search past food entries by name |
| PUT | `/api/food/{id}` | Update a food entry |
| DELETE | `/api/food/{id}` | Delete a food entry |

### Weight

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/weight` | Log a weight measurement |
| GET | `/api/weight` | Get weight history |

### Activity

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/activity` | Log an exercise activity |
| GET | `/api/activity` | Get activities for a date (default: today) |
| GET | `/api/activity/range` | Get activities for a date range |
| PUT | `/api/activity/{id}` | Update an activity entry |
| DELETE | `/api/activity/{id}` | Delete an activity entry |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/health` | Log a health measurement |
| GET | `/api/health` | Get health measurement history |
| PUT | `/api/health/{id}` | Update a health measurement |
| DELETE | `/api/health/{id}` | Delete a health measurement |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/daily-summary` | Get full daily summary with goals and intake |
| GET | `/api/weekly-report` | Get a 7-day aggregated report |
| GET | `/api/history/daily-totals` | Get daily calorie/macro totals for charting |

### Gamification

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gamification` | Get current streak, XP, and elite status |

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/csv` | Export food, weight, activity, or health data as CSV |

### Seed

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/seed-demo-data` | Populate the database with 30 days of demo data |

## Configuration

NutriTrack is configured through environment variables. For Docker deployments, set these in a `.env` file or in your `docker-compose.yml`. For direct installs, export them before running the server.

| Variable | Default | Description |
|----------|---------|-------------|
| `NUTRITRACK_DB_PATH` | `nutritrack.db` | Path to the SQLite database file |
| `NUTRITRACK_HOST` | `0.0.0.0` | Server bind address |
| `NUTRITRACK_PORT` | `8000` | Server port |
| `NUTRITRACK_CORS_ORIGINS` | `*` | CORS allowed origins (comma-separated or `*` for all) |
| `SEED_DEMO_DATA` | `false` | Auto-seed demo data on first startup when the database is empty |
| `TZ` | `UTC` | Timezone for the container |

## Architecture

```
User <---> AI Agent <---> NutriTrack Server (FastAPI) <---> SQLite
                                  |
                           Web Dashboard
```

The user interacts with an AI agent in natural language. The agent translates those conversations into HTTP API calls to the NutriTrack FastAPI server. The server persists all data in a local SQLite database. The web dashboard reads from the same API endpoints to render charts and summaries in the browser.

## Tech Stack

- **FastAPI** -- async Python web framework serving the REST API and Swagger docs
- **SQLite** -- embedded database with WAL mode for concurrent reads
- **Vanilla JS** -- zero-dependency frontend, no build step required
- **Chart.js** -- interactive charts for calories, macros, weight trends, and health vitals

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
