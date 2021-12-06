import os
import json
from threading import Thread
from tqdm import tqdm
import requests
import io
from PIL import Image
import hashlib
import time
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

#TERMS = ["stringing", "overextrusion", "underextrusion", "weak infill"]
TERMS = ["blobbing", "delamination", "warping"]
RUN_DIR = os.path.join(os.getcwd(), "runs")
runs = sorted(os.listdir(RUN_DIR))
START_TIME = default_timer

IMG_DIR = os.path.join(os.getcwd(),"imgs")
RESIZE_DIR = os.path.join(os.getcwd(), "imgsResized")


def collectUrls():
    shared = {t: set() for t in TERMS}
    print(runs)
    for r in runs[-1:]:
        with open(os.path.join(RUN_DIR, r), "r") as f:
            data = json.load(f)
            for k in list(data.keys()):
                for e in TERMS: 
                    if e in k:
                        for i in range(len(data[k])):
                            shared[e].add(data[k][i])
    print("urls per term")
    print({k : len(s) for k,s in shared.items()})
    return shared


""" data (dict) is the dictionary of {terms : urls} to be saved """
def saveImgs(data, imgDir=os.path.join(os.getcwd(),"imgs")):
    assert data is not None
    print(f"image sizes {[len(d) for d in list(data.values())]}")
    s = time.time()
    for term in list(data.keys())[:1]:
        # make dirs by search term
        drnm = term.replace(" ", "_")
        if drnm not in os.listdir(imgDir):
            os.mkdir(os.path.join(imgDir, drnm))

        print(f"saving images of: {term}") 
        for url in tqdm(list(data[term])): # save each url
            #print(f"url {url}")
            #print(f"url type is {type(url)}")
            fetchExc = 0
            try:
                imgData = requests.get(url).content
            except Exception as e:
                #print(f"caught {e} while fetching {url}")
                fetchExc += 1

            saved = 0
            imgExc = 0
            try:
                imgFile = io.BytesIO(imgData)
                img = Image.open(imgFile).convert("RGB")
                fpath = os.path.join(imgDir, drnm, hashlib.sha1(imgData).hexdigest()[:16] + '.png')
                if not os.path.exists(fpath):
                    with open(fpath, 'wb') as f:
                        img.save(f, "PNG", quality=85)
                        saved += 1 # dummy save
            except Exception as e:
                #print(f"caught {e} while saving image at {url}")
                imgExc += 1
    e = time.time()
    print(f"done in {e-s}s")
    print(f"saved {saved} images, fetch excepted {fetchExc}, image excepted {imgExc} in {e-s} seconds")


def fetch(session, url, drnm):
    with session.get(url) as response:
        imgData = response.content
        if response.status_code != 200:
            print(f"failed with url {url}")

        try:
            imgFile = io.BytesIO(imgData)
            img = Image.open(imgFile).convert("RGB")
            fpath = os.path.join(IMG_DIR, drnm, hashlib.sha1(imgData).hexdigest()[:16] + '.png')
            print(f"fpath is {fpath}")
            with open(fpath, 'wb') as f:
                img.save(f, "PNG", quality=85)
                #saved += 1 # dummy save
        except Exception as e:
            print(f"caught {e} while saving image at {url}")
            #imgExc += 1
            pass

        #elapsed = default_timer() - START_TIME
        return


async def getImgDataAsync(urls, drnm):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()
            START_TIME = default_timer()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, url, drnm)
                )
                for url in urls
            ]
            for response in await asyncio.gather(*tasks):
                pass 


def main(data):
    terms = list(data.keys())
    print(f"terms {terms}")
    for t in tqdm(terms):
        print(f"current term {t}")
        drnm = t.replace(" ", "_")
        print(f"drnm is {drnm}")
        urls = list(data[t])

        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(getImgDataAsync(urls, drnm))
        loop.run_until_complete(future)


def dataSummary():
    l = []
    ds = os.listdir("/Users/michael/printerr/imgsResized")
    for d in ds:
        if d != ".DS_Store":
        # dsf = ".DS_Store" in d
        # print(f"DS_Store found {dsf}")
            fz = os.listdir(os.path.join("/Users/michael/printerr/imgs", d))
            sz = len(fz)
            l.append(sz)
            print(f"error type: {d} count: {sz}")
    print("----------------")
    print(f"total images in dataset: {sum(l)}")


""" resize all images to 128 by 128 """
def resizeImgs(newSize=500):
    count = 0
    for di in tqdm(os.listdir(IMG_DIR)):
        if not os.path.exists(os.path.join(RESIZE_DIR, di)):
            os.mkdir(os.path.join(RESIZE_DIR, di))
        for img in os.listdir(os.path.join(IMG_DIR, di)):
            im = Image.open(os.path.join(IMG_DIR, di, img))
            sz = (newSize, newSize)
            imsz = im.resize(sz)
            imsz.save(os.path.join(RESIZE_DIR, di, img))
            count +=1 
    print(count)
    print("done resizing")


""" create a single directory of images from subfolders """
def makeFlatImgdir(srcdir, dstdir):
    allFiles = []
    allFileSet = set()
    fls = os.listdir(srcdir)
    fls.remove(".DS_Store")
    for d in fls:
        print(f"d {d}")
        for f in os.listdir(os.path.join(srcdir, d)):
            print(f"f {f}")
            allFiles.append(f)
            allFileSet.add(f)
            src = os.path.join(srcdir, d, f)
            dst = os.path.join(dstdir, f)
            print(f"src {src}")
            print(f"dst {dst}")
            shutil.move(src, dst)
    print(f"dest dir size {len(os.listdir(dstdir))}")
    print(f"{len(allFiles)}/{len(allFileSet)}")


