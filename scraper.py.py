import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
import requests

# Taranacak RSS Kaynakları
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
    
    # İstenmeyen imza ve kaynak ibarelerini içeren etiketleri tamamen kaldır
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
                
                # İçeriği al (content varsa öncelikli, yoksa summary)
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # Temizlik işlemleri
                cleaned_content = clean_html(content)
                
                # Görsel bulma
                image = "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?auto=format&fit=crop&w=600&q=80"
                if hasattr(entry, 'media_content') and entry.media_content:
                    image = entry.media_content[0].get('url', image)
                elif 'links' in entry:
                    for l in entry.links:
                        if 'image' in l.get('type', ''):
                            image = l.get('href')
                            break
                            
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
    
    # Klasör yoksa oluştur
    os.makedirs("haberler", exist_ok=True);
    
    # JSON dosyasına kaydet
    output_path = os.path.join("haberler", "haberler.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Toplam {len(articles)} haber başarıyla kaydedildi.")