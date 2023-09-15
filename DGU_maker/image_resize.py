from PIL import Image

"""image_list = ["beach", "line", "ocean", "sand"]
j = 3

for i in range(1000):
    i += 1
    img = Image.open('img_data/all_image/'+ image_list[j] +' ('+str(i)+').jpg')
    img_resize = img.resize((250, 250))
    img_resize.save('all_resize_img/'+ image_list[j] +' ('+str(i)+').jpg')"""

img = Image.open('img_data\img_data.png')
img_resize = img.resize((1120, 960))
img_resize.save('img_data\img_data1.png')