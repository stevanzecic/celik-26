import base64
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

from PIL.Image import Image as PilImage

from gui.widgets.label_row import LabelRow


class IdCardWidget(QWidget):
    def __init__(self):
        super().__init__()

        main = QHBoxLayout(self)

        # ---- Portrait ----
        self.photo = QLabel()
        self.photo.setFixedSize(160, 200)
        self.photo.setFrameShape(QFrame.Shape.Box)
        self.photo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main.addWidget(self.photo)

        # ---- Data ----
        data = QVBoxLayout()
        main.addLayout(data)

        self.full_name = QLabel()
        self.full_name.setStyleSheet("font-size: 18px; font-weight: bold;")
        data.addWidget(self.full_name)

        self.rows = {
            "jmbg": LabelRow("Personal number:"),
            "dob": LabelRow("Date of birth:"),
            "pob": LabelRow("Place of birth:"),
            "sex": LabelRow("Sex:"),
            "nationality": LabelRow("Nationality:"),
            "doc_no": LabelRow("Document number:"),
            "chip": LabelRow("Chip serial number:"),
            "issued": LabelRow("Issued:"),
            "expires": LabelRow("Expires:"),
            "authority": LabelRow("Issuing authority:"),
            "address": LabelRow("Address:")
        }

        for row in self.rows.values():
            data.addWidget(row)

        data.addStretch()

    def _pil_to_pixmap(self, pil_img):
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        w, h = pil_img.size
        data = pil_img.tobytes("raw", "RGB")

        qimg = QImage(
            data,
            w,
            h,
            QImage.Format.Format_RGB888
        )

        return QPixmap.fromImage(qimg).scaled(
            self.photo.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

    def set_data(self, doc):
        self.full_name.setText(
            f"{doc.given_name} {doc.parent_given_name} {doc.surname}"
        )

        self.rows["jmbg"].set_value(doc.personal_number)
        self.rows["dob"].set_value(doc.date_of_birth)
        self.rows["pob"].set_value(
            f"{doc.place_of_birth}, {doc.community_of_birth}, {doc.state_of_birth}"
        )
        self.rows["sex"].set_value(doc.sex)
        self.rows["nationality"].set_value(doc.nationality_full)
        self.rows["doc_no"].set_value(doc.document_serial_number)
        self.rows["chip"].set_value(doc.chip_serial_number)
        self.rows["issued"].set_value(doc.issuing_date)
        self.rows["expires"].set_value(doc.expiry_date)
        self.rows["authority"].set_value(doc.issuing_authority)
        self.rows["address"].set_value(
            f"{doc.street} {doc.house_number}, {doc.community}, {doc.place}"
        )

        portrait = getattr(doc, "portrait", None)
        if portrait:
            self.photo.setPixmap(self._pil_to_pixmap(portrait))
