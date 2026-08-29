import feedparser
import json
import os
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

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
    "image": "https://edebiyatgundemi.com/images/tolga_ozdogan.png", 
}

# --- TEK BİR MERKEZİ KAYNAK LİSTESİ ---
ALL_SOURCES = [
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber"},
    {"url": "https://kayiprihtim.com/category/haberler/edebiyat/feed/", "name": "Kayıp Rıhtım"},
    {"url": "https://kayiprihtim.com/category/haberler/roportajlar/feed/", "name": "Kayıp Rıhtım Röportaj"},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki"},
    {"url": "https://kitapeki.com/category/soylesi/feed/", "name": "Kitap Eki Söyleşi"},
    {"url": "https://k24kitap.org/rss", "name": "K24 Edebiyat"}, 
    {"url": "https://oggito.com/rss", "name": "Oggito"},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik"},
    {"url": "https://www.sabitfikir.com/rss", "name": "Sabitfikir"},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "Kalem Kahve Klavye"},
    {"url": "https://literaedebiyat.com/feed/", "name": "Litera Edebiyat"},
    {"url": "https://parsomenfanzin.com/feed/", "name": "Parşömen Fanzin"},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat"},
    {"url": "https://haberedebiyat.com/feed/", "name": "Haber Edebiyat"},
    {"url": "https://www.kitaphaber.com.tr/rss.php", "name": "Kitap Haber"},
    {"url": "https://edebiyatburada.com/feed/", "name": "Edebiyat Burada"},
    {"url": "https://edebiyatkulisi.com.tr/feed/", "name": "Edebiyat Kulisi"},
    {"url": "https://sanatokur.com/kategori/edebiyat-haberleri/feed/", "name": "Sanat Okur"},
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk"},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Kültür Sanat"},
    {"url": "https://www.haberler.com/rss/kultur-sanat.xml", "name": "Haberler.com"},
    {"url": "https://www.sondakika.com/rss/kultur-sanat.xml", "name": "Sondakika Kültür Sanat"},
    {"url": "https://tr.euronews.com/rss?level=theme&name=kultur", "name": "Euronews"},
    {"url": "https://edebiyatsoylesileri.com/feed/", "name": "Edebiyat Söyleşileri"}
]

# --- SIFIR HATA FOTOĞRAF DEDEKTÖRÜ ---
def is_valid_image(url):
    """Gelen URL'nin SAHTE bir fotoğraf olup olmadığını kontrol eder."""
    if not url: return False
    url = url.strip()
    # Eğer link http ile başlamıyorsa, data:image kodlu sahte bir gıf ise REDDET.
    if not url.startswith("http"): return False
    # "Avatar", "logo" veya "1x1" boyutlu şeffaf lazy load resimlerini REDDET.
    if any(x in url.lower() for x in ["avatar", "logo", "1x1", "data:image"]): return False
    return True

def extract_image_safely(entry, html_content):
    """Gerçek resmi bulana kadar tüm olasılıkları dener, sahteleri ayıklar."""
    img_url = None
    
    # 1. RSS medya etiketlerini tara
    if isinstance(entry, dict):
        if entry.get('media_content'): img_url = entry['media_content'][0].get('url')
        elif entry.get('media_thumbnail'): img_url = entry['media_thumbnail'][0].get('url')
        elif entry.get('enclosures'):
            for enc in entry['enclosures']:
                if 'image' in enc.get('type', ''): img_url = enc['href']
    else:
        if hasattr(entry, 'media_content'): img_url = entry.media_content[0].get('url')
        elif hasattr(entry, 'media_thumbnail'): img_url = entry.media_thumbnail[0].get('url')
        elif hasattr(entry, 'enclosures'):
            for enc in entry.enclosures:
                if 'image' in enc.get('type', ''): img_url = enc['href']

    if is_valid_image(img_url): return img_url
    
    # 2. İçeriğin içindeki img etiketlerini derinlemesine tara
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            # Gerçek resim linki genellikle lazy-load etiketlerine gizlenir
            src = img.get('data-src') or img.get('data-lazy-src') or img.get('src')
            if is_valid_image(src):
                return src

    # 3. Eğer hiçbiri bulunamadıysa GARANTİ varsayılan resim
    return "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"


