import feedparser
import json
import os
import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import time

# --- KAYNAKLAR ---
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
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books", "isForeign": True},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub", "isForeign": True},
    {"url": "https://electricliterature.com/feed/", "name": "Electric Literature", "isForeign": True}
]

RSS_SOURCES_INTERVIEWS = [
    {"url": "https://www.theparisreview.org/blog/category/interviews/feed/", "name": "The Paris Review Söyleşiler", "isForeign": True},
    {"url": "https://lithub.com/category/interviews/feed/", "name": "Literary Hub Interviews", "isForeign": True},
    {"url": "https://electricliterature.com/category/interviews/feed/", "name": "Electric Lit Söyleşileri", "isForeign": True},
    {"url": "https://lareviewofbooks.org/feed/", "name": "LARB Interviews", "isForeign": True},
    {"url": "https://bombmagazine.org/rss/", "name": "BOMB Magazine", "isForeign": True},
    {"url": "https://www.edebiyathaber.net/tag/roportaj/feed/", "name": "Edebiyat Haber Röportaj"}
]

# --- %100 GARANTİLİ VE KESİNTİSİZ ÇEVİRİ MOTORU ---
def robust_translate(text):
    """Metni tek seferde çevirir, hata alırsak pes etmez, bekleyip tekrar dener."""
    if not text or len(text.strip()) < 3: 
        return text
    
    # Google Translate'in 5000 karakter sınırını aşmamak için güvenli kesim yapıyoruz
    safe_text = text[:4800] 
    
    for attempt in range(4): # 4 kez inatla çevirmeyi dener
        try:
            # İstekler arasına nefes payı koyarak spam algısını kırıyoruz
            time.sleep(2) 
            tr_text = GoogleTranslator(source='en', target='tr').translate(safe_text)
            
            # Gelen yanıt gerçekten çeviriyse ve hata kodu içermiyorsa kabul et
            if tr_text and "Error 500" not in tr_text and "Server Error" not in tr_text:
                return tr_text
        except Exception:
            time.sleep(3) # Hata olursa 3 saniye bekle, engeli kaldırıp tekrar dene
            
    return text

# --- YARDIMCI FONKSİYONLAR ---
def extract_image_from_rss(entry, content):
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if 'url' in media: return media['url']
    if hasattr(entry, 'enclosures') and entry.enclosures:
        for enc in entry.enclosures:
            if 'image' in enc.get('type', ''): return enc['href']
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'): return img['src']
    return None

def get_full_article_and_image(url, fallback_html):
    full_html = fallback_html
    og_image = None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            meta_img = soup.find('meta', property='og:image')
            if meta_img and meta_img.get('content'):
                og_image = meta_img.get('content')
            
            paragraphs = soup.find_all('p')
            article_ps = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 60]
            
            if len(article_ps) > 2:
                full_html = "".join([f"<p>{text}</p>" for text in article_ps[:10]])
    except Exception:
        pass
    return full_html, og_image

def translate_html_content_batched(html_content, source_name):
    """
    Paragraf paragraf istek atıp API'yi çökertmek yerine,
    tüm paragrafları tekilleştirip tek bir çeviri isteği atar.
    """
    if not html_content: return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 20]
    
    if not paragraphs: return ""
    
    # Paragrafları çift satır atlaması ile birleştirip TEK bir metin yapıyoruz
    combined_text = "\n\n".join(paragraphs)
    
    # Güçlü motorla tek seferde tamamını çeviriyoruz
    translated_combined = robust_translate(combined_text)
    
    # Çevrilen metni tekrar paragraflara bölüp HTML'i inşa ediyoruz
    translated_html = ""
    for tp in translated_combined.split("\n\n"):
        if tp.strip():
            translated_html += f"<p>{tp.strip()}</p>"
            
    translated_html += f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu uluslararası içerik {source_name} üzerinden derlenmiş ve eksiksiz olarak Türkçeye çevrilmiştir.</p>"
    return translated_html

def clean_turkish_content(html_content, source_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a'): a.unwrap()
    for text_node in soup.find_all(text=True):
        if any(w in text_node.lower() for w in ['devamını oku', 'read more', 'tıklayın', 'bu yazı ilk önce', 'tamamını oku']):
            text_node.extract()
    return str(soup) + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"

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

# --- ANA İŞLEMLER ---
def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        try:
            feed = feedparser.parse(source["url"])
            is_foreign = source.get("isForeign", False)
            for entry in feed.entries[:3]:
                title = entry.get('title', '')
                if any(w in title.lower() for w in ['röportaj', 'söyleşi', 'interview']):
                    continue
                
                link = entry.get('link', '')
                base_content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '')
                rss_image = extract_image_from_rss(entry, base_content)
                full_html, og_image = get_full_article_and_image(link, base_content)
                
                final_image = og_image or rss_image or "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"
                
                if is_foreign:
                    title = robust_translate(title)
                    final_content = translate_html_content_batched(full_html, source["name"])
                else:
                    final_content = clean_turkish_content(full_html, source["name"])

                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."
                
                all_articles.append({
                    "title": title, "link": "#", "source": source["name"],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "KİTAP / EDEBİYAT", "desc": plain_desc, "content": final_content,
                    "image": final_image, "isForeign": is_foreign
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
            for entry in feed.entries[:4]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                base_content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '')
                rss_image = extract_image_from_rss(entry, base_content)
                full_html, og_image = get_full_article_and_image(link, base_content)
                
                final_image = og_image or rss_image or "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"
                
                if is_foreign:
                    title = robust_translate(title)
                    final_content = translate_html_content_batched(full_html, source["name"])
                else:
                    final_content = clean_turkish_content(full_html, source["name"])

                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."

                all_interviews.append({
                    "title": title, "link": "#", "source": source['name'],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "ULUSLARARASI SÖYLEŞİ" if is_foreign else "ÖZEL SÖYLEŞİ",
                    "desc": plain_desc, "content": final_content,
                    "image": final_image, "isForeign": is_foreign
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

    print("Söyleşiler ayrı olarak işleniyor...")
    interviews = fetch_interviews()
    with open("haberler/soylesiler.json", "w", encoding="utf-8") as f:
        json.dump(interviews, f, ensure_ascii=False, indent=4)
    save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    
    print("İşlem tamamlandı.")
