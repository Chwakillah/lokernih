# Project Loker Scraping

## 1. Deskripsi Data

* **Sumber**: Data lowongan kerja diambil dari laman [loker.id](https://www.loker.id/cari-lowongan-kerja).
* **Fitur (Kolom)**:

  * `Perusahaan`: Nama perusahaan yang membuka lowongan.
  * `Posisi`: Jabatan atau posisi yang ditawarkan.
  * `Lokasi`: Daerah penempatan posisi.
  * `Sistem Kerja`: Tipe kontrak (badge pertama, misal: Kontrak, Fulltime).
  * `Pendidikan Minimal`: Tingkatan pendidikan (SMA, Sarjana/S1, Diploma).
  * `Pengalaman Kerja`: Rentang pengalaman (1-2 Tahun, 3-5 Tahun, dst).
  * `Kriteria`: Kriteria tambahan lainnya.
  * `Gaji`: Rentang gaji (diambil dari badge khusus).
* **Jumlah Data**: Total baris tergantung jumlah halaman (`max_pages`) yang di-scrape. Contoh yang dipakai 10 page (1 page =21 card): 210 entri.

## 2. Proses Scraping

* **Tools**: Python 3.x, Selenium WebDriver (Chrome), BeautifulSoup, Pandas.
* **Flow**:

  1. Inisialisasi Chrome WebDriver (opsi headless optional).
  2. Akses URL loker.id dan tunggu sampai elemen artikel lowongan (`article.card`) muncul.
  3. Scroll halaman untuk memuat konten dinamis.
  4. Parse `page_source` dengan BeautifulSoup, ekstrak elemen:

     * Nama perusahaan, posisi, lokasi.
     * Kumpulan badge (`span.badge-small`) untuk kriteria.
     * Gaji dari `div.flex.gap-2 span[translate='no']`.
  5. Klik tombol **Next** menggunakan XPath `//button[.//span[text()='Next']]`, di-scroll ke viewport, dan klik via JavaScript.
  6. Ulangi hingga jumlah halaman terpenuhi atau tombol Next tidak ditemukan.

## 3. Proses Preprocessing

* **Langkah**:

  1. Lowercase semua teks.
  2. Hapus karakter non-alfabet dan HTML tags.
  3. Tokenisasi dengan `nltk.word_tokenize`.
  4. Hapus stopwords Bahasa Indonesia.
  5. Stemming menggunakan `PorterStemmer`.
* **Contoh Sebelum-Sesudah**:

  ```python
  # Sebelum:
  "Staff Accounting Sr. – Kantor Pusat"

  # Sesudah:
  "staff account kantor pusat"
  ```

## 4. Refleksi

* **Kendala**:

  * Masih bingung mencari class untuk scrapping data tiap elemen yang diperlukan.
  * Pagination: tombol Next terkadang tertutup, perlu scrollIntoView dan klik via JS.
  * Selector kompleks: menangani kelas dengan tanda titik atau atribut `translate`.
  * Jaringan internet lambat.
* **Solusi**:

  * Gunakan `WebDriverWait` untuk kehadiran dan clickable.
  * Klik lewat `driver.execute_script("arguments[0].click()")`.
  * CSS selector atribut dan XPath untuk akurasi pemilihan elemen.

---
