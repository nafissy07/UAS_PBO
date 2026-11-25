"""Pengujian logika aplikasi. Jalankan dari folder proyek:
    python -m unittest discover -s tests -v
"""
import unittest

from controllers.kedai_controller import KedaiController
from database.dao import MenuDAO, TransaksiDAO
from database.database_manager import DatabaseManager
from models import (Kasir, Kopi, Makanan, Menu, NonKopi, Orang, Pelanggan,
                    PembayaranKurangError, Pelayanan, Pesanan)


class TestMenu(unittest.TestCase):
    def test_menu_abstract_tidak_bisa_dibuat(self):
        with self.assertRaises(TypeError):
            Menu("X", 1000)

    def test_polymorphism_info_menu(self):
        daftar = [Kopi("Latte", 25000, "Susu"), NonKopi("Teh", 15000, "Teh"),
                  Makanan("Roti", 17000, "Roti")]
        hasil = [m.info_menu() for m in daftar]
        self.assertTrue(hasil[0].startswith("[Kopi]"))
        self.assertTrue(hasil[1].startswith("[Non-Kopi]"))
        self.assertTrue(hasil[2].startswith("[Makanan]"))

    def test_factory_dan_inheritance(self):
        m = Menu.buat("Non-Kopi", "Matcha", 26000, "Teh")
        self.assertIsInstance(m, NonKopi)
        self.assertIsInstance(m, Menu)
        with self.assertRaises(ValueError):
            Menu.buat("Tidak Ada", "X", 1000)

    def test_validasi_encapsulation(self):
        m = Kopi("Espresso", 18000)
        m.ubah_harga(20000)
        self.assertEqual(m.harga, 20000)
        for salah in (0, -5, "abc"):
            with self.assertRaises(ValueError):
                m.ubah_harga(salah)
        with self.assertRaises(ValueError):
            Kopi("  ", 1000)


class TestPesananDanTransaksi(unittest.TestCase):
    def setUp(self):
        self.kopi = Kopi("Kopi Susu", 22000, "Susu", 1)
        self.roti = Makanan("Croissant", 20000, "Roti", 2)

    def test_hitung_total_dan_item(self):
        p = Pesanan()
        p.tambah_item(self.kopi, 2)
        p.tambah_item(self.roti)
        p.tambah_item(self.kopi)                       # menu sama: jumlah bertambah
        self.assertEqual(len(p.daftar_item), 2)
        self.assertEqual(p.hitung_total(), 3 * 22000 + 20000)

    def test_ubah_dan_hapus_item(self):
        p = Pesanan()
        p.tambah_item(self.kopi, 2)
        p.ubah_jumlah(self.kopi, 5)
        self.assertEqual(p.hitung_total(), 5 * 22000)
        p.ubah_jumlah(self.kopi, 0)                    # 0 = hapus
        self.assertTrue(p.kosong)

    def test_pembayaran_dan_kembalian(self):
        kasir = Kasir("Azhalia")
        p = Pesanan("Dina")
        p.tambah_item(self.kopi, 2)
        t = kasir.proses_pesanan(p, 50000)
        self.assertEqual(t.total, 44000)
        self.assertEqual(t.kembalian, 6000)
        self.assertEqual(p.status, Pesanan.STATUS_DIBAYAR)

    def test_uang_kurang_ditolak(self):
        kasir = Kasir("Azhalia")
        p = Pesanan()
        p.tambah_item(self.kopi)
        with self.assertRaises(PembayaranKurangError):
            kasir.proses_pesanan(p, 10000)
        self.assertEqual(p.status, Pesanan.STATUS_BARU)

    def test_pesanan_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            Kasir("Azhalia").proses_pesanan(Pesanan(), 10000)

    def test_struk_memuat_data(self):
        p = Pesanan("Dina")
        p.tambah_item(self.kopi)
        t = Kasir("Azhalia").proses_pesanan(p, 25000, "0812")
        struk = t.cetak_struk()
        for teks in ("Azhalia", "Dina", "0812", "Kopi Susu", "Rp 22.000", "Rp 3.000"):
            self.assertIn(teks, struk)


class TestOrang(unittest.TestCase):
    def test_inheritance_dan_interface(self):
        kasir, pelanggan = Kasir("Azhalia"), Pelanggan("Dina", "0812")
        self.assertIsInstance(kasir, Orang)
        self.assertIsInstance(kasir, Pelayanan)
        self.assertIsInstance(pelanggan, Orang)
        self.assertNotEqual(kasir.info(), pelanggan.info())       # polymorphism

    def test_ubah_nama_kasir(self):
        kasir = Kasir("Azhalia")
        kasir.ubah_nama("Nafis")
        self.assertEqual(kasir.nama, "Nafis")
        with self.assertRaises(ValueError):
            kasir.ubah_nama("")

    def test_interface_tidak_bisa_dibuat(self):
        with self.assertRaises(TypeError):
            Pelayanan()


