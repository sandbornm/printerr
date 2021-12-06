import tkinter as tk
from PIL import Image, ImageTk
import os
import json


class ImageViewer():
    def __init__(self, imgDir=None):
        self.imgDir = imgDir
        self.window = tk.Tk()
        self.batchSize = 60

        # TODO change this after each run
        """
        to start: self.depth = [0, self.batchSize] --> 0, 60
        next: self.depth = [self.batchSize, 2 * self.batchSize] --> 60, 120
        
        len(os.listdir(imgDir)) - final step
        """
        self.depth = [self.batchSize, 2*self.batchSize] # last entry is to length of folder

        self.log = {i : None for i in sorted(os.listdir(imgDir))} # imageName : status
        self.window.geometry('800x800')
        self.cv = tk.Canvas(self.window, width=800, height=800)
        #self.exmpl1 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "7d00c5f5a6.jpg")
        #self.exmpl2 = os.path.join(os.getcwd(), "examples", "3d_print_elephant_foot", "44f98b2f30.jpg")
        #self.imgs = [self.exmpl1, self.exmpl2]
        self.dirLen, self.imgs = self.loadImgs()
        self.numSplits = self.dirLen / self.batchSize
        print(f"num images: {self.dirLen}")
        print(f"num splits {self.numSplits}")

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
        dirLen = len(os.listdir(self.imgDir))
        return dirLen, sorted(os.listdir(self.imgDir))[self.depth[0]:self.depth[1]]

    def getNextImg(self, event):
        if self.curIdx < len(self.imgs) - 1:
            self.curIdx += 1
        else:
            print("last image in dir! wrapping to first image")
            self.curIdx = 0
        print(f"next image {self.depth[0] + self.curIdx}/{self.depth[1]}")
        self.updateImg(True)

    def getLastImg(self, event):
        if self.curIdx > 0:
            self.curIdx -= 1
        else:
            print("first image in dir! wrapping to last image")
            self.curIdx = len(self.imgs) - 1
        print(f"last image {self.depth[0] + self.curIdx}/{self.depth[1]}")
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
        fname = os.path.join(os.getcwd(), "log", self.imgDir.split("/")[-1] + f"{self.depth[0]}_{self.depth[1]}" + ".json")
        with open(fname, "w") as f:
            json.dump(self.log, f)
        print(f"saved {fname}") 

# driver
if __name__ == "__main__":
    ov = os.path.join(os.getcwd(), "imgsResizedF2", "overextrusion") # example
    v = ImageViewer(ov)