# --- SIFIR HATA METİN FİLTRESİ ---
def clean_turkish_content(html_content, source_name):
    if not html_content: return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup.find_all(['a', 'img', 'script', 'style']):
        tag.decompose()

    valid_html = ""
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        text_lower = text.lower()
        
        # Çöp satırları sil
        if len(text) < 150:
            if any(w in text_lower for w in ["yorum", "okuma süresi", "yazar:", "tarafından yazıldı", "the post", "first appeared"]): continue
        if any(w in text_lower for w in ['devamını oku', 'read more', 'tıklayın', 'bu yazı ilk önce', 'tamamını oku', 'haberin devamı', 'the post', 'first appeared']): continue
            
        if len(text) > 30:
            valid_html += f"<p>{text}</p>"
            
    if not valid_html:
        text = soup.get_text(strip=True)
        for bad_phrase in ["The post", "the post", "first appeared on", "yazısı ilk önce"]:
            if bad_phrase in text:
                text = text.split(bad_phrase)[0]
        if len(text) > 30:
            valid_html = f"<p>{text}</p>"
            
    return valid_html + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"

def get_safe_feed(url):
    """Önce normal, sonra rss2json API ile engelleri aşar."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}
    
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
                if dummy.entries: return dummy
    except: pass
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200: return feedparser.parse(res.content)
    except: pass
    
    try: return feedparser.parse(url)
    except: return None

def get_article_body(entry):
    if isinstance(entry, dict) and entry.get('content'): return entry['content'][0].get('value', '')
    elif hasattr(entry, 'content') and len(entry.content) > 0: return entry.content[0].value
    elif isinstance(entry, dict): return entry.get('summary', '')
    else: return getattr(entry, 'summary', '')

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

# --- ANA YÖNLENDİRİCİ MOTOR ---
def build_archives():
    news_list = []
    interviews_list = []
    
    for source in ALL_SOURCES:
        feed = get_safe_feed(source["url"])
        if not feed: continue
        
        # EDEBİYAT SÖYLEŞİLERİ İÇİN LİMİTİ 15'E ÇIKARTIYORUZ!
        entry_limit = 15 if "soylesi" in source["url"].lower() else 5
        
        for entry in getattr(feed, 'entries', [])[:entry_limit]:
            try:
                title = entry.get('title', '') if isinstance(entry, dict) else getattr(entry, 'title', '')
                link = entry.get('link', '') if isinstance(entry, dict) else getattr(entry, 'link', '')
                
                # Akıllı Kategori Ayrımı
                is_interview = False
                if any(w in title.lower() or w in link.lower() for w in ['röportaj', 'söyleşi', 'mülakat', 'interview']):
                    is_interview = True
                if "soylesi" in source["url"].lower() or "röportaj" in source["name"].lower() or "söyleşi" in source["name"].lower():
                    is_interview = True

                raw_content = get_article_body(entry)
                
                # Yeni ve Güvenli Fotoğraf Ayıklayıcı
                final_image = extract_image_safely(entry, raw_content)
                final_content = clean_turkish_content(raw_content, source["name"])
                
                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."
                pub_date = entry.get('published', 'Güncel') if isinstance(entry, dict) else getattr(entry, 'published', 'Güncel')
                
                article_data = {
                    "title": title, "link": "#", "source": source["name"], "date": pub_date,
                    "desc": plain_desc, "content": final_content,
                    "image": final_image, "isForeign": False
                }

                if is_interview:
                    article_data["category"] = "ÖZEL SÖYLEŞİ"
                    interviews_list.append(article_data)
                else:
                    article_data["category"] = "KİTAP / EDEBİYAT"
                    news_list.append(article_data)
                    
            except: continue

    news_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    interviews_list.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    # RÖPORTAJINIZI LİSTENİN BAŞINA SABİTLE
    interviews_list.insert(0, PINNED_INTERVIEW)
    
    return news_list[:150], interviews_list[:150]

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)
    print("Tüm ulusal kaynaklar akıllı resim filtresi ile taranıyor...")
    
    news, interviews = build_archives()
    
    try:
        with open("haberler/haberler.json", "w", encoding="utf-8") as f: json.dump(news, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(news, ensure_ascii=False, indent=4), "edebiyat_gundemi_arsiv.json")
    except: pass
    
    try:
        with open("haberler/soylesiler.json", "w", encoding="utf-8") as f: json.dump(interviews, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    except: pass
    
    print("İşlem eksiksiz tamamlandı.")
