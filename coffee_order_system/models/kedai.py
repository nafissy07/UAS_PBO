"""Model KedaiKopi: memegang nama kedai dan daftar menu."""
from models.menu import Menu


class KedaiKopi:
    def __init__(self, nama: str):
        self._nama = nama
        self._daftar_menu: list[Menu] = []

    @property
    def nama(self) -> str:
        return self._nama

    @property
    def daftar_menu(self) -> list:
        return list(self._daftar_menu)

    def info(self) -> str:
        return f"{self._nama} - {len(self._daftar_menu)} menu"

    def muat_menu(self, daftar: list):
        """Ganti seluruh daftar menu (dipakai setelah membaca dari database)."""
        self._daftar_menu = list(daftar)

    def tambah_menu(self, menu: Menu):
        self._daftar_menu.append(menu)

    def ubah_menu(self, menu: Menu):
        for i, m in enumerate(self._daftar_menu):
            if m.id == menu.id:
                self._daftar_menu[i] = menu
                return

    def hapus_menu(self, id_menu: int):
        self._daftar_menu = [m for m in self._daftar_menu if m.id != id_menu]

    def cari_menu(self, id_menu: int):
        return next((m for m in self._daftar_menu if m.id == id_menu), None)

    def filter_menu(self, kategori: str = "Semua", kata: str = "") -> list:
        kata = kata.strip().lower()
        return [m for m in self._daftar_menu
                if (kategori == "Semua" or m.kategori == kategori) and kata in m.nama.lower()]
