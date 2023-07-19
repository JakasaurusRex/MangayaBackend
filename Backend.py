import asyncio
from pyppeteer import launch
from bs4 import BeautifulSoup
import json
from json import JSONEncoder

class manga:
    def __init__(self, name, link, completionStatus, imageLink, genreList):
        self.name = name
        self.link = link
        self.completionStatus = completionStatus
        self.imageLink = imageLink
        self.genreList = genreList

class manga_encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

async def main():
    browser = await launch(
        options={
            'headless': True,
        },
    )
    page = await browser.newPage()
    await page.goto('https://mangasee123.com/directory/')
    html = await page.content()
    await browser.close()
    return html

html_response = asyncio.get_event_loop().run_until_complete(main())

soup = BeautifulSoup(html_response, "html.parser")
souper = soup.find_all("a", class_="ttip ng-binding")
souped = soup.prettify()

manga_list = list()

i = 0
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

    man = manga(name, link, status, img_link, genre_list)
    manga_list.append(man)

json_text = json.dumps(manga_list, indent=4, cls=manga_encoder)
with open('json_data.json', 'w') as outfile:
    outfile.write(json_text)

#text_file = open("sample.json", "wb")
#n = text_file.write(souped.encode('utf-8'))
#text_file.close()