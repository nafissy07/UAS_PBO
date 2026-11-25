"""Komponen tampilan yang dipakai berulang."""
import inspect

import streamlit as st

# Lebar penuh untuk tombol. Streamlit versi baru memakai width="stretch",
# versi lama memakai use_container_width=True. Dipilih otomatis.
try:
    _punya_width = "width" in inspect.signature(st.button).parameters
except (TypeError, ValueError):
    _punya_width = False
LEBAR_PENUH = {"width": "stretch"} if _punya_width else {"use_container_width": True}


def judul(teks: str, keterangan: str = ""):
    st.markdown(f"# {teks}")
    if keterangan:
        st.caption(keterangan)


def kartu_stat(kolom, label: str, nilai: str):
    with kolom:
        with st.container(border=True):
            st.caption(label)
            st.markdown(f"### {nilai}")


def flash(tipe: str, teks: str):
    """Simpan pesan agar tetap tampil setelah halaman dimuat ulang."""
    st.session_state["flash"] = (tipe, teks)


def tampilkan_flash():
    pesan = st.session_state.pop("flash", None)
    if pesan:
        tipe, teks = pesan
        (st.success if tipe == "success" else st.error)(teks)
