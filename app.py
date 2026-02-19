from flask import Flask, request, jsonify, render_template, Response,send_file
import cloudinary
import cloudinary.uploader
from gradio_client import Client, handle_file
import os
import json
import requests
from numpy import sign
import fitz  # PyMuPDF
from PIL import Image
import io
import dotenv
import zipfile
from dist import city_dict

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


###====>Variable extractor
def extract_variables(json_block):
    
    cleaned = json_block.replace("\njson", "").replace("\n", "").strip()
    
    
    data = json.loads(cleaned)

    # Destructure values into variables
    title = data.get("title", "")
    lastname = data.get("lastname", "")
    firstname = data.get("firstname", "")
    gender = data.get("gender", "")
    dob_day = data.get("dob_day", "")
    dob_month = data.get("dob_month", "")
    dob_year = data.get("dob_year", "")
    father_lastname = data.get("father_lastname", "")
    father_firstname = data.get("father_firstname", "")
    flat = data.get("flat", "")
    village = data.get("village", "")
    post_office = data.get("post_office", "")
    sub_division = data.get("sub_division", "")
    district = data.get("district", "")
    state = data.get("state", "")
    telephone = data.get("telephone", "")
    aadhaar_number = data.get("aadhaar_number", "")

    # Return  as a dict
    return {
        "title": title,
        "lastname": lastname,
        "firstname": firstname,
        "gender": gender,
        "dob_day": dob_day,
        "dob_month": dob_month,
        "dob_year": dob_year,
        "father_lastname": father_lastname,
        "father_firstname": father_firstname,
        "flat": flat,
        "village": village,
        "post_office": post_office,
        "sub_division": sub_division,
        "district": district,
        "state": state,
        "telephone": telephone,
        "aadhaar_number": aadhaar_number
    }

# Configure Cloudinary 
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

# Gradio model
client = Client("CohereLabs/command-a-vision")

@app.route('/')
def index():
    return render_template("index.html")



