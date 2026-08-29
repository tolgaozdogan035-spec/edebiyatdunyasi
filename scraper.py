import feedparser
import json
import os
import re
from bs4 import BeautifulSoup
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# -- DEV RSS KAYNAKLARI LİSTESİ --
RSS_SOURCES = [
    # Türk Edebiyat & Kitap Dünyası
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber"},
    {"url": "https://kayiprihtim.com/feed/", "name": "Kayıp Rıhtım"},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki"},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat"},
    {"url": "https://fikiredebiyat.com.tr/rss/edebiyat", "name": "Fikir Edebiyat"},
    {"url": "https://www.yeniasya.com.tr/rss/kultur-sanat", "name": "Yeni Asya Sanat"},
    {"url": "https://mismishaber.com/rss/kultur-sanat?xml=1", "name": "Kültür Sanat"},
    
    # Ulusal Basın Kültür Sanat Köşeleri
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk Kültür"},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Sanat"},
    {"url": "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml", "name": "Cumhuriyet Kültür"},
    {"url": "https://www.trthaber.com/kultur-sanat_articles.rss", "name": "TRT Sanat"},
    {"url": "https://www.sozcu.com.tr/rss/kultur-sanat.xml", "name": "Sözcü Sanat"},
    {"url": "https://www.sabah.com.tr/rss/kultur-sanat.xml", "name": "Sabah Kültür"},
    {"url": "https://www.saglisolluhaber.com/kultur-sanat/rss.xml", "name": "Kültür Bülteni"},
    
    # Uluslararası Kitap ve Edebiyat Gündemi (İngilizce -> Türkçe)
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books"},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub"},
    {"url": "https://www.publishersweekly.com/pw/rss/category/international.xml", "name": "Publishers Weekly"}
]

def clean_html(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em', 'a']):
        text = element.get_text().lower()
        # Katı Filtreleme: Özel haber, röportaj, köşe yazısı süzgeci
        if any(keyword in text for keyword in [
            'köşe yazısı', 'söyleşi', 'röportaj', 'özel haber', 'exclusive',
            'konuştuk', 'anlattı', 'ilk olarak şu sitede', 'bizi takip', 'whatsapp', 'read more'
        ]):
            element.decompose()
    return str(soup)

def translate_to_turkish(text):
    if not text or len(text.strip()) < 5: return text
    try:
        # MyMemory çeviri API - Chunk ile
        chunk = text[:450]
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(chunk)}&langpair=en|tr"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            result = res.json()
            if 'responseData' in result and result['responseData']['translatedText']:
                return result['responseData']['translatedText']
    except Exception:
        pass
    return text

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
    if any(k in combined for k in ['KİTAP', 'ROMAN', 'ÖYKÜ', 'ŞİİR', 'YENİ ÇIKAN', 'YAYINEVİ']):
        return 'KİTAP / EDEBİYAT'
    if any(k in combined for k in ['SERGİ', 'TİYATRO', 'SİNEMA', 'MÜZE', 'FESTİVAL', 'KONSER']):
        return 'KÜLTÜR - SANAT'
    return 'GÜNCEL GELİŞME'

def save_to_google_drive(articles_json_str):
    try:
        creds_json = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
        if not creds_json:
            print("Uyarı: GOOGLE_DRIVE_CREDENTIALS ortam değişkeni yok.")
            return

        creds_dict = json.loads(creds_json)
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)

        file_name = "edebiyat_gundemi_arsiv.json"
        results = service.files().list(q=f"name='{file_name}' and trashed=false", spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])

        media = MediaIoBaseUpload(io.BytesIO(articles_json_str.encode('utf-8')), mimetype='application/json', resumable=True)

        if items:
            service.files().update(fileId=items[0]['id'], media_body=media).execute()
        else:
            service.files().create(body={'name': file_name, 'mimeType': 'application/json'}, media_body=media).execute()
        print("Google Drive başarıyla eşitlendi.")
    except Exception as e:
        print(f"Drive Hatası: {e}")

def fetch_all():
    all_articles = []
    for source in RSS_SOURCES:
        url = source["url"]
        source_name = source["name"]
        is_foreign = "guardian" in url or "lithub" in url or "publishers" in url

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', '')
                
                # Başlık Filtresi: Söyleşi, röportaj ve köşe yazılarını atla
                t_lower = title.lower()
                if any(w in t_lower for w in ['röportaj', 'söyleşi', 'köşe', 'özel', 'konuştuk']):
                    continue

                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                
                # İçerik Filtresi
                c_lower = content.lower()
                if 'röportaj' in c_lower or 'söyleşi' in c_lower:
                    continue

                image = extract_image(entry, content)
                
                if is_foreign:
                    title = translate_to_turkish(title)
                    content = translate_to_turkish(content)

                if not content or len(content.strip()) < 15:
                    content = f"<p><strong>{title}</strong> konulu haber {source_name} üzerinden taranarak indekslenmiştir.</p>"

                cleaned_content = clean_html(content)
                plain_desc = BeautifulSoup(cleaned_content, 'html.parser').get_text()[:200] + "..."
                
                article = {
                    "title": title,
                    "link": entry.get('link', '#'),
                    "source": source_name,
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": assign_category(title, cleaned_content),
                    "desc": plain_desc,
                    "content": cleaned_content,
                    "image": image,
                    "isForeign": is_foreign
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Hata ({source_name}): {e}")

    # Tarihe göre sırala
    all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_articles[:150] # Sadece en yeni 150 haber

if __name__ == "__main__":
    articles = fetch_all()
    os.makedirs("haberler", exist_ok=True)
    json_data = json.dumps(articles, ensure_ascii=False, indent=4)
    
    with open("haberler/haberler.json", "w", encoding="utf-8") as f:
        f.write(json_data)
        
    save_to_google_drive(json_data)
    print("Sistem başarıyla çalıştı.")
