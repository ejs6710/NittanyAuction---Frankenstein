# Nittany Auction

Dr. Frankenstein (Dhruv, Arno, Qistina, Ethan) phase 2 progress review.

# Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# DB Population
```bash
python3 data_migration.py
```

# Flask Server
```bash
python3 app.py
```

# Packages
- Flask: Used for rendering pages and passing data
- Pandas: Used for migrating CSV data due to read_csv() method
- Sqlite3: Used to communicate with the SQLite server
- Hashlib: Used to handle SHA256 encoding of passwords
