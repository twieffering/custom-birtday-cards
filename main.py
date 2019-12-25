#!/usr/bin/python3

from PIL import Image, ImageDraw, ImageFont, ImageOps
import os
import random

""" OPTIONS """
RES         = 5						# Resolution: "RES * A4"
ICONS_SCALE = 0.4
OUTPUT_DIR  = "out"
ICONS_DIR   = "icons"
BG_DIR      = "backgrounds"
CARD_BG     = "card-bg.png"
BG_OPACITY  = 128
BG_MARGIN   = (RES * 5, RES * 5)
NUM_Y       = 2
NUM_X       = 2

# Aspectratio: A4
page_width  = RES * 297 
page_heigth = RES * 210


""" FUNCTIONS """
def get_img(img_loc, scale, page_width, page_heigth, NUM_X, NUM_Y, margin=(0,0), opacity=None, fit=False):
    base = Image.open(img_loc)
    
    if opacity:
        base.putalpha(opacity)
    
    size = (round(scale * page_width / NUM_X - margin[0]), round(scale * page_heigth / NUM_Y - margin[1]))    
    base.thumbnail(size)
    
    if fit:
        base = ImageOps.fit(base, size)
    
    return base

def get_offset(local_center, image):
    x_offset = round(local_center[0] - image.size[0] / 2)
    y_offset = round(local_center[1] - image.size[1] / 2)
    return (x_offset, y_offset)

def repeat(images, scale, backgrounds=[]):

    pages = []
    page  = newpage()
    
    page_width  = page.size[0]
    page_heigth = page.size[1]
    
    dx = round(page_width / NUM_X)
    dy = round(page_heigth / NUM_Y)

    local_dx = round(dx / 2)
    local_dy = round(dy / 2)

    row, col = 0, 0
    
    for i, img_loc in enumerate(images):

        base = get_img(img_loc, scale, page_width, page_heigth, NUM_X, NUM_Y)
            
        local_center_x = (local_dx + col * dx) 
        local_center_y = (local_dy + row * dy) 
                
        print("{}\t\t\t({}, {})".format(img_loc, row, col))
        
        # paste background
        if (len(backgrounds) > 0):
            bg_loc     = random.choice(backgrounds)
            background = get_img(bg_loc, 1, page_width, page_heigth, NUM_X, NUM_Y, BG_MARGIN, BG_OPACITY, fit=True)

            tmp_page = newpage(color=(255,255,255,0))
            tmp_page.paste(background, get_offset((local_center_x, local_center_y), background))           
            page = Image.alpha_composite(page, tmp_page)
        
        # paste icon
        tmp_page = newpage(color=(255,255,255,0))
        tmp_page.paste(base, get_offset((local_center_x, local_center_y), base))
        page = Image.alpha_composite(page, tmp_page)

        # Calculate coordinates of image
        if col >= (NUM_X - 1):

            # Check if page full
            if row >= NUM_Y - 1:
                pages.append(page)
                row, col = 0, 0
                page = newpage()
            else:
                col = 0
                row += 1

        else:
            col += 1
    
    return pages

def newpage(color=(255,255,255,255)):
    return Image.new('RGBA', (page_width, page_heigth), color=color)
    
def file_list(directory, files=None):
    if not files:
        files = os.listdir(directory)
        
    return ["./" + directory + "/" + f for f in files]

""" MAIN """
if __name__ == "__main__":
	icons       = os.listdir(ICONS_DIR)
	images      = file_list(ICONS_DIR, icons)
	backgrounds = file_list(BG_DIR)
	pages       = repeat(images, ICONS_SCALE, backgrounds)

	images      = ["./" + CARD_BG for _ in range(len(icons))]
	card_backs  = repeat(images, 1)

	for i, page in enumerate(card_backs):
		pages[i].save(OUTPUT_DIR + '/' + str(i) + '1-front.png')
		card_backs[i].save(OUTPUT_DIR + '/' + str(i) + '2-back.png')
