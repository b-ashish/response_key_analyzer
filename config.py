import os

cwd = os.getcwd()

# app files
upload_save = os.path.join(cwd,'upload\\uploaded.html')
not_found_img = os.path.join(cwd,'images\\3828541.jpg')

#utils files
right_ans_save = os.path.join(cwd,'templates\\right_ans.html')
wrong_ans_save = os.path.join(cwd,'templates\\wrong_ans.html')
full_save = os.path.join(cwd,'templates\\full_analyz.html')

#pie charts images
pie_image_dir = os.path.join(cwd,'static')

# extracting images name from static folder
img_list = os.listdir(pie_image_dir)
img_paths = [os.path.join("static",i) for i in img_list]
