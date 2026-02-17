import requests

# Your image path
image_path = "sign.JPG"   # put your image name here

# Your API key
API_KEY = os.getenv("API_KEY")

response = requests.post(
    "https://api.remove.bg/v1.0/removebg",
    files={"image_file": open(image_path, "rb")},
    data={"size": "auto"},
    headers={"X-Api-Key": API_KEY},
)

if response.status_code == requests.codes.ok:
    with open("output.png", "wb") as out:
        out.write(response.content)
    print("Background removed successfully!")
else:
    print("Error:", response.status_code, response.text)
