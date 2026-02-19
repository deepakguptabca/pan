import os
import requests
from flask import Flask, request, send_file
from numpy import sign
import fitz  # PyMuPDF
from PIL import Image
import io
import dotenv
import zipfile


dotenv.load_dotenv()

app = Flask(__name__)

BG_API_KEY = os.getenv("BG_API_KEY")


def bg_remove(sign_img):
    img_byte_arr = io.BytesIO()
    sign_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": img_byte_arr},
        data={"size": "auto"},
        headers={"X-Api-Key": BG_API_KEY},
    )

    if response.status_code == requests.codes.ok:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(response.text)


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
        fpage = pdf_document[0]
        fpix = fpage.get_pixmap(dpi=300)

        # Convert second page to image
        spage = pdf_document[1]
        spix = spage.get_pixmap(dpi=300)

        # Convert pixmap to PIL Image of first page
        fimg_bytes = fpix.tobytes("jpeg")
        fbackground = Image.open(io.BytesIO(fimg_bytes))

        # Convert pixmap to PIL Image of second page
        simg_bytes = spix.tobytes("jpeg")
        sbackground = Image.open(io.BytesIO(simg_bytes))

        # Open photo and sign
        photo = Image.open(photo_file)
        sign = Image.open(sign_file)

        # Resize photo (change size as needed)
        photo = photo.resize((354, 414))
        sign = sign.resize((324, 111))

        # change bg of sign
        bg_sign = bg_remove(sign)
        # bg_sign =  bg_sign.resize((324,111))

        # Paste photo (change position as needed)
        fbackground.paste(photo, (108, 104))
        fbackground.paste(photo, (2017, 105))
        fbackground.paste(bg_sign, (264, 220), bg_sign)
        fbackground.paste(sign, (1882, 622))
        sbackground.paste(sign, (1819, 3184), bg_sign)

        # Save final image in memory of first image
        final_imgf = io.BytesIO()
        fbackground.save(final_imgf, format="JPEG")

        # Save final image in memory of second image
        final_imgs = io.BytesIO()
        sbackground.save(final_imgs, format="JPEG")

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("first_page.jpg", final_imgf.getvalue())
            zip_file.writestr("second_page.jpg", final_imgs.getvalue())

        # Reset buffer position to beginning
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="final_images.zip",
        )

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True)
