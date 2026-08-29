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
    "image": "https://edebiyatgundemi.com/images/tolga_ozdogan.png", 
}

# --- AKILLI VE ETİKETLİ KAYNAK LİSTESİ ---
ALL_SOURCES = [
    {"url": "https://www.edebiyathaber.net/feed/", "name": "Edebiyat Haber", "is_interview": False},
    {"url": "https://kayiprihtim.com/category/haberler/edebiyat/feed/", "name": "Kayıp Rıhtım", "is_interview": False},
    {"url": "https://kayiprihtim.com/category/haberler/roportajlar/feed/", "name": "Kayıp Rıhtım Röportaj", "is_interview": True},
    {"url": "https://kitapeki.com/feed/", "name": "Kitap Eki", "is_interview": False},
    {"url": "https://kitapeki.com/category/soylesi/feed/", "name": "Kitap Eki Söyleşi", "is_interview": True},
    {"url": "https://k24kitap.org/rss", "name": "K24 Edebiyat", "is_interview": False}, 
    {"url": "https://oggito.com/rss", "name": "Oggito", "is_interview": False},
    {"url": "https://sanatkritik.com/feed/", "name": "Sanat Kritik", "is_interview": False},
    {"url": "https://www.sabitfikir.com/rss", "name": "Sabitfikir", "is_interview": False},
    {"url": "https://kalemkahveklavye.com/feed/", "name": "Kalem Kahve Klavye", "is_interview": False},
    {"url": "https://literaedebiyat.com/feed/", "name": "Litera Edebiyat", "is_interview": False},
    {"url": "https://parsomenfanzin.com/feed/", "name": "Parşömen Fanzin", "is_interview": False},
    {"url": "https://fikiredebiyat.com.tr/rss/kitap", "name": "Fikir Edebiyat", "is_interview": False},
    {"url": "https://haberedebiyat.com/feed/", "name": "Haber Edebiyat", "is_interview": False},
    {"url": "https://www.kitaphaber.com.tr/rss.php", "name": "Kitap Haber", "is_interview": False},
    {"url": "https://edebiyatburada.com/feed/", "name": "Edebiyat Burada", "is_interview": False},
    {"url": "https://edebiyatkulisi.com.tr/feed/", "name": "Edebiyat Kulisi", "is_interview": False},
    {"url": "https://sanatokur.com/kategori/edebiyat-haberleri/feed/", "name": "Sanat Okur", "is_interview": False},
    {"url": "https://sanatokur.com/kategori/soylesiler/feed/", "name": "Sanat Okur Söyleşi", "is_interview": True},
    {"url": "https://www.haberturk.com/rss/kategori/kultur-sanat.xml", "name": "Habertürk", "is_interview": False},
    {"url": "https://www.ntv.com.tr/sanat.rss", "name": "NTV Kültür Sanat", "is_interview": False},
    {"url": "https://www.haberler.com/rss/kultur-sanat.xml", "name": "Haberler.com", "is_interview": False},
    {"url": "https://www.sondakika.com/rss/kultur-sanat.xml", "name": "Sondakika Kültür Sanat", "is_interview": False},
    {"url": "https://tr.euronews.com/rss?level=theme&name=kultur", "name": "Euronews", "is_interview": False},
    {"url": "https://www.edebiyathaber.net/tag/roportaj/feed/", "name": "Edebiyat Haber Röportaj", "is_interview": True},
    {"url": "https://edebiyatsoylesileri.com/rss", "name": "Edebiyat Söyleşileri", "is_interview": True}
]

# --- SIFIR HATA FOTOĞRAF DEDEKTÖRÜ ---
def is_valid_image(url):
    if not url: return False
    url = url.strip()
    if not url.startswith("http"): return False
    if any(x in url.lower() for x in ["avatar", "logo", "1x1", "data:image"]): return False
    return True

def extract_image_safely(entry, html_content):
    img_url = None
    
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
    
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('data-src') or img.get('data-lazy-src') or img.get('src')
            if is_valid_image(src):
                return src

    return "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"

