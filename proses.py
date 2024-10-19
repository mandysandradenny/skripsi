import numpy as np
from scipy.stats import norm
import pandas as pd
import re
import joblib
from datetime import datetime, timedelta 
from sklearn.impute import KNNImputer
from sklearn.preprocessing import RobustScaler, LabelEncoder, StandardScaler
from tensorflow.keras.models import Sequential, load_model


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

    # Scaling data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_data)

    imputer = KNNImputer(n_neighbors=3)
    imputed_data = imputer.fit_transform(df_lengkap[['Jumlah Produk Dibeli']])
    imputed_series = pd.Series(imputed_data.ravel())

    # df_lengkap['Jumlah Produk Dibeli'].fillna(imputed_series, inplace=True)
    df_lengkap.fillna({'Jumlah Produk Dibeli': imputed_series}, inplace=True)

    df_lengkap['Ukuran'] = df_lengkap['Nama Produk'].apply(lambda product_name: 
    re.search(r'\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*(?:½)?\s*[×xX]\s*\d+[.,]?\d*\s*(cm)?', product_name, re.IGNORECASE).group(0).strip().replace('×', 'x').replace('X', 'x').replace('Cm', 'cm').replace('CM', 'cm')
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
    # le = LabelEncoder()
    # data['Ukuran'] = le.fit_transform(data['Ukuran'])

    # scaler = RobustScaler()
    # data[['Jumlah Produk Dibeli']] = scaler.fit_transform(data[['Jumlah Produk Dibeli']])
    
    # Load model GRU yang sudah disimpan
    model = load_model('model/model_gru.keras')

    # Load RobustScaler
    scaler = joblib.load('model/scaler.pkl')

    # Load LabelEncoder classes
    le = LabelEncoder()
    le.classes_ = np.load('model/classes.npy', allow_pickle=True)

    # Identifikasi ukuran baru yang tidak dikenal (tidak ada di le.classes_)
    unknown_sizes = ~data['Ukuran'].isin(le.classes_)

    # Tampilkan ukuran yang tidak dikenal (jika ada)
    if unknown_sizes.any():
        print(f"Ukuran baru yang tidak dikenal ditemukan: {data.loc[unknown_sizes, 'Ukuran'].unique()}")

    # Filter data yang mengandung ukuran yang dikenal
    data = data[~unknown_sizes].copy()

    # LabelEncoder pada kolom 'Ukuran'
    data['Ukuran'] = le.transform(data['Ukuran'])

    # Misalnya, data_new adalah DataFrame baru yang ingin diprediksi
    seq_length = 30  # Harus sama dengan yang digunakan saat pelatihan
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

    # prediksi untuk 14 hari kedepan
    tanggal_prediksi = pd.date_range(start=tanggal_akhir + pd.Timedelta(days=1), periods=14)

    # Mengambil hanya 14 hari dari hasil prediksi
    predicted_jumlah_produk = predicted_jumlah_produk_load[:14].flatten()
    predicted_ukuran = predicted_ukuran_asli_load[:14]
    
    # Membuat DataFrame untuk membandingkan hasil prediksi
    hasil_prediksi_load = pd.DataFrame({
        'Tanggal Pembayaran': tanggal_prediksi,  # Menggunakan tanggal dari data
        'Ukuran Prediksi': predicted_ukuran,
        'Jumlah Produk Dibeli Prediksi': predicted_jumlah_produk.flatten()
    })

    return hasil_prediksi_load






