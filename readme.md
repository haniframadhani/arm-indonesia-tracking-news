```
# Indonesian News Monitoring – Python System Setup & Workflow

## Goal
- Monitor Indonesian news daily.  
- Detect articles about semiconductor, ARM, engineers, training, job postings, and numbers like "15000".  
- Summarize matched articles using Gemini API.  
- Save each match to separate file with URL, source, timestamp.  
- Skip already processed articles across runs.

---

## Environment Setup

1. Install Python 3.10+ on your machine.  
2. Navigate to project folder: `cd /path/to/project`
3. Create virtual environment:  `python -m venv venv`
4. Activate virtual environment:  
 - Windows: `venv\Scripts\activate`  
 - Mac/Linux: `source venv/bin/activate`
5. Install required packages:  `pip install requests beautifulsoup4 lxml`
6. Generate `requirements.txt` for portability: `pip freeze > requirements.txt`
7. On another machine: create virtual environment, activate it, then:  
`pip install -r requirements.txt`

---

## Folder Structure
project_folder/
│
├─ venv/ # Python virtual environment
├─ seen_urls.json # tracks processed URLs
├─ summaries/ # matched article summaries
│ ├─ national/
│ └─ regional/
├─ requirements.txt
├─ main_monitor.py # main monitoring script
└─ README.md

---

## Daily Workflow

1. Activate virtual environment.  
2. Run `main_monitor.py` manually (once per day).  
3. Script actions:  
   - Request latest Indonesian news from NewsAPI (max 30/day).  
   - For each article:  
     - Skip if URL already in `seen_urls.json`.  
     - Fetch full article content.  
     - Clean HTML (remove scripts, footer, navigation, ads).  
     - Search for keywords with regex.  
     - If matched:  
       - Summarize with Gemini API.  
       - Save summary + URL + source + timestamp in `summaries/national/` or `summaries/regional/`.  
       - Add URL to `seen_urls.json`.  
   - Add small delay (2–3 seconds) between requests for politeness.

---

## Advantages
- Only process new articles (persistent history).  
- Clean, readable summaries via AI.  
- Safe for daily manual runs.  
- Portable across machines using virtual environment + `requirements.txt`.  
- Organized file structure for long-term monitoring.

---

## Notes
- Focus AI summarization on: semiconductor training, engineer counts, registration info, ARM mentions.  
- Optional: truncate very long articles to first 5–10 paragraphs for faster processing.  
- Optional automation: cron (Linux/Mac) or Task Scheduler (Windows) in future. 
```