""" return dictionary from the specified json file """
def loadJson(fname):
    with open(fname) as f:
        data = json.load(f)
    return data


""" given a list of dictionaries merge them into a single one"""
def mergeDicts(ldict):

    def removeNones(di):
        return {k: v for k, v in di.items() if v is not None}

    data = {}
    for d in ldict:
        data.update(removeNones(d))
    #print(f"len merged dict {len(data.items())}")
    p = [k for k, v in data.items() if v == "pass"]
    e = [k for k, v in data.items() if v == "edit"]
    t = [k for k, v in data.items() if v == "trash"]
    print(f"len pass/edit: {len(p) + len(e)} len trash: {len(t)}")
    return data


""" iterate over the json logs for each of the printer errors and place data into 
    pass, trash, and edit folders
"""
def organizeLogs(logDir):

    blob = []
    delam = []
    ovrex = []
    undrex = []
    strng = []
    warp = []
    wkinf = []
    ls = os.listdir(logDir)

    lcount = 0
    for l in ls:
        print(os.path.join(logDir, l))
        data = loadJson(os.path.join(logDir, l))
        lcount += 1
        if "blobbing" in l:
            print(f"l {l}")
            blob.append(data)
        elif "delamination" in l:
            print(f"l {l}")
            delam.append(data)
        elif "overextrusion" in l:
            print(f"l {l}")
            ovrex.append(data)
        elif "stringing" in l:
            print(f"l {l}")
            strng.append(data)
        elif "underextrusion" in l:
            print(f"l {l}")
            undrex.append(data)
        elif "warping" in l:
            print(f"l {l}")
            warp.append(data)
        elif "weak_infill" in l:
            print(f"l {l}")
            wkinf.append(data)
    print(f"done, lcount={lcount}")

    # return merged dicts
    merged = []
    for x in (blob, delam, ovrex, undrex, strng, warp, wkinf):
        merged.append(mergeDicts(x))
    print(sum([len(x.items()) for x in merged]))
    return merged


""" given a list of dictionaries of image names : labels
    move each image in the dictionary to the appropriate folder based on label
"""
def mvImagesToFiltered(ldicts):
    FLAT_DIR = os.path.join(os.getcwd(), "imgsResizedF2")
    FILTER_DIR = os.path.join(os.getcwd(), "filtered")
    tmoved = 0
    emoved = 0
    pmoved = 0
    dne = 0
    dnes = []
    for l in ldicts:
        for k, v in l.items():
            src = os.path.join(FLAT_DIR, k)
            dst = os.path.join(FILTER_DIR, v, k)
            print(f"src {src}")
            print(f"dst {dst}")
            #if not os.path.exists(dst):
            if os.path.exists(src):
                shutil.copyfile(src, dst)
                if "pass" in dst:
                    pmoved += 1
                elif "trash" in dst:
                    tmoved += 1
                elif "edit" in dst:
                    emoved += 1
            else:
                dnes.append(src)
                dne += 1
    print(f"moved pass {pmoved} edit {emoved} trash {tmoved} imgs")
    print(f"dne {dne}")
    return dnes


""" read keyboard input for image label 
s for stringing
p for warping/cracking/layer separation
b for bad extrusion

label based on most prominent error
"""
def getLabel(img):
    label = input(f"label for {img}: ")
    if label == "s":
        return "stringing"
    elif label == "p":
        return "warping"
    elif label == "b":
        return "extrusion"
    else:
        print("bad label")


""" get the label counts for each of the classes studied 
classes:
    - warping, cracking, peeling
    - stringing
    - bad extrusion / over / under
"""
def getLabelCounts():
    stringing = 0
    warping = 0
    extrusion = 0
    with open(os.path.join(os.getcwd(), "labels.txt")) as f:
        for line in f:
            if "stringing" in line:
                stringing += 1
            elif "warping" in line:
                warping += 1
            elif "extrusion" in line:
                extrusion += 1
    sm = stringing + warping + extrusion
    print(f"counts: stringing - {round(stringing/sm, 2)*100}% \n warping - {round(warping/sm, 2)*100}% \n extrusion - {round(extrusion/sm, 2)*100}%")


def viewImages(imdir):
    #labels = []
    lcount = 0
    imgs = os.listdir(imdir)
    leftOff = imgs.index('6e7d54e4a8037f18.png')
    #'df288c28c47724bb.png')
    #'d1e915f753729925.png')
    #print(f"index of left off: {leftOff}")
    for i in imgs[leftOff:]:
        img = os.path.join(imdir, i)
        #with Image.open(img) as im:
        im = Image.open(img)
        im.show()
        with open(os.path.join("labels.txt"), 'a') as f:
            imtitle = img.split("/")[-1]
            label = getLabel(imtitle)
            f.write(f"{imtitle}, {label}\n")
            lcount += 1
        im.close()
    print(f"len labels {lcount}")
    print(f"len imgs {len(imgs)}")


# driver
if __name__ == "__main__":
    data = collectUrls()
    main(data)
    dataSummary()

