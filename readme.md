# LoL Multi-Account Manager

Backend CLI application built with Python 3 that allows registering multiple League of Legends accounts and retrieving both individual and consolidated statistics using the Riot Games API.

This project was developed as a backend learning exercise, focusing on clean structure, modular design, and clarity over overengineering.

---

## Project Goals

- Practice backend fundamentals with Python
- Consume a real external API (Riot Games API)
- Structure a multi-module project
- Compute aggregated statistics
- Build a complete MVP in 20–40 hours

---

## Features (MVP v1.0)

### Account Management

- Register accounts using:
  - `summoner_name`
  - `tag_line`
  - `region`
- List registered accounts
- Persistent storage using JSON

### Individual Account Summary

For each account:

- Summoner level
- SoloQ rank:
  - Tier
  - Rank
  - LP
  - Wins / Losses
  - Winrate
- Top 3 most played champions
- Last 5 matches overview

### Master Account (Multi-Account Summary)

Aggregated statistics across all registered accounts:

- Average winrate
- Average KDA
- Average CS per minute
- Most played role
- Internal ranking by winrate

---

## Architecture Overview

The project follows a modular structure:

- `riot_client.py` → Handles communication with Riot API
- `accounts.py` → Account registration and persistence
- `metrics.py` → Individual account metrics calculation
- `master_summary.py` → Aggregated multi-account metrics
- `data/accounts.json` → Persistent account storage
- CLI entry point → User interaction

Design principles:

- Clear separation of concerns
- No unnecessary abstractions
- No external libraries beyond standard Python
- No async or advanced patterns (intentionally kept simple)

---

## Not Included (Intentionally)

This is an MVP. The following improvements were intentionally left for future learning:

- API response caching (TTL)
- Full-season match aggregation
- Rate-limit optimization strategies
- Authentication layer
- Web interface
- Database integration

---

## Requirements

- Python 3.10+
- Riot Games API Key

Set your API key as an environment variable:

```bash
export RIOT_API_KEY=your_key_here

Or configure it directly in the project (not recommended for production).

Running the Project
python main.py

Follow the CLI prompts to:

Register accounts

View individual summaries

View consolidated statistics

What I Learned

How to structure a backend project from scratch

How to consume and handle real-world APIs

Error handling for HTTP status codes

Aggregating and transforming external data

Designing and closing an MVP intentionally

Version

v1.0 — Stable MVP

Future improvements may include caching and extended season statistics.

License

Personal learning project.