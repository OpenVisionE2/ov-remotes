#!/usr/bin/python
from os import listdir
from os.path import join, isfile
from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET


for f in listdir("./rc/"):
    if "png" in f and isfile(join("./rc", f.replace(".png", ".xml"))):
        with Image.open(join("./rc", f)) as im:
            dst = Image.new('RGBA', (154, 500))
            dst.paste((255, 255, 255), [0, 0, dst.size[0], dst.size[1]])
            l = 154 - im.width
            t = 500 - im.height
            dst.paste(im, (0, 0))
            preview = Image.new('RGBA', (154 * 3, 500))
            preview.paste(dst, (0, 0))
            tree = ET.parse(join("./rc", f.replace(".png", ".xml")))
            root = tree.getroot()
            rc = root.find("rc")
            bpos = 1
            legend = Image.new('RGBA', (154, 500))
            legend.paste((255, 255, 255), [0, 0, legend.size[0], legend.size[1]])
            ldraw = ImageDraw.Draw(legend)
            ldraw.text((20, 10), f.replace(".png", ""), fill="black")
            try:
                for button in rc.findall("button"):
                    pp = [int(x.strip()) for x in button.attrib.get("pos", "0").split(",")]
                    p_x, p_y = pp[0], pp[1]
                    draw = ImageDraw.Draw(dst)
                    draw.ellipse((p_x - 10, p_y - 10, p_x + 10, p_y + 10), fill=(255, 255, 255, 50), outline=(255, 255, 0))
                    draw.text((p_x - 5, p_y - 5), str(bpos), fill="red")
                    txt = "%s - %s" % (str(bpos), button.attrib.get("id"))
                    ldraw.text((10, 20 + (bpos * 9)), txt, fill="black")
                    bpos += 1
            except:
                pass
            preview.paste(dst, (155, 0))
            preview.paste(legend, (155 + 154, 0))
            preview.save(join("./previews", f))
