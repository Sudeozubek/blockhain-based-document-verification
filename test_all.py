"""
Test Suite
==========
blockchain.py, models.py ve app.py için kapsamlı testler.
"""

import os
import sys
import json
import time
import pytest
import tempfile
import hashlib

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain import Block, Blockchain, hash_file
import models


# ─── Test Fixtures ───


@pytest.fixture
def temp_db(tmp_path):
    """Her test için geçici veritabanı."""
    db_path = str(tmp_path / "test.db")
    models.DATABASE_PATH = db_path
    models.init_db()
    yield db_path


@pytest.fixture
def chain():
    """Temiz blockchain instance."""
    bc = Blockchain()
    bc.create_genesis_block()
    return bc


@pytest.fixture
def client(temp_db):
    """Flask test client."""
    # app.py'yi import etmeden önce DB path'i ayarla
    os.environ["DATABASE_PATH"] = temp_db
    # Re-import to pick up new DB
    import importlib
    import app as app_module
    importlib.reload(models)
    models.DATABASE_PATH = temp_db
    models.init_db()

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        with app_module.app.app_context():
            models.init_db()
            # Genesis bloğu ekle
            bc = Blockchain()
            genesis = bc.create_genesis_block()
            try:
                models.save_block(genesis)
            except Exception:
                pass  # Zaten varsa
            app_module._load_chain_from_db()
        yield client


@pytest.fixture
def sample_pdf(tmp_path):
    """Basit test PDF dosyası."""
    # Minimal geçerli PDF
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n115\n%%EOF"
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(pdf_content)
    return pdf_path, pdf_content


@pytest.fixture
def modified_pdf(tmp_path):
    """Değiştirilmiş test PDF dosyası."""
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n% MODIFIED\nxref\n0 3\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \ntrailer\n<< /Size 3 /Root 1 0 R >>\nstartxref\n115\n%%EOF"
    pdf_path = tmp_path / "test_modified.pdf"
    pdf_path.write_bytes(pdf_content)
    return pdf_path, pdf_content


# ═══════════════════════════════════════════
# BLOCKCHAIN CORE TESTS
# ═══════════════════════════════════════════


class TestBlock:
    """Block sınıfı testleri."""

    def test_block_creation(self):
        block = Block(0, time.time(), {"test": True}, "0" * 64)
        assert block.index == 0
        assert block.hash is not None
        assert len(block.hash) == 64  # SHA-256 = 64 hex karakter

    def test_block_hash_deterministic(self):
        """Aynı içerik → aynı hash."""
        ts = 1000000.0
        b1 = Block(1, ts, {"msg": "hello"}, "abc")
        b2 = Block(1, ts, {"msg": "hello"}, "abc")
        assert b1.hash == b2.hash

    def test_block_hash_changes_with_data(self):
        """Farklı data → farklı hash."""
        ts = 1000000.0
        b1 = Block(1, ts, {"msg": "hello"}, "abc")
        b2 = Block(1, ts, {"msg": "world"}, "abc")
        assert b1.hash != b2.hash

    def test_block_hash_changes_with_nonce(self):
        """Farklı nonce → farklı hash."""
        ts = 1000000.0
        b1 = Block(1, ts, {"msg": "hello"}, "abc", nonce=0)
        b2 = Block(1, ts, {"msg": "hello"}, "abc", nonce=1)
        assert b1.hash != b2.hash

    def test_block_to_dict(self):
        block = Block(0, 1000.0, {"test": True}, "prev")
        d = block.to_dict()
        assert d["index"] == 0
        assert d["data"] == {"test": True}
        assert "hash" in d

    def test_block_from_dict(self):
        original = Block(1, 1000.0, {"key": "val"}, "prev123")
        d = original.to_dict()
        restored = Block.from_dict(d)
        assert restored.index == original.index
        assert restored.data == original.data
        assert restored.hash == original.hash


