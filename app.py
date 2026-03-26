"""
Flask Application
=================
Doküman doğrulama sistemi API endpoint'leri.

Endpoints:
    POST /upload           — PDF yükle, hash'le, bloğa ekle
    POST /verify           — PDF yükle, hash'i zincirle karşılaştır
    GET  /chain            — Tüm blockchain'i getir
    GET  /chain/validate   — Zincir bütünlüğünü doğrula
    GET  /block/<index>    — Belirli bir bloğu getir
    GET  /documents        — Kayıtlı dokümanları listele
    GET  /stats            — Sistem istatistikleri
"""

import os
import time
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template

from blockchain import Blockchain, hash_file
from models import (
    init_db,
    save_block,
    save_document,
    get_all_blocks,
    get_block_by_index,
    get_block_count,
    find_document_by_hash,
    get_all_documents,
    get_document_count,
    document_hash_exists,
)

# ─── App Setup ───

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

ALLOWED_EXTENSIONS = {"pdf"}

# Blockchain instance (zincir DB'den yüklenir)
blockchain = Blockchain()


def _load_chain_from_db():
    """Zinciri veritabanından yükle."""
    rows = get_all_blocks()
    blockchain.load_from_db_rows(rows)


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _format_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─── Startup ───

with app.app_context():
    init_db()
    _load_chain_from_db()
    # Genesis yoksa oluştur
    if len(blockchain.chain) == 0:
        genesis = blockchain.create_genesis_block()
        save_block(genesis)


# ─── Page Routes ───


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/upload.html")
def upload_page():
    return render_template("upload.html")


@app.route("/verify.html")
def verify_page():
    return render_template("verify.html")


@app.route("/dashboard.html")
def dashboard_page():
    return render_template("dashboard.html")


@app.route("/history.html")
def history_page():
    return render_template("history.html")


# ─── API Endpoints ───


@app.route("/upload", methods=["POST"])
def upload_document():
    """
    PDF doküman yükle ve blockchain'e kaydet.

    Request: multipart/form-data, field name: "file"
    Response: {
        "message": str,
        "block_index": int,
        "hash": str,
        "filename": str,
        "file_size": int,
        "timestamp": str
    }
    """
    # Dosya kontrolü
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Dosyayı oku ve hash'le
    file_bytes = file.read()
    file_size = len(file_bytes)
    file_hash = hash_file(file_bytes)

    # Aynı doküman daha önce kayıtlı mı?
    if document_hash_exists(file_hash):
        existing = find_document_by_hash(file_hash)
        return jsonify({
            "error": "Document already registered",
            "existing_block_index": existing["block_index"],
            "hash": file_hash,
            "registered_at": _format_timestamp(existing["registered_at"]),
        }), 409

    # Zinciri DB'den yenile
    _load_chain_from_db()

    # Yeni blok oluştur
    block_data = {
        "type": "document",
        "document_hash": file_hash,
        "filename": file.filename,
        "file_size": file_size,
    }

    new_block = blockchain.add_block(block_data)
    now = time.time()

    # DB'ye kaydet
    save_block(new_block)
    save_document(
        filename=file.filename,
        file_hash=file_hash,
        file_size=file_size,
        block_index=new_block.index,
        registered_at=now,
    )

    return jsonify({
        "message": "Document registered successfully",
        "block_index": new_block.index,
        "hash": file_hash,
        "block_hash": new_block.hash,
        "filename": file.filename,
        "file_size": file_size,
        "nonce": new_block.nonce,
        "timestamp": _format_timestamp(now),
    }), 201


@app.route("/verify", methods=["POST"])
def verify_document():
    """
    PDF dokümanı yükle ve blockchain'deki kayıtla karşılaştır.

    Request: multipart/form-data, field name: "file"
    Response: {
        "verified": bool,
        "status": "ORIGINAL" | "TAMPERED" | "NOT_FOUND",
        "current_hash": str,
        ...
    }
    """
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    file_bytes = file.read()
    current_hash = hash_file(file_bytes)

    # Zincirde ara
    existing = find_document_by_hash(current_hash)

    if existing:
        # Hash eşleşti → orijinal doküman
        return jsonify({
            "verified": True,
            "status": "ORIGINAL",
            "message": "Document is authentic and unmodified",
            "current_hash": current_hash,
            "original_hash": existing["file_hash"],
            "filename": existing["filename"],
            "block_index": existing["block_index"],
            "registered_at": _format_timestamp(existing["registered_at"]),
        })
    else:
        # Hash bulunamadı → ya hiç kayıtlı değil ya da değiştirilmiş
        # Dosya adıyla eşleşen bir kayıt var mı kontrol et
        all_docs = get_all_documents()
        name_match = None
        for doc in all_docs:
            if doc["filename"] == file.filename:
                name_match = doc
                break

        if name_match:
            # Aynı isimde dosya kayıtlı ama hash farklı → TAMPERED
            return jsonify({
                "verified": False,
                "status": "TAMPERED",
                "message": "Document has been modified since registration",
                "current_hash": current_hash,
                "original_hash": name_match["file_hash"],
                "filename": file.filename,
                "block_index": name_match["block_index"],
                "registered_at": _format_timestamp(name_match["registered_at"]),
            })
        else:
            # Hiç kayıtlı değil
            return jsonify({
                "verified": False,
                "status": "NOT_FOUND",
                "message": "Document not found in the blockchain",
                "current_hash": current_hash,
                "filename": file.filename,
            }), 404


@app.route("/chain", methods=["GET"])
def get_chain():
    """Tüm blockchain'i getir."""
    _load_chain_from_db()
    return jsonify({
        "chain": [block.to_dict() for block in blockchain.chain],
        "length": len(blockchain.chain),
    })


@app.route("/chain/validate", methods=["GET"])
def validate_chain():
    """Blockchain bütünlüğünü doğrula."""
    _load_chain_from_db()
    result = blockchain.validate_chain()
    return jsonify(result)


@app.route("/block/<int:index>", methods=["GET"])
def get_block(index: int):
    """Belirli bir bloğu index'e göre getir."""
    row = get_block_by_index(index)
    if not row:
        return jsonify({"error": f"Block {index} not found"}), 404

    block_data = row.copy()
    block_data["data"] = json.loads(block_data["data"]) if isinstance(block_data["data"], str) else block_data["data"]
    block_data["timestamp_formatted"] = _format_timestamp(block_data["timestamp"])
    return jsonify(block_data)


@app.route("/documents", methods=["GET"])
def list_documents():
    """Tüm kayıtlı dokümanları listele."""
    docs = get_all_documents()
    for doc in docs:
        doc["registered_at_formatted"] = _format_timestamp(doc["registered_at"])
    return jsonify({
        "documents": docs,
        "count": len(docs),
    })


@app.route("/stats", methods=["GET"])
def get_stats():
    """Sistem istatistikleri."""
    _load_chain_from_db()
    validation = blockchain.validate_chain()
    return jsonify({
        "total_blocks": get_block_count(),
        "total_documents": get_document_count(),
        "chain_valid": validation["valid"],
        "chain_errors": len(validation["errors"]),
    })


# ─── Error Handlers ───


@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16 MB."}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


# ─── Run ───

if __name__ == "__main__":
    print("🚀 Document Verification System starting...")
    print(f"📦 Blocks in chain: {get_block_count()}")
    print(f"📄 Documents registered: {get_document_count()}")
    print(f"🔗 http://localhost:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
