```
# Indonesian News Monitoring System – Blueprint (File-Based Logging)

## 1. Goal
- Monitor Indonesian news websites daily.  
- Detect articles about:
  - Semiconductor  
  - ARM  
  - Engineer / Insinyur  
  - Training / Pelatihan  
  - Job postings (Lowongan, Posisi, Pendaftaran)  
  - Numbers like “15000” (participants, engineers, etc.)  
- Summarize matched articles with AI for readability.  
- Save each matched article (summary + URL + source + timestamp) to a separate file.

---

## 2. Sources
- NewsAPI to fetch recent articles in Indonesian.  
- Target sites:
  - Kompas  
  - Detik  
  - Tempo  
  - CNN Indonesia  
  - Tribunnews  
  - Antara News  
- Use keyword filters in API query:
`semikonduktor OR ARM OR training OR pelatihan OR engineer OR insinyur OR pendaftaran OR lowongan OR posisi OR 15000`

---

## 3. Fetch and Filter Workflow
1. Request articles from NewsAPI (max ~30 per day).  
2. For each article:
   - Skip if URL already processed (avoid duplicates).  
   - Extract full HTML content from the article page.  
   - Clean content: remove scripts, navigation, footer, ads.  
   - Search for keywords using regex or boolean matching.  
3. If a match is found, mark for AI summarization.

---

## 4. AI Summarization
- Use Gemini API for clean summaries.  
- Input: full article text + focus instructions (semiconductor training, engineer counts, registration info).  
- Output: concise, human-readable summary.  
- Save each match to a **separate file** with:
  - Summary  
  - URL  
  - Source  
  - Timestamp  
- File naming can include date + article ID to avoid collisions.  

---

## 5. Logging & History
- Maintain a persistent record of seen URLs in a separate file.  
- Only process new URLs to avoid repeated work.  
- Store summaries in a dedicated folder for easy review.  

---

## 6. Politeness & Reliability
- Add a small delay between article requests (2–3 seconds).  
- Handle failed requests gracefully (retry or skip).  
- Respect Indonesian news websites’ servers.  
- Avoid scraping unnecessary pages.  

---

## 7. Daily Run Pattern
- Manual run (once per day) on local machine.  
- Optional automation via cron or Task Scheduler later.  
- Only call AI API for matched articles to minimize cost and usage.  

---

## 8. Summary Logic
- Step 1: NewsAPI filtering (title + description) → first-level relevance.  
- Step 2: Full-text regex check → second-level accuracy.  
- Step 3: AI summarization → clean, readable summary.  
- Step 4: Save each match to a separate file, update seen URL log.  

---

## 9. Advantages
- Accurate detection using full-text + AI.  
- Efficient: only matched articles are summarized.  
- Safe: polite scraping, avoids repeated processing.  
- Easy review: each match stored in its own file.  
- Scalable: can add automation later if needed.
```