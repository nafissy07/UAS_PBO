"""Titik masuk aplikasi. Jalankan dengan:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

from controllers.kedai_controller import KedaiController
from views import dashboard, manajemen_menu, pemesanan, riwayat, style

st.set_page_config(page_title="Coffee Order System", page_icon="☕", layout="wide")

DB_PATH = str(Path(__file__).parent / "data" / "kedai_kopi.db")

HALAMAN = {
    "🏠 Dashboard": dashboard.tampilkan,
    "🧾 Pemesanan": pemesanan.tampilkan,
    "📋 Manajemen Menu": manajemen_menu.tampilkan,
    "🕘 Riwayat Transaksi": riwayat.tampilkan,
}


@st.cache_resource
def ambil_controller() -> KedaiController:
    """Controller dibuat sekali saja, lalu dipakai ulang di setiap interaksi."""
    return KedaiController(DB_PATH)


def main():
    ctrl = ambil_controller()
    style.terapkan()

    with st.sidebar:
        st.markdown('<div class="brand">☕ Coffee Order<small>System · Kelompok 3</small></div>',
                    unsafe_allow_html=True)
        st.write("")
        pilihan = st.radio("Navigasi", list(HALAMAN), label_visibility="collapsed")
        st.divider()
        st.caption(f"Kasir aktif · {ctrl.kasir.id_kasir}")
        nama = st.text_input("Nama kasir", value=ctrl.kasir.nama, key="input_kasir")
        if nama != ctrl.kasir.nama:
            try:
                ctrl.ganti_nama_kasir(nama)
            except ValueError:
                st.warning("Nama kasir tidak boleh kosong")

    HALAMAN[pilihan](ctrl)


main()
