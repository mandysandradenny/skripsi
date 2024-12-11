# Sistem Manajemen Inventori Melalui Prediksi Penjualan pada Toko LAYBox
Sistem berbasis web yang dirancang untuk memberikan informasi manajemen inventori melalui hasil prediksi penjualan pada toko online LAYBox

## Fitur ✨
- Prediksi penjualan menggunakan metode Gated Recurrent Unit (GRU).
- Manajemen Inventori menggunakan metode Probabilistik Sederhana.
- Upload data penjualan dalam format Excel yang diunduh dari website Tokopedia.
- Visualisasi hasil prediksi dalam bentuk grafik dan tabel.
- Tabel informasi manajemen inventori mencakup:
  + Safety Stock
  + Reorder Point
  + Stok Optimal
  + Ekspektasi Kekurangan Barang

## Requirements 📋
- Virtual Environment di VS Code (Disarankan)
- Python 3.xx
- XAMPP / MySQL

## Cara Instalasi Program 💻
1. Clone repositori:
   ```
   git clone <URL_REPOSITORY>;
   ```
2. Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   ```
   Windows:
   ```
   venv\Scripts\activate
   ```
   Linux:
   ```
   source venv/bin/activate
   ```
4. Pastikan XAMPP telah berjalan [Klik untuk ke bagian Informasi Instalasi XAMPP](#cara-instalasi-xampp)
5. Install requirements library:
   ```
   pip install -r requirements.txt
   ```  
6. Copy syntax pada file `init.sql` dan jalankan di phpmyadmin
7. Daftarkan user terlebih dahulu:
   - Buka file `regist.py`
   - Uncomment code `register_user('username', 'password')`
   - Masukkan username dan password yang diinginkan `register_user('admin', 'admin')`
   - Jalankan file `regist.py`
   - Comment kembali code `register_user('username', 'password')`
9. Jalankan sistem:
   ```
   python app.py
   ```
10. Sistem sudah siap dan dapat diakses pada browser <br>
    🌐 <http://localhost:8080>

## Manual Program 📖
Manual program berisikan cara penggunaan web yang dapat dilihat pada file `manual_program.pdf` <br>
[Klik untuk baca Manual Program](manual_program.pdf)

Data untuk mencoba sistem:
[Klik untuk Unduh Data](https://drive.google.com/drive/folders/16UQujsiP80QSte23-4mEruWhwe4uFSh1?usp=sharing)

## Cara Instalasi XAMPP

