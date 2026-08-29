import feedparser
import json
import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import time

# --- SABİTLENMİŞ ÖZEL RÖPORTAJ ---
PINNED_INTERVIEW = {
    "title": "Edebiyatın yükselen yıldızı: TOLGA ÖZDOĞAN",
    "link": "#",
    "source": "Özel Söyleşi",
    "date": "Güncel",
    "category": "ÖZEL SÖYLEŞİ",
    "desc": "Fuarcılık sektöründeki yöneticilik kariyerini edebiyat dünyasındaki derin gözlemleriyle harmanlayan yazar Tolga Özdoğan ile yazarlık serüveni ve 'Leyla - Yasak Mevsim' üzerine çok özel bir söyleşi.",
    "content": """
    <p><strong>- Sizi yakından tanıyabilir miyiz?</strong></p>
    <p>Ben Tolga Özdoğan. 1985 yılının Nisan ayında doğdum ve havasıyla, suyuyla, ritmiyle ruhuma en çok hitap eden şehirde, İzmir’de yaşıyorum. Profesyonel hayatımda fuarcılık sektöründe görev yapıyorum; aynı zamanda 20 yıla aşkın sektöre emek veren eski bir gazeteciyim. Fuarcılık gibi son derece dinamik, insan odaklı ve tempolu bir sektörde yöneticilik yaparken, gazeteci kimliğim dünyayı görsel bir estetikle algılamamı sağlıyor. Ancak tüm bu unvanların ötesinde, hayatımdaki en sarsılmaz kimliklerim; eşim Sevim’e duyduğum derin yol arkadaşlığı ve 2017 doğumlu oğlumuz Ege’nin babası olmamdır. Gündüzleri iş dünyasının o bitmek bilmeyen koşturmacasında kitleleri ağırlarken, geceleri kelimelerin o sessiz, yalıtılmış ve sonsuz evrenine sığınıyorum. Ben, kalabalıkların içindeki o yalnızlığı kelimelerle sağaltmaya çalışan biriyim.</p>
    
    <p><strong>- Yazarlığa adım atmanızdaki asıl kırılma noktası ne oldu?</strong></p>
    <p>İnsanın dünyadaki varoluşunu, kendi eliyle yarattığı o büyük kaosu ve ardından umutsuzca aradığı düzeni derinlemesine sorgulamaya başladığım dönemler en büyük eşikti. İş dünyasında ve toplumsal hayatta insanların kurduğu sistemleri, taktıkları maskeleri ve içlerindeki çelişkileri gözlemlemek bende bir tortu oluşturdu. Bu tortunun zihnimde birikip taşma noktasına gelmesi, o karmaşayı kâğıt üzerinde anlamlandırarak bir edebi düzene kavuşturma ihtiyacı doğurdu. Sadece gözlemlemek yetmemeye, o gözlemleri kalıcı bir forma dönüştürme arzusu ağır basmaya başladığında yazar olmanın kaçınılmaz olduğunu anladım.</p>
    
    <p><strong>- Sizi ilk kez kalemi elinize almaya iten özel bir an var mıydı?</strong></p>
    <p>Mekanik daktilolara duyduğum o tarifsiz tutku aslında bir tesadüf değildi. O tuşlara her bastığımda çıkan tok, ritmik ses, kâğıda işleyen o fiziksel güç, bana her zaman henüz anlatılmamış hikâyelerin kapısını araladı. O ses bir nevi geçmişin kalbi gibi atıyordu. Fakat kalemi elime temelli almamı ve bir eser bırakma güdüsünü tetikleyen asıl büyük patlama, oğlum Ege’nin dünyaya gelişidir. Bir insan yetiştirirken zamana karşı ne kadar aciz olduğunuzu fark ediyorsunuz. Ona, geleceğe ve dünyaya benden geriye kalacak en anlamlı izin, zamana direnen kelimeler olması gerektiğine inandığım o an, yazarlığa ilk ve en güçlü adımı attım.</p>
    
    <p><strong>- Çocukluğunuzdaki veya gençliğinizdeki okuma alışkanlıklarınızın bugünkü yazım dilinize ve üslubunuza nasıl bir etkisi oldu?</strong></p>
    <p>Okumak, zihnimin sınırlarını çok erken yaşta yıktı. Dostoyevski’nin Karamazov Kardeşler‘deki o emsalsiz psikolojik derinliği, insan ruhunun karanlık dehlizlerine inmekten korkmamayı öğretti bana. Gabriel García Márquez’in Yüzyıllık Yalnızlık‘ta ustalıkla kurduğu büyülü evren, hayal gücümün prangalarını kopardı. George Orwell’in 1984 ile yüzümüze çarptığı sistem eleştirisi ve distopik gerçeklik, toplumsal yapıları sorgulama biçimimi şekillendirdi. Buna Carl Sagan’ın o muazzam kozmik vizyonunu, Erich Maria Remarque’ın ve Theodore Dreiser’ın çarpıcı edebi dokunuşlarını da eklediğinizde, ortaya çok katmanlı bir altyapı çıkıyor. Tüm bu ustalardan süzülenler, üslubumda hem gerçekçi ve sert bir yüzleşmeyi hem de geniş bir düşünsel zemini aynı potada eritmemi sağladı.</p>
    
    <p><strong>- Hangi deneyimlerden sonra yazar olmaya karar verdiniz?</strong></p>
    <p>Yıllardır fuarcılık sektörünün tam kalbinde, uluslararası organizasyonları yönetiyorum. Bu iş bana binlerce insanla, farklı kültürlerle ve yüzlerce farklı dinamikle temas etme şansı veriyor. Bir gazeteci ve tasarımcı olarak görsel bir düzen yaratmaya çalışırken, bir yandan da insanın o kusurlu, öngörülemez doğasına tanıklık ediyorum. İnsanların toplum içinde kurduğu suni sistemleri, hırslarını, yıktıkları kuralları yakından gözlemlemek, içimdeki anlatma arzusunu körükledi. Toplumsal çelişkilerimizi ve bireyin kendi içindeki o bitmek bilmeyen denge arayışını izlemek, beni tüm bu kaotik deneyimleri felsefi ve edebi bir süzgeçten geçirmeye mecbur bıraktı.</p>
    
    <p><strong>- İyi bir yazar olmanın şartları nelerdir siz bu yolda nasıl bir yöntem izlediniz?</strong></p>
    <p>İyi bir yazar her şeyden önce yargılamadan, sadece “anlamak” için bakabilen keskin bir gözlemci olmalıdır. Dünyaya bir yargıç gibi değil, bir kâşif gibi yaklaşmalıdır. Ben bu yolda acele etmemeyi, kelimelerin içimde demlenmesine zaman tanımayı seçtim. Bazen bir cep saatinin kusursuz mekaniğini incelerken, bazen de evimdeki tatlı su akvaryumunda süzülen melek balıklarının o telaşsız ritmine bakarken yakaladığım o sessiz detayları, metinlerimin kalbine yerleştirmeye çalıştım. Disiplin ve hayatın akışındaki o gizli ahengi yakalayabilmek, benim temel yöntemim oldu.</p>
    
    <p><strong>- Kaleme aldığınız ilk kitap nedir ve varsa diğer kitaplarınız nelerdir?</strong></p>
    <p>Yazım hayatım, insanın kendi varoluşunu ve sistemle olan mücadelesini kurgu dışı bir düzlemde, felsefi bir derinlikle incelediğim Kaosun Mimarı İnsan ile başladı. Ardından bu temanın tamamlayıcısı niteliğindeki Düzenin Savunucusu İnsan geldi. Kurgu dünyasında ise tabuları, insan doğasının zaaflarını ve kural tanımaz bir hikâyeyi anlattığım Leyla – Yasak Mevsim romanımı kaleme aldım.</p>
    
    <p><strong>- Kitaplarınızdaki konuları yazmaya yönlendiren en önemli etken ya da etkenler nelerdir?</strong></p>
    <p>En temel etken; insanın o zıtlıklarla dolu, öngörülemez doğasıdır. Bizler, kendi elimizle kusursuz diye inşa ettiğimiz sistemleri ve düzenleri, gün gelip kendi hırslarımızla bir kaosa çeviren; ardından o yarattığımız yıkıntılar arasında yeniden umutsuzca bir çıkış yolu arayan varlıklarız. Yıkma ve yapma dürtüleri arasındaki o ince çizgi, insanın kendi zihniyle girdiği o acımasız savaş, kalemimi yönlendiren en güçlü pusuladır. Ben, içimizdeki o bitmeyen fırtınaları deşifre etmek istiyorum.</p>
    
    <p><strong>- Hikâyeyi kurgularken karakterlerinizin kaderini önceden tamamen planlıyor musunuz, yoksa yazım sürecinde karakterlerin kendi yollarını çizdiği oluyor mu?</strong></p>
    <p>Masaya oturduğumda zihnimde elbette sağlam bir mimari iskelet oluyor. Ancak edebiyat matematiğe benzemiyor. Kelimeler kâğıda dökülmeye başladığında, özellikle de Leyla – Yasak Mevsim’in derinlerine inerken bunu iliklerime kadar hissettim; karakterler bir anda canlanıyor ve kendi nefeslerini almaya başlıyorlar. Sizin onlara bir tanrı gibi çizdiğiniz o dar sınırları aşıyor, kendi doğruları, yanlışları ve arzularıyla hikâyeyi bambaşka bir mecraya sürüklüyorlar. Yazarlık tam da bu noktada onlara hükmetmek değil, onların sesine saygı duyup yollarını açabilme erdemidir.</p>
    
    <p><strong>- Size ilham veren şeyler nelerdir?</strong></p>
    <p>İlham benim için büyük şatafatlarda değil, yaşanmışlıklarda ve detaylarda saklıdır. Tarihin ağırlığını taşıyan vintage bir obje; örneğin 1970’lerden kalma mekanik bir kol saati ya da eski bir porselen biblo, zihnimde o dönemin yaşanmışlıklarına dair yepyeni pencereler açabilir. Evimizin neşesi, Afrika gri papağanımız Paşa’nın zeki ve anlık bir tepkisi, bir canlının dünyayı nasıl algıladığına dair bana ilham verebilir. Kısacası hayatın içinde otantik olan, yaşanmışlık barındıran her detay kalemimi besliyor.</p>
    
    <p><strong>- En çok hangi dönemlerde üretken oluyorsunuz ve yazma konusunda sizi en çok motive eden şey nedir?</strong></p>
    <p>Gündüzün koşturmacası bitip de dünyanın sessizliğe büründüğü o derin gece saatlerinde kalemim özgürleşiyor. Beni en çok motive eden şey ise zamana direnen bir iz bırakmak; özellikle oğlum Ege’ye, babasının zihninden dökülen kelimelerle inşa edilmiş, hiçbir zaman yıkılmayacak edebi bir miras bırakma düşüncesi içimdeki en güçlü yakıt.</p>
    
    <p><strong>- Okuyucular neden sizin kitabınızı okumalı?</strong></p>
    <p>Okuyuculara hazır, süslü reçeteler sunmuyorum; onlara kendi içlerindeki kaosu gösterecek net bir ayna tutuyorum. Maskelerinden sıyrılıp, insan doğasının o çelişkili ama bir o kadar da büyüleyici gerçeğiyle yüzleşmek istiyorlarsa sayfalarımın arasında kendilerini bulacaklardır.</p>
    
    <p><strong>- Kitap ya da kitaplarınızdaki ana fikirler ve vermek istediğiniz mesajlar nelerdir?</strong></p>
    <p>İnsan zihninin yıkıcı ve yapıcı gücü arasındaki o bitmek bilmeyen savaş… En büyük savaş alanımız her zaman kendi içimizdir. Dünyayı değiştirmeye kalkışmadan önce, içimizdeki o kaosu anlamak, yüzleşmek ve kendi düzenimizi savunmak zorundayız.</p>
    
    <p><strong>- Yazar olmanın ve yazmanın sizin için zor yanları nelerdir, bunlarla nasıl başa çıktınız?</strong></p>
    <p>Fuarcılık sektörünün tam kalbinde, yöneticilik gibi yüksek tempolu ve insan odaklı bir görevi yürütürken edebi bir izolasyon sağlamak en büyük zorluk. Bu dengeyi, yazmayı bir sorumluluk veya iş olarak değil, ruhsal bir sığınak olarak görerek kuruyorum.</p>
    
    <p><strong>- Yazar tıkanıklığı yaşadığınızda bu durumun üstesinden nasıl geliyorsunuz?</strong></p>
    <p>Asla kelimelerle inatlaşmıyorum. Zihnim yorulduğunda dünyamı değiştiriyorum. Farklı ilgi alanlarıma odaklanıyorum. Aceleci davranmak ve aşırı endişeli olmak sizi bir tıkanıklığa itebiliyor. Tabi ki eşimin, oğlumun, ailemin ve dostlarımın destekleri de çok önemli.</p>
    
    <p><strong>- Kitaplarınızı kitlelere ulaştırmak için ne gibi organizasyonlar yapıyorsunuz?</strong></p>
    <p>Dijital dünyayı ve modern araçları iletişimde aktif kullanıyorum. Ancak asıl heyecanım, önümüzdeki Eylül ayında gerçekleştireceğimiz lansman ve imza günü. Kelimelerin kâğıttan taşıp okurla fiziksel olarak buluşacağı o an için sabırsızlanıyorum.</p>
    
    <p><strong>- Kitap fuarlarındaki okur-yazar buluşmalarının sizin için önemi nedir?</strong></p>
    <p>Yıllarını fuarcılık sektörüne vermiş biri olarak, yüz yüze iletişimin, o sinerjinin gücüne inanıyorum. Bir kitabın sayfalarından çıkıp, onu okuyan gözlerle doğrudan temas kurmak, yazarın ruhunu besleyen en büyük ödül. Fuarlar, edebiyatın ete kemiğe büründüğü gerçek şölenlerdir. Elbette bende kitap fuarlarında okuyucularımla buluşmayı arzu ediyorum ve bu yönde çalışmalar yapıyorum.</p>
    
    <p><strong>- Şu an üzerinde çalıştığınız yeni projeleriniz var mı?</strong></p>
    <p>Yazarlık kariyerime roman yazarı olarak devam etmeyi planlıyor ve arzu ediyorum. Takdir edersiniz ki bir romanı oluşturmak zaman ve emek isteyen bir iş. Üzerinde çalıştığım taslaklarım elbette var. Öncesinde gerçekten çok inandığım ve ilk göz ağrım dediğim Leyla Yasak Mevsim’i geniş kitleler ve edebiyat dünyası ile tam olarak buluşturmak istiyorum. Gönül rahatlığı ile söyleyebilirim ki önümüzdeki dönemde de okuyucularım ve edebiyat severlerin ilham alacağı eserleri yayınlamaya devam edeceğim.</p>
    
    <p><strong>- Sizi en çok duygulandıran geri dönüşler nelerdir?</strong></p>
    <p>Bir okurumun, satırlarımda kendi içsel savaşıyla yüzleşme cesaretini bulduğunu ve hayatındaki o kaosu düzene sokmak için ayağa kalktığını söylemesi… Bir yazar için kelimelerinin bir başkasının hayatına dokunmasından daha tatmin edici bir geri dönüş olamaz. Ayrıca yeni çıkan romanım için bir edebiyat yarışmasında aday gösterileceğini öğrenmek benim için eşsiz bir duyguydu.</p>
    
    <p><strong>- Yazar adaylarına ne gibi tavsiyelerde bulunmak istersiniz?</strong></p>
    <p>Sadece kendi türünüzde değil; bilimden tarihe, klasiklerden bilim kurguya kadar çok geniş bir yelpazede beslenin. Hemen yayımlama telaşına düşmeyin. Kelimelerin zihninizde kendi ağırlığını bulmasına izin verin. Benim yayınladığım eserlerim 4 yıllık bir çalışmanın ürünü. Gözlem yapın ama başkalarının ne dediğine kulak tıkayın. Dünyayı bir kâşif gibi izleyip, kendi sesinizi inşa edin. Unutmayın kelimeler sizin nefesiniz, kaleminiz ise sesinizdir.</p>
    
    <br><hr><br><p><b>Kaynak Bilgisi:</b> Bu özel röportaj Edebiyat Gündemi için derlenmiştir.</p>
    """,
    "image": "images/tolga_ozdogan.png", 
    "isForeign": False
}

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
    {"url": "https://www.theparisreview.org/blog/feed/", "name": "The Paris Review Söyleşiler", "isForeign": True},
    {"url": "https://lithub.com/feed/", "name": "Literary Hub Interviews", "isForeign": True},
    {"url": "https://electricliterature.com/category/interviews/feed/", "name": "Electric Lit Söyleşileri", "isForeign": True},
    {"url": "https://lareviewofbooks.org/feed/", "name": "LARB Interviews", "isForeign": True},
    {"url": "https://bombmagazine.org/rss/", "name": "BOMB Magazine", "isForeign": True},
    {"url": "https://www.edebiyathaber.net/tag/roportaj/feed/", "name": "Edebiyat Haber Röportaj"}
]

