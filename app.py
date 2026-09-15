import base64
import os
from io import BytesIO
import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request
import qrcode

app = Flask(__name__)

# Configuración de Cloudinary (toma los valores de Render o usa los que coloques por defecto)
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", "qvuwhflg"),
    api_key=os.environ.get("CLOUDINARY_API_KEY", "645633281489516"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", "SYC17l57V2LSXcxCh2-bZcIGPe0"),
    secure=True,
)

# Extensiones permitidas para la subida de archivos
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}


def archivo_permitido(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/", methods=["GET", "POST"])
def index():
    qr_base64 = None
    modo_activo = "texto"
    texto_url = ""
    ssid = ""
    password = ""
    seguridad = "WPA"
    archivo_url = None
    error_msg = None

    if request.method == "POST":
        modo_activo = request.form.get("modo", "texto")
        contenido_qr = ""

        # Opción 1: Texto o URL
        if modo_activo == "texto":
            texto_url = request.form.get("texto_url", "").strip()
            contenido_qr = texto_url

        # Opción 2: Conexión WiFi
        elif modo_activo == "wifi":
            ssid = request.form.get("ssid", "").strip()
            password = request.form.get("password", "").strip()
            seguridad = request.form.get("seguridad", "WPA")

            if seguridad == "nopass":
                contenido_qr = f"WIFI:S:{ssid};T:nopass;;"
            else:
                contenido_qr = f"WIFI:S:{ssid};T:{seguridad};P:{password};;"

        # Opción 3: Foto / PDF (Cloudinary)
        elif modo_activo == "archivo":
            if "archivo" in request.files:
                file = request.files["archivo"]
                if (
                    file
                    and file.filename != ""
                    and archivo_permitido(file.filename)
                ):
                    try:
                        # Subir archivo directamente a Cloudinary
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
                    error_msg = "Formato no permitido. Selecciona una imagen (PNG, JPG, GIF) o un archivo PDF."
            else:
                error_msg = "No se ha seleccionado ningún archivo."

        # Generar imagen QR si hay datos válidos
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
        archivo_url=archivo_url,
        error_msg=error_msg,
    )


if __name__ == "__main__":
    app.run(debug=True)
