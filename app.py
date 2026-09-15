import base64
import os
from io import BytesIO
import cloudinary
import cloudinary.uploader
from flask import Flask, redirect, render_template, request, session, url_for
import qrcode

app = Flask(__name__)
# Necesario para manejar sesiones en Flask
app.secret_key = os.environ.get("SECRET_KEY", "mi_clave_secreta_12345")

# Configuración de Cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "qvuwhflg"),
    api_key=os.environ.get("CLOUDINARY_API_KEY", "645633281489516"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "SYC17l57V2LSXcxCh2-bZcIGPe0"),
    secure=True,
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}


def archivo_permitido(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        modo_activo = request.form.get("modo", "texto")
        contenido_qr = ""
        error_msg = None
        archivo_url = None

        if modo_activo == "texto":
            texto_url = request.form.get("texto_url", "").strip()
            contenido_qr = texto_url

        elif modo_activo == "wifi":
            ssid = request.form.get("ssid", "").strip()
            password = request.form.get("password", "").strip()
            seguridad = request.form.get("seguridad", "WPA")

            if seguridad == "nopass":
                contenido_qr = f"WIFI:S:{ssid};T:nopass;;"
            else:
                contenido_qr = f"WIFI:S:{ssid};T:{seguridad};P:{password};;"

        elif modo_activo == "archivo":
            if "archivo" in request.files:
                file = request.files["archivo"]
                if (
                    file
                    and file.filename != ""
                    and archivo_permitido(file.filename)
                ):
                    try:
                        upload_result = cloudinary.uploader.upload(
                            file, resource_type="auto"
                        )
                        contenido_qr = upload_result.get("secure_url")
                        archivo_url = contenido_qr
                    except Exception as e:
                        error_msg = (
                            f"Error al subir el archivo a Cloudinary: {str(e)}"
                        )
                else:
                    error_msg = "Formato no permitido. Selecciona una imagen (PNG, JPG, GIF) o un PDF."
            else:
                error_msg = "No se ha seleccionado ningún archivo."

        # Generar código QR
        qr_base64 = None
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

        # Guardar resultado en sesión temporal y REDIRIGIR (GET)
        session["qr_code"] = qr_base64
        session["modo_activo"] = modo_activo
        session["archivo_url"] = archivo_url
        session["error_msg"] = error_msg

        return redirect(url_for("index"))

    # Cuando es una petición GET (acceso normal o recargar)
    qr_code = session.pop("qr_code", None)
    modo_activo = session.pop("modo_activo", "texto")
    archivo_url = session.pop("archivo_url", None)
    error_msg = session.pop("error_msg", None)

    return render_template(
        "index.html",
        qr_code=qr_code,
        modo_activo=modo_activo,
        archivo_url=archivo_url,
        error_msg=error_msg,
    )


if __name__ == "__main__":
    app.run(debug=True)
