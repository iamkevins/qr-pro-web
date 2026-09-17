import os
import cloudinary
import cloudinary.uploader
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

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


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    if "archivo" not in request.files:
        return jsonify({"error": "No se ha seleccionado ningún archivo."}), 400

    file = request.files["archivo"]
    if file.filename == "":
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if file and archivo_permitido(file.filename):
        try:
            upload_result = cloudinary.uploader.upload(
                file, resource_type="auto"
            )
            return jsonify({"url": upload_result.get("secure_url")})
        except Exception as e:
            return (
                jsonify(
                    {"error": f"Error al subir archivo a Cloudinary: {str(e)}"}
                ),
                500,
            )

    return (
        jsonify(
            {
                "error": "Formato no permitido. Selecciona una imagen (PNG, JPG, GIF) o un PDF."
            }
        ),
        400,
    )


if __name__ == "__main__":
    app.run(debug=True)
