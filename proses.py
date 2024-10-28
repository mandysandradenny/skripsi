import numpy as np
import scipy.stats as stats
import pandas as pd
import re
import joblib
from datetime import datetime, timedelta 
from sklearn.impute import KNNImputer
from sklearn.preprocessing import RobustScaler, LabelEncoder, StandardScaler
from tensorflow.keras.models import Sequential, load_model # type: ignore
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
import hashlib
from db import insert_users


def preprocessing(file):
    df = pd.read_excel(file, skiprows=4)
    # Hapus baris yang punya tanggal pesanan dibatalkan
    df = df[df['Tanggal Pesanan Dibatalkan'].isna()]

    columns_to_drop = [
        'Nomor', 'Nomor Invoice', 'Status Terakhir','Harga Jual (IDR)', 'Total Penjualan (IDR)', 'Tanggal Pesanan Selesai', 'Waktu Pesanan Selesai',
        'Tanggal Pesanan Dibatalkan', 'Waktu Pesanan Dibatalkan', 'Tipe Produk',
        'Nomor SKU', 'Catatan Produk Pembeli', 'Catatan Produk Penjual', 'Jenis Kupon Toko Terpakai',
        'Kode Kupon Toko Yang Digunakan', 'Biaya Pengiriman Tunai (IDR)', 'Biaya Asuransi Pengiriman (IDR)',
        'Total Biaya Pengiriman (IDR)', 'Nama Pembeli', 'No Telp Pembeli', 'Nama Penerima', 'No Telp Penerima',
        'Alamat Pengiriman', 'Kota', 'Provinsi', 'Nama Kurir', 'Tipe Pengiriman (regular, same day, etc)',
        'No Resi / Kode Booking', 'Tanggal Pengiriman Barang', 'Waktu Pengiriman Barang', 'Gudang Pengiriman',
        'Nama Campaign', 'Nama Bundling', 'Tipe Bebas Ongkir (Bebas Ongkir, Bebas Ongkir DT)', 'COD', 'Jumlah Produk Yang Dikurangkan',
        'Total Pengurangan (IDR)', 'Nama Penawaran Terpakai', 'Tingkatan Promosi Terpakai', 'Diskon Penawaran Terpakai (IDR)', 'Harga Awal (IDR)',
        'Harga Satuan Bundling (IDR)', 'Diskon Produk (IDR)', 'Jumlah Subsidi Tokopedia (IDR)', 'Nilai Kupon Toko Terpakai (IDR)']

    # Drop columns that are not needed
    df = df.drop(columns = columns_to_drop)

    df['Tanggal Pembayaran'] = pd.to_datetime(df['Tanggal Pembayaran'], format='%d-%m-%Y %H:%M:%S').dt.strftime('%d-%m-%Y')
    df['Tanggal Pembayaran'] = pd.to_datetime(df['Tanggal Pembayaran'], format='%d-%m-%Y') # Convert 'Tanggal Pembayaran' to datetime object
    
    # Menyaring model yang tidak ingin digunakan
    model_tidak_diinginkan = ['model botol', 'model nampan', 'tanpa tutup', 'lembaran', 'lembar', 'layer', 'bubble', 'tatakan']

    # Mengubah semua teks dalam 'Nama Produk' menjadi huruf kecil
    df['nama produk lowercase'] = df['Nama Produk'].str.lower()

    pattern = '|'.join(model_tidak_diinginkan)  # Membuat pola regex dari daftar
    df_filtered = df[~df['nama produk lowercase'].str.contains(pattern, na=False)] # Added na=False to handle potential NaN values

    df = df_filtered.drop(columns=['nama produk lowercase'])

    # Get today's date
    today = df.iloc[0]['Tanggal Pembayaran']

    # Calculate the first day of the current month
    first_day = today.replace(day=1)

    # Calculate the last day of the previous month
    last_day = first_day + timedelta(days=31)
    last_day = last_day.replace(day=1) - timedelta(days=1)

    # Buat rentang tanggal lengkap
    start_date = pd.to_datetime(first_day.strftime('%Y-%m-%d'))
    if datetime.now() < last_day:
        end_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
    else:
        end_date = pd.to_datetime(last_day.strftime('%Y-%m-%d'))

    date_range = pd.date_range(start=start_date, end=end_date)

    # Buat DataFrame baru dengan tanggal lengkap
    df_lengkap = pd.DataFrame({'Tanggal Pembayaran': date_range})

    # Gabungkan dengan DataFrame asli, isi nilai yang hilang dengan 0
    df_lengkap = df_lengkap.merge(df, on='Tanggal Pembayaran', how='left')
    # df_lengkap = df_lengkap.merge(df, on='Tanggal Pembayaran', how='left').fillna(0)

    # Mengisi nilai yang hilang pada kolom 'Nama Produk' menggunakan forward fill dan backward fill
    df_lengkap['Nama Produk'] = df_lengkap['Nama Produk'].fillna(method='ffill').fillna(method='bfill')

    # Pisahkan kolom numerik yang akan diimputasi
    numeric_data = df_lengkap[['Jumlah Produk Dibeli']]

    # # Scaling data
    # scaler = StandardScaler()
    # scaled_data = scaler.fit_transform(numeric_data)

    imputer = KNNImputer(n_neighbors=11)
    imputed_data = imputer.fit_transform(numeric_data)
    imputed_series = pd.Series(imputed_data.ravel())

    df_lengkap.fillna({'Jumlah Produk Dibeli': imputed_series}, inplace=True)

    df_lengkap['Ukuran'] = df_lengkap['Nama Produk'].apply(lambda product_name: 
    re.search(r'\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*(?:½)?\s*[×xX]\s*\d+[.,]?\d*\s*(cm)?', product_name, re.IGNORECASE).group(0).strip().replace('×', 'x').replace('X', 'x').replace('Cm', 'cm').replace('CM', 'cm').replace(' ', '')
    if re.search(r'\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*(?:½)?\s*[×xX]\s*\d+[.,]?\d*\s*(cm)?', product_name, re.IGNORECASE) 
    else np.nan)

    df_lengkap = df_lengkap[df_lengkap['Ukuran'].apply(lambda x: len(re.findall(r'[×xX]', str(x))) == 2)]
    df_lengkap = df_lengkap.drop('Nama Produk', axis=1)
    df_lengkap = df_lengkap[['Tanggal Pembayaran', 'Ukuran', 'Jumlah Produk Dibeli']]

    df_lengkap['Tanggal Pembayaran'] = pd.to_datetime(df_lengkap['Tanggal Pembayaran']).dt.strftime('%Y-%m-%d')

    # # Mengelompokan total penjualan produk pada tanggal yang sama dan ukuran yang sama
    # df_lengkap = df_lengkap.groupby(['Tanggal Pembayaran', 'Ukuran']).agg({
    #     'Jumlah Produk Dibeli': 'sum',
    # }).reset_index()
    # print(df_lengkap)

    return df_lengkap