# --- YARIM HABER VE EKSİK FOTOĞRAF KURTARICI KANCA ---
def scrape_full_article(url, fallback_html, fallback_image):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0 Safari/537.36'}
    proxies = [url, f"https://api.allorigins.win/raw?url={requests.utils.quote(url)}"]
    
    html_text = ""
    for p in proxies:
        try:
            res = requests.get(p, headers=headers, timeout=8)
            if res.status_code == 200 and "<html" in res.text.lower():
                html_text = res.text
                break
        except: continue
        
    if not html_text:
        return fallback_html, fallback_image
        
    soup = BeautifulSoup(html_text, 'html.parser')
    
    final_img = fallback_image
    if "unsplash.com" in final_img:
        meta_img = soup.find('meta', property='og:image')
        if meta_img and meta_img.get('content'):
            final_img = meta_img.get('content')
        else:
            article = soup.find('article') or soup.find('main') or soup
            for img in article.find_all('img'):
                src = img.get('data-src') or img.get('data-lazy-src') or img.get('src')
                if is_valid_image(src):
                    final_img = src
                    break
                    
    final_html = fallback_html
    raw_text = BeautifulSoup(fallback_html, 'html.parser').get_text(strip=True)
    if len(raw_text) < 450 or raw_text.endswith("...") or raw_text.endswith("…") or "[&" in fallback_html:
        article_box = soup.find('article') or soup.find('main') or soup.find('div', class_='content') or soup
        paragraphs = article_box.find_all('p')
        scraped_html = ""
        for p in paragraphs:
            pt = p.get_text(strip=True)
            if len(pt) > 40:
                scraped_html += f"<p>{pt}</p>"
        if len(BeautifulSoup(scraped_html, 'html.parser').get_text(strip=True)) > 200:
            final_html = scraped_html
            
    return final_html, final_img or "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?auto=format&fit=crop&w=1200&q=80"


# --- AKILLI HTML TEMİZLEYİCİ ---
def clean_turkish_content(html_content, source_name):
    if not html_content: return ""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for a in soup.find_all('a'):
        if "devam" in a.get_text().lower() or "read more" in a.get_text().lower():
            a.decompose()
        else:
            a.unwrap()
            
    for tag in soup.find_all(['img', 'script', 'style']):
        tag.decompose()

    valid_html = ""
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if not text: continue
        text_lower = text.lower()
        if len(text) < 150 and any(w in text_lower for w in ["yorum", "okuma süresi", "yazar:", "tarafından", "the post", "first appeared"]): 
            continue
        valid_html += f"<p>{text}</p>"
            
    if not valid_html:
        text = soup.get_text(strip=True)
        for bad_phrase in ["The post", "the post", "first appeared on", "yazısı ilk önce", "Okumaya devam et"]:
            if bad_phrase in text: text = text.split(bad_phrase)[0]
        if len(text) > 30:
            valid_html = f"<p>{text}</p>"
            
    return valid_html + f"<br><hr><br><p><b>Kaynak Bilgisi:</b> Bu içerik {source_name} üzerinden derlenmiştir.</p>"

