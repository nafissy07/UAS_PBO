# Coffee Order System · Kelompok 3

Aplikasi pemesanan kedai kopi untuk kasir, dibuat dengan Python + Streamlit + SQLite.

## Cara menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Database `data/kedai_kopi.db` dibuat otomatis saat pertama dijalankan, lengkap dengan 9 menu contoh.

Menjalankan pengujian:

```bash
python -m unittest discover -s tests -v
```

## Struktur proyek (MVC + DAO)

```
app.py                      titik masuk, navigasi sidebar
models/                     MODEL  : class sesuai class diagram
  menu.py                     Menu (abstract), Kopi, NonKopi, Makanan
  pesanan.py                  Pesanan, ItemPesanan
  transaksi.py                Transaksi, RiwayatTransaksi
  orang.py                    Orang, Pelanggan, Kasir, Pelayanan (interface)
  kedai.py                    KedaiKopi
database/                   LAPISAN DATA
  database_manager.py         DatabaseManager (Singleton), koneksi SQLite
  dao.py                      BaseDAO[T] generik, MenuDAO, TransaksiDAO
controllers/
  kedai_controller.py       CONTROLLER : penghubung View dan Model/DAO
views/                      VIEW   : tampilan Streamlit
  dashboard.py  pemesanan.py  manajemen_menu.py  riwayat.py
tests/test_kedai.py         pengujian
```

Alur data: **View → Controller → Model / DAO → DatabaseManager → SQLite**.
View tidak pernah menyentuh database secara langsung.

## Letak konsep OOP (untuk presentasi)

| Konsep | Lokasi |
|---|---|
| Encapsulation | Atribut `_nama`, `_harga`, dst. dengan `@property` dan validasi di setter (`models/menu.py`) |
| Inheritance | `Kopi`, `NonKopi`, `Makanan` → `Menu`; `Kasir`, `Pelanggan` → `Orang` |
| Polymorphism | `info_menu()` di tiap jenis menu; `info()` di `Kasir` dan `Pelanggan` |
| Abstraction | `Menu` (abstract class), `Pelayanan` (interface), `BaseDAO` |
| Generics | `BaseDAO(ABC, Generic[T])` → `MenuDAO(BaseDAO[Menu])`, `TransaksiDAO(BaseDAO[Transaksi])` |
| Singleton | `DatabaseManager.__new__` (`database/database_manager.py`) |
| DAO | `database/dao.py`, satu-satunya tempat perintah SQL |

## Kesesuaian dengan class diagram

Semua class di diagram ada di kode dengan nama method yang sama (versi snake_case):
`tambahMenu → tambah_menu`, `hitungTotal → hitung_total`, `prosesBayar → proses_bayar`,
`hitungKembalian → hitung_kembalian`, `cetakStruk → cetak_struk`, `ubahNama → ubah_nama`, dst.

## Catatan

- Riwayat menyimpan **salinan** nama dan harga saat transaksi, jadi riwayat lama tidak berubah walau harga menu diubah.
- Pembayaran hanya tunai, sesuai batasan ruang lingkup di presentasi.
- Nama kasir bisa diganti di sidebar dan ikut tercatat di transaksi berikutnya.
