"""Model pengguna: Orang -> Pelanggan, Kasir. Pelayanan adalah interface."""
from abc import ABC, abstractmethod

from models.pesanan import Pesanan
from models.transaksi import Transaksi


class Pelayanan(ABC):
    """Interface: class yang melayani pesanan wajib punya method ini."""

    @abstractmethod
    def layani_pesanan(self, pesanan: Pesanan):
        ...


class Orang:
    """Class induk: menyimpan atribut yang sama milik Kasir dan Pelanggan."""

    def __init__(self, nama: str):
        self._nama = ""
        self.nama = nama

    @property
    def nama(self) -> str:
        return self._nama

    @nama.setter
    def nama(self, nilai):
        nilai = (nilai or "").strip()
        if not nilai:
            raise ValueError("Nama tidak boleh kosong")
        self._nama = nilai

    def info(self) -> str:
        return f"Nama: {self._nama}"


class Pelanggan(Orang):
    def __init__(self, nama: str = "Umum", no_telepon: str = ""):
        super().__init__(nama)
        self._no_telepon = (no_telepon or "").strip()

    @property
    def no_telepon(self) -> str:
        return self._no_telepon

    def info(self) -> str:                      # polymorphism: override
        return f"Pelanggan: {self._nama} ({self._no_telepon or '-'})"

    def buat_pesanan(self) -> Pesanan:
        return Pesanan(self._nama)


class Kasir(Orang, Pelayanan):
    def __init__(self, nama: str, id_kasir: str = "KSR-01"):
        super().__init__(nama)
        self._id_kasir = id_kasir

    @property
    def id_kasir(self) -> str:
        return self._id_kasir

    def info(self) -> str:                      # polymorphism: override
        return f"Kasir: {self._nama} ({self._id_kasir})"

    def ubah_nama(self, nama_baru: str):
        self.nama = nama_baru

    def layani_pesanan(self, pesanan: Pesanan):
        if pesanan.kosong:
            raise ValueError("Pesanan masih kosong")
        return pesanan

    def proses_pesanan(self, pesanan: Pesanan, uang_bayar: int, telepon: str = "") -> Transaksi:
        """Layani pesanan lalu proses pembayarannya. Hasilnya berupa Transaksi."""
        self.layani_pesanan(pesanan)
        transaksi = Transaksi.dari_pesanan(pesanan, self._nama, telepon)
        transaksi.proses_bayar(uang_bayar)
        return transaksi

    def lihat_riwayat(self, riwayat) -> list:
        return riwayat.tampilkan_semua()
