"""Fungsi bantu yang dipakai di banyak tempat."""


def rupiah(nilai) -> str:
    """Ubah angka menjadi format rupiah. Contoh: 22000 -> 'Rp 22.000'."""
    return "Rp " + f"{int(nilai):,}".replace(",", ".")
