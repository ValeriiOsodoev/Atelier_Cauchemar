# Use official Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Ensure data directory exists (shared volume)
RUN mkdir -p /shared && chmod 777 /shared
VOLUME /shared

# Run the bot
CMD ["python", "-m", "atelier_bot.main"]
