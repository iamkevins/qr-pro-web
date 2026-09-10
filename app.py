from flask import Flask, render_template, request
import qrcode
import sqlite3
import os

app = Flask(__name__)

os.makedirs("static/qr", exist_ok=True)

DB = "database.db"


def inicializar_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS historial(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contenido TEXT
    )
    """)

    conn.commit()
    conn.close()


inicializar_db()


@app.route("/", methods=["GET", "POST"])
def index():

    qr_generado = None

    if request.method == "POST":

        accion = request.form.get("accion")

        if accion == "texto":

            contenido = request.form.get("contenido")

            if contenido:

                img = qrcode.make(contenido)

                ruta = "static/qr/ultimo_qr.png"

                img.save(ruta)

                conn = sqlite3.connect(DB)

                conn.execute(
                    "INSERT INTO historial(contenido) VALUES(?)",
                    (contenido,)
                )

                conn.commit()
                conn.close()

                qr_generado = ruta

        if accion == "wifi":

            ssid = request.form.get("ssid")
            password = request.form.get("password")

            wifi_data = (
                f"WIFI:T:WPA;"
                f"S:{ssid};"
                f"P:{password};;"
            )

            img = qrcode.make(wifi_data)

            ruta = "static/qr/wifi_qr.png"

            img.save(ruta)

            conn = sqlite3.connect(DB)

            conn.execute(
                "INSERT INTO historial(contenido) VALUES(?)",
                (f"WiFi: {ssid}",)
            )

            conn.commit()
            conn.close()

            qr_generado = ruta

    conn = sqlite3.connect(DB)

    historial = conn.execute("""
        SELECT contenido
        FROM historial
        ORDER BY id DESC
        LIMIT 20
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        qr_generado=qr_generado,
        historial=historial
    )


if __name__ == "__main__":
    app.run(debug=True)