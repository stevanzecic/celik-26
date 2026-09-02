from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class IdCardWidget(QWidget):
    """Display all ID-card data in the same logical groups as the official app."""

    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        root = QVBoxLayout(container)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        root.addWidget(self._build_header())

        content = QHBoxLayout()
        content.setSpacing(14)
        content.addLayout(self._build_photo_column())
        content.addWidget(self._build_person_group(), 1)
        root.addLayout(content)

        root.addWidget(self._build_document_group())
        self.additional_group = self._build_additional_group()
        self.additional_group.hide()
        root.addWidget(self.additional_group)
        root.addStretch()

        scroll.setWidget(container)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

        self.clear_data()

    def _build_header(self):
        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(header)
        layout.setContentsMargins(14, 9, 14, 9)
        layout.setSpacing(1)

        self.country_title = QLabel("Republika Srbija · Republic of Serbia")
        self.country_title.setStyleSheet("font-size: 14px; font-weight: 600;")

        self.document_title = QLabel("LIČNA KARTA · IDENTITY CARD")
        self.document_title.setStyleSheet("font-size: 18px; font-weight: 700;")

        layout.addWidget(self.country_title)
        layout.addWidget(self.document_title)
        return header

    def _build_photo_column(self):
        layout = QVBoxLayout()
        layout.setSpacing(6)

        self.photo = QLabel("Fotografija nije dostupna")
        self.photo.setFixedSize(225, 285)
        self.photo.setFrameShape(QFrame.Shape.StyledPanel)
        self.photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo.setWordWrap(True)
        self.photo.setStyleSheet(
            "QLabel { padding: 4px; background: palette(base); color: palette(mid); }"
        )

        caption = QLabel("Fotografija sa čipa")
        caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        caption.setStyleSheet("font-size: 11px; color: palette(mid);")

        layout.addWidget(self.photo)
        layout.addWidget(caption)
        layout.addStretch()
        return layout

    def _build_person_group(self):
        group = QGroupBox("Podaci o građaninu")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)
        grid.setColumnStretch(1, 1)

        self.rows = {}
        row = 0
        row = self._add_row(grid, row, "Prezime:", "surname")
        row = self._add_row(grid, row, "Ime:", "given_name")
        row = self._add_row(grid, row, "Ime jednog roditelja:", "parent_name")
        row = self._add_row(grid, row, "Datum rođenja:", "birth_date")
        row = self._add_row(
            grid,
            row,
            "Mesto rođenja, opština i država:",
            "birth_place",
        )
        row = self._add_row(
            grid,
            row,
            "Prebivalište i adresa stana:",
            "address",
        )
        row = self._add_row(grid, row, "Datum promene adrese:", "address_date")

        jmbg_label = self._field_label("JMBG:")
        sex_label = self._field_label("Pol:")
        self.rows["jmbg"] = self._value_label()
        self.rows["sex"] = self._value_label()
        grid.addWidget(jmbg_label, row, 0)
        grid.addWidget(self.rows["jmbg"], row, 1)
        grid.addWidget(sex_label, row, 2)
        grid.addWidget(self.rows["sex"], row, 3)

        row += 1
        self._add_row(grid, row, "Državljanstvo:", "nationality")
        return group

    def _build_document_group(self):
        group = QGroupBox("Podaci o dokumentu")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(12)

        fields = (
            ("Dokument izdaje:", "authority"),
            ("Broj dokumenta:", "document_number"),
            ("Datum izdavanja:", "issue_date"),
            ("Važi do:", "expiry_date"),
        )
        for column, (title, key) in enumerate(fields):
            label = self._field_label(title)
            value = self._value_label()
            self.rows[key] = value
            grid.addWidget(label, 0, column)
            grid.addWidget(value, 1, column)
            grid.setColumnStretch(column, 1)

        return group

    def _build_additional_group(self):
        group = QGroupBox("Dodatni podaci sa čipa")
        grid = QGridLayout(group)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(7)
        grid.setColumnStretch(1, 1)

        self.additional_rows = {}
        row = 0
        for title, key in (
            ("Vrsta dokumenta:", "document_type"),
            ("Naziv dokumenta:", "document_name"),
            ("Registarski broj:", "registration_number"),
            ("Serijski broj čipa:", "chip_number"),
            ("Oznaka adrese:", "address_label"),
            ("Svrha boravka:", "purpose_of_stay"),
            ("Elektronska napomena:", "electronic_note"),
        ):
            label = self._field_label(title)
            value = self._value_label()
            self.rows[key] = value
            self.additional_rows[key] = (label, value)
            grid.addWidget(label, row, 0)
            grid.addWidget(value, row, 1, 1, 3)
            row += 1

        return group

    def _add_row(self, grid, row, title, key):
        label = self._field_label(title)
        value = self._value_label()
        self.rows[key] = value
        grid.addWidget(label, row, 0)
        grid.addWidget(value, row, 1, 1, 3)
        return row + 1

    @staticmethod
    def _field_label(text):
        label = QLabel(text)
        label.setStyleSheet("font-weight: 600;")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return label

    @staticmethod
    def _value_label():
        label = QLabel()
        label.setMinimumHeight(26)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setStyleSheet(
            "QLabel {"
            " padding: 3px 6px;"
            " border: 1px solid palette(mid);"
            " border-radius: 2px;"
            " background: palette(base);"
            "}"
        )
        return label

    @staticmethod
    def _joined(*values):
        return ", ".join(value for value in values if value)

    def _set_value(self, key, value):
        self.rows[key].setText(str(value or ""))

    def _pil_to_pixmap(self, pil_img):
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        width, height = pil_img.size
        image = QImage(
            pil_img.tobytes("raw", "RGB"),
            width,
            height,
            QImage.Format.Format_RGB888,
        ).copy()

        return QPixmap.fromImage(image).scaled(
            self.photo.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def set_data(self, doc):
        self._set_value("surname", doc.surname)
        self._set_value("given_name", doc.given_name)
        self._set_value("parent_name", doc.parent_given_name)
        self._set_value("birth_date", doc.date_of_birth)
        self._set_value(
            "birth_place",
            self._joined(
                doc.place_of_birth,
                doc.community_of_birth,
                doc.state_of_birth,
            ),
        )
        self._set_value("address", doc.address())
        self._set_value("address_date", doc.address_date or "Nije dostupan")
        self._set_value("jmbg", doc.personal_number)
        self._set_value("sex", doc.sex)
        self._set_value("nationality", doc.nationality_full)

        self._set_value("authority", doc.issuing_authority)
        self._set_value("document_number", doc.document_serial_number)
        self._set_value("issue_date", doc.issuing_date)
        self._set_value("expiry_date", doc.expiry_date)

        additional = {
            "document_type": doc.document_type,
            "document_name": doc.document_name,
            "registration_number": doc.doc_reg_no,
            "chip_number": doc.chip_serial_number,
            "address_label": doc.address_label,
            "purpose_of_stay": doc.purpose_of_stay,
            "electronic_note": doc.e_note,
        }
        for key, value in additional.items():
            self._set_value(key, value)
            for widget in self.additional_rows[key]:
                widget.setVisible(bool(value))

        self.additional_group.setVisible(any(additional.values()))

        title = (doc.document_name or "").strip() or "LIČNA KARTA"
        self.document_title.setText(f"{title.upper()} · IDENTITY CARD")

        self.photo.clear()
        portrait = getattr(doc, "portrait", None)
        if portrait:
            self.photo.setPixmap(self._pil_to_pixmap(portrait))
        else:
            self.photo.setText("Fotografija nije dostupna")

    def clear_data(self):
        if hasattr(self, "rows"):
            for value in self.rows.values():
                value.clear()
        self.document_title.setText("LIČNA KARTA · IDENTITY CARD")
        self.photo.clear()
        self.photo.setText("Fotografija nije dostupna")
        self.additional_group.hide()
