from flask import Flask, request, jsonify, render_template_string, Response
import cloudinary
import cloudinary.uploader
from gradio_client import Client, handle_file
import os
import json
from datetime import datetime

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
    cloud_name='dcajb02df',
    api_key='862192414383365',
    api_secret='TDuIQPd_iRf5_ThniMlwn8Gaaq8'
)

# Gradio model
client = Client("CohereLabs/command-a-vision")

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title> OCR </title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 flex items-center justify-center min-h-screen">
  <div class="bg-white p-6 rounded-lg shadow-md w-full max-w-md">
    <h2 class="text-2xl font-bold mb-4 text-center">Upload Aadhaar Front and Back for OCR</h2>

    <form id="uploadForm">
      <label class="block mb-1 font-medium">Front Side (Image 1)</label>
      <input type="file" name="image1" accept="image/*" required class="mb-2 block w-full">
      <img id="preview1" class="mb-4 w-full object-contain max-h-60 rounded border" style="display: none;" />

      <label class="block mb-1 font-medium">Back Side (Image 2, Optional)</label>
      <input type="file" name="image2" accept="image/*">
      <img id="preview2" class="mb-4 w-full object-contain max-h-60 rounded border" style="display: none;" />

      <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full">Upload</button>
    </form>

    <div id="result" class="mt-6 text-sm whitespace-pre-wrap"></div>
  </div>

  <script>
    const form = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('result');
    const preview1 = document.getElementById('preview1');
    const preview2 = document.getElementById('preview2');

    form.image1.addEventListener('change', (e) => {
      if (e.target.files[0]) {
        preview1.src = URL.createObjectURL(e.target.files[0]);
        preview1.style.display = 'block';
      }
    });

    form.image2.addEventListener('change', (e) => {
      if (e.target.files[0]) {
        preview2.src = URL.createObjectURL(e.target.files[0]);
        preview2.style.display = 'block';
      }
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      resultDiv.innerText = 'Processing...';

      const file1 = form.image1.files[0];
      const file2 = form.image2.files[0];

      if (!file1) {
        resultDiv.innerText = 'Please select the front image.';
        return;
      }

      const img1 = await loadImage(file1);
      let finalBlob;

      if (file2) {
        const img2 = await loadImage(file2);

        const canvas = document.createElement('canvas');
        const width = Math.max(img1.width, img2.width);
        const height = img1.height + img2.height;

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, width, height);
        ctx.drawImage(img1, 0, 0);
        ctx.drawImage(img2, 0, img1.height);

        finalBlob = await new Promise(resolve => {
          canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.95);
        });
      } else {
        finalBlob = file1;
      }

      const formData = new FormData();
      formData.append('image', finalBlob, 'combined.jpg');

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error(await response.text());
        }

        // Expect plain text response
        const text = await response.text();
        resultDiv.innerText = text;

      } catch (err) {
        resultDiv.innerText = 'Error: ' + err.message;
      }
    });

    function loadImage(file) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = URL.createObjectURL(file);
      });
    }
  </script>
</body>
</html>
    """)

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
  "telephone": "",
  "aadhaar_number": ""
}
""",
                "files": [handle_file(image_url)]
            },
            api_name="/chat"
        )
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        filepath = f"./ocr_result_{timestamp}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("OCR Result:", result)

        variables = extract_variables(result)
        print("aadhaar:", variables.get("aadhaar_number"))
       
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
  residencepincode: "40{variables['telephone'] }001",
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



"""
        print("JS Code:", js_code)
        return Response(js_code, mimetype="text/plain")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)