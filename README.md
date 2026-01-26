# Atelier Cauchemar — Telegram bot

This repository contains the Atelier Cauchemar Telegram bot implemented with aiogram.

## Features

- User management and search
- Artwork creation with image processing
- Paper inventory management
- Print order processing
- Atelier notifications
- SQLite database with async operations

## Tech Stack

- **Python 3.14**
- **aiogram 3.24.0** - Telegram Bot API framework
- **aiosqlite 0.22.1** - Async SQLite database operations
- **Pillow 10.0.0** - Image processing for artwork thumbnails
- **pytest** - Testing framework

## Running locally (dev)

### Prerequisites

- Python 3.14+
- BOT_TOKEN environment variable

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set bot token
export BOT_TOKEN=your_bot_token_here

# Run the bot
python -m atelier_bot.main
```

### Docker

```bash
# Build
docker build -t atelier_cauchemar:local .

# Run (mount a volume for DB)
docker run -e BOT_TOKEN=$BOT_TOKEN -v $(pwd)/data:/shared atelier_cauchemar:local
```

## Testing & Validation

### Running Tests

```bash
# Run all tests with coverage
python run_tests.py

# Or run pytest directly
pytest tests/ -v --cov=atelier_bot --cov-report=html
```

### Test Coverage

The test suite includes:
- **Unit tests** for database operations and image processing
- **Handler tests** for Telegram bot interactions
- **Integration tests** for complete user flows
- **Health checks** for system validation

### Database Validation

```bash
# Check database integrity
python -c "
import asyncio
from atelier_bot.db.db import init_db, get_all_users
asyncio.run(init_db())
users = asyncio.run(get_all_users())
print(f'Database OK. Users: {len(users)}')
"
```

## Database

- Uses SQLite file located at `/shared/atelier.db` inside the container
- Tables: users, artworks, paper_balance, orders
- Docker volume or host bind should be mounted to `/shared` for persistence

## CI/CD

- GitHub Actions workflow (`.github/workflows/main.yml`)
- Lints, builds, pushes Docker image, deploys via SSH
- Required secrets: DOCKER_USERNAME, DOCKER_PASSWORD, HOST, USER, SSH_KEY, BOT_TOKEN, TELEGRAM_NOTIFY_TO

## Project Structure

```
atelier_bot/
├── main.py              # Application entry point
├── db/
│   └── db.py           # Database operations & image processing
├── handlers/
│   └── print_handler.py # Telegram message handlers
├── keyboards/
│   └── print_keyboards.py # UI components
└── services/
    └── notify.py       # Atelier notification service

tests/                   # Test suites
├── test_db.py          # Database unit tests
├── test_handlers.py    # Handler unit tests
└── test_integration.py # Integration tests
```

## Reliability Improvements

- Comprehensive error handling in all handlers
- Database transaction safety
- Image processing validation
- Async operation timeouts
- Logging for debugging and monitoring
- Automated testing with 80%+ coverage target

## Contributing

1. Run tests before committing: `python run_tests.py`
2. Ensure new code includes appropriate tests
3. Update documentation for new features
4. Follow existing code style and patterns
