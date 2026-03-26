"""
Database Models
===============
SQLite veritabanı yönetimi.
blocks ve documents tablolarını yönetir.
"""

import sqlite3
import json
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = os.environ.get("DATABASE_PATH", "blockchain.db")


@contextmanager
def get_db():
    """Veritabanı bağlantısı context manager."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Veritabanı tablolarını oluştur."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS blocks (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                index_num       INTEGER UNIQUE NOT NULL,
                timestamp       REAL    NOT NULL,
                data            TEXT    NOT NULL,
                previous_hash   TEXT    NOT NULL,
                hash            TEXT    NOT NULL,
                nonce           INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS documents (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                filename        TEXT    NOT NULL,
                file_hash       TEXT    NOT NULL,
                file_size       INTEGER NOT NULL,
                block_index     INTEGER NOT NULL,
                registered_at   REAL    NOT NULL,
                FOREIGN KEY (block_index) REFERENCES blocks(index_num)
            );

            CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);
            CREATE INDEX IF NOT EXISTS idx_blocks_hash ON blocks(hash);
        """)


# ─── Block Operations ───


def save_block(block) -> None:
    """Bloğu veritabanına kaydet."""
    with get_db() as conn:
        conn.execute(
            """INSERT INTO blocks (index_num, timestamp, data, previous_hash, hash, nonce)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                block.index,
                block.timestamp,
                json.dumps(block.data, ensure_ascii=False),
                block.previous_hash,
                block.hash,
                block.nonce,
            ),
        )


def get_all_blocks() -> List[Dict[str, Any]]:
    """Tüm blokları sıralı getir."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM blocks ORDER BY index_num ASC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_block_by_index(index: int) -> Optional[Dict[str, Any]]:
    """Index'e göre blok getir."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM blocks WHERE index_num = ?", (index,)
        ).fetchone()
        return dict(row) if row else None


def get_block_count() -> int:
    """Toplam blok sayısı."""
    with get_db() as conn:
        result = conn.execute("SELECT COUNT(*) FROM blocks").fetchone()
        return result[0]


# ─── Document Operations ───


def save_document(filename: str, file_hash: str, file_size: int, block_index: int, registered_at: float) -> int:
    """Dokümanı veritabanına kaydet. Yeni ID döndürür."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO documents (filename, file_hash, file_size, block_index, registered_at)
               VALUES (?, ?, ?, ?, ?)""",
            (filename, file_hash, file_size, block_index, registered_at),
        )
        return cursor.lastrowid


def find_document_by_hash(file_hash: str) -> Optional[Dict[str, Any]]:
    """Hash'e göre doküman ara."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE file_hash = ? ORDER BY registered_at DESC LIMIT 1",
            (file_hash,),
        ).fetchone()
        return dict(row) if row else None


def get_all_documents() -> List[Dict[str, Any]]:
    """Tüm dokümanları getir."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM documents ORDER BY registered_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_document_count() -> int:
    """Toplam doküman sayısı."""
    with get_db() as conn:
        result = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
        return result[0]


def document_hash_exists(file_hash: str) -> bool:
    """Bu hash zaten kayıtlı mı?"""
    with get_db() as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE file_hash = ?",
            (file_hash,),
        ).fetchone()
        return result[0] > 0
