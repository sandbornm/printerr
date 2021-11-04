
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import requests
from PIL import Image
import hashlib
import io
from tqdm import tqdm


"""
The main object for collecting images from the web.
"""
class Scraper():
    def __init__(self):
        self.loadTerms()
        self.getBrowser()
        self.log = os.path.join(os.getcwd(), "track.txt")
        self.metaData = {t: set() for t in self.terms}
        print("Scraper initialized")

    def loadTerms(self):
        with open(os.path.join(os.getcwd(),"terms.txt")) as f:
            self.terms = f.read().splitlines()

    def getBrowser(self):
        # Driver Code
        opts = Options()
        opts.headless = True
        browser = webdriver.Chrome(executable_path=os.path.join(os.getcwd(),"./chromedriver"), options=opts)
        self.browser=browser

    def saveImgs(self, imgDir=os.path.join(os.getcwd(),"img")):
        # create directories for each search term
        # todo maybe do this with the log text file instead
        for term in tqdm(self.terms):
            print("saving images")
            drnm = term.replace(" ", "_")
            if drnm not in os.listdir(imgDir):
                os.mkdir(os.path.join(imgDir, drnm))
        
            urls = list(self.metaData[term])

            for url in urls:
        
                try:
                    imgData = requests.get(url).content
                except Exception as e:
                    print(f"error downloading image at {url}")

                try:
                    imgFile = io.BytesIO(imgData)
                    img = Image.open(imgFile).convert("RGB")
                    fpath = os.path.join(imgDir, drnm, hashlib.sha1(imgData).hexdigest()[:10] + ".jpg")
                    with open(fpath, 'wb') as f:
                        img.save(f, "JPEG", quality=85)
                    print(f"img at {url} saved as {fpath}")
                except Exception as e:
                    print(f"Exception {e} while saving image at {url}")
                
    def writeUrl(self, url):
        with open(self.log) as f:
            f.write(url + "\n")

    """ the main scraping entry point """
    def scrape(self, imgsPerTerm=10):
        br = self.browser
        terms = self.terms
        def bottomScroll():
            br.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

        # image search url
        url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
        for term in terms:
            rstart = 0 # track position of results for current term
            print(f"current search term is \'{term}\'")
            qterm = term.replace(" ", "+")
            br.get(url.format(q=qterm))

            # update log with current term
            with open(self.log, 'w') as f:
                f.write(term + "\n")

            while len(self.metaData[term]) < imgsPerTerm:
                bottomScroll()

                res = br.find_elements_by_css_selector("img.Q4LuWd")
                print(f"found {len(res)} results")
                print(f"len(res): {len(res)}")
                print(f"rstart: {rstart}")
                for img in res[rstart:len(res)]:
                    try:
                        img.click() # get img
                        time.sleep(1)
                        # add image url to term database
                        self.metaData[term].add(br.current_url)
                        rstart = len(res)
                    except Exception as e:
                        print(e)
                        pass

                    # get image urls
                    imgs = br.find_elements_by_css_selector("img.n3VNCb")
                    for im in imgs:
                        if im.get_attribute("src") and 'http' in im.get_attribute("src"):
                            self.metaData[term].add(im.get_attribute("src"))
                    
                    if len(self.metaData[term]) >= imgsPerTerm:
                        print("found enough for this term")
                        break
                    else:
                        diff = imgsPerTerm - len(self.metaData[term])
                        print(f"fetching {diff} more images...")
                        time.sleep(2)
                        loadMore = br.find_element_by_css_selector(".mye4qd")
                        if loadMore:
                            br.execute_script("document.querySelector('.mye4qd').click();")

                    #rstart = len(res)
        # done, now store the images we found
        self.saveImgs()



# Driver
if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape()
