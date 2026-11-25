"""Halaman Pemesanan: pilih produk, atur jumlah, lalu bayar."""
import streamlit as st

from models.menu import Menu
from utils import rupiah
from views.komponen import LEBAR_PENUH, judul


# ---------- callback tombol (dijalankan sebelum halaman digambar ulang) ----------
def _tambah(menu):
    st.session_state.pesanan.tambah_item(menu)


def _ubah_jumlah(menu, selisih):
    pesanan = st.session_state.pesanan
    for item in pesanan.daftar_item:
        if item.menu.id == menu.id:
            pesanan.ubah_jumlah(menu, item.jumlah + selisih)   # <= 0 berarti terhapus
            return


def _hapus(menu):
    st.session_state.pesanan.hapus_item(menu)


def _set_uang(nilai):
    st.session_state.uang_bayar = int(nilai)


def _tutup_struk():
    st.session_state.struk = None


def _bayar(ctrl):
    ss = st.session_state
    try:
        transaksi = ctrl.bayar(ss.pesanan, ss.get("uang_bayar", 0),
                               ss.get("nama_pelanggan", ""), ss.get("telepon", ""))
    except ValueError as e:                     # uang kurang / pesanan kosong
        ss.error_bayar = str(e)
        return
    ss.error_bayar = None
    ss.struk = transaksi
    ss.pesanan = ctrl.pesanan_baru()            # mulai pesanan baru
    ss.uang_bayar = 0
    ss.nama_pelanggan = ""
    ss.telepon = ""


# ---------- tampilan ----------
def _katalog(ctrl):
    with st.container(border=True):
        kata = st.text_input("Cari produk", placeholder="Cari produk...",
                             label_visibility="collapsed", key="cari_produk")
        kategori = st.radio("Kategori", ["Semua", *Menu.daftar_kategori()],
                            horizontal=True, label_visibility="collapsed", key="kategori")
        daftar = ctrl.daftar_menu(kategori, kata)
        if not daftar:
            st.info("Produk tidak ditemukan")
            return
        kolom = st.columns(3)
        for i, menu in enumerate(daftar):
            with kolom[i % 3]:
                st.button(f"{type(menu).IKON} {menu.nama} · {rupiah(menu.harga)}",
                          key=f"tambah_{menu.id}", on_click=_tambah, args=(menu,),
                          **LEBAR_PENUH)


def _keranjang(ctrl):
    ss = st.session_state
    pesanan = ss.pesanan
    total = pesanan.hitung_total()
    with st.container(border=True):
        st.markdown("### Daftar Pesanan")
        a, b = st.columns(2)
        a.text_input("Nama pelanggan", key="nama_pelanggan", placeholder="Nama pelanggan",
                     label_visibility="collapsed")
        b.text_input("No. telepon", key="telepon", placeholder="No. telepon",
                     label_visibility="collapsed")

        if pesanan.kosong:
            st.caption("Keranjang kosong. Klik produk untuk menambah.")
        for item in pesanan.daftar_item:
            menu = item.menu
            nama, minus, plus, hapus = st.columns([4, 1, 1, 1])
            nama.markdown(f"**{menu.nama}**  \n{rupiah(menu.harga)} × {item.jumlah}")
            minus.button("➖", key=f"min_{menu.id}", on_click=_ubah_jumlah, args=(menu, -1))
            plus.button("➕", key=f"plus_{menu.id}", on_click=_ubah_jumlah, args=(menu, 1))
            hapus.button("🗑️", key=f"hapus_{menu.id}", on_click=_hapus, args=(menu,))

        st.markdown(f"### Total: {rupiah(total)}")
        uang = st.number_input("Nominal bayar (Rp)", min_value=0, step=1000, key="uang_bayar")
        c1, c2, c3 = st.columns(3)
        c1.button("Uang pas", on_click=_set_uang, args=(total,), **LEBAR_PENUH)
        c2.button("50.000", on_click=_set_uang, args=(50000,), **LEBAR_PENUH)
        c3.button("100.000", on_click=_set_uang, args=(100000,), **LEBAR_PENUH)

        st.markdown(f"Kembalian: **{rupiah(max(0, uang - total))}**")
        if ss.get("error_bayar"):
            st.error(ss.error_bayar)
        st.button("Proses Bayar", type="primary", on_click=_bayar, args=(ctrl,),
                  disabled=pesanan.kosong or uang < total, **LEBAR_PENUH)


def _struk():
    with st.container(border=True):
        st.success("Transaksi berhasil disimpan ✓")
        st.code(st.session_state.struk.cetak_struk(), language=None)
        st.button("Tutup struk", on_click=_tutup_struk)


def tampilkan(ctrl):
    ss = st.session_state
    if "pesanan" not in ss:
        ss.pesanan = ctrl.pesanan_baru()
    ss.setdefault("struk", None)
    ss.setdefault("error_bayar", None)

    judul("Pemesanan", "Pilih produk, tentukan jumlah, lalu proses pembayaran.")
    if ss.struk is not None:
        _struk()
    kiri, kanan = st.columns([2, 1], gap="large")
    with kiri:
        _katalog(ctrl)
    with kanan:
        _keranjang(ctrl)
