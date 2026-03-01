# Indonesian Semiconductor News Monitoring System

An automated Python script that daily monitors Indonesian news websites via NewsAPI, filtering out specific articles related to the semiconductor industry, engineer training, and the 15,000 engineer initiative. High-matching articles are passed through Google's Gemini API to create concise, human-readable summaries that are categorized by region and saved as Markdown files.

## Features

- **Automated Scraping:** Uses the external `newsapi.org` service to fetch breaking Indonesian news across targeted keyword domains.
- **Smart Filtering:** Extracts full HTML bodies and applies robust Regex checks for precise match verification (to reduce API hallucination and API usage costs on non-relevant articles).
- **AI Summarization:** Leverages the gemini models to convert long news texts into structured summary documents with specialized "Final Verdicts" for quick reading.
- **Deduplication:** Maintains a list of `seen_urls.json` to ensure the script only processes net-new articles across multiple run dates.
- **Rate-Limit Safe:** Automatically spaces out API requests and implements exponential backoff/retry sequences on 429 Too Many Request exceptions.
- **Clean Architecture:** Uses Python virtual environments (`venv`) and `.env` variables to completely segregate secrets and dependencies from global environments.

---

## Prerequisites

Before starting, ensure you have the following installed on your machine:

- **Python 3.10+**
- **Git** (optional, for cloning)
- Valid API keys for both:
  - [NewsAPI](https://newsapi.org/)
  - [Google Gemini API](https://aistudio.google.com/app/apikey)

---

## 🛠️ Environment Setup & Installation

### 1. Clone & Setup Folder

If you haven't already, clone or navigate into your project folder:

```bash
git clone https://github.com/haniframadhani/arm-indonesia-tracking-news.git
cd arm-indonesia-tracking-news
```

### 2. Python Virtual Environment

Keep dependencies isolated by creating a virtual environment:

```bash
# Create it
python -m venv venv

# Activate it (Mac / Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

### 3. Install Requirements

With the virtual environment active, install the necessary Python packages:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment template into your live `.env` file:

```bash
cp .env.example .env
```

Open `.env` in any text editor and paste your authentication keys into the provided strings:

```env
NEWSAPI_KEY="your_real_newsapi_key_here"
GEMINI_API_KEY="your_real_gemini_key_here"
```

---

## 🚀 Daily Workflow & Execution

**1. Activate the environment (if not already active):**

```bash
source venv/bin/activate
```

**2. Run the monitor script:**

```bash
python main.py
```

### What Happens When You Run the Script?

1. It reads your `.env` to authenticate.
2. It cycles through 8 smaller targeted queries against NewsAPI (fetching up to ~240 articles max), automatically avoiding 400 Bad Request URL limit errors.
3. It extracts the raw URL texts, stripping out ads, scripts, and footers.
4. It checks against the regex filters (`semikonduktor`, `pendaftaran`, `15 ribu`, etc.).
5. If an article matches, it sends the full body to Gemini.
6. The resulting summary incorporates a **Final Verdict**, indicating registration rules and Indonesian-ARM deal specifics.
7. The output is placed inside `/summaries/national` or `/summaries/regional` with a clean timestamped filename.
8. The processed URL is added to `seen_urls.json` so it will be permanently ignored on the next run.

---

## 📂 Project Structure

```text
arm-indonesia-tracking-news/
├── .env                  # (Hidden) Your API keys
├── .env.example          # Template for .env
├── .gitignore            # Git exclusions (pycache, env vars, etc.)
├── main.py               # Core scraping/AI logic
├── requirements.txt      # Python dependencies bundle
├── seen_urls.json        # Persistent JSON tracker file
└── summaries/            # Generated Markdown outputs
    ├── national/         # Nationwide news
    └── regional/         # Region-locked domains (e.g. jogja, jabar)
```

---

## ⏳ Future Capabilities

- **Automation:** Add the script to a Linux `cron` job or Windows Task Scheduler to automate it to run everyday at 12:00 AM completely hands-free.
- **Prompt Customization:** Readjust the `summarize_with_gemini()` prompt body at any time if target goals change.
