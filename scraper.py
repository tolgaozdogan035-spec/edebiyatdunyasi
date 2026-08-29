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

# -------------------------------------------------------------------------
# 1. ANA SAYFA (index.html) İÇİ HABER KAYNAKLARI LİSTESİ
# (Ulusal ve küresel kültür-sanat, eleştiri ve edebiyat portalları)
# -------------------------------------------------------------------------
RSS_SOURCES_NEWS = [
    # Edebiyat, Eleştiri ve Kitap Dünyası
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber"},
    {"url": "https://kayiprihtim.com/feed/", "name": "Kayıp Rıhtım"},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki"},
    {"url": "https://k24kitap.org/rss", "name": "K24"}, 
    {"url": "https://oggito.com/rss", "name": "Oggito"},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik"},
    {"url": "https://www.sabitfikir.com/rss", "name": "Sabitfikir"},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "KalemKahveKlavye"},
    {"url": "https://literaedebiyat.com/feed/", "name": "Litera Edebiyat"},
    {"url": "https://parsomenfanzin.com/feed/", "name": "Parşömen Fanzin"},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat"},
    
    # Ulusal Basın Kültür Sanat Köşeleri
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk Kültür"},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Sanat"},
    {"url": "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml", "name": "Cumhuriyet Kültür"},
    {"url": "https://www.trthaber.com/kultur-sanat_articles.rss", "name": "TRT Sanat"},
    {"url": "https://www.sozcu.com.tr/rss/kultur-sanat.xml", "name": "Sözcü Sanat"},
    {"url": "https://www.sabah.com.tr/rss/kultur-sanat.xml", "name": "Sabah Kültür"},
    {"url": "https://www.gazeteduvar.com.tr/rss/kultur-sanat", "name": "Gazete Duvar Kültür"},
    
    # Uluslararası Kitap ve Edebiyat Gündemi (İngilizce -> Türkçe)
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books"},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub"},
    {"url": "https://electricliterature.com/feed/", "name": "Electric Literature"},
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review"},
    {"url": "https://www.publishersweekly.com/pw/rss/category/international.xml", "name": "Publishers Weekly"}
]

# -------------------------------------------------------------------------
# 2. RÖPORTAJ SAYFASI (soylesi.html) İÇİN KAYNAKLAR
# SADECE Uluslararası Edebi Söyleşiler (Çevrilecek)
# -------------------------------------------------------------------------
RSS_SOURCES_INTERVIEWS = [
    {"url": "https://www.theparisreview.org/blog/category/interviews/feed/", "name": "The Paris Review"},
    {"url": "https://lithub.com/category/interviews/feed/", "name": "Literary Hub"},
    {"url": "https://electricliterature.com/category/interviews/feed/", "name": "Electric Literature"},
    {"url": "https://bombmagazine.org/rss/", "name": "BOMB Magazine"},
    {"url": "https://www.theguardian.com/books/interviews/rss", "name": "The Guardian"}
]

# ================= ORTAK YARDIMCI FONKSİYONLAR =================

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
    return "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=80"

def translate_text(text):
    """Metni MyMemory API ile Türkçeye çevirir."""
    if not text or len(text.strip()) < 5: return text
    try:
        chunk = text[:490]
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(chunk)}&langpair=en|tr"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            result = res.json()
            if 'responseData' in result and result['responseData']['translatedText']:
                return result['responseData']['translatedText']
    except Exception:
        pass
    return text

def save_to_google_drive(json_str, file_name):
    try:
        creds_json = os.environ.get("GOOGLE_DRIVE_CREDENTIALS")
        if not creds_json:
            return

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
        print(f"Google Drive: {file_name} eşitlendi.")
    except Exception as e:
        print(f"Drive Hatası ({file_name}): {e}")

# ================= HABERLERİ İŞLEME (INDEX.HTML) =================

def clean_html_news(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em', 'a']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in [
            'köşe yazısı', 'söyleşi', 'röportaj', 'özel haber', 'exclusive',
            'konuştuk', 'anlattı', 'ilk olarak şu sitede', 'bizi takip', 'whatsapp', 'read more',
            'mülakat', 'köşemde', 'benim görüşüm', 'bence'
        ]):
            element.decompose()
    return str(soup)

def assign_category_news(title, content):
    combined = (str(title) + " " + str(content)).upper()
    if any(k in combined for k in ['KİTAP', 'ROMAN', 'ÖYKÜ', 'ŞİİR', 'YENİ ÇIKAN', 'YAYINEVİ', 'ÇEVİRİ', 'EDEBİYAT ÖDÜLÜ']):
        return 'KİTAP / EDEBİYAT'
    if any(k in combined for k in ['SERGİ', 'TİYATRO', 'SİNEMA', 'MÜZE', 'FESTİVAL', 'KONSER', 'KÜLTÜREL']):
        return 'KÜLTÜR - SANAT'
    if any(k in combined for k in ['KURAM', 'ELEŞTİRİ', 'İNCELEME', 'ANALİZ']):
        return 'ELEŞTİRİ & İNCELEME'
    return 'GÜNCEL GELİŞME'

