"""DAO (Data Access Object): satu-satunya tempat perintah SQL ditulis.

Generics : BaseDAO[T] adalah kerangka generik, dipakai MenuDAO (T = Menu)
           dan TransaksiDAO (T = Transaksi).
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, Optional, TypeVar

from database.database_manager import DatabaseManager
from models.menu import Menu
from models.transaksi import Transaksi

T = TypeVar("T")


class BaseDAO(ABC, Generic[T]):
    def __init__(self, db: DatabaseManager):
        self._db = db

    @abstractmethod
    def simpan(self, objek: T) -> T: ...

    @abstractmethod
    def semua(self) -> list: ...

    @abstractmethod
    def cari_id(self, id_objek) -> Optional[T]: ...

    @abstractmethod
    def hapus(self, id_objek) -> None: ...


class MenuDAO(BaseDAO[Menu]):
    @staticmethod
    def _ke_objek(baris) -> Menu:
        return Menu.buat(baris["kategori"], baris["nama"], baris["harga"],
                         baris["jenis"] or "", baris["id"])

    def simpan(self, menu: Menu) -> Menu:
        """Menu baru (id kosong) di-INSERT, menu lama di-UPDATE."""
        if menu.id is None:
            menu.id = self._db.execute(
                "INSERT INTO menu (nama, kategori, jenis, harga) VALUES (?, ?, ?, ?)",
                (menu.nama, menu.kategori, menu.jenis, menu.harga))
        else:
            self._db.execute(
                "UPDATE menu SET nama=?, kategori=?, jenis=?, harga=? WHERE id=?",
                (menu.nama, menu.kategori, menu.jenis, menu.harga, menu.id))
        return menu

    def semua(self) -> list:
        return [self._ke_objek(b) for b in
                self._db.fetch_all("SELECT * FROM menu ORDER BY id")]

    def cari_id(self, id_menu) -> Optional[Menu]:
        baris = self._db.fetch_one("SELECT * FROM menu WHERE id=?", (id_menu,))
        return self._ke_objek(baris) if baris else None

    def hapus(self, id_menu) -> None:
        self._db.execute("DELETE FROM menu WHERE id=?", (id_menu,))

    def jumlah(self) -> int:
        return self._db.fetch_one("SELECT COUNT(*) AS n FROM menu")["n"]


class TransaksiDAO(BaseDAO[Transaksi]):
    def _id_berikutnya(self) -> str:
        baris = self._db.fetch_one(
            "SELECT MAX(CAST(SUBSTR(id_transaksi, 5) AS INTEGER)) AS n FROM transaksi")
        return f"TRX-{(baris['n'] or 0) + 1:04d}"

    def _ke_objek(self, baris, items) -> Transaksi:
        return Transaksi(
            items=[(i["nama"], i["jumlah"], i["harga"]) for i in items],
            pelanggan=baris["pelanggan"], telepon=baris["telepon"], kasir=baris["kasir"],
            id_transaksi=baris["id_transaksi"],
            waktu=datetime.fromisoformat(baris["waktu"]),
            uang_bayar=baris["uang_bayar"], kembalian=baris["kembalian"])

    def _rakit(self, daftar_baris) -> list:
        """Ambil item semua transaksi sekaligus, lalu pasangkan satu per satu."""
        if not daftar_baris:
            return []
        ids = [b["id_transaksi"] for b in daftar_baris]
        tanda = ",".join("?" * len(ids))
        item = self._db.fetch_all(
            f"SELECT * FROM item_transaksi WHERE id_transaksi IN ({tanda}) ORDER BY id", ids)
        per_transaksi: dict = {}
        for i in item:
            per_transaksi.setdefault(i["id_transaksi"], []).append(i)
        return [self._ke_objek(b, per_transaksi.get(b["id_transaksi"], []))
                for b in daftar_baris]

    def simpan(self, transaksi: Transaksi) -> Transaksi:
        if transaksi.id_transaksi is None:
            transaksi.id_transaksi = self._id_berikutnya()
        perintah = [(
            "INSERT INTO transaksi (id_transaksi, waktu, kasir, pelanggan, telepon, "
            "total, uang_bayar, kembalian) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (transaksi.id_transaksi, transaksi.waktu.isoformat(sep=" "), transaksi.kasir,
             transaksi.pelanggan, transaksi.telepon, transaksi.total,
             transaksi.uang_bayar, transaksi.kembalian))]
        for i in transaksi.items:
            perintah.append((
                "INSERT INTO item_transaksi (id_transaksi, nama, jumlah, harga) VALUES (?, ?, ?, ?)",
                (transaksi.id_transaksi, i.nama, i.jumlah, i.harga)))
        self._db.execute_atomik(perintah)
        return transaksi

    def semua(self) -> list:
        return self._rakit(self._db.fetch_all(
            "SELECT * FROM transaksi ORDER BY waktu DESC, id_transaksi DESC"))

    def cari(self, kata: str = "") -> list:
        kata = (kata or "").strip()
        if not kata:
            return self.semua()
        pola = f"%{kata}%"
        return self._rakit(self._db.fetch_all(
            "SELECT * FROM transaksi WHERE id_transaksi LIKE ? OR pelanggan LIKE ? "
            "OR id_transaksi IN (SELECT id_transaksi FROM item_transaksi WHERE nama LIKE ?) "
            "ORDER BY waktu DESC, id_transaksi DESC", (pola, pola, pola)))

    def cari_id(self, id_transaksi) -> Optional[Transaksi]:
        baris = self._db.fetch_all("SELECT * FROM transaksi WHERE id_transaksi=?", (id_transaksi,))
        hasil = self._rakit(baris)
        return hasil[0] if hasil else None

    def hapus(self, id_transaksi) -> None:
        self._db.execute_atomik([
            ("DELETE FROM item_transaksi WHERE id_transaksi=?", (id_transaksi,)),
            ("DELETE FROM transaksi WHERE id_transaksi=?", (id_transaksi,))])

    # ---------- data untuk dashboard ----------
    def ringkasan(self) -> tuple:
        """(jumlah transaksi, total pendapatan)."""
        b = self._db.fetch_one("SELECT COUNT(*) AS n, COALESCE(SUM(total), 0) AS t FROM transaksi")
        return b["n"], b["t"]

    def menu_terlaris(self) -> Optional[tuple]:
        """(nama menu, jumlah terjual) atau None kalau belum ada transaksi."""
        b = self._db.fetch_one(
            "SELECT nama, SUM(jumlah) AS j FROM item_transaksi GROUP BY nama "
            "ORDER BY j DESC, nama LIMIT 1")
        return (b["nama"], b["j"]) if b else None
