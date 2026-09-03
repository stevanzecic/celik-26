"""Single-page A4 printing support for Serbian identity cards."""

from datetime import datetime
import re
from gui.i18n import DEFAULT_LANGUAGE, tr


PRINT_NOTE = (
    "U čipu lične karte, podaci o imenu i prezimenu imaoca lične karte "
    "ispisani su na nacionalnom pismu onako kako su ispisani na samom "
    "obrascu lične karte, dok su ostali podaci ispisani latiničkim pismom."
)


def is_printable_card_data(card_data):
    """Return whether the GUI currently holds a readable ID-card result."""
    return bool(
        isinstance(card_data, dict)
        and str(card_data.get("type", "")).upper() == "ID"
        and card_data.get("data") is not None
    )


def document_number_for_print(value):
    """Remove the card's ``ID`` prefix when followed by a 9-digit number."""
    value = str(value or "").strip()
    match = re.fullmatch(r"ID\s*(\d{9})", value, flags=re.IGNORECASE)
    return match.group(1) if match else value


def build_id_print_data(doc, printed_at=None, language=DEFAULT_LANGUAGE):
    """Return normalized plain-text values used by the print renderer."""
    printed_at = printed_at or datetime.now()
    birth_place = ", ".join(
        value
        for value in (
            doc.place_of_birth,
            doc.community_of_birth,
            doc.state_of_birth,
        )
        if value
    )

    return {
        "document_name": str(doc.document_name or "Lična karta").upper(),
        "portrait": getattr(doc, "portrait", None),
        "citizen_rows": (
            (tr("surname", language), doc.surname),
            (tr("given_name", language), doc.given_name),
            (tr("parent_name", language), doc.parent_given_name),
            (tr("birth_date", language), doc.date_of_birth),
            (tr("birth_place", language), birth_place),
            (tr("address", language), doc.address()),
            (tr("address_date", language), doc.address_date or tr("not_available", language)),
            (tr("jmbg", language), doc.personal_number),
            (tr("sex", language), doc.sex),
        ),
        "document_rows": (
            (tr("authority", language), doc.issuing_authority),
            (tr("document_number", language), document_number_for_print(doc.document_serial_number)),
            (tr("issue_date", language), doc.issuing_date),
            (tr("expiry_date", language), doc.expiry_date),
        ),
        "print_date": printed_at.strftime("%d.%m.%Y."),
    }


def _render_id_document(printer, doc, language=DEFAULT_LANGUAGE):
    """Paint exactly one A4 ID-card page on ``printer``."""
    from PyQt6.QtCore import QLineF, QRectF, Qt
    from PyQt6.QtGui import (
        QFont,
        QImage,
        QPageLayout,
        QPageSize,
        QPainter,
        QPen,
    )
    # Preview and the selected printer can use different resolutions. Use A4
    # points as logical coordinates so both receive the same layout.
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    printer.setPageOrientation(QPageLayout.Orientation.Portrait)
    printer.setFullPage(True)

    painter = QPainter()
    if not painter.begin(printer):
        raise RuntimeError("Could not start the print job")

    try:
        painter.setViewport(0, 0, printer.width(), printer.height())
        painter.setWindow(0, 0, 595, 842)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        data = build_id_print_data(doc, language=language)
        black_pen = QPen(Qt.GlobalColor.black)
        black_pen.setWidthF(0.8)
        painter.setPen(black_pen)

        align_text = (
            int(Qt.AlignmentFlag.AlignLeft)
            | int(Qt.AlignmentFlag.AlignVCenter)
            | int(Qt.TextFlag.TextWordWrap)
        )

        def set_font(pixel_size):
            font = QFont("Arial")
            font.setPixelSize(pixel_size)
            painter.setFont(font)

        def line(y):
            painter.drawLine(QLineF(59, y, 537, y))

        def text(x, y, width, height, value):
            painter.drawText(
                QRectF(x, y, width, height),
                align_text,
                str(value or ""),
            )

        def rows(values, positions):
            set_font(9)
            for (label, value), (top, height) in zip(values, positions):
                text(68, top, 120, height, label)
                text(196, top, 341, height, value)

        # Header
        line(59)
        line(89)
        set_font(10)
        text(69, 62, 458, 25, f"{tr('print_document_header', language)}: {data['document_name']}")

        # Portrait - drawn directly, with no HTML/table container.
        photo_rect = QRectF(59, 103, 121, 160)
        portrait = data["portrait"]
        if portrait is not None:
            image = portrait.convert("RGB")
            width, height = image.size
            qimage = QImage(
                image.tobytes("raw", "RGB"),
                width,
                height,
                width * 3,
                QImage.Format.Format_RGB888,
            ).copy()
            painter.drawImage(photo_rect, qimage)
        else:
            set_font(8)
            text(59, 103, 121, 160, tr("photo_missing", language))

        # Citizen section
        line(277)
        line(302)
        set_font(9)
        text(68, 279, 459, 21, tr("print_person", language))
        rows(
            data["citizen_rows"],
            (
                (306, 24),
                (330, 25),
                (355, 24),
                (379, 24),
                (403, 37),
                (440, 37),
                (477, 24),
                (501, 25),
                (526, 21),
            ),
        )

        # Document section
        line(547)
        line(572)
        set_font(9)
        text(68, 549, 459, 21, tr("print_document", language))
        rows(
            data["document_rows"],
            ((576, 25), (601, 25), (626, 24), (650, 20)),
        )

        # Print date and note
        line(670)
        line(673)
        set_font(9)
        text(68, 676, 459, 20, f"{tr('print_date', language)} {data['print_date']}")

        line(731)
        line(765)
        set_font(7)
        text(59, 735, 478, 27, PRINT_NOTE if language == "sr" else "The card stores the holder's name in the national script; other data is printed in Latin script.")
    finally:
        painter.end()



