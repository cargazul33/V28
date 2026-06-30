import sqlite3

def guardar_bd(datos):

    con = sqlite3.connect("database.sqlite")

    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS licitaciones(
            numero TEXT,
            titulo TEXT,
            organismo TEXT,
            fecha TEXT,
            puntaje INTEGER
        )
    """)

    con.commit()
    con.close()
