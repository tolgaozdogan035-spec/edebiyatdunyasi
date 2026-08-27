import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
import requests

RSS_SOURCES = [
    "https://www.kitapyurdu.com/index.php?route=common/rss/whatsnew",
    "https://kayiprihtim.com/feed/",
    "https://www.edebiyathaber.net/feed/",
    "https://kitapeki.com/feed/"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in ['ilk olarak şu sitede', 'read more', 'the post']):
            element.decompose()
    return str(soup)

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
    return "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1200&q=80"

def fetch_all():
    all_articles = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', 'Eser / Haber')
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
                
                if not content or len(content.strip()) < 15:
                    content = f"<p><strong>{title}</strong> eserine ait detaylar ve tanıtım metni bu sayfada yer almaktadır.</p>"
                
                cleaned_content = clean_html(content)
                soup_desc = BeautifulSoup(cleaned_content, 'html.parser')
                plain_desc = soup_desc.get_text()[:180] + "..."
                
                # Kitapyurdu kaynaklı olanları doğrudan KİTAP İNCELEME yapıyoruz
                category = "KİTAP İNCELEME" if "kitapyurdu" in url else "EDEBİYAT HABERLERİ"
                
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
            print(f"Hata ({url}): {e}")
            
    return all_articles

if __name__ == "__main__":
    articles = fetch_all()
    if os.path.exists("haberler") and not os.path.isdir("haberler"):
        os.remove("haberler")
    os.makedirs("haberler", exist_ok=True)
    
    # Tek ve çalışan ana dosyaya kaydediyoruz
    output_path = os.path.join("haberler", "haberler.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Toplam {len(articles)} içerik kaydedildi.")
