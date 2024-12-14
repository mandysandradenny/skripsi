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
   git clone https://github.com/mandysandradenny/skripsi
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
4. Pastikan XAMPP telah berjalan [Klik untuk ke bagian Informasi Instalasi XAMPP](#cara-instalasi-XAMPP)
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
   - Melakukan pengecekan user berhasil terdaftar:
     + Buka database `skripsi` pada phpMyAdmin.
     + Klik tabel `user`
     + Username yang didaftarkan akan tampil sebagai value pada tabel.
8. Jalankan sistem pada virtual environment `venv`:
   ```
   python app.py
   ```
9. Sistem sudah siap dan dapat diakses pada browser. <br>
    🌐 **<http://localhost:8080>**

### Notes 📝
Jika terdapat error seperti dibawah ini:
```bash
2024-12-14 18:32:06.889872: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results
due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2024-12-14 18:32:08.340456: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results
due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
 * Serving Flask app 'app'
 * Debug mode: on
An attempt was made to access a socket in a way forbidden by its access permissions
```
Maka ubah port **8080** pada file `app.py` baris 134-135
```js
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
Jalankan sistem dengan port yang telah diubah **<http://localhost:5000>**

## Manual Program 📖
Manual program berisikan cara penggunaan web yang dapat dilihat pada file `manual_program.pdf` <br>
[Klik untuk baca Manual Program](manual_program.pdf)

Data untuk mencoba sistem:
[Klik untuk Unduh Data](https://drive.google.com/drive/folders/16UQujsiP80QSte23-4mEruWhwe4uFSh1?usp=sharing)

## Cara Instalasi XAMPP
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
