<div align="center"><a name="top"></a>

<p align="center">
  <img src="./assets/img/celik-26-logo-nbg.png" width="45%" alt="celik-26-logo">
</p>

`v0.1.3`

</div>

**CELIK-26** is a Python/PyQt6 smart-card reader for identity and medical cards issued by Serbian authorities.

---

## Table of Contents

- [Table of Contents](#table-of-contents)
- [INTRODUCTION](#introduction)
  - [Project structure](#project-structure)
  - [✨ Features](#-features)
  - [🧩 Supported Cards](#-supported-cards)
- [CLI AND PYTHON API](#cli-and-python-api)
  - [CLI](#cli)
  - [Python API](#python-api)
- [RUNNING CELIK-26](#running-celik-26)
  - [From source](#from-source)
  - [Tests](#tests)
- [USAGE NOTES](#usage-notes)
  - [Printing](#printing)
  - [RFZO verification](#rfzo-verification)
  - [Privacy](#privacy)
- [CHANGELOG](#changelog)
  - [v0.1.3](#v013)
    - [Added](#added)
    - [Improved](#improved)
    - [Fixed](#fixed)
  - [v0.1.2](#v012)
    - [Added](#added-1)
    - [Improved](#improved-1)
    - [Fixed](#fixed-1)
    - [Removed](#removed)
  - [v0.1.1](#v011)
  - [v0.1.0](#v010)
- [LICENSE](#license)

[🔝 Back to top](#top)

---

## INTRODUCTION

### Project structure

```
celik-26/
├── assets/
│   └── img/
|       ├──celik-26-logo-nbg.png
│       └── celik-26-logo.png
|
├── cards/
│   ├── base_card.py
│   ├── detector.py
│   │
│   ├── id/
│   │   ├── atr.py
│   │   ├── apollo.py
│   │   └── gemalto.py
│   │
│   └── medical/
│       └── medical.py
|
├── gui/
│   ├── settings/
│   ├── translations/
│   ├── widgets/
│   ├── workers/
│   ├── app.py
│   └── main_window.py
│
├── core/
│   ├── apdu.py
│   ├── atr.py
│   ├── container.py
│   ├── encoding.py
|   ├── pcsc.py
│   └── tlv.py
│
├── documents/
│   ├── id_document.py
│   ├── id_parser.py
│   ├── medical_document.py
│   └── medical_parser.py
│
├── tests/
│   ├── test_cards.py
│   ├── test_core.py
│   ├── test_documents.py
│   ├── test_i18n.py
│   └── test_printing.py
│
├── .gitignore
├── card_reader_cli.py
├── card_reader_gui.py
├── README.md
└── requirements.txt
```

### ✨ Features

- Automatic card type detection via ATR + AID probing
- Support for multiple card manufacturers (Gemalto, Apollo)
- Strict TLV parsing with malformed-data detection
- UTF-16 decoding (Cyrillic & Latin)
- PC/SC compatible (ACS, Gemalto, OMNIKEY readers)
- CLI and PyQt6 desktop interfaces
- Background reader/card polling with manual reader selection
- Full identity-card and medical-card data views, including portrait display
- A4 identity-card printing through the native system print dialog
- Optional on-demand RFZO insurance-validity lookup for medical cards
- Serbian and English interface translations, configurable under Preferences

### 🧩 Supported Cards

| Card Type                      | Status            |
| ------------------------------ | ----------------- |
| Serbian ID (Gemalto / Veridos) | ✅ Supported       |
| Serbian ID (Apollo - legacy)   | ✅ Supported       |
| Serbian Medical Card           | ✅ Supported       |
| Vehicle Registration Card      | ⏳ Planned         |

[🔝 Back to top](#top)

---

## CLI AND PYTHON API

### CLI

CLI allows you to read card data from any connected card reader.

```bash
card_reader_cli.py [-h] [-l] [-a] [-r READER_NAME]
```

**CLI Help**

```bash
python3 card_reader_cli.py -h
```

**CLI OPTIONS**

| Option | Parameters | Description |
| :---: | :---: | --- |
| '-h' | / | Show help |
| '-l' | / | List connected card readers |
| '-a' | / | Auto-detect reader and read card |
| '-r' | <READER_NAME> | Read card from specific reader given by reader name |

### Python API

API allows easy integration of new functionalities and integration with other systems.

Main entry point is `./card_reader_cli.py` file, which contains main exposed functions.

**API Functions and Classes**

| Function | Parameters | Returns | Description |
| :---: | :---: | --- | --- |
| connect_first_reader() | / | `PcscCard` | Connect to the first available reader |
| get_readers_list() | / | `list[str]` | Fetch list of connected readers |
| connect_reader(reader_name: str) | <READER_NAME> | `PcscCard` | Connect to a specific reader given by name |
| read_card(card_reader: PcscCard) | <CARD_READER> | **_dict:_**    `{"type": "ID" \| "MED", "data": <CARD_DATA>}` | Read card in the given reader |
| auto_read_card() | / | **_dict:_**    `{"type": "ID" \| "MED", "data": <CARD_DATA>}` | Detect card and read data from first available reader |

**Usage Example**

In example below, first function is used to get list of connected card readers. Then, second function is used to connect to the first available reader, and third function is used to read card data from the connected reader.

```python
import card_reader_cli

card_reader_list = card_reader_cli.get_readers_list()
card_reader = card_reader_cli.connect_reader(card_reader_list[0])
card_data = card_reader_cli.read_card(card_reader)
```

`card_data` variable will contain card type and data:

```python
{'type': 'ID', 'data': <ID_DOCUMENT>}
{'type': 'MED', 'data': <MEDICAL_DOCUMENT>}
```

With only one card reader connected, `auto_read_card()` function can be used to read card data from the first (and only) available reader.

```python
card_data = card_reader_cli.auto_read_card()
```

[🔝 Back to top](#top)

---

## RUNNING CELIK-26

### From source

To run the project from source, follow these steps:

1. Clone the repository [https://github.com/stevanzecic/celik-26](https://github.com/stevanzecic/celik-26)
2. Create virtual environment
   ```bash
   python3 -m venv venv
   ```
3. Activate virtual environment
   ```bash
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate.bat       # Windows
   ```
4. On Debian/Ubuntu, install the system packages required by `pyscard`:
   ```bash
   sudo apt install libpcsclite-dev swig build-essential
   ```
   Then install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   On Windows, install the driver for the card reader and ensure that the
   **Smart Card** service is running before starting the application.
5. Run the GUI:
   ```bash
   python3 card_reader_gui.py
   ```
   Or run the CLI:
   ```bash
   python3 card_reader_cli.py -a
   ```

### Tests

The automated tests use synthetic card records and do not require a physical
reader or personal card data:

```bash
python3 -m unittest discover -v
```

**Dependencies**

- Python 3.10+
- Packages:

    | Package | Version |
    | --- | --- |
    | pyscard | >=2.3.1 |
    | Pillow | >=12.0.0 |
    | PyQt6 | >=6.10.1 |
    | qt-material | >=2.17 |
    | requests | >=2.32.0 |

[🔝 Back to top](#top)

---

## USAGE NOTES

### Printing

After a Serbian identity card has been read successfully, select **Print** in
the desktop application. The app first opens an A4 print preview; use its
**Print** action to select a system printer and print the displayed page.
Medical-card printing is not implemented.

### RFZO verification

The medical-card view can request an updated insurance-validity date from the
public RFZO service using the card's KZO and LBO values. This is an on-demand
network request; reading card data itself stays offline. If RFZO returns its
website instead of verification data, the app reports that the verification
service is unavailable and keeps the date stored on the card unchanged.

### Privacy

Card data, including the portrait and personal details, is read locally from
the inserted card. The application does not upload card data during normal
reading or printing. The only external request is the explicit RFZO validity
check described above, which sends the KZO and LBO values required by RFZO.

### Language

The interface starts in Serbian. Open **Settings → Preferences**, choose
**English** or **Srpski**, and select **Save**; the open window and card views
are updated immediately. The selected language is remembered for the next run.
Translation resources are stored in `gui/translations/sr.json` and
`gui/translations/en.json`. They are loaded at startup without any additional
translation toolchain.

[Back to top](#top)

---

## CHANGELOG

### v0.1.3

#### Added

- Added Serbian and English interface translations
- Added a language selector under **Settings → Preferences**
- Added persistent language selection using application settings
- Added JSON translation resources in `gui/translations/`

#### Improved

- Centralized UI translation lookup and fallback behavior
- Updated card views, menus, dialogs, status messages, and print preview for both languages

#### Fixed

- Fixed medical-card view startup failure caused by translation-aware `LabelRow` construction

---

### v0.1.2

#### Added

- Added support for legacy Apollo Serbian ID cards
- Added ATR recognition with AID probing for more reliable card type detection
- Added redesigned identity card and medical card data views
- Added A4 identity card printing through the system print dialog
- Added an A4 print preview before identity-card printing
- Added an explicit RFZO insurance-validity check in the medical-card view
- Added automated tests for card protocols, parsers, encoding, TLV/APDU handling, document models, and printing

#### Improved

- Expanded identity card and medical card field parsing
- Improved reader selection, background polling, card removal handling, and application shutdown
- Improved address and date formatting to match the official Serbian ID card reader
- Improved APDU response validation and malformed or truncated card data detection
- Improved UTF-16 decoding and Serbian medical card tag mapping
- Improved GUI reader status, manual reader selection, and theme handling
- Improved RFZO requests to match the public service and identify HTML service fallbacks clearly

#### Fixed

- Fixed Apollo and Gemalto file selection and binary reading
- Fixed detection of cards sharing the same ATR
- Fixed stale card data and portrait images remaining visible after card removal
- Fixed invalid dates such as `01.01.0001.` being displayed as real dates
- Fixed stale data after a reader disconnects
- Fixed the incorrectly named `requiremets.txt` file

#### Removed

- Removed obsolete test scripts and raw medical card data logging
- Disabled unfinished Save and medical card printing actions


### v0.1.1

- Minor refactoring
- Added docstrings to all classes and functions for better documentation

### v0.1.0

- Initial release
- Card reader detection and connection
- Support for Gemalto / Veridos ID cards
- Support for Serbian Medical cards

[🔝 Back to top](#top)

---

## LICENSE

[MIT](./LICENSE)

[🔝 Back to top](#top)

---
