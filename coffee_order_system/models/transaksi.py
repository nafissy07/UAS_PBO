"""Model Transaksi dan RiwayatTransaksi."""
from collections import namedtuple
from datetime import datetime
from typing import TYPE_CHECKING

from utils import rupiah

if TYPE_CHECKING:       # hanya untuk petunjuk tipe, tidak di-import saat berjalan
    from database.dao import TransaksiDAO
    from models.pesanan import Pesanan

# Salinan satu baris pesanan saat transaksi terjadi.
# Disalin supaya riwayat tidak berubah walau harga menu diubah kemudian.
ItemStruk = namedtuple("ItemStruk", "nama jumlah harga")


class PembayaranKurangError(ValueError):
    """Dilempar saat uang yang dibayarkan kurang dari total."""


class Transaksi:
    def __init__(self, items, pelanggan="Umum", telepon="", kasir="",
                 id_transaksi=None, waktu=None, uang_bayar=0, kembalian=0,
                 pesanan: "Pesanan" = None):
        self._items = [ItemStruk(*i) for i in items]
        self._pelanggan = pelanggan or "Umum"
        self._telepon = telepon or ""
        self._kasir = kasir
        self._id = id_transaksi
        self._waktu = waktu or datetime.now().replace(microsecond=0)
        self._uang_bayar = int(uang_bayar)
        self._kembalian = int(kembalian)
        self._pesanan = pesanan

    @classmethod
    def dari_pesanan(cls, pesanan: "Pesanan", kasir: str, telepon: str = "") -> "Transaksi":
        items = [(i.menu.nama, i.jumlah, i.menu.harga) for i in pesanan.daftar_item]
        return cls(items, pesanan.nama_pelanggan, telepon, kasir, pesanan=pesanan)

    # ---------- property ----------
    @property
    def id_transaksi(self):
        return self._id

    @id_transaksi.setter
    def id_transaksi(self, nilai):
        self._id = nilai

    @property
    def waktu(self) -> datetime:
        return self._waktu

    @property
    def kasir(self) -> str:
        return self._kasir

    @property
    def pelanggan(self) -> str:
        return self._pelanggan

    @property
    def telepon(self) -> str:
        return self._telepon

    @property
    def items(self) -> list:
        return list(self._items)

    @property
    def jumlah_item(self) -> int:
        return sum(i.jumlah for i in self._items)

    @property
    def total(self) -> int:
        return sum(i.jumlah * i.harga for i in self._items)

    @property
    def uang_bayar(self) -> int:
        return self._uang_bayar

    @property
    def kembalian(self) -> int:
        return self._kembalian

    # ---------- proses pembayaran ----------
    def hitung_kembalian(self, uang_bayar: int) -> int:
        return int(uang_bayar) - self.total

    def proses_bayar(self, uang_bayar: int):
        if self.total <= 0:
            raise ValueError("Pesanan masih kosong")
        uang_bayar = int(uang_bayar)
        if uang_bayar < self.total:
            raise PembayaranKurangError(
                f"Uang kurang {rupiah(self.total - uang_bayar)} dari total {rupiah(self.total)}")
        self._uang_bayar = uang_bayar
        self._kembalian = self.hitung_kembalian(uang_bayar)
        if self._pesanan is not None:
            self._pesanan.tandai_dibayar()

    def cetak_struk(self) -> str:
        lebar = 38

        def baris(kiri, kanan):
            return kiri + " " * max(1, lebar - len(kiri) - len(kanan)) + kanan

        garis = "-" * lebar
        tel = f" ({self._telepon})" if self._telepon else ""
        teks = [
            "COFFEE ORDER".center(lebar),
            f"{self._id or '-'}  {self._waktu:%d %b %Y %H:%M}".center(lebar),
            f"Kasir     : {self._kasir}",
            f"Pelanggan : {self._pelanggan}{tel}",
            garis,
        ]
        for i in self._items:
            teks.append(baris(f"{i.jumlah}x {i.nama}", rupiah(i.jumlah * i.harga)))
        teks += [
            garis,
            baris("Total", rupiah(self.total)),
            baris("Bayar (tunai)", rupiah(self._uang_bayar)),
            baris("Kembalian", rupiah(self._kembalian)),
            garis,
            "Terima kasih, selamat menikmati".center(lebar),
        ]
        return "\n".join(teks)


class RiwayatTransaksi:
    """Menyimpan dan mencari transaksi. Penyimpanannya diserahkan ke DAO."""

    def __init__(self, dao: "TransaksiDAO"):
        self._dao = dao

    def simpan(self, transaksi: Transaksi) -> Transaksi:
        return self._dao.simpan(transaksi)

    def cari(self, kata: str = "") -> list:
        return self._dao.cari(kata)

    def tampilkan_semua(self) -> list:
        return self._dao.semua()
