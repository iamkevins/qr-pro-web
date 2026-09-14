import base64
from io import BytesIO
from flask import Flask, render_template, request
import qrcode

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    qr_base64 = None
    modo_activo = "texto"
    texto_url = ""
    ssid = ""
    password = ""
    seguridad = "WPA"

    if request.method == "POST":
        modo_activo = request.form.get("modo", "texto")

        if modo_activo == "texto":
            texto_url = request.form.get("texto_url", "").strip()
            contenido_qr = texto_url

        elif modo_activo == "wifi":
            ssid = request.form.get("ssid", "").strip()
            password = request.form.get("password", "").strip()
            seguridad = request.form.get("seguridad", "WPA")

            # Formato estándar para conexión WiFi mediante código QR
            if seguridad == "nopass":
                contenido_qr = f"WIFI:S:{ssid};T:nopass;;"
            else:
                contenido_qr = f"WIFI:S:{ssid};T:{seguridad};P:{password};;"

        # Generación del QR
        if contenido_qr:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(contenido_qr)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffered = BytesIO()
            img.save(buffered, format="PNG")

            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template(
        "index.html",
        qr_code=qr_base64,
        modo_activo=modo_activo,
        texto_url=texto_url,
        ssid=ssid,
        password=password,
        seguridad=seguridad,
    )


if __name__ == "__main__":
    app.run(debug=True)
