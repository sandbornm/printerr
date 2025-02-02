import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json


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
        opts = Options()
        opts.headless = True
        browser = webdriver.Chrome(executable_path=os.path.join(os.getcwd(),"./chromedriver"), options=opts)
        self.browser=browser
                
    def writeData(self):
        metaData = {k : list(v) for k, v in self.metaData.items()}
        with open(self.log, 'w') as f:
            f.write(json.dumps(metaData))

    """ the main scraping entry point """
    def scrape(self, imgsPerTerm=400):
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
            # with open(self.log, 'w') as f:
            #     f.write(term + "\n")

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
        # done, now store the image data to download images
        print("scraping complete")

# driver
if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape()
    scraper.writeData()
    print("done")
