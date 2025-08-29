# Scientist Scraper Agent

A Portia agent that scrapes Wikipedia pages of famous scientists and extracts their profiles and publications.

## Purpose

This agent automatically:
- Retrieves Wikipedia pages for famous scientists
- Extracts text content from the HTML
- Identifies and extracts publication sections when available
- Uses LLM analysis to create structured scientist profiles
- Outputs formatted scientist information including name, birth/death dates, nationality, and notable achievements

## How to Run

```bash
uv sync
uv run main.py
```

