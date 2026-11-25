"""Model Menu.

Konsep OOP di file ini:
- Abstraction   : Menu adalah abstract class (tidak bisa dibuat objeknya langsung).
- Inheritance   : Kopi, NonKopi, Makanan mewarisi Menu.
- Polymorphism  : info_menu() ada di semua turunan dengan isi yang berbeda.
- Encapsulation : atribut diawali _ dan diubah lewat property / method.
"""
from abc import ABC, abstractmethod

from utils import rupiah


class Menu(ABC):
    KATEGORI = ""      # diisi oleh class turunan
    IKON = "🍽️"
    _registry: dict = {}   # kategori -> class, dipakai oleh Menu.buat()

    def __init_subclass__(cls, **kwargs):
        """Setiap turunan yang punya KATEGORI otomatis terdaftar."""
        super().__init_subclass__(**kwargs)
        if cls.KATEGORI:
            Menu._registry[cls.KATEGORI] = cls

    def __init__(self, nama, harga, id_menu=None):
        self._id = id_menu
        self._nama = ""
        self._harga = 0
        self.nama = nama      # lewat setter, jadi ikut divalidasi
        self.harga = harga

    # ---------- property (encapsulation) ----------
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, nilai):
        self._id = nilai

    @property
    def nama(self) -> str:
        return self._nama

    @nama.setter
    def nama(self, nilai):
        nilai = (nilai or "").strip()
        if not nilai:
            raise ValueError("Nama menu tidak boleh kosong")
        self._nama = nilai

    @property
    def harga(self) -> int:
        return self._harga

    @harga.setter
    def harga(self, nilai):
        try:
            nilai = int(nilai)
        except (TypeError, ValueError):
            raise ValueError("Harga harus berupa angka")
        if nilai <= 0:
            raise ValueError("Harga harus lebih dari 0")
        self._harga = nilai

    @property
    def kategori(self) -> str:
        return self.KATEGORI

    def ubah_harga(self, harga_baru):
        self.harga = harga_baru

    # ---------- wajib dibuat oleh turunan (abstraction) ----------
    @property
    @abstractmethod
    def jenis(self) -> str:
        """Atribut khusus tiap kategori (jenis kopi / minuman / makanan)."""

    @abstractmethod
    def info_menu(self) -> str:
        """Teks ringkas tentang menu ini."""

    # ---------- factory ----------
    @classmethod
    def buat(cls, kategori, nama, harga, jenis="", id_menu=None) -> "Menu":
        """Buat objek menu sesuai kategori, tanpa if-else panjang."""
        kelas = cls._registry.get(kategori)
        if kelas is None:
            raise ValueError(f"Kategori tidak dikenal: {kategori}")
        return kelas(nama, harga, jenis, id_menu)

    @classmethod
    def daftar_kategori(cls) -> list:
        return list(cls._registry)

    def __repr__(self):
        return f"<{type(self).__name__} #{self._id} {self._nama} {self._harga}>"


class Kopi(Menu):
    KATEGORI = "Kopi"
    IKON = "☕"

    def __init__(self, nama, harga, jenis="", id_menu=None):
        super().__init__(nama, harga, id_menu)
        self._jenis_kopi = (jenis or "").strip()

    @property
    def jenis(self) -> str:
        return self._jenis_kopi

    def info_menu(self) -> str:
        return f"[Kopi] {self.nama} - jenis kopi: {self._jenis_kopi or '-'} - {rupiah(self.harga)}"


class NonKopi(Menu):
    KATEGORI = "Non-Kopi"
    IKON = "🧋"

    def __init__(self, nama, harga, jenis="", id_menu=None):
        super().__init__(nama, harga, id_menu)
        self._jenis_minuman = (jenis or "").strip()

    @property
    def jenis(self) -> str:
        return self._jenis_minuman

    def info_menu(self) -> str:
        return f"[Non-Kopi] {self.nama} - jenis minuman: {self._jenis_minuman or '-'} - {rupiah(self.harga)}"


class Makanan(Menu):
    KATEGORI = "Makanan"
    IKON = "🥐"

    def __init__(self, nama, harga, jenis="", id_menu=None):
        super().__init__(nama, harga, id_menu)
        self._jenis_makanan = (jenis or "").strip()

    @property
    def jenis(self) -> str:
        return self._jenis_makanan

    def info_menu(self) -> str:
        return f"[Makanan] {self.nama} - jenis makanan: {self._jenis_makanan or '-'} - {rupiah(self.harga)}"