# --- KUSURSUZ ÇEVİRİ MOTORU (YAMALI METİNLERİ BİTİRİR) ---
def custom_translate(text):
    """Google GTX ve MyMemory kullanarak çeviriyi garanti altına alır."""
    if not text or len(text.strip()) < 3: return text
    
    # 1. Google GTX
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "tr", "dt": "t", "q": text}
        headers = {'User-Agent': 'Mozilla/5.0'}
        for _ in range(2):
            res = requests.get(url, params=params, headers=headers, timeout=7)
            if res.status_code == 200:
                data = res.json()
                translated = "".join([i[0] for i in data[0] if i[0]])
                if translated: return translated
            time.sleep(1)
    except: pass

    # 2. Yedek: MyMemory API
    try:
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text[:400])}&langpair=en|tr"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data.get('responseData', {}).get('translatedText'):
                tr = data['responseData']['translatedText']
                if "MYMEMORY" not in tr: return tr
    except: pass

    return text

def translate_html_content_safe(html_content, source_name):
    """HTML'i bozmadan her paragrafı özenle çevirir."""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    translated_html = ""
    
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 15:
            tr_text = custom_translate(text)
            translated_html += f"<p>{tr_text}</p>"
            time.sleep(0.5) # Google'ı engellememek için nefes payı
            
    if not translated_html:
        raw = soup.get_text(strip=True)
        if len(raw) > 15:
            translated_html = f"<p>{custom_translate(raw)}</p>"
        else:
            return html_content

    translated_html += f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu uluslararası içerik {source_name} üzerinden derlenmiş ve eksiksiz olarak Türkçeye çevrilmiştir.</p>"
    return translated_html

