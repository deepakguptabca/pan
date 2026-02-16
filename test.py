data = {
    "title": "Shri",
    "lastname": "Bhan",
    "firstname": "Udaya",
    "gender": "MALE",
    "dob_day": "13",
    "dob_month": "03",
    "dob_year": "1982",
    "father_lastname": "",
    "father_firstname": "",
    "flat": "S/O Lallan",
    "village": "SADHANA",
    "post_office": "Garhi",
    "sub_division": "Harsau",
    "district": "Gurgaon",
    "state": "Haryana",
    "telephone": "",
    "aadhaar_number": "980063077821",
}

# Convert and save back
data["dob_month"] = str(int(data["dob_month"]))

print(data["dob_month"])   # 3