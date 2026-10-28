# N-Queens sebagai CSP: Backtracking vs Backtracking + Forward Checking

Program ini merupakan implementasi penyelesaian masalah penempatan ratu (*N-Queens*) yang dimodelkan sebagai *Constraint Satisfaction Problem* (CSP). Program ini membandingkan kinerja algoritma **Backtracking (BT) polos** dengan **Backtracking + Forward Checking (BT+FC)**.

---

## 1. Versi Python
- **Python 3.14** (Kompatibel penuh dengan Python 3.9+)
- Hanya menggunakan pustaka standar (*standard library*): `json`, `argparse`, `time`, `sys`, `os`, `datetime`.
- **Tidak ada dependensi eksternal**.

---

## 2. Struktur Proyek
```text
nqueens/
├── main.py            # Titik masuk program: baca argumen, validasi, eksekusi, ringkasan, pencatatan log
├── algorithms.py      # Implementasi algoritma Backtracking dan Backtracking + Forward Checking
├── config.json        # File parameter terpusat
├── inputs/            # Berkas input skenario pengujian
│   ├── n3_tanpa_solusi.json
│   ├── n4_mudah.json
│   ├── n8_acuan.json
│   ├── n8_descending.json
│   ├── n12_sulit.json
│   └── n16_lebih_besar.json
├── results/           # Log eksperimen otomatis (results/log_eksperimen.txt)
├── requirements.txt   # Keterangan dependensi
└── README.md          # Dokumentasi proyek
```

---

## 3. Model Masalah (CSP)
- **Variabel**: $X_1, X_2, \dots, X_N$, di mana $X_i$ menyatakan **BARIS** tempat ratu diletakkan pada **KOLOM** ke-$i$.
- **Domain**: $\{1, 2, \dots, N\}$.
- **Constraint**: Untuk setiap pasangan kolom $i \neq j$:
  1. $X_i \neq X_j$ (tidak berada di baris yang sama).
  2. $|X_i - X_j| \neq |i - j|$ (tidak berada di diagonal yang sama).
- **Urutan Variabel**: Kolom 1 sampai $N$ (dari kiri ke kanan, tetap).
- **Urutan Nilai (*value_order*)**:
  - `ascending`: $1, 2, \dots, N$.
  - `descending`: $N, N-1, \dots, 1$.
- **Penghentian**: Berhenti tepat saat **solusi pertama** ditemukan.

---

## 4. Definisi Hitungan Metrik

- **Assignment**: Nilai yang lolos cek konsistensi dan disimpan pada papan.
- **Backtrack**: Assignment yang kemudian dibatalkan karena jalan buntu (*dead-end*).

### Detail Alur Algoritma:
1. **Backtracking polos**:
   - Untuk kolom $c$, coba nilai $r$ sesuai `value_order`.
   - Cek konflik **HANYA** terhadap ratu yang sudah diletakkan di kolom $1 \dots c-1$.
   - Jika lolos: `assignment += 1`, simpan penempatan ratu, lanjut ke kolom $c+1$.
   - Jika kolom berikutnya gagal: batalkan nilai tersebut, `backtrack += 1`, coba nilai berikutnya.
   - Jika semua nilai habis: gagal, mundur ke kolom sebelumnya.

2. **Backtracking + Forward Checking**:
   - Setiap kolom memiliki domain (kondisi awal penuh $\{1 \dots N\}$).
   - Untuk kolom $c$, lakukan iterasi nilai sesuai `value_order`, **HANYA** pada nilai yang masih ada di domain kolom $c$. Nilai yang sudah dicoret dilewati dan tidak dihitung apa pun.
   - Saat nilai $r$ diambil dari domain: `assignment += 1` **LANGSUNG** (dihitung **SEBELUM** pencoretan), simpan penempatan ratu.
   - Untuk setiap kolom masa depan $j > c$, coret dari $\text{domain}[j]$ nilai:
     - $r$ (konflik baris)
     - $r - (j - c)$ (konflik diagonal turun)
     - $r + (j - c)$ (konflik diagonal naik)
   - Catat semua pencoretan $(j, \text{nilai})$ dalam list agar bisa dikembalikan persis.
   - Jika ada domain kolom yang menjadi kosong: kembalikan semua pencoretan, `backtrack += 1`, coba nilai berikutnya.
   - Jika tidak ada domain kosong, lanjut ke kolom $c+1$; jika kolom berikutnya gagal: kembalikan semua pencoretan, `backtrack += 1`.

