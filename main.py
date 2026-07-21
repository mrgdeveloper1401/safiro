from urllib.request import urlretrieve

image_url = "https://d03.wpvn.ir/Mytravel/wp-content/uploads/2023/12/img1-2.jpeg"
output_path = "static/media/background-header.png"

try:
    urlretrieve(image_url, output_path)
    print("Image downloaded to {}".format(output_path))
except Exception as e:
    print(e)