class TestBlockchain:
    """Blockchain sınıfı testleri."""

    def test_genesis_block(self, chain):
        assert len(chain.chain) == 1
        assert chain.chain[0].index == 0
        assert chain.chain[0].previous_hash == "0" * 64

    def test_add_block(self, chain):
        block = chain.add_block({"document_hash": "abc123"})
        assert block.index == 1
        assert block.previous_hash == chain.chain[0].hash
        assert len(chain.chain) == 2

    def test_add_multiple_blocks(self, chain):
        for i in range(5):
            chain.add_block({"doc": f"doc_{i}"})
        assert len(chain.chain) == 6  # genesis + 5

    def test_chain_linking(self, chain):
        """Her blok önceki bloğun hash'ine bağlı."""
        chain.add_block({"doc": "1"})
        chain.add_block({"doc": "2"})
        for i in range(1, len(chain.chain)):
            assert chain.chain[i].previous_hash == chain.chain[i - 1].hash

    def test_validate_valid_chain(self, chain):
        chain.add_block({"doc": "a"})
        chain.add_block({"doc": "b"})
        result = chain.validate_chain()
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_tampered_chain(self, chain):
        """Bir bloğun verisi değiştirilirse validation başarısız olmalı."""
        chain.add_block({"doc": "original"})
        chain.add_block({"doc": "next"})

        # Bloğu boz
        chain.chain[1].data = {"doc": "TAMPERED"}
        # Hash'i güncellemeden bırak → mismatch

        result = chain.validate_chain()
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_proof_of_work(self, chain):
        """Blok hash'i difficulty kadar leading zero ile başlamalı."""
        block = chain.add_block({"doc": "pow_test"})
        assert block.hash.startswith("0" * Blockchain.DIFFICULTY)

    def test_find_document_hash(self, chain):
        chain.add_block({"document_hash": "deadbeef123"})
        found = chain.find_document_hash("deadbeef123")
        assert found is not None
        assert found.data["document_hash"] == "deadbeef123"

    def test_find_nonexistent_hash(self, chain):
        found = chain.find_document_hash("doesnotexist")
        assert found is None


class TestHashFile:
    """hash_file fonksiyonu testleri."""

    def test_hash_file_basic(self):
        result = hash_file(b"hello world")
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected

    def test_hash_file_empty(self):
        result = hash_file(b"")
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_hash_file_deterministic(self):
        h1 = hash_file(b"same content")
        h2 = hash_file(b"same content")
        assert h1 == h2

    def test_hash_file_different_content(self):
        h1 = hash_file(b"content A")
        h2 = hash_file(b"content B")
        assert h1 != h2

    def test_hash_file_length(self):
        result = hash_file(b"test")
        assert len(result) == 64  # SHA-256 = 64 hex chars


# ═══════════════════════════════════════════
# DATABASE TESTS
# ═══════════════════════════════════════════


class TestDatabase:
    """models.py veritabanı testleri."""

    def test_init_db(self, temp_db):
        """Tablolar oluşturulmalı."""
        assert os.path.exists(temp_db)

    def test_save_and_get_block(self, temp_db):
        block = Block(0, time.time(), {"type": "genesis"}, "0" * 64)
        models.save_block(block)

        result = models.get_block_by_index(0)
        assert result is not None
        assert result["hash"] == block.hash

    def test_get_nonexistent_block(self, temp_db):
        result = models.get_block_by_index(999)
        assert result is None

    def test_block_count(self, temp_db):
        assert models.get_block_count() == 0
        block = Block(0, time.time(), {"type": "genesis"}, "0" * 64)
        models.save_block(block)
        assert models.get_block_count() == 1

    def test_save_and_find_document(self, temp_db):
        # Önce bir blok lazım (foreign key)
        block = Block(0, time.time(), {"type": "genesis"}, "0" * 64)
        models.save_block(block)

        now = time.time()
        models.save_document("test.pdf", "abc123hash", 1024, 0, now)

        found = models.find_document_by_hash("abc123hash")
        assert found is not None
        assert found["filename"] == "test.pdf"
        assert found["file_size"] == 1024

    def test_document_hash_exists(self, temp_db):
        block = Block(0, time.time(), {"type": "genesis"}, "0" * 64)
        models.save_block(block)
        models.save_document("test.pdf", "uniquehash", 512, 0, time.time())

        assert models.document_hash_exists("uniquehash") is True
        assert models.document_hash_exists("nothash") is False

    def test_get_all_documents(self, temp_db):
        block = Block(0, time.time(), {"type": "genesis"}, "0" * 64)
        models.save_block(block)

        models.save_document("a.pdf", "hash_a", 100, 0, time.time())
        models.save_document("b.pdf", "hash_b", 200, 0, time.time())

        docs = models.get_all_documents()
        assert len(docs) == 2


