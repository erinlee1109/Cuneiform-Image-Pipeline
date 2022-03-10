import os, sys
import pathlib
import re
import numpy as np
import re
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline 

def create_thresh(raw_scan, kernel_size, low_thresh): 
    grayscaled = cv2.cvtColor(raw_scan, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(grayscaled, kernel_size)
    _,thresh = cv2.threshold(blurred,int(low_thresh),255,cv2.THRESH_BINARY)
    thresh = cv2.medianBlur(thresh, kernel_size)
    blurred_thresh = cv2.medianBlur(thresh, kernel_size)
    return blurred_thresh

def apply_mask(raw_scan, mask): # mask is thresh
    new_im = cv2.bitwise_and(raw_scan,raw_scan,mask=mask)
    return new_im

def crop_params(thresh):
    top_found = False
    left_found = False
    NUM_PIXELS=100
    for i, horizontal_line in enumerate(thresh):
        # are there at least 50 white pixels in the row? Likely tablet
        if not top_found: 
            if (np.sum(horizontal_line) > 255*NUM_PIXELS): 
                top_edge = i
                top_found = True
        # are there less than 50 white pixels in the row? Likely noise 
        else: 
            if(np.sum(horizontal_line) < 255*NUM_PIXELS):
                bottom_edge = i
                break
    
    for i, vertical_line in enumerate(thresh.T):
        # are there at least 50 white pixels in the column? Likely tablet 
        if not left_found:
            if (np.sum(vertical_line) > 255*NUM_PIXELS):
                left_most_edge = i
                left_found = True
        # are there at least 50 white pixels in the column? Likely noise
        else:
            if(np.sum(vertical_line) < 255*NUM_PIXELS):
                right_most_edge = i
                break
                
    print (top_edge, bottom_edge, left_most_edge, right_most_edge)
    return top_edge, bottom_edge, left_most_edge, right_most_edge

def crop(mask_applied, thresh, padding):
    top, bottom, left, right = crop_params(thresh)
    cropped = mask_applied[top-padding:bottom+padding,left-padding:right+padding]
    
    return cropped

def produce_crop(raw_scan, padding):
    thresh = create_thresh(raw_scan,5,50)
    mask_applied = apply_mask(raw_scan, thresh)  
    cropped = crop(mask_applied, thresh, padding)
    return cropped

"""Replaces abbreviations in the image filename, and displays titles on the subplot for readability.""" 
def replace_abbr(filename): 
    abbrs = {'r': 'reverse', 're':'right', 'le':'left', 'te':'top', 'be':'bottom','o':'obverse'}
    res = re.search(r'_.*?\d', filename).group()
    abbr = abbrs[res[1:-1]]
    return abbr

def put_on_canvas(tablet_dict):
    h, w = 6000, 3400 # initial canvas is big to accomodate scans of bigger tablets 
    background = np.zeros((h, w, 3), np.uint8) #4 channels
    
    vertical_center = w//2
    
    # place top scan on the canvas
    top_h, top_w, channels = tablet_dict['top'].shape
    top_w = 2*(top_w//2)
    background[:top_h, vertical_center-top_w//2:vertical_center+top_w//2, :3] = tablet_dict['top'][:,:top_w,:3]
    
    # place obverse scan on the canvas
    obverse_h, obverse_w, channels = tablet_dict['obverse'].shape
    obverse_w = 2*(obverse_w//2)
    background[top_h:top_h+obverse_h,vertical_center-obverse_w//2:vertical_center+obverse_w//2, :3] = tablet_dict['obverse'][:,:obverse_w,:3]
    
    # place bottom scan on the canvas
    bottom_h, bottom_w, channels = tablet_dict['bottom'].shape
    bottom_w = 2*(bottom_w//2)
    background[top_h+obverse_h:top_h+obverse_h+bottom_h,vertical_center-bottom_w//2:vertical_center+bottom_w//2, :3] = tablet_dict['bottom'][:,:bottom_w,:3]
    
    # place reverse scan on the canvas
    reverse_h, reverse_w, channels = tablet_dict['reverse'].shape
    reverse_w = 2*(reverse_w//2)
    background[top_h+obverse_h+bottom_h:top_h+obverse_h+bottom_h+reverse_h,vertical_center-reverse_w//2:vertical_center+reverse_w//2, :3] = tablet_dict['reverse'][:,:reverse_w,:3]
    horizontal_center = top_h + obverse_h//2

    # place left scan on the canvas
    left_h, left_w, channels = tablet_dict['left'].shape
    left_h = 2*(left_h//2)
    background[horizontal_center-left_h//2:horizontal_center+left_h//2, vertical_center-obverse_w//2-left_w:vertical_center-obverse_w//2, :3] = tablet_dict['left'][:left_h,:,:3]
    
    # place left scan on the canvas
    right_h, right_w, channels = tablet_dict['right'].shape
    right_h = 2*(right_h//2)
    background[horizontal_center-right_h//2:horizontal_center+right_h//2, vertical_center+obverse_w//2:vertical_center+obverse_w//2+right_w, :3] = tablet_dict['right'][:right_h,:,:3]
    
    return background

def build_flatcross(ID):
    file_dir = PATH + '/'+ ID + '/'
    filenames = os.listdir(file_dir)
    
    tablet_dict = {}
    for i, file in enumerate(filenames, 1):
        tablet_side = mpimg.imread(file_dir+file)
        abbr = replace_abbr(file)
        tablet_dict[abbr] = produce_crop(tablet_side, 60)
        print(abbr,"shape is ", tablet_dict[abbr].shape)
    final = put_on_canvas(tablet_dict)

    cv2.imwrite(PATH+"/poster/"+ID+".png", cv2.cvtColor(final, cv2.COLOR_RGB2BGR))

"""Finally, build fatcross for all images in the large scan batch."""

# PATH = "/earlhamcs/eccs/users/elee17/Capstone/scan-batch-large"
PATH = "/Users/yujeong/Cuneiform-Image-Pipeline/Cuneiform-Image-Pipeline/small-batch-scans"

def produce_flatcrosses():
    IDS = os.listdir(PATH)
    os.mkdir(PATH+"/output")
    
    for ID in IDS:
        try:
            build_flatcross(ID)
            print("Finished building fatcross for ID:", ID)
        except:
            print("There was some error with fatcross - it's probably a skinnycross with ID:", ID)  
        
produce_flatcrosses()