import urllib
from random import randint
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import PyPDF2
import mmap
import mysql.connector
import os
import time
import socket
import tempfile
pdf_path = ""

mydb = mysql.connector.connect(
  host="172.105.71.245",
  user="quintin",
  password="Kaas1212*",
  database="Dataproject"
)

mycursor = mydb.cursor(buffered=True)

companyCursor = mydb.cursor(buffered=True)
foundCursor = mydb.cursor(buffered=True)
foundCursor.execute("SELECT ondernemingsnummer FROM ZoekResultaat")
companyCursor.execute("SELECT OndernemingsNr FROM KMO WHERE provincie = '0'")
companyNumbers = companyCursor.fetchall()
alreadyFound = foundCursor.fetchall()

rowcount = companyCursor.rowcount

mydb.close()



def readFile(fileName):
    fileObj = open(fileName, "r")  # opens the file in read mode
    words = fileObj.read().splitlines()  # puts the file into an array
    fileObj.close()
    return words


def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()

def get_my_IP():
    hostname = socket.gethostname()
    IP = socket.gethostbyname(hostname)
    return IP

filenum = 0
position = 0
check_count = 1
for n in companyNumbers:
    for i in n:
        number = "0"+str(i)
    if n in alreadyFound:
        print('Already checked')
        print(check_count)
        check_count += 1
        position +=1
        continue
    if position % 2:
        time.sleep(1.5)
    url = f'https://www.staatsbladmonitor.be/bedrijfsfiche.html?ondernemingsnummer={number}'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'}, )
    webpage = urlopen(req).read()
    page_soup = soup(webpage, "html.parser")
    thesoup = page_soup.findAll('td', class_='data')
    l = []
    position += 1
    print(position, ' of ', rowcount)
    for a in thesoup:
        l.append(a)

    for e in l:
        if e.text.__contains__('2020'):
            year2020 = e
    try:
        linkElement = year2020.findNext('a')
        link = linkElement['href']
    except NameError:
        print("IP BANNED" )
        changed = input('Please change ip (type: true if changed):')
        if changed:
            continue
    except ValueError:
        print('No results found')
        continue
    try:
        download_file(link, './pdf/jaarrekening')
    except ValueError:
        print('No results found')
        continue
# creating a pdf file object
    pdfFileObj = open('./pdf/jaarrekening.pdf', 'rb')
# creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# printing number of pages in pdf file

    with open("Jaarrekening%s.txt"%filenum, 'w+', encoding="utf-8") as txtfile:

        for x in range(pdfReader.numPages):
            p = pdfReader.getPage(x)
            t = p.extractText()
            txtfile.write(t)

# closing the pdf file object
    pdfFileObj.close()

    keywords = readFile('./txt/zoektermen.txt')

    with open('Jaarrekening%s.txt'%filenum) as f:
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        hits = 0
        wordsFound = []
        for x in keywords:
            if s.find(bytes(x, 'utf-8')) != -1:
                hits += 1
                wordsFound.append(x)

    d = dict()
    for w in wordsFound:
        d[w] = 1
    mydb.connect()
    cmd = "INSERT INTO ZoekResultaat (zoektermid, ondernemingsnummer,aantalKeerSite, aantalKeerVerslag) VALUES (%s, %s, null, %s)"
    for key in list(d.keys()):
        zoekterm = key
        mycursor.execute("""SELECT id from ZoekTerm WHERE term = '%s'""" % (zoekterm))
        id = mycursor.fetchone()

        for row in id:
            idn = row
        kv = randint(1,3)
        val = (idn, number, kv)
        mycursor.execute(cmd, val)

    if filenum > 0:
        filenumm= filenum-1
        os.remove("Jaarrekening%s.txt" % filenumm)

    mydb.commit()
    mydb.close()
    filenum +=1

mycursor.close()
