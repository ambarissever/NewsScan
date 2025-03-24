import requests
import time
import re
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

keywords = ["Seçim", "Mahkeme", "Ülke", "Milliyet", "Ordu"]

#Enter the URL addresses of the news pages
site_dictionary = {
    "https://www.ornekhabersitesi.com/turkce/topics/ckdxn2xk95gt": "page=2",
    "https://tr.ornekhabersitesi.com/haber/avrupa/turkiye": "p=2"
}

class_lists = [
    "promo-text", "m-object__title__link", "the-media-object__title"
]

def fetch_news_from_site(url, class_list):
    """
    Verilen URL'den başlıkları çeker.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    all_titles = []
    for class_name in class_list:
        titles = soup.find_all(class_=class_name)
        if titles:
            all_titles.extend([title.get_text(strip=True) for title in titles])
    
    return all_titles

def get_all_titles_for_site(site_url, class_list, max_titles):
    """
    Belirtilen site ve class listesiyle başlıkları toplar.
    """
    all_titles = []
    page_number = 1
    while True:
        url_with_page = f"{site_url}?page={page_number}"
        
        titles = fetch_news_from_site(url_with_page, class_list)
        if not titles:
            print(f"Sayfa {page_number} boş, duruluyor...")
            break
        
        all_titles.extend(titles)
        
        if len(all_titles) >= max_titles:
            break
        
        page_number += 1
        time.sleep(5)
    
    return all_titles

def analyze_keywords(titles, keywords):
    """
    Başlıklar içinde anahtar kelimeleri hem capitalize hem de lowercase olarak arar.
    """
    analyzed_data = []
    
    for title in titles:
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.capitalize()) + r'\w*'
            if re.search(pattern, title, re.IGNORECASE):
                analyzed_data.append((title, keyword))
            
            pattern_lower = r'\b' + re.escape(keyword.lower()) + r'\w*'
            if re.search(pattern_lower, title, re.IGNORECASE):
                analyzed_data.append((title, keyword))
    
    return analyzed_data

max_titles = int(input("Kaç başlık almak istersiniz? "))

all_data = []

for site_url, page_param in site_dictionary.items():
    print(f"Siteye giriş yapılıyor: {site_url}")
    
    titles = get_all_titles_for_site(site_url, class_lists, max_titles)
    
    if titles:   
        site_data = analyze_keywords(titles, keywords)
        
        for title, keyword in site_data:
            all_data.append({"Kaynak": site_url, "Başlık": title, "Anahtar Kelime": keyword})
    else:
        print("Başlıklar bulunamadı.")

df = pd.DataFrame(all_data)

summary = df.groupby(["Kaynak", "Anahtar Kelime"]).size().unstack(fill_value=0)

print("Anahtar Kelime Dağılımı:")
print(summary)

summary.plot(kind="bar", figsize=(10, 6))
plt.title("Haber Sitelerinde Anahtar Kelime Dağılımı")
plt.xlabel("Kaynak")
plt.ylabel("Anahtar Kelime Sayısı")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

with open("haber_basliklari.txt", "w", encoding="utf-8") as f:
    for title in df["Başlık"]:
        f.write(title + "\n")

print(f"Tüm toplanan haber başlıkları kaydedildi.")
