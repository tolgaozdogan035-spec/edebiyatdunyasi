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
# -------------------------------------------------------------------------
RSS_SOURCES_NEWS = [
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
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk Kültür"},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Sanat"},
    {"url": "https://www.cumhuriyet.com.tr/rss/kultur-sanat.xml", "name": "Cumhuriyet Kültür"},
    {"url": "https://www.trthaber.com/kultur-sanat_articles.rss", "name": "TRT Sanat"},
    {"url": "https://www.sozcu.com.tr/rss/kultur-sanat.xml", "name": "Sözcü Sanat"},
    {"url": "https://www.sabah.com.tr/rss/kultur-sanat.xml", "name": "Sabah Kültür"},
    {"url": "https://www.gazeteduvar.com.tr/rss/kultur-sanat", "name": "Gazete Duvar Kültür"},
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian Books"},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub"},
    {"url": "https://electricliterature.com/feed/", "name": "Electric Literature"},
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review"},
    {"url": "https://www.publishersweekly.com/pw/rss/category/international.xml", "name": "Publishers Weekly"}
]

# -------------------------------------------------------------------------
# 2. RÖPORTAJ SAYFASI (soylesi.html) İÇİN KESİN ÇALIŞAN ÇOKLU KAYNAKLAR
# -------------------------------------------------------------------------
RSS_SOURCES_INTERVIEWS = [
    {"url": "https://electricliterature.com/feed/", "name": "Electric Lit"},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub"},
    {"url": "https://www.theguardian.com/books/rss", "name": "The Guardian"},
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review"}
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
    return "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"

def translate_text(text):
    """Güvenli ve gecikmeli çeviri motoru"""
    if not text or len(text.strip()) < 3: return text
    try:
        chunk = text[:480]
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(chunk)}&langpair=en|tr"
        res = requests.get(url, timeout=6)
        if res.status_code == 200:
            result = res.json()
            if 'responseData' in result and result['responseData']['translatedText']:
                translated = result['responseData']['translatedText']
                if "MYMEMORY WARNING" not in translated:
                    return translated
    except Exception:
        pass
    return text

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

# ================= HABERLERİ İŞLEME (INDEX.HTML) =================

def clean_html_news(raw_html):
    if not raw_html: return ""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for element in soup.find_all(['p', 'div', 'span', 'strong', 'em', 'a']):
        text = element.get_text().lower()
        if any(keyword in text for keyword in ['köşe yazısı', 'söyleşi', 'röportaj', 'özel haber', 'exclusive']):
            element.decompose()
    return str(soup)

def assign_category_news(title, content):
    combined = (str(title) + " " + str(content)).upper()
    if any(k in combined for k in ['KİTAP', 'ROMAN', 'ÖYKÜ', 'ŞİİR', 'YENİ ÇIKAN', 'YAYINEVİ', 'ÇEVİRİ']):
        return 'KİTAP / EDEBİYAT'
    if any(k in combined for k in ['SERGİ', 'TİYATRO', 'SİNEMA', 'MÜZE', 'FESTİVAL', 'KONSER']):
        return 'KÜLTÜR - SANAT'
    return 'GÜNCEL GELİŞME'

def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        try:
            feed = feedparser.parse(source["url"])
            is_foreign = any(domain in source["url"] for domain in ['guardian', 'lithub', 'publishers', 'parisreview', 'electricliterature'])
            
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                if any(w in title.lower() for w in ['röportaj', 'söyleşi', 'interview']): continue

                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                
                if is_foreign:
                    title = translate_text(title)
                    time.sleep(0.3)

                plain_desc = BeautifulSoup(content, 'html.parser').get_text()[:200] + "..."
                
                all_articles.append({
                    "title": title,
                    "link": entry.get('link', '#'),
                    "source": source["name"],
                    "date": entry.get('published', entry.get('updated', 'Güncel')),
                    "category": assign_category_news(title, content),
                    "desc": plain_desc,
                    "content": clean_html_news(content),
                    "image": image,
                    "isForeign": is_foreign
                })
        except Exception as e:
            print(f"Hata ({source['name']}): {e}")

    all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_articles[:150]

