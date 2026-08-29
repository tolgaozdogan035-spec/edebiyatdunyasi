import feedparser
import json
import os
from bs4 import BeautifulSoup
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Kesin çalışan ve tam Türkçe içerik üreten yerli ve seçkin kaynak havuzu
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
    {"url": "https://www.dunyakitap.com.tr/rss", "name": "Dünya Kitap"}
]

RSS_SOURCES_INTERVIEWS = [
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber Söyleşi"},
    {"url": "https://oggito.com/rss", "name": "Oggito Söyleşileri"},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik Söyleşi"},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "Kalem Kahve Söyleşi"}
]

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
    return "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"

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

def clean_content(html_content, source_name):
    if not html_content: 
        return f"<p><i>Bu içerik {source_name} arşivinden derlenmiştir.</i></p>"
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a'): a.unwrap()
    return str(soup) + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"

def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                cleaned = clean_content(content, source["name"])
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
                    "isForeign": False
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
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                cleaned = clean_content(content, source["name"])
                plain_desc = BeautifulSoup(cleaned, 'html.parser').get_text()[:200] + "..."

                all_interviews.append({
                    "title": title,
                    "link": "#",
                    "source": source['name'],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "ÖZEL SÖYLEŞİ",
                    "desc": plain_desc,
                    "content": cleaned,
                    "image": image,
                    "isForeign": False
                })
        except Exception as e:
             print(f"Söyleşi Hatası ({source['name']}): {e}")
    all_interviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_interviews

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)
    news_articles = fetch_news()
    with open("haberler/haberler.json", "w", encoding="utf-8") as f:
        json.dump(news_articles, f, ensure_ascii=False, indent=4)
    save_to_google_drive(json.dumps(news_articles, ensure_ascii=False, indent=4), "edebiyat_gundemi_arsiv.json")

    interviews = fetch_interviews()
    with open("haberler/soylesiler.json", "w", encoding="utf-8") as f:
        json.dump(interviews, f, ensure_ascii=False, indent=4)
    save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    print("İşlem tamamlandı.")
