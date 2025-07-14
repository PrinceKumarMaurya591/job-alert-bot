import os
import smtplib
import requests
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from dotenv import load_dotenv
 
load_dotenv()
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")
 
JOB_SITES = [
    ("Indeed – Full Stack",     "https://www.indeed.com/jobs?q=Full+Stack+Software+Engineer&limit=5"),
    ("Indeed – Java Backend",   "https://www.indeed.com/jobs?q=Java+Backend+Developer&limit=5"),
    ("LinkedIn – Full Stack",   "https://www.linkedin.com/jobs/search/?keywords=Full%20Stack%20Engineer&location=India"),
    ("LinkedIn – Java Backend", "https://www.linkedin.com/jobs/search/?keywords=Java%20Backend%20Developer&location=India"),
    ("Naukri – Full Stack",     "https://www.naukri.com/fullstack-engineer-jobs"),
    ("Naukri – Java Backend",   "https://www.naukri.com/java-backend-developer-jobs"),
    ("Glassdoor – Full Stack",  "https://www.glassdoor.co.in/Job/full-stack-developer-jobs-SRCH_IL.0,2_IN69_KO3,24.htm"),
    ("Instahyre – Software Eng","https://www.instahyre.com/?q=software+engineer"),  # public search page
]
 
HEADERS = {"User-Agent": "Mozilla/5.0"}
 
def fetch_jobs(title, url):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    if "indeed.com" in url:
        sel = soup.select("div.job_seen_beacon")
        for div in sel[:5]:
            a = div.find("a")
            if a and a.get("href"):
                link = "https://www.indeed.com" + a["href"]
                jobs.append(f"- [{title}] {a.get_text(strip=True)}: {link}")
    elif "linkedin.com" in url:
        sel = soup.select("a.base-card__full-link")
        for a in sel[:5]:
            jobs.append(f"- [{title}] {a.get_text(strip=True)}: {a['href']}")
    elif "naukri.com" in url:
        sel = soup.select("a.title")
        for a in sel[:5]:
            jobs.append(f"- [{title}] {a.get_text(strip=True)}: {a['href']}")
    elif "glassdoor.co.in" in url:
        sel = soup.select("a.jobLink")
        for a in sel[:5]:
            link = "https://www.glassdoor.co.in" + a["href"]
            jobs.append(f"- [{title}] {a.get_text(strip=True)}: {link}")
    elif "instahyre.com" in url:
        sel = soup.select("div._3WaOx")
        for div in sel[:5]:
            a = div.find("a", href=True)
            if a:
                jobs.append(f"- [{title}] {a.get_text(strip=True)}: {a['href']}")
    return jobs
 
def main():
    all_jobs = []
    for title, url in JOB_SITES:
        try:
            all_jobs.extend(fetch_jobs(title, url))
        except Exception as e:
            all_jobs.append(f"- [{title}] ⚠️ Error: {e}")
 
    body = ("Here are today’s job listings:\n\n" + "\n".join(all_jobs)) if all_jobs else "No jobs found."
    msg = MIMEText(body)
    msg["Subject"] = "Daily Job Alerts"
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL
 
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)
 
    print("✅ Email sent!")
 
if __name__ == "__main__":
    main()

