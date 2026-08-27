def fetch_news():
    all_articles = []
    for url in RSS_SOURCES:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get('title', 'Başlıksız')
                link = entry.get('link', '#')
                published = entry.get('published', entry.get('updated', ''))
                
                content = ""
                if hasattr(entry, 'content') and entry.content:
                    content = entry.content[0].value
                elif hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description
                
                # EĞER METİN BOŞ GELİRSE BAŞLIĞA GÖRE ÖZEL İÇERİK ÜRET
                if not content or len(content.strip()) < 15:
                    content = f"<p><strong>{title}</strong> hakkında edebiyat dünyasından derlenen en güncel detaylar ve ayrıntılar kısa süre içinde bu alanda yer alacaktır. Haberin tüm ayrıntılarını ve gelişmelerini takip edebilirsiniz.</p>"
                
                image = extract_image(entry, content)
                cleaned_content = clean_html(content)
                
                soup_desc = BeautifulSoup(cleaned_content, 'html.parser')
                plain_desc = soup_desc.get_text()[:180] + "..."
                
                article = {
                    "title": title,
                    "link": link,
                    "date": published,
                    "category": assign_category(title, entry.get('tags', [])),
                    "desc": plain_desc,
                    "content": cleaned_content,
                    "image": image
                }
                all_articles.append(article)
        except Exception as e:
            print(f"Hata oluştu ({url}): {e}")
            
    return all_articles
