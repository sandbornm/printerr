import tkinter as tk
from PIL import Image, ImageTk
import os


""" specify directory """
class ImageViewer():
    def __init__(self, imgDir=None):
        self.imgDir = imgDir
        self.log = {} # imageName : status
        self.window = tk.Tk()
        self.window.geometry('600x600')
        self.exmpl1 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "7d00c5f5a6.jpg")
        self.exmpl2 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "44f98b2f30.jpg")
        print(self.exmpl1)
        self.im1, self.im2 = self.loadImgs()
        photo = ImageTk.PhotoImage(self.im1)
        self.cv = tk.Canvas()
        self.cv.pack(side='top', fill='both', expand='yes')
        self.cv.create_image(0, 0, image=photo, anchor='nw')
        self.window.bind("<Escape>", self.handleEsc)
        self.window.bind("<Left>", self.getLastImg)
        self.window.bind("<Right>", self.getNextImg)

        """ commands to label images """
        self.window.bind("<p>", self.handleP)
        self.window.bind("<e>", self.handleE)
        self.window.bind("<t>", self.handleT)

        self.window.mainloop()
    
    def loadImgs(self):
        im1 = Image.open(self.exmpl1)
        im2 = Image.open(self.exmpl2)
        return im1, im2

    def getNextImg(self, event):
        print(f"next image")

    def getLastImg(self, event):
        print(f"last image")

    # pass
    def handleP(self, event):
        print("pass")

    # edit
    def handleE(self, event):
        print("edit")

    # trash
    def handleT(self, event):
        print("trash")

    # save and quit
    def handleEsc(self, event):
        self.save()
        self.window.destroy()

    
    def save(self):
        print("save") 




v = ImageViewer()




