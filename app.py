from flask import Flask, request, jsonify, render_template, Response, send_file
import os
import json
import requests
from numpy import sign
import fitz  # PyMuPDF
from PIL import Image
import io
import dotenv
import zipfile


dotenv.load_dotenv()

app = Flask(__name__)

BG_API_KEY = 'none'


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
        print("Background removed successfully")
        return Image.open(io.BytesIO(response.content))
    else:
        print("Background removal failed", response.text)
        raise Exception(response.text)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bg_api_key",methods=["POST"])
def get_bg_api_key():
    global BG_API_KEY
    data = request.get_json()
    BG_API_KEY = data["api_key"]
    return {"message": "API key updated successfully"}

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
        photo = photo.resize((411, 528))
        sign = sign.resize((369, 109))

        # change bg of sign
        bg_sign = bg_remove(sign)
        # bg_sign =  bg_sign.resize((324,111))

        # Paste photo (change position as needed)
        fbackground.paste(photo, (190, 96))
        fbackground.paste(photo, (1847, 98))
        fbackground.paste(bg_sign, (489, 348), bg_sign)
        sbackground.paste(bg_sign, (1628, 2840), bg_sign)

        # Save final image in memory of first image
        final_imgf = io.BytesIO()
        fbackground.save(final_imgf, format="JPEG")
        final_imgf.seek(0)

        # Save final image in memory of second image
        final_imgs = io.BytesIO()
        sbackground.save(final_imgs, format="JPEG")
        final_imgs.seek(0)

        print("First image size:", len(final_imgf.getvalue()))
        print("Second image size:", len(final_imgs.getvalue()))
        if len(pdf_document) < 2:
            return {"error": "PDF must have at least 2 pages"}, 400

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("first_page.jpg", final_imgf.getvalue())
            zip_file.writestr("second_page.jpg", final_imgs.getvalue())

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="final_images.zip",
        )

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/convertCorrection", methods=["POST"])
def convert_pdf_and_stick_photo_correction():
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
        photo = photo.resize((411, 528))
        sign = sign.resize((369, 109))

        # change bg of sign
        bg_sign = bg_remove(sign)
        # bg_sign =  bg_sign.resize((324,111))

        # Paste photo (change position as needed)
        fbackground.paste(photo, (150, 99))
        fbackground.paste(photo, (1924,100))
        fbackground.paste(bg_sign, (452, 361), bg_sign)
        sbackground.paste(bg_sign, (1556,674), bg_sign)

        # Save final image in memory of first image
        final_imgf = io.BytesIO()
        fbackground.save(final_imgf, format="JPEG")
        final_imgf.seek(0)

        # Save final image in memory of second image
        final_imgs = io.BytesIO()
        sbackground.save(final_imgs, format="JPEG")
        final_imgs.seek(0)

        print("First image size:", len(final_imgf.getvalue()))
        print("Second image size:", len(final_imgs.getvalue()))
        if len(pdf_document) < 2:
            return {"error": "PDF must have at least 2 pages"}, 400

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("first_page.jpg", final_imgf.getvalue())
            zip_file.writestr("second_page.jpg", final_imgs.getvalue())

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="final_images.zip",
        )

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/utiNewPanCard",methods=["POST"])
def UTI_NEW_PAN_CARD():
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
        photo = photo.resize((403, 521))
        sign = sign.resize((350, 104))

        # change bg of sign
        bg_sign = bg_remove(sign)

        # Paste photo (change position as needed)
        fbackground.paste(photo, (68, 468))
        fbackground.paste(photo, (2018,468))
        fbackground.paste(bg_sign, (320,700), bg_sign)
        sbackground.paste(bg_sign,(1623,3197),bg_sign)

        # Save final image in memory of first image
        final_imgf = io.BytesIO()
        fbackground.save(final_imgf, format="JPEG")
        final_imgf.seek(0)

        # Save final image in memory of second image
        final_imgs = io.BytesIO()
        sbackground.save(final_imgs, format="JPEG")
        final_imgs.seek(0)

        print("First image size:", len(final_imgf.getvalue()))
        print("Second image size:", len(final_imgs.getvalue()))
        if len(pdf_document) < 2:
            return {"error": "PDF must have at least 2 pages"}, 400

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("first_page.jpg", final_imgf.getvalue())
            zip_file.writestr("second_page.jpg", final_imgs.getvalue())

        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype="application/zip",
            as_attachment=True,
            download_name="final_images.zip",
        )

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/utiCorrection",methods=["POST"])
def UTI_CORRECTION():
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
        photo = photo.resize((400, 518))
        sign = sign.resize((389,96))

        # change bg of sign
        bg_sign = bg_remove(sign)
        if(bg_sign): return {"error": "Background removal failed"}, 500 

        # Paste photo (change position as needed)
        fbackground.paste(photo, (72, 485))
        fbackground.paste(photo, (2015,486))
        fbackground.paste(bg_sign, (361,721), bg_sign)
        sbackground.paste(bg_sign,(1733,1493),bg_sign)

        # Save final image in memory of first image
        final_imgf = io.BytesIO()
        fbackground.save(final_imgf, format="JPEG")
        final_imgf.seek(0)

        # Save final image in memory of second image
        final_imgs = io.BytesIO()
        sbackground.save(final_imgs, format="JPEG")
        final_imgs.seek(0)

        print("First image size:", len(final_imgf.getvalue()))
        print("Second image size:", len(final_imgs.getvalue()))
        if len(pdf_document) < 2:
            return {"error": "PDF must have at least 2 pages"}, 400

        # Create zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("first_page.jpg", final_imgf.getvalue())
            zip_file.writestr("second_page.jpg", final_imgs.getvalue())

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
    app.run(host="0.0.0.0",host=8001)
