from rembg import remove
from PIL import Image

# Open image
input_image = Image.open("input.jpg")

# Remove background
output_image = remove(input_image)

# Save as PNG (important)
output_image.save("output.png")

print("Background removed successfully!")
