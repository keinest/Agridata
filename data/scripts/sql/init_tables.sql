CREATE TABLE IF NOT EXISTS exploitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT,
    type TEXT
);

CREATE TABLE IF NOT EXISTS parcelles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    surface_ha REAL,
    culture TEXT,
    exploitation_id INTEGER REFERENCES exploitations(id)
);

CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    temperature REAL,
    humidity REAL,
    parcelle_id INTEGER REFERENCES parcelles(id)
);

CREATE TABLE IF NOT EXISTS soil_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    ph REAL,
    moisture REAL,
    parcelle_id INTEGER REFERENCES parcelles(id)
);