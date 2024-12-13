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
   git clone https://github.com/mandysandradenny/skripsi;
   ```
2. Buka folder repositori 'skripsi' di VSCode.
3. Buat dan aktifkan virtual environment di VSCode:
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
4. Pastikan XAMPP telah berjalan [Klik untuk ke bagian Informasi Instalasi XAMPP](#cara-instalasi-XAMPP-<img src="https://seeklogo.com/images/X/xampp-logo-1C1A9E3689-seeklogo.com.png" width="33">)
5. Copy syntax pada file `init.sql` dan jalankan di phpmyadmin.
6. Install requirements library:
   ```
   pip install -r requirements.txt
   ```  
7. Daftarkan user terlebih dahulu:
   - Buka file `regist.py`
   - Uncomment code `register_user('username', 'password')`
   - Masukkan username dan password yang diinginkan `register_user('admin', 'admin')`
   - Jalankan file `regist.py`
   - Comment kembali code `register_user('username', 'password')`
8. Jalankan sistem:
   ```
   python app.py
   ```
9. Sistem sudah siap dan dapat diakses pada browser. <br>
    🌐 <http://localhost:8080>

## Manual Program 📖
Manual program berisikan cara penggunaan web yang dapat dilihat pada file `manual_program.pdf` <br>
[Klik untuk baca Manual Program](manual_program.pdf)

Data untuk mencoba sistem:
[Klik untuk Unduh Data](https://drive.google.com/drive/folders/16UQujsiP80QSte23-4mEruWhwe4uFSh1?usp=sharing)

## Cara Instalasi XAMPP <img src="https://seeklogo.com/images/X/xampp-logo-1C1A9E3689-seeklogo.com.png" width="33">

1. Buka website <https://www.apachefriends.org/>
2. Unduh XAMPP sesuai dengan sistem operasi yang digunakan.
3. Jalankan file instalasi (**pastikan Apache dan MySQL dicentang**)
4. Setelah instalasi selesai, jalankan aplikasi `XAMPP Control Panel`.
5. Klik tombol **Start** pada modul **Apache** dan **MySQL** (tampil highlight hijau pada modul)
6. Memastikan MySQL berjalan dan dapat digunakan: <br>
   - Buka browser dan akses URL <http://localhost/>
   - Pada halaman dashboard, klik menu `phpMyAdmin`
   - Akan tampil tampilan antarmuka **phpMyAdmin**
   - Klik `SQL` untuk menjalankan syntax yang digunakan.