# ═══════════════════════════════════════════
# API ENDPOINT TESTS
# ═══════════════════════════════════════════


class TestAPIEndpoints:
    """Flask endpoint testleri."""

    def test_root_page(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_get_chain(self, client):
        response = client.get("/chain")
        assert response.status_code == 200
        data = response.get_json()
        assert "chain" in data
        assert "length" in data
        assert data["length"] >= 1  # En az genesis

    def test_validate_chain(self, client):
        response = client.get("/chain/validate")
        assert response.status_code == 200
        data = response.get_json()
        assert data["valid"] is True

    def test_get_block(self, client):
        response = client.get("/block/0")
        assert response.status_code == 200

    def test_get_nonexistent_block(self, client):
        response = client.get("/block/999")
        assert response.status_code == 404

    def test_upload_no_file(self, client):
        response = client.post("/upload")
        assert response.status_code == 400

    def test_upload_pdf(self, client, sample_pdf):
        pdf_path, pdf_content = sample_pdf
        response = client.post(
            "/upload",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["hash"] == hashlib.sha256(pdf_content).hexdigest()
        assert data["block_index"] >= 1

    def test_upload_duplicate(self, client, sample_pdf):
        """Aynı dosyayı iki kez yüklemek hata vermeli."""
        pdf_path, _ = sample_pdf

        client.post(
            "/upload",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )

        response = client.post(
            "/upload",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 409

    def test_upload_non_pdf(self, client, tmp_path):
        """PDF olmayan dosya reddedilmeli."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")

        response = client.post(
            "/upload",
            data={"file": (open(txt_file, "rb"), "test.txt")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 400

    def test_verify_original(self, client, sample_pdf):
        """Orijinal dosya ORIGINAL dönmeli."""
        pdf_path, _ = sample_pdf

        # Önce yükle
        client.post(
            "/upload",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )

        # Aynı dosyayı doğrula
        response = client.post(
            "/verify",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["verified"] is True
        assert data["status"] == "ORIGINAL"

    def test_verify_tampered(self, client, sample_pdf, modified_pdf):
        """Değiştirilmiş dosya TAMPERED dönmeli."""
        pdf_path, _ = sample_pdf
        mod_path, _ = modified_pdf

        # Orijinali yükle
        client.post(
            "/upload",
            data={"file": (open(pdf_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )

        # Değiştirilmişi doğrula (aynı isimle)
        response = client.post(
            "/verify",
            data={"file": (open(mod_path, "rb"), "test.pdf")},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        assert data["verified"] is False
        assert data["status"] == "TAMPERED"

    def test_verify_not_found(self, client, sample_pdf):
        """Hiç kayıtlı olmayan dosya NOT_FOUND dönmeli."""
        pdf_path, _ = sample_pdf

        response = client.post(
            "/verify",
            data={"file": (open(pdf_path, "rb"), "unknown.pdf")},
            content_type="multipart/form-data",
        )
        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "NOT_FOUND"

    def test_stats(self, client):
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert "total_blocks" in data
        assert "total_documents" in data
        assert "chain_valid" in data

    def test_documents_list(self, client):
        response = client.get("/documents")
        assert response.status_code == 200
        data = response.get_json()
        assert "documents" in data
        assert "count" in data
