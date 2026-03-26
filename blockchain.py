"""
Blockchain Core
================
SHA-256 tabanlı blok zinciri.
Her blok bir dokümanın hash'ini, timestamp'ini ve önceki bloğun hash'ini tutar.
"""

import hashlib
import json
import time
from typing import List, Optional, Dict, Any


class Block:
    """Zincirdeki tek bir blok."""

    def __init__(
        self,
        index: int,
        timestamp: float,
        data: Dict[str, Any],
        previous_hash: str,
        nonce: int = 0,
    ):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        """Blok içeriğinden SHA-256 hash hesapla."""
        block_content = json.dumps(
            {
                "index": self.index,
                "timestamp": self.timestamp,
                "data": self.data,
                "previous_hash": self.previous_hash,
                "nonce": self.nonce,
            },
            sort_keys=True,
        )
        return hashlib.sha256(block_content.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Block":
        """Sözlükten Block oluştur (DB'den okurken kullanılır)."""
        block = cls(
            index=d["index"],
            timestamp=d["timestamp"],
            data=d["data"],
            previous_hash=d["previous_hash"],
            nonce=d.get("nonce", 0),
        )
        # DB'deki hash ile hesaplanan hash tutarlı olmalı
        if block.hash != d.get("hash"):
            block.hash = d["hash"]  # DB'den gelen hash'i koru (validasyon ayrı yapılır)
        return block


class Blockchain:
    """
    Basit blockchain implementasyonu.
    Doküman hash'lerini immutable bir zincirde saklar.
    """

    DIFFICULTY = 2  # Leading zero sayısı (demo için düşük)

    def __init__(self):
        self.chain: List[Block] = []

    @property
    def latest_block(self) -> Optional[Block]:
        return self.chain[-1] if self.chain else None

    def create_genesis_block(self) -> Block:
        """Genesis (ilk) bloğu oluştur."""
        genesis = Block(
            index=0,
            timestamp=time.time(),
            data={"type": "genesis", "message": "Genesis Block"},
            previous_hash="0" * 64,
        )
        self.chain.append(genesis)
        return genesis

    def add_block(self, data: Dict[str, Any]) -> Block:
        """Zincire yeni blok ekle (basit PoW ile)."""
        if not self.chain:
            self.create_genesis_block()

        previous = self.latest_block
        new_block = Block(
            index=previous.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous.hash,
        )

        # Basit Proof of Work
        target = "0" * self.DIFFICULTY
        while not new_block.hash.startswith(target):
            new_block.nonce += 1
            new_block.hash = new_block.compute_hash()

        self.chain.append(new_block)
        return new_block

    def validate_chain(self) -> Dict[str, Any]:
        """
        Tüm zinciri doğrula.
        Her bloğun hash'i doğru mu? previous_hash bağlantıları tutarlı mı?
        """
        errors = []

        for i in range(len(self.chain)):
            block = self.chain[i]

            # Hash doğrulama
            computed = block.compute_hash()
            if block.hash != computed:
                errors.append({
                    "block_index": i,
                    "error": "hash_mismatch",
                    "stored_hash": block.hash,
                    "computed_hash": computed,
                })

            # Bağlantı doğrulama (genesis hariç)
            if i > 0:
                previous = self.chain[i - 1]
                if block.previous_hash != previous.hash:
                    errors.append({
                        "block_index": i,
                        "error": "broken_link",
                        "expected_previous": previous.hash,
                        "actual_previous": block.previous_hash,
                    })

        return {
            "valid": len(errors) == 0,
            "chain_length": len(self.chain),
            "errors": errors,
        }

    def find_document_hash(self, doc_hash: str) -> Optional[Block]:
        """Zincirde belirli bir doküman hash'ini ara."""
        for block in self.chain:
            if block.data.get("document_hash") == doc_hash:
                return block
        return None

    def load_from_db_rows(self, rows: list):
        """Veritabanı satırlarından zinciri yükle."""
        self.chain = []
        for row in rows:
            data = json.loads(row["data"]) if isinstance(row["data"], str) else row["data"]
            block = Block(
                index=row["index_num"],
                timestamp=row["timestamp"],
                data=data,
                previous_hash=row["previous_hash"],
                nonce=row["nonce"],
            )
            block.hash = row["hash"]
            self.chain.append(block)


def hash_file(file_bytes: bytes) -> str:
    """Dosya içeriğinin SHA-256 hash'ini hesapla."""
    return hashlib.sha256(file_bytes).hexdigest()
