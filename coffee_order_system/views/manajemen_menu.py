"""Halaman Manajemen Menu: tambah, ubah, hapus, dan lihat daftar menu."""
import streamlit as st

from models.menu import Menu
from utils import rupiah
from views.komponen import judul, flash, tampilkan_flash


def _mulai_ubah(id_menu):
    st.session_state.edit_id = id_menu


def _batal_ubah():
    st.session_state.edit_id = None


def _minta_hapus(id_menu):
    st.session_state.hapus_id = id_menu


def _batal_hapus():
    st.session_state.hapus_id = None


def _konfirmasi_hapus(ctrl):
    ctrl.hapus_menu(st.session_state.hapus_id)
    st.session_state.hapus_id = None
    flash("success", "Menu dihapus")


def _form(ctrl):
    ss = st.session_state
    menu = ctrl.cari_menu(ss.edit_id) if ss.edit_id else None
    kategori = Menu.daftar_kategori()
    with st.container(border=True):
        st.markdown("### Ubah Menu" if menu else "### Tambah Menu")
        with st.form(f"form_menu_{ss.edit_id}", clear_on_submit=True):
            nama = st.text_input("Nama produk", value=menu.nama if menu else "")
            kat = st.selectbox("Kategori", kategori,
                               index=kategori.index(menu.kategori) if menu else 0)
            jenis = st.text_input("Jenis (mis. Espresso, Teh, Roti)", value=menu.jenis if menu else "")
            harga = st.number_input("Harga (Rp)", min_value=0, step=1000,
                                    value=menu.harga if menu else 0)
            kirim = st.form_submit_button("Simpan" if menu else "Tambah", type="primary")
        if menu:
            st.button("Batal", on_click=_batal_ubah)
        if kirim:
            try:
                if menu:
                    ctrl.ubah_menu(menu.id, kat, nama, jenis, harga)
                    flash("success", "Menu diperbarui ✓")
                else:
                    ctrl.tambah_menu(kat, nama, jenis, harga)
                    flash("success", "Menu ditambahkan ✓")
                ss.edit_id = None
                st.rerun()
            except ValueError as e:                 # nama kosong / harga tidak valid
                st.error(str(e))


def _daftar(ctrl):
    ss = st.session_state
    daftar = ctrl.daftar_menu()
    with st.container(border=True):
        st.markdown(f"### Daftar Menu ({len(daftar)})")
        if ss.hapus_id:
            menu = ctrl.cari_menu(ss.hapus_id)
            if menu:
                st.warning(f"Hapus menu “{menu.nama}”?")
                ya, tidak, _ = st.columns([1, 1, 3])
                ya.button("Ya, hapus", on_click=_konfirmasi_hapus, args=(ctrl,), type="primary")
                tidak.button("Batal", on_click=_batal_hapus, key="batal_hapus")
        if not daftar:
            st.info("Belum ada menu.")
            return
        for menu in daftar:
            nama, kat, harga, ubah, hapus = st.columns([4, 2, 2, 1, 1])
            nama.markdown(f"**{menu.nama}**  \n{menu.jenis or '-'}")
            kat.write(f"{type(menu).IKON} {menu.kategori}")
            harga.write(rupiah(menu.harga))
            ubah.button("Ubah", key=f"ubah_{menu.id}", on_click=_mulai_ubah, args=(menu.id,))
            hapus.button("Hapus", key=f"hapus_{menu.id}", on_click=_minta_hapus, args=(menu.id,))


def tampilkan(ctrl):
    ss = st.session_state
    ss.setdefault("edit_id", None)
    ss.setdefault("hapus_id", None)
    judul("Manajemen Menu", "Tambah, ubah, hapus, dan lihat daftar menu kopi, non-kopi, dan makanan.")
    tampilkan_flash()
    kiri, kanan = st.columns([1, 2], gap="large")
    with kiri:
        _form(ctrl)
    with kanan:
        _daftar(ctrl)
