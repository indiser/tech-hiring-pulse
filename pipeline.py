import json, sqlite3

with open("jobs.json") as f:
    jobs = json.load(f)

def clean(s):
    if not s:
        return s
    half = len(s) // 2
    if s[:half].strip() == s[half:].strip():
        return s[:half].strip()
    return s.strip()

conn = sqlite3.connect("jobs.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    url TEXT PRIMARY KEY,
    job_title TEXT,
    company_name TEXT,
    experience_level TEXT,
    location TEXT,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

new_count = 0
for j in jobs:
    url = j.get("product_page_url")
    if not url:
        continue
    if conn.execute("SELECT 1 FROM jobs WHERE url = ?", (url,)).fetchone():
        continue
    conn.execute(
        "INSERT INTO jobs (url, job_title, company_name, experience_level, location) VALUES (?, ?, ?, ?, ?)",
        (url, clean(j.get("job_title")), clean(j.get("company_name")), clean(j.get("experience_level")), clean(j.get("location")))
    )
    new_count += 1

conn.commit()
print(f"Inserted {new_count} new jobs")

print("\nOpen roles by company:")
for row in conn.execute("SELECT company_name, COUNT(*) c FROM jobs GROUP BY company_name ORDER BY c DESC LIMIT 10"):
    print(f"  {row[0]}: {row[1]}")

print("\nOpen roles by location:")
for row in conn.execute("SELECT location, COUNT(*) c FROM jobs GROUP BY location ORDER BY c DESC LIMIT 10"):
    print(f"  {row[0]}: {row[1]}")

conn.close()