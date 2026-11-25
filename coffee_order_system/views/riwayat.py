"""Halaman Riwayat Transaksi: lihat dan cari transaksi sebelumnya."""
import streamlit as st

from utils import rupiah
from views.komponen import judul


def tampilkan(ctrl):
    judul("Riwayat Transaksi", "Cari dan lihat kembali pesanan sebelumnya.")
    with st.container(border=True):
        kata = st.text_input("Cari transaksi", key="cari_riwayat",
                             placeholder="Cari ID, pelanggan, atau nama produk...",
                             label_visibility="collapsed")
        data = ctrl.cari_riwayat(kata)
        if not data:
            st.info("Tidak ada transaksi yang cocok 🔍" if kata else "Belum ada transaksi ☕")
            return
        st.dataframe([{
            "ID": t.id_transaksi,
            "Waktu": t.waktu.strftime("%d %b %Y %H:%M"),
            "Pelanggan": t.pelanggan,
            "Item": t.jumlah_item,
            "Total": rupiah(t.total),
            "Bayar": rupiah(t.uang_bayar),
            "Kembali": rupiah(t.kembalian),
            "Status": "Lunas",
        } for t in data], hide_index=True)

        pilihan = st.selectbox("Lihat struk", [t.id_transaksi for t in data])
        transaksi = next(t for t in data if t.id_transaksi == pilihan)
        st.code(transaksi.cetak_struk(), language=None)
