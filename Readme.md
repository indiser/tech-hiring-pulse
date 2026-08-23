# 🔍 Tech Hiring Pulse

> A self-healing job scraper that tracks live tech roles on Instahyre and turns them into a queryable dataset — built with Bright Data Scraper Studio + Python + SQLite.

---

## What It Does

- Scrapes live job listings from [Instahyre](https://www.instahyre.com/search) using an AI-generated extractor (no hand-written selectors)
- Cleans and deduplicates raw JSON output
- Loads structured data into a local SQLite database
- Reports top hiring companies and hottest locations instantly
- **Self-heals** broken extraction logic with a single CLI command — no code rewrite needed

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| Node.js + npm | Run the Bright Data CLI via `npx` |
| Python 3 | Run the data pipeline |
| [Bright Data account](https://brightdata.com) | Scraper Studio access (use promo code `wemakedevs` for free credits) |

---

## Setup & Usage

### 1. Authenticate the CLI

```bash
npx -p @brightdata/cli bdata login
```

Opens a browser for OAuth. On success, auto-creates the `cli_unlocker` and `cli_browser` zones needed for scraping.

> To install permanently: `npm install -g @brightdata/cli`, then use `bdata ...` directly.

---

### 2. Create the Scraper (one prompt, no code)

```bash
bdata scraper create https://www.instahyre.com/search \
  "job title, company name, salary range, experience level, location, posted date"
```

Bright Data's AI reads the live page and builds extraction logic from your plain-language field list. Takes ~5–25 minutes.

You'll get back a Collector ID:
```
Collector ID: c_mt5evkhh7xjyn2fi0
```

---

### 3. Run the Scraper

```bash
bdata scraper run c_mt5evkhh7xjyn2fi0 https://www.instahyre.com/search --pretty > jobs.json
```

Returns structured JSON, one object per listing:

```json
{
  "job_title": "Senior Software Engineer",
  "company_name": "Toast",
  "experience_level": "5-8 Years",
  "location": "Bangalore",
  "product_page_url": "https://www.instahyre.com/job-422225-..."
}
```

> Note: Some text fields come duplicated (e.g. `"Bangalore Bangalore"`) due to how the site renders DOM. The pipeline handles this automatically.

---

### 4. Run the Pipeline

```bash
python pipeline.py
```

This will:
- Load `jobs.json`
- Clean duplicated text fields
- Insert new rows into `jobs.db` (SQLite), deduplicated by URL
- Print a summary report

Sample output:
```
Inserted 200 new jobs

Open roles by company:
  Infosys: 6
  Deutsche Telekom Digital Labs: 6
  Toast: 5
  Arcana: 5
  Nielsen: 4

Open roles by location:
  Bangalore: 104
  Gurgaon: 21
  Work From Home: 20
  Hyderabad: 9
  Mumbai: 5
```

The pipeline is safe to re-run (e.g. on a cron schedule) — it only inserts new jobs, building a time series of hiring activity over time.

---

### 5. Self-Heal Demo

This is the core feature — the scraper survives real-world site changes without a rewrite.

1. Open the scraper config: `https://brightdata.com/cp/scrapers/c_mt5evkhh7xjyn2fi0`
2. Deliberately break a field's extraction rule (e.g. point `job_title` at a wrong selector). Save.
3. Confirm the field returns empty:
   ```bash
   bdata scraper run c_mt5evkhh7xjyn2fi0 https://www.instahyre.com/search --pretty
   ```
4. Heal it with a plain-language description:
   ```bash
   bdata scraper heal c_mt5evkhh7xjyn2fi0 "job_title field returning empty, extraction broke"
   ```
5. Re-run and confirm the field is populated again.
6. Re-run `python pipeline.py` — new data flows into the same `jobs.db`, zero schema changes needed.

---

## Project Structure

```
.
├── pipeline.py        # Cleans JSON → loads into SQLite → prints report
├── jobs.json          # Raw scraper output (regenerated each run)
├── jobs.db            # SQLite database (accumulates over time)
├── instructions.md    # Detailed build log and notes
└── README.md
```

---

## Notes

- **Salary range** comes back empty for all rows — Instahyre hides salary behind a login wall on the public search page. This is expected, not a scraper bug.
- **Government domains** (e.g. `eprocure.gov.in`) are blocked by Bright Data's platform (returns `400 Domain not allowed`).
- The Collector ID `c_mt5evkhh7xjyn2fi0` is specific to this project's scraper instance.

---

## Submission

- Demo video: create → run → break → heal → run → pipeline re-run
- Submit at: https://forms.gle/iQf2SjHQViSJaRAv7