@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']

    try:
        # Upload to Cloud
        upload_result = cloudinary.uploader.upload(file)
        image_url = upload_result['secure_url']

        # Send to Gradio OCR model
        result = client.predict(
            message={
                "text": """Extract the following fields from this Aadhaar card image and return **only** the result as a raw JSON object. Do not include any explanations, Markdown formatting, or backticks. Leave any missing field value as an empty string,and title is based on gender,and give aadhar number without spacing,fill district name in dist_code too.Fill mobile no,email id and father name also,extract this from image.if father name or name is a single word then put that in lastname and leave firstname empty.

{
  "title": Shri / Smt.,
  "lastname": "",
  "firstname": "",
  "gender": "",
  "dob_day": "",
  "dob_month": "",
  "dob_year": "",
  "father_lastname": "",
  "father_firstname": "",
  "flat": "",
  "village": "",
  "post_office": "",
  "sub_division": "",
  "district": "",
  "state": "",
  "pincode": "",
  "aadhaar_number": "",
  "dist_code": "",
  "mob":"",
  "email":""
}
""",
                "files": [handle_file(image_url)]
            },
            api_name="/chat"
        )
        
        data_dict = json.loads(result)
        data_dict["dob_day"] = str(int(data_dict["dob_day"]))
        data_dict["state"] = data_dict["state"].upper()

        dobm = data_dict["dob_month"]
        if(dobm=="01"):
            data_dict["dob_month"] = "January"
        elif(dobm=="02"):
            data_dict["dob_month"] = "February"
        elif(dobm=="03"):
            data_dict["dob_month"] = "March"
        elif(dobm=="04"):   
            data_dict["dob_month"] = "April"
        elif(dobm=="05"):
            data_dict["dob_month"] = "May"
        elif(dobm=="06"):
            data_dict["dob_month"] = "June"
        elif(dobm=="07"):
            data_dict["dob_month"] = "July"
        elif(dobm=="08"):
            data_dict["dob_month"] = "August"
        elif(dobm=="09"):
            data_dict["dob_month"] = "September"
        elif(dobm=="10"):
            data_dict["dob_month"] = "October"
        elif(dobm=="11"):
            data_dict["dob_month"] = "November"
        elif(dobm=="12"):
            data_dict["dob_month"] = "December"
        
        extract_dist = data_dict["district"].upper()
        dist_code = None

        for code, name in city_dict.items():
            if name == extract_dist:
                dist_code = code
                break
        
        print("Extracted Data:", data_dict)
        variables = data_dict

       
        # Inject dict directly into JS as object
        js_code = f"""


let select = document.getElementById("applicant_check");
select.value =  "{variables['title'] }";
select.dispatchEvent(new Event("change", {{ bubbles: true }}));


const lastNameInput = document.getElementById("alastnameind");
lastNameInput.value = "{variables['lastname'] }";
lastNameInput.dispatchEvent(new Event("change",{{ bubbles: true }} ));

const city_code = document.getElementById("citys");
city_code.value = "{dist_code}";
city_code.dispatchEvent(new Event("change",{{ bubbles: true }} ));

const mobile_no = document.getElementById("contactdtl");
mobile_no.value = "{variables['mob']}";
mobile_no.dispatchEvent(new Event("change",{{ bubbles: true }} ));

const email_id = document.getElementById("venderemailids");
email_id.value = "{variables['email']}";
email_id.dispatchEvent(new Event("change",{{ bubbles: true }} ));

setTimeout(()=>{{
const firstNameInput = document.getElementById("afirstnameind");
firstNameInput.value = "{variables['firstname'] }";
firstNameInput.dispatchEvent(new Event("change", {{ bubbles: true }}));
}},1000)


const dobDay = document.getElementById("dobd");
dobDay.value = "{variables['dob_day'] }";
dobDay.dispatchEvent(new Event("change",  {{ bubbles: true }}));

const dobMonth = document.getElementById("dobm");
dobMonth.value = "{variables['dob_month'] }";
dobMonth.dispatchEvent(new Event("change", {{ bubbles: true }}));

const dobYear = document.getElementById("doby");
dobYear.value = "{variables['dob_year'] }";
dobYear.dispatchEvent(new Event("change", {{ bubbles: true }}));

const father_last = document.getElementById("fatherlastname");
father_last.value = "{variables['father_lastname'] }";
father_last.dispatchEvent(new Event("change", {{ bubbles: true }}));

const father_first = document.getElementById("fatherfirstname");
father_first.value = "{variables['father_firstname'] }";
father_first.dispatchEvent(new Event("change", {{ bubbles: true }}));



const fields = {{
  regflat: "{variables['flat'] }",
  nopbuilding: "{variables['village'] }",
  roadstreet: "{variables['post_office'] }",
  arealocality: "{variables['sub_division'] }",
  towncity: "{variables['district'] }",
  dstate: "{variables['state'] }",
  residencepincode: "{variables['pincode'] }",
  aadhaarnumber: "{variables['aadhaar_number'] }"
}};

for (const [id, value] of Object.entries(fields)) {{
  const input = document.getElementById(id);
  if (input) {{
    input.value = value;
    input.dispatchEvent(new Event("change", {{ bubbles: true }}));
  }} else {{
    console.warn(`Element with id "${id}" not found.`);
  }}
}}

const verifierPlace = document.getElementById("verifierplace");
verifierPlace.value = "{variables['state'] }";
verifierPlace.dispatchEvent(new Event("change", {{ bubbles: true }}));


"""
        
        if(dist_code):
            js_code += f"""

const dropdown1 = document.getElementById('areacode_dropdown');
const dropdown2 = document.getElementById('aotype_dropdown');
const dropdown3 = document.getElementById('rangecode_dropdown');
const dropdown4 = document.getElementById('anno_dropdown');

setTimeout(() => {{
    dropdown1.selectedIndex = 1;
    dropdown1.dispatchEvent(new Event('change', {{ bubbles: true }}));

    setTimeout(() => {{
        dropdown2.selectedIndex = 1;
        dropdown2.dispatchEvent(new Event('change', {{ bubbles: true }}));

        setTimeout(() => {{
            dropdown3.selectedIndex = 1;
            dropdown3.dispatchEvent(new Event('change', {{ bubbles: true }}));

            setTimeout(() => {{
                dropdown4.selectedIndex = 1;
                dropdown4.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}, 1000);

        }}, 1000);

    }}, 1000);

}}, 1000);


    """
        

        # print("JS Code:", js_code)
        return Response(js_code, mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

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

if __name__ == '__main__':
    app.run(debug=True)