# Fraud Detection API

> Real-time credit card transaction fraud detection combining association rule mining with a rule-based inference engine — deployed as a REST API.

---

## Overview

This project detects fraudulent credit card transactions using a **two-stage approach**:

1. **Offline ML stage** — Association rule mining and decision tree analysis on a labeled fraud dataset to extract interpretable fraud patterns
2. **Online inference stage** — FastAPI server applies the extracted rules in real-time against incoming transactions

The result is a lightweight, interpretable fraud detection system that can explain *why* a transaction is flagged — a key requirement in regulated financial environments.

---

## Architecture

```
Labeled Transaction Dataset
        │
        ▼
┌─────────────────────────┐
│   Offline ML Pipeline   │
│  (MLproject.ipynb)      │
│                         │
│  • Feature engineering  │
│  • Association rules    │
│  • Decision tree        │
│  • Rule extraction      │
└──────────┬──────────────┘
           │ rules_simple.csv (200+ rules)
           ▼
┌─────────────────────────┐
│   FastAPI Inference      │
│   Server                │
│                         │
│  POST /detect/          │
│  • Normalize input      │
│  • Geo-IP enrichment    │
│  • Rule pattern match   │
│  • Return fraud verdict │
└─────────────────────────┘
```

---

## Features

- **Interpretable predictions** — every fraud verdict traces to a specific mined rule
- **Real-time inference** — sub-millisecond rule matching
- **Geo-IP enrichment** — transaction location automatically enriched via IP lookup
- **Multi-dimensional rules** — patterns across age, distance, amount, category, time-of-day, population density
- **Partial rule matching** — rules act as wildcards; a rule fires when ALL non-null fields match

---

## Technical Details

### Input Features

| Feature | Type | Bucketing |
|---|---|---|
| `distance` | int (km) | nearby / moderate / far |
| `age` | int | young (<40) / middle (40-56) / old (≥56) |
| `gender` | str | male / female |
| `category` | str | grocery / shopping / travel / etc. |
| `amount` | int | low / mid / high (log-scaled thresholds) |
| `population` | int | sparsely / moderately / highly populated |
| `transaction_time` | auto (server clock) | forenoon / afternoon / evening |

### Rule Mining (Offline)

The ML notebook (`MLproject.ipynb`) performs:
- Feature discretization and encoding
- Association rule mining (support/confidence/lift thresholds)
- Decision tree extraction for high-confidence fraud patterns
- Rule deduplication and simplification (`reduce.ipynb`)

Output: `rules_simple.csv` — 200+ partial-match fraud rules

### API Endpoint

```http
POST /detect/
Content-Type: application/json

{
  "distance": 120,
  "age": 35,
  "gender": "female",
  "category": "grocery",
  "amount": 450,
  "population": 3
}
```

Response:
```json
{
  "fraud": true,
  "matched_rule": {"distance": "far", "category": "grocery", "gender": "female"}
}
```

---

## Stack

- **Python 3.x** + **FastAPI** + **Uvicorn**
- **pandas** for rule CSV loading and matching
- **scikit-learn** for offline ML (decision tree, preprocessing)
- **ipinfo.io** API for geo-IP enrichment
- **Jupyter Notebook** for offline training pipeline

---

## Run Locally

```bash
pip install fastapi uvicorn pandas requests python-dotenv
uvicorn main:app --reload --port 8000
```

---

## Research Context

This project demonstrates the practical value of **interpretable ML for security applications** — a core requirement in fraud detection, intrusion detection, and regulatory compliance. The association rule approach allows auditors to verify every decision, unlike black-box neural networks.

This work informed the author's Master's research on ML-based intrusion detection systems for IoMT environments.