def predict_model(data):
    # Load model GRU yang sudah disimpan
    model = load_model('model/model_gru.keras')

    # Load RobustScaler
    scaler = joblib.load('model/scaler.pkl')

    # Load LabelEncoder classes
    le = LabelEncoder()
    le.classes_ = np.load('model/classes.npy', allow_pickle=True)

    # # Identifikasi ukuran baru yang tidak dikenal (tidak ada di le.classes_)
    # unknown_sizes = ~data['Ukuran'].isin(le.classes_)

    # # Tampilkan ukuran yang tidak dikenal (jika ada)
    # if unknown_sizes.any():
    #     print(f"Ukuran baru yang tidak dikenal ditemukan: {data.loc[unknown_sizes, 'Ukuran'].unique()}")

    # # Filter data yang mengandung ukuran yang dikenal
    # data = data[~unknown_sizes].copy()

    # LabelEncoder pada kolom 'Ukuran'
    data['Ukuran'] = le.transform(data['Ukuran'])

    # Misalnya, data_new adalah DataFrame baru yang ingin diprediksi
    seq_length = 14  # Harus sama dengan yang digunakan saat pelatihan
    X_new = []
    dates = []  # List untuk menyimpan tanggal

    for i in range(len(data) - seq_length):
        X_new.append(data.iloc[i:i+seq_length, 1:3].values)  # Ambil jumlah produk dibeli dan ukuran
        dates.append(data.iloc[i+seq_length]['Tanggal Pembayaran']) # Menyimpan tanggal pembayaran untuk prediksi

    data = np.array(X_new)  # Ubah ke array nump

    # Reshape data menjadi 2D untuk melakukan scaling pada kolom jumlah produk dibeli (kolom ke-1)
    X_reshaped = data.reshape(-1, data.shape[-1])
    # X_reshaped = data.reshape(-1, 1)
    X_scaled = data.copy()
    X_scaled[:, :, 1] = scaler.transform(X_reshaped[:, 1].reshape(-1, 1)).reshape(data.shape[0], data.shape[1])

    # Lakukan prediksi
    prediction = model.predict(X_scaled)

    # Prediksi untuk Jumlah Produk Dibeli -> inverse scaling (hanya pada kolom jumlah produk dibeli)
    predicted_jumlah_produk_load = scaler.inverse_transform(prediction[0].reshape(-1, 1))

    # Prediksi untuk Ukuran -> ambil prediksi kelas terbesar
    predicted_ukuran_load = np.argmax(prediction[1], axis=1)

    # Mengembalikan hasil prediksi ukuran dari encoded labels ke ukuran asli
    predicted_ukuran_asli_load = []
    valid_classes = np.arange(len(le.classes_))

    for y in predicted_ukuran_load:
        if y in valid_classes:
            predicted_ukuran_asli_load.append(le.inverse_transform([y])[0])  # Transform ukuran valid
        else:
            predicted_ukuran_asli_load.append("Unknown")  # Nilai default untuk ukuran yang tidak dikenali

    # Mendapatkan tanggal terakhir dari data yang diupload
    tanggal_akhir = pd.to_datetime(dates).max()

    # Ambil hasil prediksi 30 data dan jika ada nilai negatif diubah menjadi 0
    # predicted_jumlah_produk = np.where(predicted_jumlah_produk_load[:30].flatten() < 0, 0, predicted_jumlah_produk_load[:30].flatten())
    predicted_jumlah_produk = np.where(predicted_jumlah_produk_load.flatten() < 0, 0, predicted_jumlah_produk_load.flatten())

    # Pastikan panjang `predicted_jumlah_produk` dan `predicted_ukuran_asli_load` sama
    min_length = min(len(predicted_jumlah_produk), len(predicted_ukuran_asli_load))

    # Potong keduanya agar sama panjang
    predicted_jumlah_produk = predicted_jumlah_produk[:min_length]
    predicted_ukuran = predicted_ukuran_asli_load[:min_length]
    
    # Tanggal Prediksi
    # tanggal_prediksi = pd.date_range(start=tanggal_akhir + pd.Timedelta(days=1), periods=min_length).to_period('M')
    # Tentukan bulan dan tahun prediksi (bulan setelah tanggal_akhir)
    bulan_tahun_prediksi = (tanggal_akhir + pd.Timedelta(days=1)).replace(day=1).strftime('%Y-%m')

    # Mengisi kolom 'Tanggal Pembayaran' dengan bulan_tahun_prediksi yang diulang sesuai panjang prediksi
    tanggal_prediksi = [bulan_tahun_prediksi] * min_length

    # predicted_ukuran = predicted_ukuran_asli_load[:30]
    
    # Membuat DataFrame untuk membandingkan hasil prediksi
    hasil_prediksi_load = pd.DataFrame({
        'Tanggal Pembayaran': tanggal_prediksi,
        'Ukuran Prediksi': predicted_ukuran,
        'Jumlah Produk Dibeli Prediksi': predicted_jumlah_produk.flatten()
    })

    return hasil_prediksi_load

