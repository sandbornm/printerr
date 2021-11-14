import tkinter as tk
from PIL import Image, ImageTk
import os
import json

""" specify directory """
class ImageViewer():
    def __init__(self, imgDir=None):
        self.imgDir = imgDir
        self.window = tk.Tk()

        self.log = {i : None for i in sorted(os.listdir(imgDir))} # imageName : status
        self.window.geometry('800x800')
        self.cv = tk.Canvas(self.window, width=800, height=800)
        #self.exmpl1 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "7d00c5f5a6.jpg")
        #self.exmpl2 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "44f98b2f30.jpg")
        #self.imgs = [self.exmpl1, self.exmpl2]
        self.imgs = self.loadImgs()
        print(self.imgs[:10])
        self.curIdx = 0 # start at beginning of list
        
        while True:
            self.window.bind("<Escape>", self.handleEsc)
            self.window.bind("<Left>", self.getLastImg)
            self.window.bind("<Right>", self.getNextImg)
            self.window.bind("<p>", self.handleP)
            self.window.bind("<e>", self.handleE)
            self.window.bind("<t>", self.handleT)
            self.updateImg()
        
        
    def updateImg(self, next=False):

        #prev = self.curIdx - 1 if next else self.curIdx + 1
        self.curImg = Image.open(os.path.join(self.imgDir, self.imgs[self.curIdx]))
        photo = ImageTk.PhotoImage(self.curImg)
        self.cv.pack(fill='both', expand='yes')
        self.cv.delete("all")
        self.cv.create_image(0, 0, image=photo, anchor='nw')
        self.window.mainloop()

    def loadImgs(self):
        return sorted(os.listdir(self.imgDir))[:10]

    def getNextImg(self, event):
        print("next image")
        if self.curIdx < len(self.imgs) - 1:
            self.curIdx += 1
        else:
            print("last image in dir! wrapping to first image")
            self.curIdx = 0
        self.updateImg(True)

    def getLastImg(self, event):
        print("last image")
        if self.curIdx > 0:
            self.curIdx -= 1
        else:
            print("first image in dir! wrapping to last image")
            self.curIdx = len(self.imgs) - 1
        self.updateImg(False)


    # pass
    def handleP(self, event):
        print(f"pass {self.imgs[self.curIdx]}")
        self.log[self.imgs[self.curIdx]] = "pass"


    # edit
    def handleE(self, event):
        print(f"edit {self.imgs[self.curIdx]}")
        self.log[self.imgs[self.curIdx]] = "edit"

    # trash
    def handleT(self, event):
        print(f"trash {self.imgs[self.curIdx]}")
        self.log[self.imgs[self.curIdx]] = "trash"

    # save and quit
    def handleEsc(self, event):
        self.save()
        self.window.destroy()

    
    def save(self):
        fname = os.path.join(os.getcwd(), "log", self.imgDir.split("/")[-1] + ".json")
        with open(fname, "w") as f:
            json.dump(self.log, f)
        print(f"saved") 


# error types
ov = os.path.join(os.getcwd(), "imgs", "overextrusion") # ty
st = os.path.join(os.getcwd(), "imgs", "stringing") # ty
un = os.path.join(os.getcwd(), "imgs", "underextrusion") # ty
we = os.path.join(os.getcwd(), "imgs", "weak_infill")
wa = os.path.join(os.getcwd(), "imgs", "warping") # michael 
bl = os.path.join(os.getcwd(), "imgs", "blobbing") # michael
de = os.path.join(os.getcwd(), "imgs", "delamination") # michael

xy = os.path.join(os.getcwd(), "imgsResized", "stringing")
v = ImageViewer(xy)




