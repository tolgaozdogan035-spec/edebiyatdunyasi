import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
import requests

RSS_SOURCES = [
    "https://kayiprihtim.com/feed/",
    "https://www.edebiyathaber.net/feed/",
    "https://kitapeki.com/feed/",
    "https://www.haberturk.com/rss/kategori/kultur-sanat.xml",
    "https://www.ntv.com.tr/sanat.rss",
    "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in [
            'ilk olarak şu sitede yayımlanmıştır', 'yazının kaynağı bu sitedir', 
            'appeared first on', 'ilk ortaya çıktı', 'kayıp rıhtım forum', 
            'whatsapp üzerinden takip', 'google news', 'read more', 'the post'
        ]):
            element.decompose()
    return str(soup)

def scrape_full_article(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            img_url = og_image['content'] if og_image and og_image.get('content') else None
            
            article_body = soup.find('article') or soup.find('div', class_=re.compile('content|entry|post', re.I))
            if article_body:
                paragraphs = article_body.find_all(['p', 'h2', 'h3'])
                full_text = "".join([str(p) for p in paragraphs])
                if len(full_text.strip()) > 80:
                    return clean_html(full_text), img_url
        return None, None
    except Exception:
        return None, None

def extract_image(entry, content):
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media: return media['url']
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        if 'url' in entry.media_thumbnail[0]: return entry.media_thumbnail[0]['url']
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'): return img['src']
    return "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80"

def assign_category(title, content):
    combined = (str(title) + " " + str(content)).upper()
    # Kesin olarak söyleşi veya röportaj içerenleri doğrudan SÖYLEŞİ yapıyoruz
    if 'SÖYLEŞİ' in combined or 'RÖPORTAJ' in combined or 'KONUŞTUK' in combined:
        return 'SÖYLEŞİ'
    if 'ŞİİR' in combined:
        return 'ŞİİR'
    if any(k in combined for k in ['ROMAN', 'ÖYKÜ', 'KİTAP']):
        return 'ROMAN/ÖYKÜ'
    if any(k in combined for k in ['SİNEMA', 'TİYATRO', 'SERGİ', 'KÜLTÜR']):
        return 'KÜLTÜR-SANAT'
    return 'EDEBİYAT HABERLERİ'

def fetch_news():
    all_articles = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', 'Başlıksız Haber')
                link = entry.get('link', '#')
                published = entry.get('published', entry.get('updated', ''))
                
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                image = extract_image(entry, content)
                
                scraped_content, scraped_img = None, None
                if not content or len(content.strip()) < 150 or "Read more" in content:
                    scraped_content, scraped_img = scrape_full_article(link)
                
                if scraped_content: content = scraped_content
                if scraped_img: image = scraped_img
                
                if not content or len(content.strip()) < 15:
                    content = f"<p><strong>{title}</strong> hakkında edebiyat dünyasından derlenen en güncel detaylar bu alanda yer almaktadır.</p>"
                
                cleaned_content = clean_html(content)
                soup_desc = BeautifulSoup(cleaned_content, 'html.parser')
                plain_desc = soup_desc.get_text()[:180] + "..."
                
                category = assign_category(title, cleaned_content)
                
                article = {
                    "title": title,
                    "link": link,
                    "date": published if published else "Güncel",
                    "category": category,
                    "desc": plain_desc,
                    "content": cleaned_content,
                    "image": image
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Hata oluştu ({url}): {e}")
            
    return all_articles

if __name__ == "__main__":
    articles = fetch_news()
    if os.path.exists("haberler") and not os.path.isdir("haberler"):
        os.remove("haberler")
    os.makedirs("haberler", exist_ok=True)
    
    output_path = os.path.join("haberler", "haberler.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Toplam {len(articles)} içerik başarıyla kaydedildi.")
