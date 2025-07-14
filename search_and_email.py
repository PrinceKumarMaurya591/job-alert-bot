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
    ("Full Stack Software Engineer", "https://www.indeed.com/jobs?q=Full+Stack+Software+Engineer&limit=10"),
    ("Java Backend Developer",    "https://www.indeed.com/jobs?q=Java+Backend+Developer&limit=10"),
]
 
def fetch_jobs(title, url):
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")
    jobs = []
    for div in soup.select("div.job_seen_beacon")[:5]:
        a = div.find("a")
        if a and 'href' in a.attrs:
            link = "https://www.indeed.com" + a["href"]
            jobs.append(f"- [{title}] {div.get_text(strip=True)}: {link}")
    return jobs
 
def main():
    all_jobs = []
    for title, url in JOB_SITES:
        jobs = fetch_jobs(title, url)
        all_jobs.extend(jobs)
 
    if not all_jobs:
        body = "No new job listings found today."
    else:
        body = "Here are today’s job listings:\n\n" + "\n".join(all_jobs)
 
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
 