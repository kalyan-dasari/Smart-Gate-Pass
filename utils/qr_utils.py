import qrcode
import socket
from pathlib import Path

QR_DIR = Path("static/qr")
QR_DIR.mkdir(parents=True, exist_ok=True)

def get_base_url():
    # Always use localhost for laptop-only scanner
    return "http://localhost:5000"

def generate_qr_for_pass(pass_id: int) -> str:
    url = f"{get_base_url()}/security/verify/{pass_id}"
    img = qrcode.make(url)
    filename = f"gatepass_{pass_id}.png"
    save_path = QR_DIR / filename
    img.save(save_path)
    return filename