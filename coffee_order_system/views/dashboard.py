"""Halaman Dashboard."""
from datetime import datetime

import streamlit as st

from utils import rupiah
from views.komponen import judul, kartu_stat


def _sapaan() -> str:
    jam = datetime.now().hour
    if jam < 11:
        return "pagi"
    if jam < 15:
        return "siang"
    if jam < 18:
        return "sore"
    return "malam"


def tampilkan(ctrl):
    ringkas = ctrl.ringkasan()
    judul(f"Selamat {_sapaan()}, {ctrl.kasir.nama}!", "Ringkasan aktivitas Coffee Order System.")

    terlaris = ringkas["menu_terlaris"]
    kolom = st.columns(4)
    kartu_stat(kolom[0], "💰 Total pendapatan", rupiah(ringkas["total_pendapatan"]))
    kartu_stat(kolom[1], "🧾 Jumlah transaksi", str(ringkas["jumlah_transaksi"]))
    kartu_stat(kolom[2], "📋 Item menu", str(ringkas["jumlah_menu"]))
    kartu_stat(kolom[3], "⭐ Menu terlaris", f"{terlaris[0]} ({terlaris[1]})" if terlaris else "-")

    with st.container(border=True):
        st.markdown("### Transaksi terbaru")
        terbaru = ctrl.cari_riwayat("")[:5]
        if not terbaru:
            st.info("Belum ada transaksi ☕")
        else:
            st.dataframe([{
                "ID": t.id_transaksi,
                "Waktu": t.waktu.strftime("%d %b %Y %H:%M"),
                "Pelanggan": t.pelanggan,
                "Total": rupiah(t.total),
            } for t in terbaru], hide_index=True)
