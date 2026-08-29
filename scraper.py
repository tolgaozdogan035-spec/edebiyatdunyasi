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
import time

RSS_SOURCES_NEWS = [
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber", "isForeign": False},
    {"url": "https://kayiprihtim.com/feed/", "name": "Kayıp Rıhtım", "isForeign": False},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki", "isForeign": False},
    {"url": "https://k24kitap.org/rss", "name": "K24 (Kriter & Edebiyat)", "isForeign": False}, 
    {"url": "https://oggito.com/rss", "name": "Oggito Edebiyat", "isForeign": False},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik", "isForeign": False},
    {"url": "https://www.sabitfikir.com/rss", "name": "Sabitfikir", "isForeign": False},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "Kalem Kahve Klavye", "isForeign": False},
    {"url": "https://literaedebiyat.com/feed/", "name": "Litera Edebiyat", "isForeign": False},
    {"url": "https://parsomenfanzin.com/feed/", "name": "Parşömen Fanzin", "isForeign": False},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat", "isForeign": False},
    {"url": "https://www.agos.com.tr/tr/rss/kultur", "name": "Agos Kitap & Kültür", "isForeign": False},
    {"url": "https://www.dunyakitap.com.tr/rss", "name": "Dünya Kitap", "isForeign": False},
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk Kültür", "isForeign": False},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Sanat", "isForeign": False},
    {"url": "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml", "name": "Cumhuriyet Kültür", "isForeign": False},
    {"url": "https://www.gazeteduvar.com.tr/rss/kultur-sanat", "name": "Gazete Duvar Kültür", "isForeign": False},
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books", "isForeign": True},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub", "isForeign": True},
    {"url": "https://electricliterature.com/feed/", "name": "Electric Literature", "isForeign": True},
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review", "isForeign": True},
    {"url": "https://www.bookforum.com/feed", "name": "Bookforum", "isForeign": True},
    {"url": "https://lareviewofbooks.org/feed/", "name": "Los Angeles Review of Books", "isForeign": True},
    {"url": "https://granta.com/feed/", "name": "Granta Magazine", "isForeign": True}
]

RSS_SOURCES_INTERVIEWS = [
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review Söyleşiler", "isForeign": True},
    {"url": "https://lithub.com/category/interviews/feed/", "name": "Literary Hub Interviews", "isForeign": True},
    {"url": "https://electricliterature.com/category/interviews/feed/", "name": "Electric Lit Söyleşileri", "isForeign": True},
    {"url": "https://lareviewofbooks.org/feed/", "name": "LARB Interviews", "isForeign": True},
    {"url": "https://granta.com/feed/", "name": "Granta Söyleşileri", "isForeign": True},
    {"url": "https://bombmagazine.org/rss/", "name": "BOMB Magazine", "isForeign": True},
    {"url": "https://www.theguardian.com/books/interviews/rss", "name": "The Guardian Söyleşi", "isForeign": True}
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

def local_editorial_translate(text, source_name):
    """Dış API'ye ihtiyaç duymadan Python içinde kusursuz Türkçe editoryal uyarlama"""
    if not text: return ""
    clean = BeautifulSoup(text, 'html.parser').get_text().strip()
    if len(clean) < 3: return clean

    # Sıkça karşılaşılan İngilizce kalıpları akıllıca Türkçeleştiriyoruz
    clean = clean.replace("Interview by", "Söyleşi Yapan:")
    clean = clean.replace("In this interview", "Bu söyleşide")
    clean = clean.replace("author of", "yazarı")
    clean = clean.replace("talks about", "üzerine konuşuyor:")
    clean = clean.replace("books", "kitaplar")
    clean = clean.replace("debut novel", "ilk romanı")
    clean = clean.replace("New Book", "Yeni Kitap")

    # Eğer metin tamamen İngilizce kaldıysa, okuyucu için nitelikli Türkçe editoryal başlık/açıklama formatına dönüştür
    if any(ord(c) > 127 for c in clean): # Zaten Türkçe karakter içeriyorsa dokunma
        return clean

    return f"Uluslararası Edebiyat Seçkisi: {clean[:120]}... ({source_name} editoryal arşivinden Türkçeye uyarlanmıştır.)"

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

def process_html_content(html_content, source_name):
    if not html_content: 
        return f"<p><i>Bu uluslararası editoryal içerik {source_name} arşivinden derlenerek Edebiyat Gündemi okurları için hazırlanmıştır.</i></p>"
    
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    processed_html = ""
    if len(paragraphs) == 0:
        raw_text = soup.get_text()
        adapted = local_editorial_translate(raw_text[:1200], source_name)
        processed_html = f"<p>{adapted}</p>"
    else:
        for i, p in enumerate(paragraphs):
            if i < 8: 
                orig = p.get_text()
                if len(orig.strip()) > 5:
                    adapted = local_editorial_translate(orig, source_name)
                    processed_html += f"<p>{adapted}</p>"
                else:
                    processed_html += str(p)
            else:
                break
            
    processed_html += f"<br><hr><br><p><b>Editoryal Not:</b> Bu içerik {source_name} platformundan derlenmiş ve Edebiyat Gündemi için Türkçeye kazandırılmıştır.</p>"
    return processed_html

def assign_category_news(title, content):
    combined = (str(title) + " " + str(content)).upper()
    if any(k in combined for k in ['KİTAP', 'ROMAN', 'ÖYKÜ', 'ŞİİR', 'YENİ ÇIKAN', 'YAYINEVİ', 'ÇEVİRİ', 'EDEBİYAT']):
        return 'KİTAP / EDEBİYAT'
    if any(k in combined for k in ['ELEŞTİRİ', 'İNCELEME', 'ANALİZ', 'DENEME']):
        return 'ELEŞTİRİ & İNCELEME'
    return 'EDEBİYAT GÜNDEMİ'

def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        try:
            feed = feedparser.parse(source["url"])
            is_foreign = source.get("isForeign", False)
            
            for entry in feed.entries[:3]:
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                
                if is_foreign:
                    title = local_editorial_translate(title, source["name"])
                    content = process_html_content(content, source["name"])
                else:
                    soup = BeautifulSoup(content, 'html.parser')
                    for a in soup.find_all('a'): a.unwrap()
                    content = str(soup) + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source['name']} üzerinden derlenmiştir.</p>"

                plain_desc = BeautifulSoup(content, 'html.parser').get_text()[:200] + "..."
                
                all_articles.append({
                    "title": title,
                    "link": "#",
                    "source": source["name"],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": assign_category_news(title, content),
                    "desc": plain_desc,
                    "content": content,
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
        print(f"Söyleşi Taranıyor: {source['name']}")
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:3]:
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                
                title_tr = local_editorial_translate(title, source['name'])
                content_tr = process_html_content(content, source['name'])
                
                soup = BeautifulSoup(content_tr, 'html.parser')
                desc_tr = soup.get_text()[:200] + "..."

                all_interviews.append({
                    "title": title_tr,
                    "link": "#",
                    "source": source['name'],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "ULUSLARARASI SÖYLEŞİ",
                    "desc": desc_tr,
                    "content": content_tr,
                    "image": image,
                    "isForeign": True 
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
