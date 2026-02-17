from flask import Flask, request, jsonify, render_template, Response
import cloudinary
import cloudinary.uploader
from gradio_client import Client, handle_file
import os
import json
from datetime import datetime
import dotenv

dotenv.load_dotenv()

app = Flask(__name__)

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
                "text": """Extract the following fields from this Aadhaar card image and return **only** the result as a raw JSON object. Do not include any explanations, Markdown formatting, or backticks. Leave any missing field value as an empty string,and title is based on gender,father name could be found on address line and give aadhar number without spacing.

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
  "aadhaar_number": ""
}
""",
                "files": [handle_file(image_url)]
            },
            api_name="/chat"
        )
        
        data_dict = json.loads(result)
        print("Extracted Data:", data_dict)
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
        # print("Extracted Data:", data_dict)
        

        variables = data_dict

       
        # Inject dict directly into JS as object
        js_code = f"""


let select = document.getElementById("applicant_check");
select.value =  "{variables['title'] }";
select.dispatchEvent(new Event("change", {{ bubbles: true }}));




const lastNameInput = document.getElementById("alastnameind");
lastNameInput.value = "{variables['lastname'] }";
lastNameInput.dispatchEvent(new Event("change",{{ bubbles: true }} ));


const firstNameInput = document.getElementById("afirstnameind");
firstNameInput.value = "{variables['firstname'] }";
firstNameInput.dispatchEvent(new Event("change", {{ bubbles: true }}));


const dobDay = document.getElementById("dobd");
dobDay.value = "{variables['dob_day'] }";
dobDay.dispatchEvent(new Event("change",  {{ bubbles: true }}));

const dobMonth = document.getElementById("dobm");
dobMonth.value = "{variables['dob_month'] }";
dobMonth.dispatchEvent(new Event("change", {{ bubbles: true }}));

const dobYear = document.getElementById("doby");
dobYear.value = "{variables['dob_year'] }";
dobYear.dispatchEvent(new Event("change", {{ bubbles: true }}));


const fatherLastName = document.getElementById("fatherlastname");
fatherLastName.value = "{variables['father_lastname'] }";
fatherLastName.dispatchEvent(new Event("change", {{bubbles: true   }}));const fatherFirstName = document.getElementById("fatherfirstname");
fatherFirstName.value = "{variables['father_firstname'] }";
fatherFirstName.dispatchEvent(new Event("change", {{bubbles: true }}));

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
        # print("JS Code:", js_code)
        return Response(js_code, mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)