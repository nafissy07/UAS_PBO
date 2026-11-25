"""Controller: penghubung antara View (tampilan) dan Model + DAO (data).

View tidak pernah mengakses database. View hanya memanggil method di sini.
"""
from database.dao import MenuDAO, TransaksiDAO
from database.database_manager import DatabaseManager
from models.kedai import KedaiKopi
from models.menu import Menu
from models.orang import Kasir, Pelanggan
from models.pesanan import Pesanan
from models.transaksi import RiwayatTransaksi, Transaksi

# Menu awal, hanya dimasukkan kalau tabel menu masih kosong.
MENU_AWAL = [
    ("Kopi", "Espresso", "Espresso", 18000),
    ("Kopi", "Americano", "Espresso", 20000),
    ("Kopi", "Cappuccino", "Susu", 25000),
    ("Kopi", "Kopi Susu Gula Aren", "Susu", 22000),
    ("Non-Kopi", "Matcha Latte", "Teh", 26000),
    ("Non-Kopi", "Coklat Panas", "Coklat", 23000),
    ("Non-Kopi", "Teh Lemon", "Teh", 15000),
    ("Makanan", "Croissant", "Roti", 20000),
    ("Makanan", "Roti Bakar Coklat", "Roti", 17000),
]


class KedaiController:
    def __init__(self, db_path: str = "data/kedai_kopi.db", nama_kasir: str = "Azhalia"):
        db = DatabaseManager.get_instance(db_path)      # Singleton
        self._menu_dao = MenuDAO(db)
        self._transaksi_dao = TransaksiDAO(db)
        self._riwayat = RiwayatTransaksi(self._transaksi_dao)
        self._kedai = KedaiKopi("Coffee Order System")
        self._kasir = Kasir(nama_kasir, "KSR-01")
        self._isi_menu_awal()
        self.muat_ulang_menu()

    def _isi_menu_awal(self):
        if self._menu_dao.jumlah() == 0:
            for kategori, nama, jenis, harga in MENU_AWAL:
                self._menu_dao.simpan(Menu.buat(kategori, nama, harga, jenis))

    # ---------- kasir ----------
    @property
    def kasir(self) -> Kasir:
        return self._kasir

    def ganti_nama_kasir(self, nama_baru: str):
        self._kasir.ubah_nama(nama_baru)

    # ---------- menu ----------
    @property
    def kedai(self) -> KedaiKopi:
        return self._kedai

    def muat_ulang_menu(self):
        self._kedai.muat_menu(self._menu_dao.semua())

    def daftar_menu(self, kategori: str = "Semua", kata: str = "") -> list:
        return self._kedai.filter_menu(kategori, kata)

    def cari_menu(self, id_menu: int):
        return self._kedai.cari_menu(id_menu)

    def tambah_menu(self, kategori: str, nama: str, jenis: str, harga: int) -> Menu:
        menu = self._menu_dao.simpan(Menu.buat(kategori, nama, harga, jenis))
        self._kedai.tambah_menu(menu)
        return menu

    def ubah_menu(self, id_menu: int, kategori: str, nama: str, jenis: str, harga: int) -> Menu:
        menu = self._menu_dao.simpan(Menu.buat(kategori, nama, harga, jenis, id_menu))
        self._kedai.ubah_menu(menu)
        return menu

    def hapus_menu(self, id_menu: int):
        self._menu_dao.hapus(id_menu)
        self._kedai.hapus_menu(id_menu)

    # ---------- pemesanan & pembayaran ----------
    def pesanan_baru(self, nama_pelanggan: str = "Umum") -> Pesanan:
        return Pelanggan(nama_pelanggan or "Umum").buat_pesanan()

    def bayar(self, pesanan: Pesanan, uang_bayar: int,
              nama_pelanggan: str = "", telepon: str = "") -> Transaksi:
        """Proses pembayaran lalu simpan ke riwayat. Error dilempar ke pemanggil."""
        pesanan.nama_pelanggan = nama_pelanggan
        transaksi = self._kasir.proses_pesanan(pesanan, uang_bayar, telepon)
        return self._riwayat.simpan(transaksi)

    # ---------- riwayat & dashboard ----------
    def cari_riwayat(self, kata: str = "") -> list:
        return self._riwayat.cari(kata)

    def ringkasan(self) -> dict:
        jumlah, total = self._transaksi_dao.ringkasan()
        return {"jumlah_transaksi": jumlah, "total_pendapatan": total,
                "jumlah_menu": len(self._kedai.daftar_menu),
                "menu_terlaris": self._transaksi_dao.menu_terlaris()}
