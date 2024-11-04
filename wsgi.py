import sys
import os
from app import app as app  # Ubah 'app' sesuai nama file aplikasi utama Anda

# Tambahkan path proyek ke sistem PATH
sys.path.insert(0, os.path.dirname(__file__))
