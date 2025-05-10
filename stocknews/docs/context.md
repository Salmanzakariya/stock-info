
# 📈 Indian Stock Market News App - Developer Guide

## 1. Tech Stack

| Component         | Technology                                  |
| ----------------- | ------------------------------------------- |
| **Frontend**      | HTML/CSS + JavaScript + Django Templates    |
| **Backend**       | Django + Django REST Framework + PostgreSQL |
| **UI Framework**  | Tailwind CSS (or Bootstrap)                 |
| **AI Processing** | DeepSeek for Sentiment + Summary            |

---

## 2. App Overview

This web app delivers live, India-specific stock market news to retail investors. News is enriched with AI-generated sentiment tags and summaries, helping users identify trends, hot stocks, and market direction.

---

## 3. User Flow

### 🔵 Welcome & Auth

* On first visit, user sees a clean welcome screen.
* User can **Sign Up / Log In** using email/password (via Django Auth).

### 🟢 Main Dashboard (News Feed)

* After login, user lands on the **News Dashboard**.
* This screen shows a **list of news articles** with:

  * Title
  * Short summary (AI-generated)
  * Source and timestamp
  * Tags: company symbols (e.g., INFY, RELIANCE), sectors (e.g., IT, Pharma)
  * AI Sentiment: 👍 Positive | ⚠️ Neutral | 👎 Negative

### 🟡 Stock Highlights Section (Trending Panel)

* Highlights most-mentioned stocks from today's news
* Tagged with AI-inferred labels: `Bullish`, `Volatile`, `Bearish`
* Each item links to a detailed view with historical charts and related news

### 🔍 Search & Filter

* Users can search by:

  * Company name (e.g., TCS)
  * Sector (e.g., Banking)
  * Sentiment (Positive/Negative)
* Results shown in real-time from Django DB/API

### 🔔 Daily Digest (Optional Notifications)

* App emails daily summaries each evening:

  * Top 5 market headlines
  * Top gainers/losers
  * Sentiment heatmap

---

## 4. Features by Module

### 📰 News Aggregation

* Fetched from curated Indian business news sources (e.g., Moneycontrol, LiveMint)
* Stored in PostgreSQL via Django models with fields:

  * title, link, summary, timestamp
  * sentiment (string), tags (list)

### 🧠 AI Sentiment & Summary

* Use DeepSeek API to:

  * Summarize long news articles
  * Detect sentiment from headlines/body

### 📊 Trending Stock Detection

* Run daily cron job (via `manage.py` command or Celery + Redis)
* Count company mentions in latest articles
* Rank and label top 10 mentioned stocks

### 📱 Focused UI with Tailwind

* Clean, card-based layout for each news item
* Sections: `News` | `Trending` | `Search`
* Support for light and dark mode with Django context toggle

---

## 5. Developer Notes

* Django models:

  * `Article`: stores news data
  * `Company`: optional metadata on listed companies
  * `User`: default Django auth model

* All frontend templates use Django's template engine

* DeepSeek API is triggered after news is scraped

* Sentiment + summary saved directly to database

---

## 6. Future Enhancements

* Push notification system (via Django Channels or email)
* Watchlist with personalized stock feeds
* Add REST API for potential mobile app or React frontend in future

---

> This document should help your developer get a clear understanding of the architecture, flow, and responsibilities of each module. Let me know if you'd like a visual flowchart or wireframe added next!