# Grafik menggunakan matplotlib
def create_chart(ukuran, qty_data):
    plt.figure(figsize=(6, 4))
    plt.bar(range(1, len(qty_data) + 1), qty_data, color='skyblue')  # Membuat bar chart dengan X mulai dari 1, 2, 3, dst.

    plt.title(f"Prediksi untuk Ukuran {ukuran}")
    plt.xlabel("Order")
    plt.ylabel("Produk Dibeli")

    plt.xticks(range(1, len(qty_data) + 1))  # Menampilkan ticks di sumbu X mulai dari 1, 2, 3, dst.

    # Simpan grafik ke dalam buffer dan encode menjadi base64
    buffer = io.BytesIO()  # Membuat buffer di memory
    plt.savefig(buffer, format="png")  # Simpan grafik ke buffer dengan format PNG
    buffer.seek(0)  # Reset pointer buffer ke awal
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')  # Encode buffer ke base64
    plt.close()  # Tutup figure untuk membebaskan memori

    return f"data:image/png;base64,{image_base64}"

def inventory_management(data):
    # Nilai z untuk tingkat kepercayaan 95%
    Za = 1.65
    # Lead time dalam hari (misalnya 2 hari)
    L = 2

    # Buat data frame
    data = pd.DataFrame({
        'Jumlah Produk Dibeli Prediksi': [x[1] for x in data],
        'Ukuran Prediksi': [x[0] for x in data]
    })

    # Loop melalui setiap produk
    for ukuran in np.unique(data['Ukuran Prediksi']):

        # Filter data berdasarkan ukuran produk
        produk_data = data[data['Ukuran Prediksi'] == ukuran]

        # Data yang diprediksi untuk produk tertentu (jumlah produk dibeli)
        y_pred_product = produk_data['Jumlah Produk Dibeli Prediksi'].values

        # Hitung standar deviasi dari error prediksi
        S = np.std(y_pred_product)

        # Hitung standar deviasi selama lead time (dalam hari)
        # S_L = S * np.sqrt(L)
        S_L = S * np.sqrt(L)

        # Hitung nilai N
        phi = stats.norm.pdf(Za)
        Psi = stats.norm.cdf(Za) * Za
        N = S_L * (Psi - phi)

        # Hitung cadangan pengaman (SS)
        SS = Za * S_L

        # Rata-rata permintaan selama lead time (dalam hari)
        DL = np.mean(y_pred_product) * L

        # Hitung saat pemesanan ulang (r)
        r = DL + SS

        # Hitung tingkat pelayanan (η)
        eta = 1 - (N / DL) if DL != 0 else 0  # Menghindari pembagian dengan nol

        # Hitung stok optimal
        optimal_stock = SS + r

        # Simpan hasil dalam dictionary
        return {
            "SS": round(SS),
            "ReorderPoint": round(r),
            "OptimalStock": round(optimal_stock),
            "Ekspektasi": round(N)
        }
    
