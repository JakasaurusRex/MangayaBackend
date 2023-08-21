import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import json
import requests
from json import JSONEncoder
import xml.etree.ElementTree as ET
import time

class manga:
    def __init__(self, name, link, completionStatus, imageLink, genreList, series):
        self.name = name
        self.link = link
        self.rss = link[:24] + "rss" + link[29:] + ".xml"
        self.completionStatus = completionStatus
        self.imageLink = imageLink
        self.genreList = genreList
        self.series = series

class series:
    def __init__(self, name, author, alternate_names, genres, type, image_url, released, desc, chapter_list, link):
        self.name = name
        self.author = author
        self.alternate_names = alternate_names
        self.genres = genres
        self.type = type
        self.image_url = image_url
        self.released = released
        self.desc = desc
        self.chapter_list = chapter_list
        self.manga = link
        self.rss = link[:24] + "rss" + link[29:] + ".xml"

class chapter:
    def __init__(self, chapter_num, chapter_link, release_date):
        self.chapter_num = chapter_num
        self.chapter_link = chapter_link
        self.release_date = release_date


class manga_encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

class series_encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
        
class chapter_encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

async def get_html(url):
    browser = await launch(
        options={
            'headless': True,
        },
    )
    page = await browser.newPage()
    await page.goto(url)
    html = await page.content()
    await browser.close()
    return html

def get_directory():
    html_response = asyncio.get_event_loop().run_until_complete(get_html('https://mangasee123.com/directory/'))

    soup = BeautifulSoup(html_response, "html.parser")
    souper = soup.find_all("a", class_="ttip ng-binding")
    souped = soup.prettify()

    manga_list = list()

    i = 0

    counter = 1
    total = len(souper)
    start = time.time()

    for result in souper:
        link = "https://mangasee123.com" + result["href"]

        megaString = result["title"]
        
        megaString = megaString[megaString.index("src=") + 5:len(megaString)]
        img_link = megaString[0:megaString.index("\'")]
        
        if(i == 0):
            print(megaString)
            i = 1

        status = "Completed"
        if(megaString.find("Ongoing&") >= 0):
            status = "Ongoing"

        genre_list = list()
        genre_string = megaString[megaString.index("Genre") + 11:len(megaString)] 
        genre = ""
        for i in range(len(genre_string)):
            if(genre_string[i] == "&"):
                break
            if(genre_string[i] == ","):
                genre_list.append(genre)
                genre = ""
                i += 1
                continue
            genre += genre_string[i]
        
        name = result.string

        rss = link[:24] + "rss" + link[29:] + ".xml"

        print(f"On manga {name} which is {counter}/{total} at {time.time()-start} seconds")
        counter += 1

        ser = load_series(link, rss)

        man = manga(name, link, status, img_link, genre_list, ser)
        manga_list.append(man)

    end = time.time()
    print(f"Got all manga, took {end-start} seconds")

    json_text = json.dumps(manga_list, indent=4, cls=manga_encoder)
    with open('json_data.json', 'w') as outfile:
        outfile.write(json_text)

def load_chapter(url):
    html_response = asyncio.get_event_loop().run_until_complete(get_html(url))

    soup = BeautifulSoup(html_response, "html.parser")
    souped = soup.prettify()
    souper = soup.find_all("img", class_="img-fluid")

    results = list()

    for result in souper:
        results.append(result)

    return results 

def load_series(url, rss):
    html_response = asyncio.get_event_loop().run_until_complete(get_html(url))

    soup = BeautifulSoup(html_response, "html.parser")
    souped = soup.prettify()
    
    souper = soup.find_all("li", class_="list-group-item d-none d-sm-block")
    title = souper[0].text.strip()

    

    souper = soup.find_all("li", class_="list-group-item d-none d-md-block")

    counter = 0

    alternate_names = list()

    if(souper[counter].find("span").text.strip() == "Alternate Name(s):"):
        for child in souper[counter].findChildren("a"):
            alternate_names.append(child.text.strip())
        counter += 1

    author = souper[counter].findChild("a").text.strip()
    counter += 1

    genres = list()

    for child in souper[counter].findChildren("a"):
        genres.append(child.text.strip())

    counter += 1

    type = souper[counter].findChild("a").text.strip()
    counter += 1
    
    released = souper[counter].findChild("a").text.strip()
    counter += 1

    if(souper[counter].find("span").text.strip() == "Official Translation:"):
        counter+=1

    status = list()
    for child in souper[counter].findChildren("a"):
        status.append(child.text.strip())

    counter += 2

    desc = souper[counter].findChild("div").text.strip()

    response = requests.get(rss)   

    # Parse the XML file
    root = ET.fromstring(response.content)

    root = root[0]

    image_link = ""

    chapter_list = list()

    for child in root:
        if(child.tag == "image"):
            image_link = child[0].text
        elif(child.tag == "item"):
            chapter_num = child[0].text[child[0].text.find("Chapter"):]
            chapter_link = child[1].text
            release_date = child[2].text[:11]

            cha = chapter(chapter_num, chapter_link, release_date)
            chapter_list.append(cha)

    ser = series(title, author, alternate_names, genres, type, image_link, released, desc, chapter_list, url)

    return ser
    #json_text = json.dumps(ser, indent=4, cls=series_encoder)
    #with open('series_data.json', 'w') as outfile:
    #    outfile.write(json_text)



def main():
    get_directory()
    #load_chapter('https://mangasee123.com/read-online/Kanojo-Okarishimasu-chapter-291.html')
    #load_series("https://mangasee123.com/manga/JoJos-Bizarre-Adventure-Part-9-The-JOJOLands", 'https://mangasee123.com/rss/JoJos-Bizarre-Adventure-Part-9-The-JOJOLands.xml')

main()
#text_file = open("sample.json", "wb")
#n = text_file.write(souped.encode('utf-8'))
#text_file.close()


#if(series):
#        await page.content()
#        if(await page.querySelector("div.list-group-item.ShowAllChapters.ng-scope") != None):
#            await page.click("div.list-group-item.ShowAllChapters.ng-scope")