def print_id_document(parent, doc, language=DEFAULT_LANGUAGE):
    """Preview an ID-card printout with a menu bar and let the user print it.

    Deliberately built from ``QPrintPreviewWidget`` + a plain ``QMenuBar``
    instead of ``QPrintPreviewDialog``. The stock dialog's toolbar is a
    private, undocumented widget: under the app-wide qt_material stylesheet
    (see app.py's apply_stylesheet(...) call) its buttons get padded wide
    enough that Print is pushed into an overflow "»" button that's nearly
    invisible until hovered. A menu bar has no row-width limit, so that
    failure mode doesn't exist here at all.
    """
    from PyQt6.QtGui import QAction, QKeySequence, QPageLayout, QPageSize
    from PyQt6.QtPrintSupport import QPrintDialog, QPrintPreviewWidget, QPrinter
    from PyQt6.QtWidgets import QDialog, QMenuBar, QVBoxLayout

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setDocName("Očitana lična karta")
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    printer.setPageOrientation(QPageLayout.Orientation.Portrait)
    printer.setFullPage(True)

    dialog = QDialog(parent)
    dialog.setWindowTitle(tr("print_preview", language))
    dialog.resize(1000, 800)

    preview_widget = QPrintPreviewWidget(printer, dialog)
    preview_widget.paintRequested.connect(
        lambda preview_printer: _render_id_document(preview_printer, doc, language)
    )

    def do_print():
        # Mirrors QPrintPreviewDialog's own behaviour: let the user pick a
        # printer/settings first, then render the page and send the job.
        print_dialog = QPrintDialog(printer, dialog)
        if print_dialog.exec() == QDialog.DialogCode.Accepted:
            preview_widget.print()
            dialog.accept()

    menu_bar = QMenuBar(dialog)

    print_action = QAction(tr("print", language), dialog)
    print_action.setShortcut(QKeySequence.StandardKey.Print)
    print_action.triggered.connect(do_print)
    menu_bar.addAction(print_action)

    close_action = QAction(tr("close", language), dialog)
    close_action.setShortcut(QKeySequence.StandardKey.Close)
    close_action.triggered.connect(dialog.reject)
    menu_bar.addAction(close_action)

    view_menu = menu_bar.addMenu(tr("view", language))

    zoom_in_action = QAction(tr("zoom_in", language), dialog)
    zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
    zoom_in_action.triggered.connect(preview_widget.zoomIn)
    view_menu.addAction(zoom_in_action)

    zoom_out_action = QAction(tr("zoom_out", language), dialog)
    zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
    zoom_out_action.triggered.connect(preview_widget.zoomOut)
    view_menu.addAction(zoom_out_action)

    view_menu.addSeparator()

    fit_width_action = QAction(tr("fit_width", language), dialog)
    fit_width_action.triggered.connect(preview_widget.fitToWidth)
    view_menu.addAction(fit_width_action)

    fit_page_action = QAction(tr("fit_page", language), dialog)
    fit_page_action.triggered.connect(preview_widget.fitInView)
    view_menu.addAction(fit_page_action)

    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setMenuBar(menu_bar)
    layout.addWidget(preview_widget)

    return dialog.exec() == QDialog.DialogCode.Accepted
