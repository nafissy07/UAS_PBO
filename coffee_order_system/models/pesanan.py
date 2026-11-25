"""Model Pesanan dan ItemPesanan (composition: ItemPesanan tidak ada tanpa Pesanan)."""
import uuid

from models.menu import Menu


class ItemPesanan:
    """Satu baris pesanan: sebuah menu beserta jumlahnya."""

    def __init__(self, menu: Menu, jumlah: int = 1):
        self._menu = menu
        self._jumlah = 1
        self.jumlah = jumlah

    @property
    def menu(self) -> Menu:
        return self._menu

    @property
    def jumlah(self) -> int:
        return self._jumlah

    @jumlah.setter
    def jumlah(self, nilai):
        nilai = int(nilai)
        if nilai < 1:
            raise ValueError("Jumlah minimal 1")
        self._jumlah = nilai

    def ubah_jumlah(self, jumlah):
        self.jumlah = jumlah

    def hitung_subtotal(self) -> int:
        return self._menu.harga * self._jumlah


class Pesanan:
    STATUS_BARU = "Baru"
    STATUS_DIBAYAR = "Dibayar"

    def __init__(self, nama_pelanggan: str = "Umum", id_pesanan: str = None):
        self._id = id_pesanan or "PSN-" + uuid.uuid4().hex[:6].upper()
        self._nama_pelanggan = (nama_pelanggan or "").strip() or "Umum"
        self._daftar_item: list[ItemPesanan] = []
        self._status = self.STATUS_BARU

    # ---------- property ----------
    @property
    def id_pesanan(self) -> str:
        return self._id

    @property
    def nama_pelanggan(self) -> str:
        return self._nama_pelanggan

    @nama_pelanggan.setter
    def nama_pelanggan(self, nilai):
        self._nama_pelanggan = (nilai or "").strip() or "Umum"

    @property
    def status(self) -> str:
        return self._status

    @property
    def daftar_item(self) -> list:
        return list(self._daftar_item)      # salinan, supaya list asli aman

    @property
    def kosong(self) -> bool:
        return not self._daftar_item

    @property
    def jumlah_item(self) -> int:
        return sum(i.jumlah for i in self._daftar_item)

    # ---------- operasi pesanan ----------
    def _cari(self, menu: Menu):
        for item in self._daftar_item:
            sama = (item.menu.id == menu.id) if menu.id is not None else (item.menu is menu)
            if sama:
                return item
        return None

    def tambah_item(self, menu: Menu, jumlah: int = 1):
        item = self._cari(menu)
        if item:
            item.jumlah += int(jumlah)
        else:
            self._daftar_item.append(ItemPesanan(menu, jumlah))

    def ubah_jumlah(self, menu: Menu, jumlah: int):
        """Jumlah <= 0 berarti item dihapus dari pesanan."""
        if int(jumlah) <= 0:
            self.hapus_item(menu)
            return
        item = self._cari(menu)
        if item:
            item.ubah_jumlah(jumlah)

    def hapus_item(self, menu: Menu):
        item = self._cari(menu)
        if item:
            self._daftar_item.remove(item)

    def hitung_total(self) -> int:
        return sum(i.hitung_subtotal() for i in self._daftar_item)

    def tandai_dibayar(self):
        self._status = self.STATUS_DIBAYAR
