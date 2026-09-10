import base64
from io import BytesIO
from flask import Flask, render_template, request
import qrcode

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    qr_base64 = None
    user_input = ""

    if request.method == "POST":
        user_input = request.form.get("texto_url", "").strip()

        if user_input:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(user_input)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffered = BytesIO()
            img.save(buffered, format="PNG")

            qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template(
        "index.html", qr_code=qr_base64, original_text=user_input
    )


if __name__ == "__main__":
    app.run(debug=True)