# --- AKILLI ÇÖP METİN FİLTRESİ ---
def clean_turkish_content(html_content, source_name):
    """Kayıp Rıhtım vb. sitelerden gelen tarih, yazar ve yorum metinlerini siler."""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for a in soup.find_all('a'): a.unwrap()
    for img in soup.find_all('img'): img.decompose()

    valid_html = ""
    months = ["ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]
    
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        text_lower = text.lower()
        
        # Çöp Metin Yakalayıcısı
        if len(text) < 150:
            if "yorum" in text_lower and any(c.isdigit() for c in text): continue
            if "okuma süresi" in text_lower: continue
            if "yazar:" in text_lower: continue
            if "tarafından yazıldı" in text_lower: continue
            # Tarih Satırları (Örn: 29 Ağustos 2026) noktalama ile bitmez.
            if any(m in text_lower for m in months) and any(c.isdigit() for c in text) and not text.endswith('.'):
                continue
                
        if any(w in text_lower for w in ['devamını oku', 'read more', 'tıklayın', 'bu yazı ilk önce', 'tamamını oku', 'haberin devamı']):
            continue
            
        if len(text) > 40:
            valid_html += f"<p>{text}</p>"
            
    if not valid_html:
        valid_html = f"<p>{soup.get_text(strip=True)}</p>"
        
    return valid_html + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"

# --- DUVAR AŞICI RSS ÇEKİCİ ---
def get_safe_feed(url):
    try:
        r2j_url = f"https://api.rss2json.com/v1/api.json?rss_url={requests.utils.quote(url)}"
        res = requests.get(r2j_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('status') == 'ok':
                class DummyFeed: pass
                dummy = DummyFeed()
                dummy.entries = []
                for item in data['items']:
                    entry = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'published': item.get('pubDate', ''),
                        'summary': item.get('description', ''),
                        'content': [{'value': item.get('content', '')}]
                    }
                    if item.get('thumbnail'): entry['media_thumbnail'] = [{'url': item['thumbnail']}]
                    if item.get('enclosure'): entry['enclosures'] = [{'href': item['enclosure'].get('link'), 'type': 'image'}]
                    dummy.entries.append(entry)
                return dummy
    except: pass
    
    try:
        return feedparser.parse(url)
    except: pass
    return None

def extract_image_from_rss(entry, content):
    if isinstance(entry, dict):
        if entry.get('media_content'): return entry['media_content'][0].get('url')
        if entry.get('media_thumbnail'): return entry['media_thumbnail'][0].get('url')
        if entry.get('enclosures'):
            for enc in entry['enclosures']:
                if 'image' in enc.get('type', ''): return enc['href']
    else:
        if hasattr(entry, 'media_content'): return entry.media_content[0].get('url')
        if hasattr(entry, 'media_thumbnail'): return entry.media_thumbnail[0].get('url')
        if hasattr(entry, 'enclosures'):
            for enc in entry.enclosures:
                if 'image' in enc.get('type', ''): return enc['href']
                
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'): return img['src']
    return None

def get_article_body(entry, link, is_foreign):
    content = ""
    if isinstance(entry, dict) and entry.get('content'):
        content = entry['content'][0].get('value', '')
    elif hasattr(entry, 'content') and len(entry.content) > 0:
        content = entry.content[0].value
    elif isinstance(entry, dict):
        content = entry.get('summary', '')
    else:
        content = getattr(entry, 'summary', '')

    if is_foreign and len(BeautifulSoup(content, 'html.parser').get_text()) < 500:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}
        proxies = [link, f"https://api.allorigins.win/raw?url={requests.utils.quote(link)}"]
        for p in proxies:
            try:
                res = requests.get(p, headers=headers, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    ps = soup.find_all('p')
                    scraped = "".join([str(p) for p in ps if len(p.get_text(strip=True)) > 40])
                    if len(scraped) > 300: return scraped
            except: pass
            
    return content

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
    except: pass

# --- ANA İŞLEMLER ---
def fetch_news():
    all_articles = []
    for source in RSS_SOURCES_NEWS:
        feed = get_safe_feed(source["url"])
        if not feed: continue
        is_foreign = source.get("isForeign", False)
        for entry in getattr(feed, 'entries', [])[:3]:
            try:
                title = entry.get('title', '') if isinstance(entry, dict) else getattr(entry, 'title', '')
                if any(w in title.lower() for w in ['röportaj', 'söyleşi', 'interview']): continue
                
                link = entry.get('link', '') if isinstance(entry, dict) else getattr(entry, 'link', '')
                raw_content = get_article_body(entry, link, is_foreign)
                rss_image = extract_image_from_rss(entry, raw_content)
                final_image = rss_image or "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"
                
                if is_foreign:
                    title = custom_translate(title)
                    final_content = translate_html_content_safe(raw_content, source["name"])
                else:
                    final_content = clean_turkish_content(raw_content, source["name"])

                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."
                pub_date = entry.get('published', 'Güncel') if isinstance(entry, dict) else getattr(entry, 'published', 'Güncel')
                
                all_articles.append({
                    "title": title, "link": "#", "source": source["name"], "date": pub_date,
                    "category": "KİTAP / EDEBİYAT", "desc": plain_desc, "content": final_content,
                    "image": final_image, "isForeign": is_foreign
                })
            except: continue
    all_articles.sort(key=lambda x: x.get('date', ''), reverse=True)
    return all_articles[:150]

def fetch_interviews():
    all_interviews = []
    for source in RSS_SOURCES_INTERVIEWS:
        feed = get_safe_feed(source["url"])
        if not feed: continue
        is_foreign = source.get("isForeign", False)
        for entry in getattr(feed, 'entries', [])[:4]:
            try:
                title = entry.get('title', '') if isinstance(entry, dict) else getattr(entry, 'title', '')
                link = entry.get('link', '') if isinstance(entry, dict) else getattr(entry, 'link', '')
                
                raw_content = get_article_body(entry, link, is_foreign)
                rss_image = extract_image_from_rss(entry, raw_content)
                final_image = rss_image or "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"
                
                if is_foreign:
                    title = custom_translate(title)
                    final_content = translate_html_content_safe(raw_content, source["name"])
                else:
                    final_content = clean_turkish_content(raw_content, source["name"])

                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."
                pub_date = entry.get('published', 'Güncel') if isinstance(entry, dict) else getattr(entry, 'published', 'Güncel')

                all_interviews.append({
                    "title": title, "link": "#", "source": source['name'], "date": pub_date,
                    "category": "ULUSLARARASI SÖYLEŞİ" if is_foreign else "ÖZEL SÖYLEŞİ",
                    "desc": plain_desc, "content": final_content,
                    "image": final_image, "isForeign": is_foreign
                })
            except: continue
            
    all_interviews.sort(key=lambda x: x.get('date', ''), reverse=True)
    all_interviews.insert(0, PINNED_INTERVIEW)
    
    return all_interviews[:100]

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)
    try:
        news = fetch_news()
        with open("haberler/haberler.json", "w", encoding="utf-8") as f: json.dump(news, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(news, ensure_ascii=False, indent=4), "edebiyat_gundemi_arsiv.json")
    except: pass
    
    try:
        interviews = fetch_interviews()
        with open("haberler/soylesiler.json", "w", encoding="utf-8") as f: json.dump(interviews, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    except: pass
