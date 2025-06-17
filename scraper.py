import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
}

def scrape_dgr():
    print("🔍 Scraping DGR website...")
    base_url = "https://dgrindia.gov.in"
    jobs = []
    try:
        url = f"{base_url}/latest-jobs"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        notices = soup.select(".notice-list a") or soup.select("a[href*='job']")
        for notice in notices[:10]:
            title = notice.get_text(strip=True)
            if not title:
                continue
            link = urljoin(base_url, notice['href'])
            jobs.append({
                "title": title,
                "company": "Government of India",
                "location": "Multiple Locations",
                "link": link,
                "source": "DGR",
                "posted": "N/A",
                "scraped_at": datetime.now().isoformat(),
                "is_official": True
            })
        print(f"✅ DGR scraped {len(jobs)} jobs")
    except Exception as e:
        print("❌ DGR error:", str(e))
    return jobs

def scrape_awpo():
    print("🔍 Scraping AWPO...")
    base_url = "http://www.exarmynaukri.com"
    jobs = []
    try:
        url = f"{base_url}/latest-job-openings"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.job-list tr")[1:]
        for row in rows[:10]:
            cols = row.select("td")
            if len(cols) < 3:
                continue
            title = cols[0].get_text(strip=True)
            company = cols[1].get_text(strip=True) or "N/A"
            location = cols[2].get_text(strip=True) or "Multiple Locations"
            link = urljoin(base_url, cols[0].find("a")["href"]) if cols[0].find("a") else "#"
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "source": "AWPO",
                "posted": "N/A",
                "scraped_at": datetime.now().isoformat(),
                "is_official": True
            })
        print(f"✅ AWPO scraped {len(jobs)} jobs")
    except Exception as e:
        print("❌ AWPO error:", str(e))
    return jobs

def scrape_mygov():
    print("🔍 Scraping MyGov for veterans...")
    base_url = "https://www.mygov.in"
    jobs = []
    try:
        url = f"{base_url}/job/?search_keyword=veteran"
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        cards = soup.select(".job-listing-block")
        for card in cards[:10]:
            title = card.select_one(".job-title")
            org = card.select_one(".job-org")
            location = card.select_one(".job-location")
            posted = card.select_one(".job-posted")
            link = card.select_one("a.view-details")
            if not title:
                continue
            jobs.append({
                "title": title.get_text(strip=True),
                "company": org.get_text(strip=True) if org else "Government Organization",
                "location": location.get_text(strip=True) if location else "Multiple Locations",
                "link": urljoin(base_url, link['href']) if link else "#",
                "source": "MyGov",
                "posted": posted.get_text(strip=True) if posted else "N/A",
                "scraped_at": datetime.now().isoformat(),
                "is_official": True
            })
        print(f"✅ MyGov scraped {len(jobs)} jobs")
    except Exception as e:
        print("❌ MyGov error:", str(e))
    return jobs

def scrape_state_boards():
    print("🔍 Scraping Karnataka Sainik Welfare Board...")
    jobs = []
    try:
        url = "https://sainikwelfare.karnataka.gov.in/english"
        res = requests.get(url, headers=HEADERS, timeout=8)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        notices = soup.select(".notice-list a") or soup.select("a[href*='notification']")
        for notice in notices[:5]:
            title = notice.get_text(strip=True)
            # Commented strict filters for testing
            # if "job" not in title.lower() and "recruitment" not in title.lower():
            #     continue
            jobs.append({
                "title": title,
                "company": "Karnataka Sainik Welfare Board",
                "location": "Karnataka",
                "link": urljoin(url, notice['href']),
                "source": "Karnataka SWB",
                "posted": "N/A",
                "scraped_at": datetime.now().isoformat(),
                "is_official": True
            })
        print(f"✅ Karnataka SWB scraped {len(jobs)} jobs")
    except Exception as e:
        print("❌ Karnataka SWB error:", str(e))
    return jobs

def scrape_all_jobs():
    print("🚀 Scraping only official veteran job sources...")
    jobs = []
    jobs.extend(scrape_dgr())
    jobs.extend(scrape_awpo())
    jobs.extend(scrape_mygov())
    jobs.extend(scrape_state_boards())

    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = (job['title'].lower(), job['company'].lower(), job['source'])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    print("📝 All scraped jobs:")
    for job in jobs:
        print("-", job["title"], "from", job["source"])
    print("🔍 Deduplicated down to", len(unique_jobs))

    return unique_jobs

def save_jobs(jobs, filename="jobs.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

def load_jobs(filename="jobs.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
