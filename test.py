from flask import Flask, request, send_file
import fitz  # PyMuPDF
from PIL import Image
import io

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert_pdf_and_stick_photo():
    try:
        # Get PDF and Photo from Postman
        pdf_file = request.files.get("pdf")
        photo_file = request.files.get("photo")
        sign_file = request.files.get("sign")

        if not pdf_file or not photo_file or not sign_file:
            return {"error": "PDF and Photo are required"}, 400

        # Read PDF in memory
        pdf_bytes = pdf_file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Convert first page to image
        page = pdf_document[0]
        pix = page.get_pixmap(dpi=300)  # Increase dpi for better quality

        img_bytes = pix.tobytes("jpeg")
        background = Image.open(io.BytesIO(img_bytes))

        # Open photo and sign
        photo = Image.open(photo_file)
        sign  = Image.open(sign_file)

        # Resize photo (change size as needed)
        photo = photo.resize((354, 414))
        sign =  sign.resize((400,200))

        # Paste photo (change position as needed)
        background.paste(photo, (108, 104))
        background.paste(photo, (2017, 105))
        background.paste(sign,(375,308),sign)

        # Save final image in memory
        final_img = io.BytesIO()
        background.save(final_img, format="JPEG")
        final_img.seek(0)

        return send_file(final_img, mimetype="image/jpeg")

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True)
