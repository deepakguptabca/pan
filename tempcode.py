const fatherLastName = document.getElementById("fatherlastname");
fatherLastName.value = "{variables['father_lastname'] }";
fatherLastName.dispatchEvent(new Event("change", {{bubbles: true   }}));const fatherFirstName = document.getElementById("fatherfirstname");
fatherFirstName.value = "{variables['father_firstname'] }";
fatherFirstName.dispatchEvent(new Event("change", {{bubbles: true }}));