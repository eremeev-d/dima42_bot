import PIL
import torch
from PIL import Image
import torchvision.transforms as transforms

# Image load/save function
def load_img(filename, img_size = 32*3):
    img = Image.open(filename)
    transform = transforms.Compose([
        transforms.Resize(img_size),
        # transforms.CenterCrop(img_size),
        transforms.ToTensor()
    ])
    img = transform(img)
    img = img.unsqueeze(0)
    img = img
    return img

def save_img(img, filename, img_size = 200):
    img = transforms.ToPILImage()(img.clone().squeeze(0).cpu())
    img = transforms.Resize(img_size)(img)
    img.save(filename)