def inventory_raw(data):
    # Nilai z untuk tingkat kepercayaan 95%
    Za = 1.65
    # Lead time dalam hari (misalnya 2 hari)
    L = 7

    # Buat data frame
    data = pd.DataFrame({
        'Jumlah Produk Dibeli Prediksi': [x[1] for x in data],
        'Ukuran Prediksi': [x[0] for x in data]
    })

    # Loop melalui setiap produk
    for ukuran in np.unique(data['Ukuran Prediksi']):

        # Filter data berdasarkan ukuran produk
        produk_data = data[data['Ukuran Prediksi'] == ukuran]

        # Data yang diprediksi untuk produk tertentu (jumlah produk dibeli)
        y_pred_product = produk_data['Jumlah Produk Dibeli Prediksi'].values

        # Hitung standar deviasi dari error prediksi
        S = np.std(y_pred_product)

        # Hitung standar deviasi selama lead time (dalam hari)
        # S_L = S * np.sqrt(L)
        S_L = S * np.sqrt(L)

        # Hitung nilai N
        phi = stats.norm.pdf(Za)
        Psi = stats.norm.cdf(Za) * Za
        N = S_L * (Psi - phi)

        # Hitung cadangan pengaman (SS)
        SS = Za * S_L

        # Rata-rata permintaan selama lead time (dalam hari)
        DL = np.mean(y_pred_product) * L

        # Hitung saat pemesanan ulang (r)
        r = DL + SS

        # Hitung tingkat pelayanan (η)
        eta = 1 - (N / DL) if DL != 0 else 0  # Menghindari pembagian dengan nol

        # Hitung stok optimal
        optimal_stock = SS + r

        # Simpan hasil dalam dictionary
        return {
            "SS": round(SS),
            "ReorderPoint": round(r),
            "OptimalStock": round(optimal_stock),
            "Ekspektasi": round(N)
        }

def hashed(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(username:str, password:str):
    password_hashed = hashed(password)
    insert_users(username, password_hashed)

# Untuk mendaftarkan user
# register_user('username', 'password')