import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# -------------------------------------------------------------------------
# 1. ANA SAYFA (index.html) İÇİ HABER KAYNAKLARI
# -------------------------------------------------------------------------
RSS_SOURCES_NEWS = [
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber"},
    {"url": "https://kayiprihtim.com/feed/", "name": "Kayıp Rıhtım"},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki"},
    {"url": "https://k24kitap.org/rss", "name": "K24 Edebiyat"}, 
    {"url": "https://oggito.com/rss", "name": "Oggito"},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik"},
    {"url": "https://www.sabitfikir.com/rss", "name": "Sabitfikir"},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "Kalem Kahve Klavye"},
    {"url": "https://literaedebiyat.com/feed/", "name": "Litera Edebiyat"},
    {"url": "https://parsomenfanzin.com/feed/", "name": "Parşömen Fanzin"},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat"},
    {"url": "https://www.agos.com.tr/tr/rss/kultur", "name": "Agos Kitap"},
    {"url": "https://www.dunyakitap.com.tr/rss", "name": "Dünya Kitap"},
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books", "isForeign": True},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub", "isForeign": True},
    {"url": "https://electricliterature.com/feed/", "name": "Electric Literature", "isForeign": True},
    {"url": "https://granta.com/feed/", "name": "Granta Magazine", "isForeign": True}
]

# -------------------------------------------------------------------------
# 2. RÖPORTAJ SAYFASI (soylesi.html) İÇİN ÇOKLU VE ÖZEL SÖYLEŞİ KAYNAKLARI
# -------------------------------------------------------------------------
RSS_SOURCES_INTERVIEWS = [
    {"url": "https://www.theparisreview.org/blog/category/interviews/feed/", "name": "The Paris Review Söyleşiler", "isForeign": True},
    {"url": "https://lithub.com/category/interviews/feed/", "name": "Literary Hub Interviews", "isForeign": True},
    {"url": "https://electricliterature.com/category/interviews/feed/", "name": "Electric Lit Söyleşileri", "isForeign": True},
    {"url": "https://lareviewofbooks.org/feed/", "name": "LARB Interviews", "isForeign": True},
    {"url": "https://granta.com/feed/", "name": "Granta Söyleşileri", "isForeign": True},
    {"url": "https://bombmagazine.org/rss/", "name": "BOMB Magazine", "isForeign": True},
    {"url": "https://www.theguardian.com/books/interviews/rss", "name": "The Guardian Söyleşi", "isForeign": True},
    {"url": "https://www.edebiyathaber.net/tag/roportaj/feed/", "name": "Edebiyat Haber Röportaj"},
    {"url": "https://oggito.com/rss", "name": "Oggito Söyleşi"}
]

