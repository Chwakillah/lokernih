import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    return webdriver.Chrome(service=Service(), options=options)

def scroll_page(driver, steps=20, pause=0.5):
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(pause)

def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    for card in soup.find_all("article", class_="card"):
        # Perusahaan
        perusahaan_tag = card.find("span", class_="text-sm text-secondary-500")
        perusahaan = perusahaan_tag.get_text(strip=True) if perusahaan_tag else ""
        # Posisi
        posisi_tag = card.select_one("h3.text-lg")
        posisi = posisi_tag.get_text(strip=True) if posisi_tag else ""
        # Lokasi
        lokasi_tag = card.find("span", attrs={"class": "mt-0.5"})
        lokasi = lokasi_tag.get_text(strip=True) if lokasi_tag else ""
        # Kriteria
        badge_spans = card.select("span.badge-small")
        kriteria = [b.get_text(strip=True) for b in badge_spans]
        # Gaji
        gaji_tag = card.select_one("div.flex.gap-2 span[translate='no']")
        gaji = gaji_tag.get_text(strip=True) if gaji_tag else ""
        jobs.append({
            "Perusahaan": perusahaan,
            "Posisi": posisi,
            "Lokasi": lokasi,
            "Kriteria": kriteria,
            "Gaji": gaji
        })
    return jobs

def scrape_all_pages(base_url, max_pages=5):
    driver = setup_driver()
    driver.get(base_url)
    all_jobs = []
    for page in range(max_pages):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.card"))
        )
        scroll_page(driver)
        time.sleep(1)
        all_jobs.extend(parse_jobs(driver.page_source))
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[.//span[normalize-space(text())='Next']]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
            time.sleep(0.2)
            next_btn.click()
            time.sleep(2)
        except:
            break
    driver.quit()
    return pd.DataFrame(all_jobs)

def split_kriteria(df):
    def extract_fields(badges):
        sistem = badges[0] if badges else ""
        looks = ['sma','sarjana','diploma']
        pendidikan = next((b for b in badges if any(w in b.lower() for w in looks)), "")
        pengalaman = next((b for b in badges if 'tahun' in b.lower()), "")
        sisanya = [b for b in badges if b not in {sistem, pendidikan, pengalaman}]
        return pd.Series([sistem, pendidikan, pengalaman, sisanya])

    df[['Sistem Kerja','Pendidikan Minimal','Pengalaman Kerja','Kriteria Lain']] = \
        df['Kriteria'].apply(extract_fields)

    df = df.drop(columns=['Kriteria'])
    df = df.rename(columns={'Kriteria Lain': 'Kriteria'})
    return df

if __name__ == "__main__":
    df = scrape_all_pages(
        base_url="https://www.loker.id/cari-lowongan-kerja",
        max_pages=10
    )
    df = split_kriteria(df)
    print(df)
    df.to_csv("loker_scrapp.csv", index=False)
    df.to_excel("loker_scrapp.xlsx", index=False)