---

## 5. Tabel Angka Acuan

Berikut hasil acuan verifikasi untuk urutan nilai `ascending`:

| N | BT Assign / Backtrack | BT+FC Assign / Backtrack | Solusi Pertama |
|---|---|---|---|
| **4** | 8 / 4 | 8 / 4 | `(2, 4, 1, 3)` |
| **8** | 113 / 105 | 88 / 80 | `(1, 5, 8, 6, 3, 7, 2, 4)` |
| **12** | 261 / 249 | 193 / 181 | `(1, 3, 5, 8, 10, 12, 6, 11, 2, 7, 9, 4)` |

---

## 6. Format File Input dan Konfigurasi

### File Input (`inputs/*.json`)
Format JSON:
```json
{
  "n": 8,
  "value_order": "ascending"
}
```
*Catatan: Nilai `value_order` dapat berupa `"ascending"` atau `"descending"`.*

### File Konfigurasi Terpusat (`config.json`)
```json
{
  "variable_order": "left_to_right",
  "default_value_order": "ascending",
  "repeat_waktu": 5
}
```
- `variable_order`: Urutan eksplorasi variabel (hanya `"left_to_right"` yang didukung).
- `default_value_order`: Nilai default urutan jika tidak didefinisikan pada file input.
- `repeat_waktu`: Jumlah pengulangan eksekusi algoritma untuk menghitung rata-rata waktu eksekusi.
- Jika file `config.json` tidak ditemukan, program secara otomatis menggunakan nilai default di atas dan menampilkan pesan peringatan singkat.

---

## 7. Cara Menjalankan Program

Program mendukung dua cara eksekusi:

### A. Mode Interaktif (Langsung Tekan Run di VS Code)
Cukup jalankan program tanpa argumen:
```bash
python main.py
```
*(atau tekan tombol **Play / Run** di VS Code)*. Menu interaktif akan muncul di terminal untuk memilih skenario masukan (1–6), algoritma yang ingin dijalankan, dan apakah ingin mengaktifkan mode `--trace`.

---

### B. Mode Baris Perintah (CLI)
Jalankan perintah langsung melalui terminal:

#### Menjalankan Kedua Algoritma (Default)
```bash
python main.py --input inputs/n4_mudah.json
```

#### Menjalankan Hanya Backtracking
```bash
python main.py --input inputs/n8_acuan.json --algo bt
```

#### Menjalankan Hanya Backtracking + Forward Checking
```bash
python main.py --input inputs/n8_acuan.json --algo bt_fc
```

#### Menjalankan dengan Mode Trace (Langkah demi Langkah)
```bash
python main.py --input inputs/n4_mudah.json --algo bt --trace
python main.py --input inputs/n4_mudah.json --algo bt_fc --trace
```

#### Menggunakan File Konfigurasi Kustom
```bash
python main.py --input inputs/n8_acuan.json --config config.json
```

---

## 8. Log Eksperimen
Setiap kali pengujian dijalankan (baik lewat menu interaktif maupun argumen baris perintah), hasil eksperimen akan otomatis disimpan ke dalam berkas terpisah berurutan pada folder `results/`:
- `results/eksperimen_1.txt`
- `results/eksperimen_2.txt`
- `results/eksperimen_3.txt`, dst.

Selain itu, berkas `results/log_eksperimen.txt` selalu diperbarui dengan salinan hasil eksperimen paling terakhir. Folder `results/` akan dibuat secara otomatis jika belum tersedia.

