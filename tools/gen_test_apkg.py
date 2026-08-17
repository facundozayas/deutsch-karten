#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera un .apkg sintético mínimo (ZIP + SQLite con el esquema mínimo de
Anki: tablas `col` y `notes`) para probar el importer de la app end-to-end,
ya que no hay acceso a AnkiWeb desde este sandbox para bajar un mazo real.

No pretende ser un .apkg 100% fiel a Anki real (le faltan `cards`, `revlog`,
media, etc.) — solo lo suficiente para validar el camino de lectura que usa
js/anki-import.js (SELECT models FROM col; SELECT id, flds, tags FROM notes).
"""
import json
import sqlite3
import zipfile
import os

OUT_PATH = "/root/german-app/tools/test-deck.apkg"
DB_TMP_PATH = "/tmp/test-collection.anki2"

MODEL_ID = "1700000000000"
FIELD_SEP = "\x1f"

# (alemán, español) — mini mazo de prueba, distinto del contenido ya cargado
# para poder distinguir visualmente que el import funcionó.
TEST_NOTES = [
    ("der Rucksack", "la mochila"),
    ("die Brille", "los anteojos"),
    ("das Fahrrad", "la bicicleta"),
    ("der Regenschirm", "el paraguas"),
    ("die Steckdose", "el enchufe"),
    ("das Kopfkissen", "la almohada"),
    ("der Wecker", "el despertador"),
    ("die Zahnbürste", "el cepillo de dientes"),
    ("<b>der Teppich</b>", "<i>la alfombra</i>"),  # con HTML, para probar el strip
    ("das Handtuch", "la toalla"),
]


def build_db():
    if os.path.exists(DB_TMP_PATH):
        os.remove(DB_TMP_PATH)

    conn = sqlite3.connect(DB_TMP_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE col (
            id INTEGER PRIMARY KEY, crt INTEGER, mod INTEGER, scm INTEGER,
            ver INTEGER, dty INTEGER, usn INTEGER, ls INTEGER,
            conf TEXT, models TEXT, decks TEXT, dconf TEXT, tags TEXT
        )
    """)

    models = {
        MODEL_ID: {
            "id": int(MODEL_ID),
            "name": "Básico DE-ES (mazo de prueba)",
            "flds": [
                {"name": "Deutsch", "ord": 0},
                {"name": "Español", "ord": 1},
            ],
        }
    }

    cur.execute(
        "INSERT INTO col VALUES (1,0,0,0,11,0,0,0,'{}',?,'{}','{}','{}')",
        (json.dumps(models),),
    )

    cur.execute("""
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY, guid TEXT, mid INTEGER, mod INTEGER,
            usn INTEGER, tags TEXT, flds TEXT, sfld TEXT, csum INTEGER,
            flags INTEGER, data TEXT
        )
    """)

    for i, (de, es) in enumerate(TEST_NOTES):
        flds = de + FIELD_SEP + es
        cur.execute(
            "INSERT INTO notes VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (1000 + i, f"guid-{i}", int(MODEL_ID), 0, 0, "", flds, de, 0, 0, ""),
        )

    conn.commit()
    conn.close()


def build_apkg():
    build_db()
    if os.path.exists(OUT_PATH):
        os.remove(OUT_PATH)

    with zipfile.ZipFile(OUT_PATH, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(DB_TMP_PATH, "collection.anki2")
        z.writestr("media", "{}")

    print(f"Generado {OUT_PATH} con {len(TEST_NOTES)} notas de prueba.")


if __name__ == "__main__":
    build_apkg()