class TestDatabase(unittest.TestCase):
    def setUp(self):
        DatabaseManager.reset()
        self.db = DatabaseManager.get_instance(":memory:")

    def tearDown(self):
        DatabaseManager.reset()

    def test_singleton(self):
        self.assertIs(DatabaseManager.get_instance(), DatabaseManager.get_instance())
        self.assertIs(DatabaseManager(), self.db)

    def test_menu_dao_crud(self):
        dao = MenuDAO(self.db)
        m = dao.simpan(Kopi("Latte", 25000, "Susu"))
        self.assertIsNotNone(m.id)
        m.ubah_harga(27000)
        dao.simpan(m)
        dibaca = dao.cari_id(m.id)
        self.assertIsInstance(dibaca, Kopi)
        self.assertEqual(dibaca.harga, 27000)
        dao.hapus(m.id)
        self.assertIsNone(dao.cari_id(m.id))

    def test_transaksi_dao_simpan_dan_cari(self):
        dao = TransaksiDAO(self.db)
        kasir = Kasir("Azhalia")
        for nama, kopi in (("Dina", "Latte"), ("Rafi", "Americano")):
            p = Pesanan(nama)
            p.tambah_item(Kopi(kopi, 20000, "", 1), 2)
            dao.simpan(kasir.proses_pesanan(p, 50000))
        semua = dao.semua()
        self.assertEqual([t.id_transaksi for t in semua], ["TRX-0002", "TRX-0001"])
        self.assertEqual([t.pelanggan for t in dao.cari("dina")], ["Dina"])
        self.assertEqual(len(dao.cari("Americano")), 1)            # cari lewat nama produk
        self.assertEqual(len(dao.cari("TRX-0001")), 1)
        self.assertEqual(dao.cari("tidak-ada"), [])
        self.assertEqual(dao.ringkasan(), (2, 80000))
        self.assertEqual(dao.menu_terlaris()[1], 2)


class TestController(unittest.TestCase):
    def setUp(self):
        DatabaseManager.reset()
        self.ctrl = KedaiController(":memory:")

    def tearDown(self):
        DatabaseManager.reset()

    def test_menu_awal_dan_filter(self):
        self.assertEqual(len(self.ctrl.daftar_menu()), 9)
        self.assertEqual(len(self.ctrl.daftar_menu("Makanan")), 2)
        self.assertEqual(len(self.ctrl.daftar_menu(kata="kopi")), 1)

    def test_tambah_ubah_hapus_menu(self):
        m = self.ctrl.tambah_menu("Kopi", "Vietnam Drip", "Susu", 24000)
        self.assertEqual(len(self.ctrl.daftar_menu()), 10)
        self.ctrl.ubah_menu(m.id, "Non-Kopi", "Vietnam Drip", "Susu", 25000)
        self.assertEqual(self.ctrl.cari_menu(m.id).kategori, "Non-Kopi")
        self.ctrl.hapus_menu(m.id)
        self.assertEqual(len(self.ctrl.daftar_menu()), 9)

    def test_alur_lengkap_pemesanan(self):
        self.assertEqual(self.ctrl.ringkasan()["jumlah_transaksi"], 0)
        p = self.ctrl.pesanan_baru()
        p.tambah_item(self.ctrl.daftar_menu()[3], 2)
        t = self.ctrl.bayar(p, 50000, "Dina", "0812")
        self.assertEqual(t.id_transaksi, "TRX-0001")
        self.assertEqual(t.kembalian, 6000)
        r = self.ctrl.ringkasan()
        self.assertEqual((r["jumlah_transaksi"], r["total_pendapatan"]), (1, 44000))
        self.assertEqual(r["menu_terlaris"], ("Kopi Susu Gula Aren", 2))

    def test_riwayat_tidak_berubah_walau_harga_menu_berubah(self):
        menu = self.ctrl.daftar_menu()[0]
        p = self.ctrl.pesanan_baru()
        p.tambah_item(menu)
        self.ctrl.bayar(p, 20000)
        self.ctrl.ubah_menu(menu.id, menu.kategori, menu.nama, menu.jenis, 99000)
        self.assertEqual(self.ctrl.cari_riwayat("")[0].total, 18000)

    def test_ganti_nama_kasir_tercatat_di_transaksi(self):
        self.ctrl.ganti_nama_kasir("Nafis")
        p = self.ctrl.pesanan_baru()
        p.tambah_item(self.ctrl.daftar_menu()[0])
        self.assertEqual(self.ctrl.bayar(p, 20000).kasir, "Nafis")


if __name__ == "__main__":
    unittest.main()
