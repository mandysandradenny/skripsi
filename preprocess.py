import numpy as np
from scipy.stats import norm
import pandas as pd
import re
from datetime import datetime, timedelta


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

    # Ffill untuk nama produk dan harga jual
    df_lengkap['Nama Produk'] = df_lengkap['Nama Produk'].ffill()
    df_lengkap['Nama Produk'] = df_lengkap['Nama Produk'].bfill()
    # Mengisi nilai yang hilang pada kolom 'Nama Produk' menggunakan forward fill dan backward fill
    # df_lengkap['Nama Produk'] = df_lengkap['Nama Produk'].fillna(method='ffill').fillna(method='bfill')

    # Menyaring model yang tidak ingin digunakan
    model_tidak_diinginkan = ['model botol', 'model nampan', 'tanpa tutup', 'lembaran', 'layer']

    # Mengubah semua teks dalam 'Nama Produk' menjadi huruf kecil
    df_lengkap['nama produk lowercase'] = df_lengkap['Nama Produk'].str.lower()

    pattern = '|'.join(model_tidak_diinginkan)  # Membuat pola regex dari daftar
    df_filtered = df_lengkap[~df_lengkap['nama produk lowercase'].str.contains(pattern, na=False)] # Added na=False to handle potential NaN values

    # Menghapus kolom tambahan yang digunakan untuk filtering
    df_filtered = df_filtered.drop(columns=['nama produk lowercase'])

    # Mengisi missing values dengan interpolasi linier
    df_filtered['Jumlah Produk Dibeli'] = df_filtered['Jumlah Produk Dibeli'].interpolate(method='linear')

    df_filtered['Ukuran'] = df_filtered['Nama Produk'].apply(lambda product_name: 
    re.search(r'\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*\s*(cm)?', product_name, re.IGNORECASE).group(0).strip() 
    if re.search(r'\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*\s*[×xX]\s*\d+[.,]?\d*\s*(cm)?', product_name, re.IGNORECASE) 
    else np.nan)

    df_filtered['Tanggal Pembayaran'] = pd.to_datetime(df_filtered['Tanggal Pembayaran']).dt.strftime('%Y-%m-%d')

    # Mengelompokan total penjualan produk pada tanggal yang sama dan ukuran yang sama
    df_filtered = df_filtered.groupby(['Tanggal Pembayaran', 'Ukuran']).agg({
        'Jumlah Produk Dibeli': 'sum',
    }).reset_index()

    return df_filtered

# df = preprocessing("D:\\Downloads\\Agustus2023.xlsx")
# for index, row in df.iterrows():
#     print(row['Tanggal Pembayaran'], row['Ukuran'], row['Jumlah Produk Dibeli'])




