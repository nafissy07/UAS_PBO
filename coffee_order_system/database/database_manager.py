"""DatabaseManager memakai Singleton Pattern.

Hanya ada SATU objek DatabaseManager selama aplikasi berjalan, jadi seluruh
bagian aplikasi memakai satu koneksi SQLite yang sama.
"""
import os
import sqlite3
import threading


class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path: str = "data/kedai_kopi.db"):
        with cls._lock:
            if cls._instance is None:               # objek dibuat hanya kali pertama
                instance = super().__new__(cls)
                instance._siapkan(db_path)
                cls._instance = instance
            return cls._instance

    def __init__(self, db_path: str = "data/kedai_kopi.db"):
        pass                                        # semua setup ada di _siapkan()

    @classmethod
    def get_instance(cls, db_path: str = "data/kedai_kopi.db") -> "DatabaseManager":
        return cls(db_path)

    @classmethod
    def reset(cls):
        """Tutup koneksi dan hapus instance. Dipakai untuk pengujian."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._koneksi.close()
            cls._instance = None

    # ---------- setup ----------
    def _siapkan(self, db_path: str):
        if db_path != ":memory:":
            folder = os.path.dirname(db_path)
            if folder:
                os.makedirs(folder, exist_ok=True)
        self._db_path = db_path
        self._akses = threading.RLock()
        self._koneksi = sqlite3.connect(db_path, check_same_thread=False)
        self._koneksi.row_factory = sqlite3.Row
        self._buat_tabel()

    def _buat_tabel(self):
        with self._akses:
            self._koneksi.executescript("""
                CREATE TABLE IF NOT EXISTS menu (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    nama     TEXT    NOT NULL,
                    kategori TEXT    NOT NULL,
                    jenis    TEXT    DEFAULT '',
                    harga    INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transaksi (
                    id_transaksi TEXT PRIMARY KEY,
                    waktu        TEXT NOT NULL,
                    kasir        TEXT,
                    pelanggan    TEXT,
                    telepon      TEXT,
                    total        INTEGER NOT NULL,
                    uang_bayar   INTEGER NOT NULL,
                    kembalian    INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS item_transaksi (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_transaksi TEXT    NOT NULL,
                    nama         TEXT    NOT NULL,
                    jumlah       INTEGER NOT NULL,
                    harga        INTEGER NOT NULL
                );
            """)
            self._koneksi.commit()

    # ---------- akses data ----------
    def execute(self, sql: str, params=()) -> int:
        """Jalankan satu perintah tulis. Mengembalikan id baris terakhir."""
        with self._akses:
            kursor = self._koneksi.execute(sql, params)
            self._koneksi.commit()
            return kursor.lastrowid

    def execute_atomik(self, perintah: list):
        """Jalankan beberapa perintah sekaligus: semua berhasil atau semua dibatalkan."""
        with self._akses:
            try:
                for sql, params in perintah:
                    self._koneksi.execute(sql, params)
                self._koneksi.commit()
            except Exception:
                self._koneksi.rollback()
                raise

    def fetch_all(self, sql: str, params=()) -> list:
        with self._akses:
            return self._koneksi.execute(sql, params).fetchall()

    def fetch_one(self, sql: str, params=()):
        with self._akses:
            return self._koneksi.execute(sql, params).fetchone()
