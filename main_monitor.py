import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import google.generativeai as genai
from urllib.parse import urlparse
from dotenv import load_dotenv

# ==========================================
# Configuration
# ==========================================
load_dotenv()
# Get API keys from environment variables
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Constants
SEEN_URLS_FILE = "seen_urls.json"
SUMMARIES_DIR = "summaries"
NATIONAL_DIR = os.path.join(SUMMARIES_DIR, "national")
REGIONAL_DIR = os.path.join(SUMMARIES_DIR, "regional")

# Filter configuration
# Regex keywords updated to reflect the CNBC article phrasing: 15 ribu (15000), pelatihan, semikonduktor, engineer, arm, chip, danantara
# KEYWORDS_REGEX = re.compile(
#     r'\b(semikonduktor|chip|arm|training|pelatihan|engineer|insinyur|pendaftaran|lowongan|posisi|15000|15 ribu|danantara)\b',
#     re.IGNORECASE
# )
KEYWORDS_REGEX = re.compile(
    r'\b(semikonduktor|chip|arm|training|pelatihan|engineer|insinyur|pendaftaran|registrasi|daftar|lowongan|posisi|15000|15\s*ribu|danantara|chip\s*design|desain\s*chip|beasiswa|rekrutmen|seleksi|teknologi|investasi|kerja\s*sama|kemitraan|inggris|london|prabowo|airlangga|rosan|hilirisasi|sdm|talenta|digital|inovasi|startup|industri|elektronik|manufaktur|pabrik|riset|penelitian|universitas|kampus|mahasiswa|sarjana|vokasi|politeknik|stem|sains|coding|programming|software|hardware|iot|ai|kecerdasan\s*buatan|data\s*center|pusat\s*data|cloud|komputasi|robotik|otomasi|otomotif|kendaraan|electric|baterai|energi|infrastruktur|ekosistem|sovereign|wealth|fund|bumn|swasta|asing|ekspor|impor|perdagangan|bilateral|mou|perjanjian|kontrak|kerja\s*sama|kolaborasi|program|beasiswa|asiswa|lulusan|fresh\s*graduate|magang|internship)\b',
    re.IGNORECASE
)

# NewsAPI query targeting specific exact phrases and broad related keywords
# NEWSAPI_QUERY = '"pendaftaran pelatihan semikonduktor" OR "pendaftaran training semikonduktor" OR ("15 ribu" AND engineer) OR ("15000" AND engineer) OR (pelatihan AND semikonduktor) OR (Arm AND semikonduktor)'
# NEWSAPI_QUERY = "semikonduktor OR ARM OR training OR pelatihan OR engineer OR insinyur OR pendaftaran OR lowongan OR posisi OR 15000"
# Split into multiple shorter queries to avoid NewsAPI 400 error (query too long)
NEWSAPI_QUERIES = [
    '(Danantara AND Arm) OR (Danantara AND semikonduktor) OR (Danantara AND teknologi) OR (Danantara AND pelatihan) OR (Danantara AND MoU) OR (Danantara AND London)',
    '(Arm AND Indonesia AND teknologi) OR (Arm AND Indonesia AND pelatihan) OR (Arm AND Indonesia AND semikonduktor) OR (Arm AND Indonesia AND engineer)',
    '(semikonduktor AND Indonesia AND pelatihan) OR (semikonduktor AND Indonesia AND pendaftaran) OR (semikonduktor AND Indonesia AND industri) OR ("chip design" AND Indonesia)',
    '("15 ribu engineer") OR ("15000 engineer") OR (engineer AND Indonesia AND rekrutmen) OR (engineer AND Indonesia AND pendaftaran) OR (engineer AND Indonesia AND beasiswa)',
    '(insinyur AND Indonesia AND pelatihan) OR (talenta AND digital AND Indonesia) OR (hilirisasi AND teknologi AND Indonesia) OR (vokasi AND teknologi AND Indonesia)',
    '(MoU AND teknologi AND Indonesia) OR (kolaborasi AND teknologi AND Indonesia) OR (investasi AND teknologi AND Indonesia AND Inggris)',
    '(AI AND Indonesia AND investasi) OR ("data center" AND Indonesia AND investasi) OR ("quantum computing" AND Indonesia) OR (IoT AND Indonesia AND industri)',
    '(Prabowo AND Inggris AND teknologi) OR (Prabowo AND London AND investasi) OR (Airlangga AND semikonduktor) OR (Rosan AND teknologi AND investasi)',
]

# ==========================================
# Helper Functions
# ==========================================
def setup_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs(NATIONAL_DIR, exist_ok=True)
    os.makedirs(REGIONAL_DIR, exist_ok=True)
    if not os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_seen_urls():
    """Load previously processed URLs from file."""
    if os.path.exists(SEEN_URLS_FILE):
        with open(SEEN_URLS_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except json.JSONDecodeError:
                return set()
    return set()

def save_seen_urls(seen_urls):
    """Save processed URLs to file."""
    with open(SEEN_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_urls), f, indent=4)

