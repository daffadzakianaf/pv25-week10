import sys
import csv
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem
)

class BukuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("form_buku.ui", self)
        self.setWindowTitle("Manajemen Data Buku")

        self.conn = sqlite3.connect("buku.db")
        self.cursor = self.conn.cursor()
        self.init_db()

        # Aksi tombol
        self.simpan.clicked.connect(self.simpan_data)
        self.hapus.clicked.connect(self.hapus_data)
        self.exportCSV.clicked.connect(self.export_csv)
        self.pencarian.textChanged.connect(self.cari_data)
        self.tabel.cellChanged.connect(self.edit_data)

        self.load_data()

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                judul TEXT,
                pengarang TEXT,
                tahun TEXT
            )
        """)
        self.conn.commit()

    def simpan_data(self):
        judul = self.judul.text()
        pengarang = self.pengarang.text()
        tahun = self.tahun.text()

        if not judul or not pengarang or not tahun:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi.")
            return

        self.cursor.execute("INSERT INTO buku (judul, pengarang, tahun) VALUES (?, ?, ?)",
                            (judul, pengarang, tahun))
        self.conn.commit()
        self.judul.clear()
        self.pengarang.clear()
        self.tahun.clear()
        self.load_data()

    def load_data(self, keyword=""):
        self.tabel.blockSignals(True)
        self.tabel.setRowCount(0)
        self.tabel.setColumnCount(4)
        self.tabel.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        if keyword:
            query = f"SELECT * FROM buku WHERE id LIKE ? OR judul LIKE ? OR pengarang LIKE ? OR tahun LIKE ?"
            keyword = f"%{keyword}%"
            self.cursor.execute(query, (keyword, keyword, keyword, keyword))
        else:
            self.cursor.execute("SELECT * FROM buku")
        for row_data in self.cursor.fetchall():
            row_number = self.tabel.rowCount()
            self.tabel.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tabel.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        self.tabel.blockSignals(False)

    def hapus_data(self):
        selected = self.tabel.currentRow()
        if selected >= 0:
            id_item = self.tabel.item(selected, 0)
            if id_item:
                id_val = id_item.text()
                self.cursor.execute("DELETE FROM buku WHERE id = ?", (id_val,))
                self.conn.commit()
                self.tabel.removeRow(selected)

    def edit_data(self, row, col):
        id_val = self.tabel.item(row, 0).text()
        new_value = self.tabel.item(row, col).text()
        kolom = ["id", "judul", "pengarang", "tahun"][col]
        if kolom != "id":
            self.cursor.execute(f"UPDATE buku SET {kolom} = ? WHERE id = ?", (new_value, id_val))
            self.conn.commit()

    def cari_data(self):
        keyword = self.pencarian.text()
        self.load_data(keyword)

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File", "", "CSV Files (*.csv)")
        if path:
            with open(path, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                self.cursor.execute("SELECT * FROM buku")
                for row in self.cursor.fetchall():
                    writer.writerow(row)
            QMessageBox.information(self, "Sukses", "Data berhasil diekspor.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BukuApp()
    window.show()
    sys.exit(app.exec())
