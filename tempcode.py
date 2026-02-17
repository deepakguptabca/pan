const fatherLastName = document.getElementById("fatherlastname");
fatherLastName.value = "{variables['father_lastname'] }";
fatherLastName.dispatchEvent(new Event("change", {{bubbles: true   }}));const fatherFirstName = document.getElementById("fatherfirstname");
fatherFirstName.value = "{variables['father_firstname'] }";
fatherFirstName.dispatchEvent(new Event("change", {{bubbles: true }}));

22

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

33

const dropdown1 = document.getElementById('areacode_dropdown');
    dropdown1.selectedIndex = 1;  
    dropdown1.dispatchEvent(new Event('change', {{ bubbles: true }}));

    const dropdown2 = document.getElementById('aotype_dropdown');
    dropdown2.selectedIndex = 1;  
    dropdown2.dispatchEvent(new Event('change', {{ bubbles: true }}));

    const dropdown3 = document.getElementById('rangecode_dropdown');
    dropdown3.selectedIndex = 1;  
    dropdown3.dispatchEvent(new Event('change', {{ bubbles: true }}));

    const dropdown4 = document.getElementById('anno_dropdown');
    dropdown4.selectedIndex = 1;  
    dropdown4.dispatchEvent(new Event('change', {{ bubbles: true }}));