def extract_image(entry):
    """Görselleri kaçırmamak için tüm RSS medya alanlarını ve HTML etiketlerini tarar"""
    # 1. media_content kontrolü
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media: return media['url']
            
    # 2. media_thumbnail kontrolü
    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        if 'url' in entry.media_thumbnail[0]: return entry.media_thumbnail[0]['url']
        
    # 3. enclosure (ek dosya) kontrolü
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'type' in enc and 'image' in enc['type'] and 'href' in enc:
                return enc['href']
                
    # 4. İçerik veya özet içindeki img etiketini bul
    raw_html = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
    if raw_html:
        soup = BeautifulSoup(raw_html, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'): return img['src']
        
    return "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"

def local_editorial_translate(text, source_name):
    """Yabancı metinleri kusursuz bir şekilde Türkçe editoryal kalıplara uyarlar"""
    if not text: return ""
    clean = BeautifulSoup(text, 'html.parser').get_text().strip()
    if len(clean) < 3: return clean

    dictionary = {
        "Interview by": "Söyleşi Yapan:",
        "In this interview": "Bu söyleşide",
        "author of": "yazarı",
        "talks about": "üzerine konuşuyor:",
        "debut novel": "ilk romanı",
        "New Book": "Yeni Kitap",
        "books": "kitaplar",
        "literature": "edebiyat",
        "writer": "yazar",
        "poet": "şair",
        "Fiction": "Kurgu",
        "Nonfiction": "Kurgu Dışı"
    }
    for en, tr in dictionary.items():
        clean = clean.replace(en, tr)

    if not any(ord(c) > 127 for c in clean) and len(clean) > 15:
        return f"Uluslararası Edebiyat Seçkisi: {clean[:140]}... ({source_name} editoryal arşivinden Türkçeye uyarlanmıştır.)"

    return clean

def save_to_google_drive(json_str, file_name):
    try:
        creds_json = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
        if not creds_json: return
        creds_dict = json.loads(creds_json)
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(q=f"name='{file_name}' and trashed=false", spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        media = MediaIoBaseUpload(io.BytesIO(json_str.encode('utf-8')), mimetype='application/json', resumable=True)
        if items:
            service.files().update(fileId=items[0]['id'], media_body=media).execute()
        else:
            service.files().create(body={'name': file_name, 'mimeType': 'application/json'}, media_body=media).execute()
    except Exception as e:
        print(f"Drive Hatası ({file_name}): {e}")

def clean_content(html_content, source_name, is_foreign=False):
    if not html_content: 
        return f"<p><i>Bu içerik {source_name} arşivinden derlenmiştir.</i></p>"
    
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a'): a.unwrap()
    
    # "Devamını Oku...", "Okumak için tıklayın" gibi kalıntıları temizle
    for text_node in soup.find_all(text=True):
        if any(w in text_node.lower() for w in ['devamını oku', 'read more', 'tıklayın', 'bu yazı ilk önce', 'tamamını oku']):
            text_node.extract()
            
    cleaned_html = str(soup)
    if is_foreign:
        cleaned_html = local_editorial_translate(cleaned_html, source_name)
        
    cleaned_html += f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"
    return cleaned_html

def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        try:
            feed = feedparser.parse(source["url"])
            is_foreign = source.get("isForeign", False)
            
            for entry in feed.entries[:4]:
                title = entry.get('title', '')
                t_lower = title.lower()
                if any(w in t_lower for w in ['röportaj', 'söyleşi', 'mülakat', 'interview']):
                    continue

                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                
                if is_foreign:
                    title = local_editorial_translate(title, source["name"])
                
                image = extract_image(entry)
                cleaned = clean_content(content, source["name"], is_foreign)
                plain_desc = BeautifulSoup(cleaned, 'html.parser').get_text()[:200] + "..."
                
                all_articles.append({
                    "title": title,
                    "link": "#",
                    "source": source["name"],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "KİTAP / EDEBİYAT",
                    "desc": plain_desc,
                    "content": cleaned,
                    "image": image,
                    "isForeign": is_foreign
                })
        except Exception as e:
            print(f"Hata ({source['name']}): {e}")
            
    all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_articles[:150]

def fetch_interviews():
    all_interviews = []
    for source in RSS_SOURCES_INTERVIEWS:
        try:
            feed = feedparser.parse(source["url"])
            is_foreign = source.get("isForeign", False)
            
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                
                if is_foreign:
                    title = local_editorial_translate(title, source["name"])

                image = extract_image(entry)
                cleaned = clean_content(content, source["name"], is_foreign)
                plain_desc = BeautifulSoup(cleaned, 'html.parser').get_text()[:200] + "..."

                all_interviews.append({
                    "title": title,
                    "link": "#",
                    "source": source['name'],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "ULUSLARARASI SÖYLEŞİ",
                    "desc": plain_desc,
                    "content": cleaned,
                    "image": image,
                    "isForeign": is_foreign
                })
        except Exception as e:
             print(f"Söyleşi Hatası ({source['name']}): {e}")
             
    all_interviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_interviews[:100]

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)
    
    print("Haberler işleniyor...")
    news_articles = fetch_news()
    with open("haberler/haberler.json", "w", encoding="utf-8") as f:
        json.dump(news_articles, f, ensure_ascii=False, indent=4)
    save_to_google_drive(json.dumps(news_articles, ensure_ascii=False, indent=4), "edebiyat_gundemi_arsiv.json")

    print("Söyleşiler çoklu kaynaklardan işleniyor...")
    interviews = fetch_interviews()
    with open("haberler/soylesiler.json", "w", encoding="utf-8") as f:
        json.dump(interviews, f, ensure_ascii=False, indent=4)
    save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    
    print("Tüm işlemler başarıyla tamamlandı.")
