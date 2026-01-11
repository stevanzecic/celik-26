<div align="center"><a name="top"></a>

<p align="center">
  <img src="./assets/img/celik-26-logo-nbg.png" width="45%" alt="celik-26-logo">
</p>

`v0.1.1`

</div>

**CELIK-26** is a Python smart card reader for ID and Medical cards issued by Serbian authorities.

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
- [CHANGELOG](#changelog)
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
├── test/
│   └── main.py
│
├── core/
│   ├── apdu.py
│   ├── atr.py
│   ├── container.py
│   ├── encoding.py
|   ├── pscs.py
│   └── tlv.py
│
├── documents/
│   ├── id_document.py
│   ├── id_parser.py
│   ├── medical_document.py
│   └── medical_parser.py
│
├── .gitignore
├── card_reader_cli.py
├── README.md
└── requirements.txt
```

### ✨ Features

- Automatic card type detection via ATR + AID probing
- Support for multiple card manufacturers (Gemalto, Apollo)
- Full TLV parsing for Serbian documents
- UTF-16 decoding (Cyrillic & Latin)
- PC/SC compatible (ACS, Gemalto, OMNIKEY readers)
- CLI interface (GUI-ready backend)

### 🧩 Supported Cards

| Card Type                      | Status            |
| ------------------------------ | ----------------- |
| Serbian ID (Gemalto / Veridos) | ✅ Fully supported |
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
4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
5. Run the project in **IDE**, or from command line:
   ```bash
   python3 card_reader_cli.py -a
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

[🔝 Back to top](#top)

---

## CHANGELOG

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