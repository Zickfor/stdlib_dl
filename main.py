import os

import pdfkit
import requests
from bs4 import BeautifulSoup
import re
import toml


def save_img(url, isbn, chapter):
    img_req = requests.get(url)
    os.makedirs(f"books/ISBN{isbn}/imgs", exist_ok=True)
    # img_name = re.search(r"pic_(\d*)\.(\w*)", url).group()
    pat = r"gd-image\(doc,ISBN" + isbn + "-" + chapter + r",(.*),-1,,00000000,\)"
    img_name = re.findall(pat, url)[0]
    with open(f"books/ISBN{isbn}/imgs/{img_name}", "wb") as file:
        file.write(img_req.content)
        file.close()
    return f"imgs/{img_name}"


def page_processor(isbn, chapter, page):
    r = requests.get(
        f"https://www.studentlibrary.ru/cgi-bin/mb4x?AJAX=1&usr_data=htmswap(swap-tab,{int(page)},{int(page)},{page},doc,ISBN{isbn}-{chapter},{page},p0:0,p1:0,)")
    soup = BeautifulSoup(r.content, 'html.parser')
    soup.find(id=f"bmark-tb-ISBN{isbn}-{chapter}-{page}").decompose()
    for img_tag in soup.find_all("img"):
        img_tag["src"] = save_img(img_tag["src"], isbn, chapter)
    return str(soup)


def extract_chapters_from_book(isbn):
    r = requests.get(f"https://www.studentlibrary.ru/ru/book/ISBN{isbn}.html?SSr={config["auth"]["SSr"]}")
    chapters = re.findall(rf'<div class="bTCont-row-doc" id="bTCont-ISBN{isbn}-(\d*)">', r.text)
    return chapters


def extract_pages_from_chapter(isbn, chapter):
    r = requests.get(f"https://www.studentlibrary.ru/ru/doc/ISBN{isbn}-{chapter}.html?SSr={config["auth"]["SSr"]}")
    chapters = re.findall(r'<div id="swx-(\d*)">', r.text)
    return chapters


def get_chapter_title(isbn, chapter):
    r = requests.get(f"https://www.studentlibrary.ru/ru/doc/ISBN{isbn}-{chapter}.html?SSr={config["auth"]["SSr"]}")
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup.title.text


def create_cover(isbn):
    r = requests.get(f"https://www.studentlibrary.ru/ru/book/ISBN{isbn}.html")
    soup = BeautifulSoup(r.content, 'html.parser')

    author = soup.find("div", {"class": "b_s_author"}).findChild("span", {"class": "value"}).string
    publisher = soup.find("div", {"class": "b_s_publishing"}).findChild("span", {"class": "value"}).string
    year = soup.find("div", {"class": "b_s_type_year"}).findChild("span", {"class": "value"}).string
    name = soup.find("div", {"class": "book_sticker_book_coll"}).findChild("h2").string

    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
    <br><br><br><br><br><br><br><br><br><br><br><br><br><br>
    <h1>""" + name + """</h1>
    <i>""" + author + """</i>
    <p>""" + publisher + """ """ + year + """</p>
    <p>ISBN: """ + isbn + """</p>
    </body>
    </html>"""
    with open(f"books/ISBN{isbn}/cover.html", "w", encoding="utf-8") as file:
        file.write(html)
        file.close()


def main(isbn):
    chapter_files = list()
    os.makedirs(f"books/ISBN{isbn}/", exist_ok=True)
    print(extract_chapters_from_book(isbn))
    for chapter in extract_chapters_from_book(isbn):
        title = get_chapter_title(isbn, chapter)
        content = ""
        print(extract_pages_from_chapter(isbn, chapter))
        for page in extract_pages_from_chapter(isbn, chapter):
            print(f"processing ISBN{isbn}-{chapter}-{page}")
            content += page_processor(isbn, chapter, page)
        content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>""" + title + """</title>
</head>
<body>
<h1>""" + title + """</h1>
""" + content + """
</body>
<style>table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}</style>
</html>"""
        with open(f"books/ISBN{isbn}/{chapter}.html", "w", encoding="utf-8") as file:
            print(file.name)
            chapter_files.append(file.name)
            file.write(content)
            file.close()
    create_cover(isbn)
    pdfkit.from_file(chapter_files, f"books/ISBN{isbn}/ISBN{isbn}.pdf",
                     options={"enable-local-file-access": "",
                              "image-dpi": "1200",
                              "image-quality": "100",
                              "page-size": "A5",
                              "header-line": "",
                              "footer-line": "",
                              "footer-right": "[page]",
                              "header-left": "[subsection]",
                              "enable-toc-back-links": ""},
                     toc={"toc-header-text": "СОДЕРЖАНИЕ"}, cover=f"books/ISBN{isbn}/cover.html", cover_first=True)


if __name__ == "__main__":
    if not os.path.exists("config.toml"):
        print("It seems to be a first start... So, please, edit config.toml file.")
        example_config = {
            "auth": {
                "SSr": "Put SSr here",
            },
            "ISBNs": [
                "9785970470145",
                "9785970474815",
            ]
        }
        with open("config.toml", "w") as f:
            toml.dump(example_config, f)
            f.close()
        exit(0)
    else:
        with open("config.toml", "r") as f:
            config = toml.load(f)
            f.close()

    for ISBN in config["ISBNs"]:
        print(f"WORKING ON {ISBN}")
        main(ISBN)
