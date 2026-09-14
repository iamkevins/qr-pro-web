import os
import uuid
import base64

from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory
)

import qrcode

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf",
    "png",
    "jpg",
    "jpeg"
}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/archivo/<filename>")
def ver_archivo(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


@app.route("/", methods=["GET", "POST"])
def index():

    qr_base64 = None

    modo_activo = "texto"

    texto_url = ""
    ssid = ""
    password = ""
    seguridad = "WPA"

    archivo_subido = None

    if request.method == "POST":

        modo_activo = request.form.get(
            "modo",
            "texto"
        )

        contenido_qr = ""

        # TEXTO / URL
        if modo_activo == "texto":

            texto_url = request.form.get(
                "texto_url",
                ""
            ).strip()

            contenido_qr = texto_url

        # WIFI
        elif modo_activo == "wifi":

            ssid = request.form.get(
                "ssid",
                ""
            ).strip()

            password = request.form.get(
                "password",
                ""
            ).strip()

            seguridad = request.form.get(
                "seguridad",
                "WPA"
            )

            if seguridad == "nopass":

                contenido_qr = (
                    f"WIFI:S:{ssid};"
                    f"T:nopass;;"
                )

            else:

                contenido_qr = (
                    f"WIFI:S:{ssid};"
                    f"T:{seguridad};"
                    f"P:{password};;"
                )

        # ARCHIVOS
        elif modo_activo == "archivo":

            archivo = request.files.get(
                "archivo"
            )

            if (
                archivo and
                allowed_file(
                    archivo.filename
                )
            ):

                extension = (
                    archivo.filename
                    .rsplit(".", 1)[1]
                    .lower()
                )

                nombre_unico = (
                    str(uuid.uuid4())
                    + "."
                    + extension
                )

                archivo.save(
                    os.path.join(
                        UPLOAD_FOLDER,
                        nombre_unico
                    )
                )

                archivo_subido = (
                    nombre_unico
                )

                contenido_qr = (
                    request.host_url
                    + "archivo/"
                    + nombre_unico
                )

        # GENERACIÓN QR
        if contenido_qr:

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )

            qr.add_data(
                contenido_qr
            )

            qr.make(
                fit=True
            )

            img = qr.make_image(
                fill_color="black",
                back_color="white"
            )

            buffered = BytesIO()

            img.save(
                buffered,
                format="PNG"
            )

            qr_base64 = (
                base64.b64encode(
                    buffered.getvalue()
                )
                .decode("utf-8")
            )

    return render_template(
        "index.html",
        qr_code=qr_base64,
        modo_activo=modo_activo,
        texto_url=texto_url,
        ssid=ssid,
        password=password,
        seguridad=seguridad,
        archivo_subido=archivo_subido
    )


if __name__ == "__main__":
    app.run(debug=True)
