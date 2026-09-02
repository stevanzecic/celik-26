from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
import threading

from gui.widgets.label_row import LabelRow


class MedicalCardWidget(QWidget):
    _rfzo_finished = pyqtSignal(object)  # error or None

    def __init__(self):
        super().__init__()

        self._doc = None
        self._rfzo_in_progress = False

        self._rfzo_finished.connect(self._on_rfzo_finished)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)

        # ---------------- Title ----------------
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.title)

        # ---------------- Rows ----------------
        self.rows = {
            # Person
            "given": LabelRow("Ime:"),
            "parent": LabelRow("Ime jednog roditelja:"),
            "family": LabelRow("Prezime:"),
            "birth": LabelRow("Datum rođenja:"),
            "place": LabelRow("Mesto, opština i država:"),
            "street": LabelRow("Ulica:"),
            "gender": LabelRow("Pol:"),
            "language": LabelRow("Jezik:"),
            "lbo": LabelRow("LBO:"),
            "jmbg": LabelRow("JMBG:"),

            # Card
            "issue": LabelRow("Datum izdavanja:"),
            "expiry": LabelRow("Datum važenja:"),
            "valid": LabelRow("Overena do:"),
            "permanent": LabelRow("Trajno overena:"),

            # Carrier
            "carrier_name": LabelRow("Nosilac osiguranja:"),
            "carrier_lbo": LabelRow("LBO nosioca:"),
            "carrier_jmbg": LabelRow("JMBG nosioca:"),
            "carrier_relation": LabelRow("Srodstvo:"),

            # Insurance
            "insurance_basis": LabelRow("Osnov osiguranja:"),
            "insurance_start": LabelRow("Početak osiguranja:"),
            "insurance_desc": LabelRow("Opis osiguranja:"),

            # Taxpayer
            "taxpayer_name": LabelRow("Naziv obveznika:"),
            "taxpayer_res": LabelRow("Sedište:"),
            "taxpayer_no": LabelRow("Registarski broj:"),
            "taxpayer_id": LabelRow("PIB / JMBG:"),
            "taxpayer_act": LabelRow("Delatnost:"),
        }

        # ---------------- Layout ----------------
        layout.addWidget(self._section("Opšti podaci o osiguraniku"))
        for k in (
            "given", "parent", "family", "birth",
            "place", "street", "gender",
            "language", "lbo", "jmbg"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("Podaci o kartici zdravstvenog osiguranja"))
        for k in ("issue", "expiry", "valid", "permanent"):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("Podaci o nosiocu osiguranja"))
        for k in (
            "carrier_name", "carrier_lbo",
            "carrier_jmbg", "carrier_relation"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("Podaci o osiguranju"))
        for k in (
            "insurance_basis",
            "insurance_start",
            "insurance_desc"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("Podaci o obvezniku"))
        for k in (
            "taxpayer_name", "taxpayer_res",
            "taxpayer_no", "taxpayer_id",
            "taxpayer_act"
        ):
            layout.addWidget(self.rows[k])

        # ---------------- RFZO ----------------
        self.rfzo_btn = QPushButton("Proveri važenje preko RFZO")
        self.rfzo_btn.clicked.connect(self._update_rfzo)
        layout.addWidget(self.rfzo_btn)

        layout.addStretch()
        scroll.setWidget(container)

        main = QVBoxLayout(self)
        main.addWidget(scroll)

    # =====================================================
    # Data binding
    # =====================================================

    def set_data(self, doc):
        if doc is not self._doc:
            self._rfzo_in_progress = False
            self.rfzo_btn.setText("Proveri važenje preko RFZO")
        self._doc = doc

        self.title.setText(doc.full_name_latin())

        self.rows["given"].set_value(f"{doc.first_name} ({doc.first_name_latin})")
        self.rows["parent"].set_value(doc.parent_name)
        self.rows["family"].set_value(f"{doc.last_name} ({doc.last_name_latin})")
        self.rows["birth"].set_value(doc.date_of_birth)
        self.rows["place"].set_value(
            ", ".join(value for value in (doc.place, doc.municipality, doc.country) if value)
        )
        self.rows["street"].set_value(
            " ".join(value for value in (doc.street, doc.number) if value)
        )
        self.rows["gender"].set_value(doc.gender)
        self.rows["language"].set_value(doc.print_language)
        self.rows["lbo"].set_value(doc.insurant_number)
        self.rows["jmbg"].set_value(doc.jmbg)

        self.rows["issue"].set_value(doc.date_of_issue)
        self.rows["expiry"].set_value(doc.date_of_expiry)
        self.rows["valid"].set_value(doc.valid_until)
        self.rows["permanent"].set_value("Da" if doc.permanently_valid else "Ne")

        # Optional sections
        self._opt(
            "carrier_name",
            " ".join(
                value
                for value in (doc.carrier_given_name_latin, doc.carrier_family_name_latin)
                if value
            ),
        )
        self._opt("carrier_lbo", getattr(doc, "carrier_insurant_number", ""))
        self._opt("carrier_jmbg", getattr(doc, "carrier_id_number", ""))
        self._opt("carrier_relation", getattr(doc, "carrier_relationship", ""))

        self._opt("insurance_basis", getattr(doc, "insurance_basis_rzzo", ""))
        self._opt("insurance_start", getattr(doc, "insurance_start_date", ""))
        self._opt("insurance_desc", getattr(doc, "insurance_description", ""))

        self._opt("taxpayer_name", getattr(doc, "taxpayer_name", ""))
        self._opt("taxpayer_res", getattr(doc, "taxpayer_residence", ""))
        self._opt("taxpayer_no", getattr(doc, "taxpayer_number", ""))
        self._opt("taxpayer_id", getattr(doc, "taxpayer_id_number", ""))
        self._opt("taxpayer_act", getattr(doc, "taxpayer_activity_code", ""))

        self.rfzo_btn.setEnabled(bool(doc.card_id and doc.insurant_number))

    def clear_data(self):
        self._doc = None
        self._rfzo_in_progress = False
        self.title.clear()
        self.rfzo_btn.setText("Proveri važenje preko RFZO")
        self.rfzo_btn.setEnabled(False)
        for row in self.rows.values():
            row.set_value("")

    # =====================================================
    # RFZO
    # =====================================================

    def _update_rfzo(self):
        if not self._doc or self._rfzo_in_progress:
            return

        self._rfzo_in_progress = True
        self.rfzo_btn.setEnabled(False)
        self.rfzo_btn.setText("Provera u toku...")
        self.rows["valid"].set_value("Provera u toku...")

        document = self._doc

        def worker():
            error = None
            try:
                document.update_from_rfzo(timeout=8)
            except Exception as e:
                error = str(e)
            self._rfzo_finished.emit((document, error))

        threading.Thread(target=worker, daemon=True).start()

    def _on_rfzo_finished(self, result):
        document, error = result
        if document is not self._doc:
            return

        self._rfzo_in_progress = False
        self.rfzo_btn.setEnabled(True)
        self.rfzo_btn.setText("Proveri važenje preko RFZO")

        if error:
            QMessageBox.warning(self, "RFZO", error)
        self.rows["valid"].set_value(document.valid_until)

    # =====================================================
    # Helpers
    # =====================================================

    def _section(self, title):
        lbl = QLabel(title)
        lbl.setStyleSheet("font-weight: bold; margin-top: 14px;")
        return lbl

    def _opt(self, key, value):
        row = self.rows[key]
        if value:
            row.set_value(value)
            row.show()
        else:
            row.hide()