def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        url = source["url"]
        source_name = source["name"]
        is_foreign = any(domain in url for domain in ['guardian', 'lithub', 'publishers', 'parisreview', 'electricliterature'])

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                t_lower = title.lower()
                if any(w in t_lower for w in ['röportaj', 'söyleşi', 'köşe', 'özel', 'konuştuk', 'benim görüşüm', 'interview']):
                    continue

                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                c_lower = content.lower()
                if 'röportaj' in c_lower or 'söyleşi' in c_lower or 'köşemde' in c_lower or 'interview' in c_lower:
                    continue

                image = extract_image(entry, content)
                
                if is_foreign:
                    title = translate_text(title)
                    content = translate_text(content)
                    time.sleep(0.4)

                cleaned_content = clean_html_news(content)
                if not cleaned_content or len(cleaned_content.strip()) < 15:
                    cleaned_content = f"<p><strong>{title}</strong> konulu nitelikli içerik <em>{source_name}</em> üzerinden taranarak indekslenmiştir.</p>"

                plain_desc = BeautifulSoup(cleaned_content, 'html.parser').get_text()[:200] + "..."
                
                all_articles.append({
                    "title": title,
                    "link": entry.get('link', '#'),
                    "source": source_name,
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": assign_category_news(title, cleaned_content),
                    "desc": plain_desc,
                    "content": cleaned_content,
                    "image": image,
                    "isForeign": is_foreign
                })
        except Exception as e:
            print(f"Hata ({source_name}): {e}")

    all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_articles[:150]

# ================= RÖPORTAJLARI ÇEVİRME VE İŞLEME (SOYLESI.HTML) =================

def translate_html_content(html_content):
    if not html_content: return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    translated_html = ""
    for i, p in enumerate(paragraphs):
        if i < 4:
            original_text = p.get_text()
            if len(original_text.strip()) > 10:
                translated_p = translate_text(original_text)
                translated_html += f"<p>{translated_p}</p>"
                time.sleep(0.4)
            else:
                translated_html += str(p)
        else:
            if i == 4:
                translated_html += "<br><hr><br><p><i>(Aşağıdaki metin orijinal dilindedir. Söyleşinin tamamına kaynak siteden ulaşabilirsiniz.)</i></p>"
            translated_html += str(p)
            
    if not translated_html:
         raw_text = soup.get_text()
         trans = translate_text(raw_text[:400])
         translated_html = f"<p>{trans}...</p><p><i>(Söyleşinin devamı için orijinal kaynağa gidiniz.)</i></p>"

    clean_soup = BeautifulSoup(translated_html, 'html.parser')
    for a in clean_soup.find_all('a'):
        a.unwrap() 
        
    return str(clean_soup)

def fetch_interviews():
    all_interviews = []
    for source in RSS_SOURCES_INTERVIEWS:
        print(f"Röportaj Taranıyor: {source['name']}")
        try:
            feed = feedparser.parse(source["url"])
            for entry in feed.entries[:4]: # Her kaynaktan en yeni 4 röportaj
                title = entry.get('title', '')
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                
                # Başlığı Türkçeye Çevir
                translated_title = translate_text(title)
                time.sleep(0.4)
                
                # İçeriği Türkçeye Çevir
                translated_content = translate_html_content(content)
                
                soup = BeautifulSoup(translated_content, 'html.parser')
                translated_desc = soup.get_text()[:200] + "..."

                all_interviews.append({
                    "title": translated_title,
                    "link": entry.get('link', '#'),
                    "source": source["name"],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": "ULUSLARARASI SÖYLEŞİ",
                    "desc": translated_desc,
                    "content": translated_content,
                    "image": image,
                    "isForeign": True 
                })
        except Exception as e:
             print(f"Röportaj Hatası ({source['name']}): {e}")

    all_interviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_interviews

# ================= ANA ÇALIŞTIRMA =================

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)

    # 1. Haberleri İşle
    print("------------------------------------------")
    print("Haberler taranıyor...")
    news_articles = fetch_news()
    news_json = json.dumps(news_articles, ensure_ascii=False, indent=4)
    with open("haberler/haberler.json", "w", encoding="utf-8") as f:
        f.write(news_json)
    save_to_google_drive(news_json, "edebiyat_gundemi_arsiv.json")
    print(f"Toplam {len(news_articles)} haber kaydedildi.")

    # 2. Söyleşileri İşle ve Çevir
    print("------------------------------------------")
    print("Uluslararası söyleşiler taranıyor ve çevriliyor...")
    interviews = fetch_interviews()
    interviews_json = json.dumps(interviews, ensure_ascii=False, indent=4)
    with open("haberler/soylesiler.json", "w", encoding="utf-8") as f:
        f.write(interviews_json)
    save_to_google_drive(interviews_json, "edebiyat_gundemi_soylesiler.json")
    print(f"Toplam {len(interviews)} söyleşi Türkçeye çevrilerek kaydedildi.")
    print("------------------------------------------")
    print("Tüm bot döngüsü başarıyla tamamlandı.")
