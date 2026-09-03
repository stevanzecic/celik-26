from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
import threading

from gui.widgets.label_row import LabelRow
from gui.i18n import DEFAULT_LANGUAGE, tr


class MedicalCardWidget(QWidget):
    _rfzo_finished = pyqtSignal(object)  # error or None

    def __init__(self):
        super().__init__()

        self.language = DEFAULT_LANGUAGE

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
            "given": LabelRow(), "parent": LabelRow(), "family": LabelRow(), "birth": LabelRow(),
            "place": LabelRow(), "street": LabelRow(), "gender": LabelRow(), "language": LabelRow(),
            "lbo": LabelRow(), "jmbg": LabelRow(),

            # Card
            "issue": LabelRow(), "expiry": LabelRow(), "valid": LabelRow(), "permanent": LabelRow(),

            # Carrier
            "carrier_name": LabelRow(), "carrier_lbo": LabelRow(), "carrier_jmbg": LabelRow(), "carrier_relation": LabelRow(),

            # Insurance
            "insurance_basis": LabelRow(), "insurance_start": LabelRow(), "insurance_desc": LabelRow(),

            # Taxpayer
            "taxpayer_name": LabelRow(), "taxpayer_res": LabelRow(), "taxpayer_no": LabelRow(),
            "taxpayer_id": LabelRow(), "taxpayer_act": LabelRow(),
        }

        # ---------------- Layout ----------------
        self.sections = {}
        layout.addWidget(self._section("medical_general"))
        for k in (
            "given", "parent", "family", "birth",
            "place", "street", "gender",
            "language", "lbo", "jmbg"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("medical_card"))
        for k in ("issue", "expiry", "valid", "permanent"):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("medical_carrier"))
        for k in (
            "carrier_name", "carrier_lbo",
            "carrier_jmbg", "carrier_relation"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("medical_insurance"))
        for k in (
            "insurance_basis",
            "insurance_start",
            "insurance_desc"
        ):
            layout.addWidget(self.rows[k])

        layout.addWidget(self._section("medical_taxpayer"))
        for k in (
            "taxpayer_name", "taxpayer_res",
            "taxpayer_no", "taxpayer_id",
            "taxpayer_act"
        ):
            layout.addWidget(self.rows[k])

        # ---------------- RFZO ----------------
        self.rfzo_btn = QPushButton()
        self.rfzo_btn.clicked.connect(self._update_rfzo)
        layout.addWidget(self.rfzo_btn)

        layout.addStretch()
        scroll.setWidget(container)

        main = QVBoxLayout(self)
        main.addWidget(scroll)
        self.set_language(self.language)

    # =====================================================
    # Data binding
    # =====================================================

    def set_data(self, doc):
        if doc is not self._doc:
            self._rfzo_in_progress = False
            self.rfzo_btn.setText(tr("rfzo", self.language))
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
        self.rows["permanent"].set_value(tr("yes" if doc.permanently_valid else "no", self.language))

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
        self.rfzo_btn.setText(tr("rfzo", self.language))
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
        self.rfzo_btn.setText(tr("rfzo_progress", self.language))
        self.rows["valid"].set_value(tr("rfzo_progress", self.language))

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
        self.rfzo_btn.setText(tr("rfzo", self.language))

        if error:
            QMessageBox.warning(self, tr("rfzo_error_title", self.language), error)
        self.rows["valid"].set_value(document.valid_until)

    # =====================================================
    # Helpers
    # =====================================================

    def _section(self, key):
        lbl = QLabel(tr(key, self.language))
        lbl.setStyleSheet("font-weight: bold; margin-top: 14px;")
        self.sections[key] = lbl
        return lbl

    def set_language(self, language):
        self.language = language
        labels = {
            "given": "given_name", "parent": "parent_name", "family": "surname", "birth": "birth_date",
            "place": "place", "street": "street", "gender": "gender", "language": "medical_language", "lbo": "lbo", "jmbg": "jmbg",
            "issue": "medical_issue", "expiry": "medical_expiry", "valid": "valid", "permanent": "permanent",
            "carrier_name": "carrier_name", "carrier_lbo": "carrier_lbo", "carrier_jmbg": "carrier_jmbg", "carrier_relation": "carrier_relation",
            "insurance_basis": "insurance_basis", "insurance_start": "insurance_start", "insurance_desc": "insurance_desc",
            "taxpayer_name": "taxpayer_name", "taxpayer_res": "taxpayer_res", "taxpayer_no": "taxpayer_no", "taxpayer_id": "taxpayer_id", "taxpayer_act": "taxpayer_act",
        }
        for key, text_key in labels.items():
            self.rows[key].set_label(tr(text_key, language))
        for key, label in self.sections.items():
            label.setText(tr(key, language))
        self.rfzo_btn.setText(tr("rfzo", language))
        if self._doc is not None:
            self.set_data(self._doc)

    def _opt(self, key, value):
        row = self.rows[key]
        if value:
            row.set_value(value)
            row.show()
        else:
            row.hide()