def fetch_news_from_api(pagesize=30):
    """Fetch recent Indonesian news by cycling through multiple shorter queries."""
    url = "https://newsapi.org/v2/everything"
    all_articles = []
    seen = set()

    for query in NEWSAPI_QUERIES:
        params = {
            'q': query,
            'language': 'id',
            'sortBy': 'publishedAt',
            'pageSize': pagesize,
            'apiKey': NEWSAPI_KEY
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])

            for article in articles:
                article_url = article.get('url')
                if article_url and article_url not in seen:
                    seen.add(article_url)
                    all_articles.append(article)

            print(f"  Query returned {len(articles)} articles: {query[:60]}...")
            time.sleep(1)  # avoid hitting rate limit between queries

        except Exception as e:
            print(f"  Failed query: {query[:60]}...\n  Error: {e}")
            continue

    return all_articles

def extract_article_text(url):
    """Fetch URL and extract clean main text using BeautifulSoup."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.124 Safari/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'lxml')
        
        # Remove noisy elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            element.decompose()
            
        # Extract paragraph text
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(separator=' ', strip=True)])
        
        return text
    except Exception as e:
        print(f"Error fetching URL content {url}: {e}")
        return ""

def summarize_with_gemini(text):
    """Summarize article text using Gemini API with retry logic for rate limits."""
    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY not configured. Summary unavailable."
        
    model = genai.GenerativeModel('gemma-3-27b-it')
    
    prompt = f"""
    Summarize the following Indonesian news article. 
    Focus specifically on subjects around: semiconductor training, engineer counts, registration info, and ARM mentions.
    Keep the summary clean, human-readable, and concise. Ensure the summary is in Indonesian.

    PENTING: Berikan "KESIMPULAN AKHIR" (FINAL VERDICT) yang jelas di akhir ringkasan Anda yang secara eksplisit menyatakan:
    1. Apakah artikel tersebut memuat informasi spesifik mengenai pendaftaran atau registrasi (Ya/Tidak), dan rincian singkatnya jika ada.
    2. Apakah artikel tersebut memuat informasi lebih lanjut mengenai kerja sama Indonesia dan ARM Limited (Ya/Tidak), beserta poin utama kerja samanya jika ada.

    Article text:
    {text}
    """
    
    # Try up to 3 times if we hit a rate limit
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"Rate limit hit. Waiting 30 seconds... (Attempt {attempt+1}/3)")
                time.sleep(30)
            else:
                print(f"Error summarizing with Gemini: {e}")
                return f"Error generating summary: {e}"
                
    return "Failed to generate summary after 3 attempts due to rate limits."

def determine_category_dir(url):
    """Determine whether the article goes to national or regional folder based on URL domain."""
    domain = urlparse(url).netloc.lower()
    regional_keywords = ['regional', 'jogja', 'jabar', 'jatim', 'jateng', 'bali', 'makassar', 'medan', 'surabaya', 'bandung']
    for reg in regional_keywords:
        if reg in domain:
            return REGIONAL_DIR
    return NATIONAL_DIR

# ==========================================
# Main Workflow
# ==========================================
def main():
    if not NEWSAPI_KEY:
        print("Error: NEWSAPI_KEY environment variable is missing. Cannot fetch news.")
        return
        
    setup_directories()
    seen_urls = load_seen_urls()
    
    print("Fetching latest news from NewsAPI...")
    try:
        articles = fetch_news_from_api(pagesize=30)
    except Exception as e:
        print(f"Failed to fetch news: {e}")
        return
        
    print(f"Found {len(articles)} articles.")
    
    for article in articles:
        url = article.get('url')
        if not url or url in seen_urls:
            continue
            
        print(f"\nProcessing: {url}")
        
        text = extract_article_text(url)
        if not text:
            # Mark as seen so we don't keep failing on the same unreadable URL
            seen_urls.add(url)
            save_seen_urls(seen_urls)
            time.sleep(2)
            continue
            
        # Step 2: Full-text regex check
        if KEYWORDS_REGEX.search(text):
            print("  [MATCH] Keywords found in full text. Generating summary...")
            summary = summarize_with_gemini(text)
            
            # Save the match
            category_dir = determine_category_dir(url)
            
            # Format filename safely
            source_name = article.get('source', {}).get('name', 'Unknown')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_source = "".join([c for c in source_name if c.isalnum()]).rstrip()
            filename = f"{timestamp}_{safe_source}.md"
            filepath = os.path.join(category_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Source: {source_name}\n")
                f.write(f"# URL: {url}\n")
                f.write(f"# Published At: {article.get('publishedAt', 'Unknown')}\n")
                f.write(f"# Processed At: {timestamp}\n\n")
                f.write("## Summary\n")
                f.write(f"{summary}\n\n")
                f.write("## Original Title\n")
                f.write(f"{article.get('title', 'Unknown Title')}\n")
            
            print(f"  [SAVED] Summary saved to {filepath}")
        else:
            print("  [SKIP] No relevant keywords found in the article body.")
            
        # Update seen URLs
        seen_urls.add(url)
        save_seen_urls(seen_urls)
        
        # 4.1 seconds ensures you stay under the 15 RPM limit for Flash-Lite
        time.sleep(4.1)

    print("\nDaily monitoring complete!")

if __name__ == "__main__":
    main()
