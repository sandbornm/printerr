import os
import json
from threading import Thread
from tqdm import tqdm
import requests
import io
from PIL import Image
import hashlib
import time

import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

#TERMS = ["stringing", "overextrusion", "underextrusion", "weak infill"]
TERMS = ["blobbing", "delamination", "warping"]
RUN_DIR = os.path.join(os.getcwd(), "runs")
runs = sorted(os.listdir(RUN_DIR))
START_TIME = default_timer

IMG_DIR = os.path.join(os.getcwd(),"imgs")


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


def fetchLog(fname):
    pass

def dataSummary():
    l = []
    ds = os.listdir("/Users/michael/printerr/imgs")
    for d in ds:
        sz = len(os.listdir(os.path.join("/Users/michael/printerr/imgs", d)))
        l.append(sz)
        print(f"error type: {d} count: {sz}")
    print("----------------")
    print(f"total images in dataset: {sum(l)}")


# driver
# data = collectUrls()
# main(data)
dataSummary()