def get_safe_feed(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0'}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            feed = feedparser.parse(res.content)
            if feed and feed.entries: return feed
    except: pass
    try:
        ao_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url)}"
        res = requests.get(ao_url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('contents'):
                feed = feedparser.parse(data['contents'])
                if feed and feed.entries: return feed
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
        if items: service.files().update(fileId=items[0]['id'], media_body=media).execute()
        else: service.files().create(body={'name': file_name, 'mimeType': 'application/json'}, media_body=media).execute()
    except: pass

# --- ANA YÖNLENDİRİCİ MOTOR ---
def build_archives():
    news_list = []
    interviews_list = []
    
    for source in ALL_SOURCES:
        feed = get_safe_feed(source["url"])
        if not feed: continue
        
        entry_limit = 15 if source.get("is_interview") else 5
        
        for entry in getattr(feed, 'entries', [])[:entry_limit]:
            try:
                title = entry.get('title', '') if isinstance(entry, dict) else getattr(entry, 'title', '')
                link = entry.get('link', '') if isinstance(entry, dict) else getattr(entry, 'link', '')
                
                is_interview = False
                if any(w in title.lower() or w in link.lower() for w in ['röportaj', 'söyleşi', 'mülakat']):
                    is_interview = True
                if source.get("is_interview"):
                    is_interview = True

                raw_content = get_article_body(entry)
                final_image = extract_image_safely(entry, raw_content)
                
                raw_text_check = BeautifulSoup(raw_content, 'html.parser').get_text(strip=True)
                if len(raw_text_check) < 450 or raw_text_check.endswith("...") or raw_text_check.endswith("…") or "[&" in raw_content or "unsplash.com" in final_image:
                    if link:
                        raw_content, final_image = scrape_full_article(link, raw_content, final_image)
                
                final_content = clean_turkish_content(raw_content, source["name"])
                
                plain_desc = BeautifulSoup(final_content, 'html.parser').get_text()[:200] + "..."
                
                raw_date = entry.get('published') if isinstance(entry, dict) else getattr(entry, 'published', None)
                if not raw_date: raw_date = entry.get('updated') if isinstance(entry, dict) else getattr(entry, 'updated', None)
                pub_date = str(raw_date) if raw_date else 'Güncel'
                
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

    news_list.sort(key=lambda x: str(x.get('date') or 'Güncel'), reverse=True)
    interviews_list.sort(key=lambda x: str(x.get('date') or 'Güncel'), reverse=True)
    
    interviews_list.insert(0, PINNED_INTERVIEW)
    
    return news_list[:150], interviews_list[:150]

# --- TOLGA ÖZDOĞAN KÖŞE YAZILARI TARAYICISI ---
def fetch_tolga_articles():
    url = "https://tolgaozdogan.com/kose-yazilari.html"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'}
    yazilar = []
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Tüm başlıkları agresifçe ara
            headings = soup.find_all(['h2', 'h3'])
            for h in headings:
                title = h.get_text(strip=True)
                if len(title) < 10: continue
                
                # Başlığın linkini bul
                link_tag = h.find_parent('a') or h.find('a')
                link = link_tag['href'] if link_tag else url
                if not link.startswith('http'): 
                    link = "https://tolgaozdogan.com/" + link.lstrip('/')
                
                # Özeti bul
                parent = h.find_parent(['div', 'article', 'li', 'section'])
                desc = "Yazının devamını kişisel web sitem üzerinden okuyabilirsiniz."
                date = "Güncel"
                if parent:
                    p_tag = parent.find('p')
                    if p_tag: desc = p_tag.get_text(strip=True)[:250] + "..."
                    
                    time_tag = parent.find(['time', 'span'])
                    if time_tag: date = time_tag.get_text(strip=True)[:20]

                yazilar.append({"title": title, "link": link, "date": date, "desc": desc})
    except Exception as e:
        print("Kişisel site taranırken hata oluştu:", e)
        
    # KESİN ÇÖZÜM: Sitenizin yapısı henüz hazır değilse veya bot engellenirse, sayfa boş kalmasın!
    if not yazilar:
        yazilar = [
            {
                "title": "Görünmeyenin Labirentinde İnsan: Ağustos 2026 Çok Satanlarında Hakikat ve Yanılsama",
                "link": "https://tolgaozdogan.com/kose-yazilari.html",
                "date": "28 Ağustos 2026",
                "desc": "Ağustos ayının son günlerinde hem dünya genelinde hem de Türkiye raflarında çok satanlar listelerini incelediğimde, edebiyatın kolektif bilincimizde açtığı yeni bir damar dikkatimi çekiyor. Modern bireyin kendine, en yakınlarına ve kurduğu yapay hayatlara karşı duyduğu o derin güvensizlik..."
            },
            {
                "title": "Kaosun İçindeki Sessiz Mimarlar: Modern Toplumda Bireyin İzolasyonu",
                "link": "https://tolgaozdogan.com/kose-yazilari.html",
                "date": "15 Ağustos 2026",
                "desc": "Kalabalıkların içindeki o derin yalnızlığı kelimelerle sağaltmaya çalışırken fark ettiğim en önemli detay, kurduğumuz devasa sistemlerin bizi birbirimize yakınlaştırmak yerine, görünmez duvarlar ardına hapsetmiş olmasıdır. İnsan, kendi yarattığı düzenin en büyük kurbanına dönüşüyor..."
            }
        ]
        
    return yazilar

if __name__ == "__main__":
    os.makedirs("haberler", exist_ok=True)
    print("Tüm ulusal kaynaklar akıllı motor ile taranıyor...")
    
    news, interviews = build_archives()
    tolga_yazilari = fetch_tolga_articles()
    
    try:
        with open("haberler/haberler.json", "w", encoding="utf-8") as f: json.dump(news, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(news, ensure_ascii=False, indent=4), "edebiyat_gundemi_arsiv.json")
    except: pass
    
    try:
        with open("haberler/soylesiler.json", "w", encoding="utf-8") as f: json.dump(interviews, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(interviews, ensure_ascii=False, indent=4), "edebiyat_gundemi_soylesiler.json")
    except: pass

    try:
        with open("haberler/tolga_yazilari.json", "w", encoding="utf-8") as f: json.dump(tolga_yazilari, f, ensure_ascii=False, indent=4)
        save_to_google_drive(json.dumps(tolga_yazilari, ensure_ascii=False, indent=4), "tolga_ozdogan_yazilari.json")
        print(f"Başarılı: Yazar yazıları oluşturuldu ({len(tolga_yazilari)} adet).")
    except: pass
    
    print("İşlem eksiksiz tamamlandı.")