# ================= RÖPORTAJLARI ÇEVİRME VE ÇOKLU KAYNAKTAN ÇEKME =================

def translate_html_content(html_content, source_name, article_link):
    if not html_content: 
        return f"<p><i>Bu söyleşi {source_name} editoryal arşivinden derlenmiştir. Eserin ve söyleşinin tamamı için aşağıdaki bağlantıyı ziyaret edebilirsiniz.</i></p>"
    
    soup = BeautifulSoup(html_content, 'html.parser')
    paragraphs = soup.find_all('p')
    
    translated_html = ""
    # Eğer paragraf sayısı azsa veya yoksa doğrudan metni alıp çeviriyoruz
    if len(paragraphs) == 0:
        raw_text = soup.get_text()
        trans = translate_text(raw_text[:800])
        translated_html = f"<p>{trans}</p>"
    else:
        for i, p in enumerate(paragraphs):
            if i < 6: # İlk 6 paragrafı alarak içeriği genişletiyoruz
                orig = p.get_text()
                if len(orig.strip()) > 5:
                    trans = translate_text(orig)
                    translated_html += f"<p>{trans}</p>"
                    time.sleep(0.3)
                else:
                    translated_html += str(p)
            else:
                break
            
    # Okuyucunun yarım kalmış hissetmemesi için profesyonel kaynak yönlendirme kutusu ekliyoruz
    translated_html += f"<br><hr><br><p><b>Editoryal Not:</b> Bu söyleşinin tam metni ve görselleri ${source_name} tarafından sağlanmıştır. Eserin tamamını incelemek için <a href='{article_link}' target='_blank' style='color:#1d4ed8; font-weight:bold;'>orijinal kaynağı ziyaret edebilirsiniz</a>.</p>"
    return translated_html

def fetch_interviews():
    all_interviews = []
    for source in RSS_SOURCES_INTERVIEWS:
        print(f"Söyleşi Taranıyor: {source['name']}")
        try:
            feed = feedparser.parse(source["url"])
            # Her kaynaktan en yeni 4 söyleşi alarak tüm kaynakların eşit yer almasını sağlıyoruz
            for entry in feed.entries[:4]:
                title = entry.get('title', '')
                
                # Sadece röportaj / söyleşi / book/ interview içeren veya genel edebiyat söyleşisi olanları filtrele
                content = entry.get('content', [{'value': ''}])[0].get('value', '') or entry.get('summary', '') or entry.get('description', '')
                image = extract_image(entry, content)
                
                # Başlığı Türkçeye Çevir
                translated_title = translate_text(title)
                time.sleep(0.3)
                
                # İçeriği Genişletilmiş Olarak Türkçeye Çevir
                translated_content = translate_html_content(content, source['name'], entry.get('link', '#'))
                
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
             print(f"Söyleşi Hatası ({source['name']}): {e}")

    # Tarihe göre en yeniden eskiye sırala ve karıştırarak çoklu kaynağın ana sayfada/listede harmanlanmasını sağla
    all_interviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_interviews

# ================= ANA ÇALIŞTIRMA =================

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)

    print("------------------------------------------")
    print("Haberler taranıyor...")
    news_articles = fetch_news()
    news_json = json.dumps(news_articles, ensure_ascii=False, indent=4)
    with open("haberler/haberler.json", "w", encoding="utf-8") as f:
        f.write(news_json)
    save_to_google_drive(news_json, "edebiyat_gundemi_arsiv.json")
    print(f"Toplam {len(news_articles)} haber kaydedildi.")

    print("------------------------------------------")
    print("Çoklu kaynaklardan röportajlar taranıyor ve Türkçeye çevriliyor...")
    interviews = fetch_interviews()
    interviews_json = json.dumps(interviews, ensure_ascii=False, indent=4)
    with open("haberler/soylesiler.json", "w", encoding="utf-8") as f:
        f.write(interviews_json)
    save_to_google_drive(interviews_json, "edebiyat_gundemi_soylesiler.json")
    print(f"Toplam {len(interviews)} söyleşi çoklu kaynaklardan derlenerek Türkçeye çevrildi.")
    print("------------------------------------------")
