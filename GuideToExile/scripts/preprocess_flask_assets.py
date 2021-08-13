# manage.py runscript preprocess_flask_assets --script-args GuideToExile\static\GuideToExile\poe_assets\Art\2DItems\Flasks
import os

from PIL import Image


def merge_image_layers(art_name):
    im = Image.open(art_name)
    width, height = im.size
    third_of_width = width // 3
    top = 0
    bottom = height

    if width != 234 or height != 156:
        return

    layer1 = im.crop((0, top, third_of_width, bottom))
    layer2 = im.crop((third_of_width, top, 2 * third_of_width, bottom))
    layer3 = im.crop((2 * third_of_width, top, width, bottom))

    new_image = Image.new('RGBA', (third_of_width, height), (250, 250, 250))
    new_image.paste(layer3, (0, 0))
    new_image.paste(layer2, (0, 0), layer2)
    new_image.paste(layer1, (0, 0), layer1)

    new_image.save(art_name)


def run(*args):
    flask_assets_dir = args[0]
    for f in os.scandir(flask_assets_dir):
        if os.path.isdir(f.path):
            continue
        merge_image_layers(f.path)
