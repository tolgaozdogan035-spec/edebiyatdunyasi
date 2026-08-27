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
    "https://www.trthaber.com/kultur-sanat_articles.rss",
    "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml"
]

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in [
            'ilk olarak şu sitede yayımlanmıştır', 
            'yazının kaynağı bu sitedir', 
            'appeared first on', 
            'ilk ortaya çıktı', 
            'kayıp rıhtım forum', 
            'whatsapp üzerinden takip', 
            'google news', 
            'read more', 
            'the post'
        ]):
            element.decompose()
    return str(soup)

def extract_image(entry, content):
    # 1. media_content kontrolü
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    # 2. media_thumbnail kontrolü
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        if 'url' in entry.media_thumbnail[0]:
            return entry.media_thumbnail[0]['url']
            
    # 3. enclosure (eklenti) kontrolü
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'type' in enc and 'image' in enc['type']:
                return enc['href']
                
    # 4. İçerik (HTML) içindeki ilk img etiketini bulma
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img['src']
            
    # Varsayılan şık bir edebiyat/kitap görseli yedek olarak
    return "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=1200&q=80"

def assign_category(title, categories):
    combined = (str(categories) + " " + str(title)).upper()
    if 'ŞİİR' in combined:
        return 'ŞİİR'
    if any(k in combined for k in ['ROMAN', 'ÖYKÜ', 'KİTAP']):
        return 'ROMAN/ÖYKÜ'
    if any(k in combined for k in ['SÖYLEŞİ', 'RÖPORTAJ']):
        return 'SÖYLEŞİ'
    if any(k in combined for k in ['SİNEMA', 'TİYATRO', 'SERGİ', 'FRAGMAN', 'KÜLTÜR']):
        return 'KÜLTÜR-SANAT'
    return 'EDEBİYAT HABERLERİ'

def fetch_news():
    all_articles = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', 'Başlıksız')
                link = entry.get('link', '#')
                published = entry.get('published', entry.get('updated', ''))
                
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # Güçlendirilmiş görsel çekme fonksiyonu
                image = extract_image(entry, content)
                
                cleaned_content = clean_html(content)
                soup_desc = BeautifulSoup(cleaned_content, 'html.parser')
                plain_desc = soup_desc.get_text()[:180] + "..."
                
                article = {
                    "title": title,
                    "link": link,
                    "date": published,
                    "category": assign_category(title, entry.get('tags', [])),
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
    print(f"Toplam {len(articles)} haber görselleştirilerek kaydedildi.")
