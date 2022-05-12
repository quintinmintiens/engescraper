import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import PyPDF2
import mmap
import mysql.connector
import os
pdf_path = ""

mydb = mysql.connector.connect(
  host="172.105.71.245",
  user="quintin",
  password="Kaas1212*",
  database="Dataproject"
)

mycursor = mydb.cursor(buffered=True)

companyCursor = mydb.cursor(buffered=True)
companyCursor.execute("SELECT OndernemingsNr FROM KMO")
companyNumbers = companyCursor.fetchall()
rowcount = companyCursor.rowcount





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



for n in companyNumbers:
    for i in n:
        number = "0"+str(i)

    print(number)
    url = f'https://www.staatsbladmonitor.be/bedrijfsfiche.html?ondernemingsnummer={number}'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    page_soup = soup(webpage, "html.parser")
    thesoup = page_soup.findAll('td', class_='data')
    l = []

    for a in thesoup:
        l.append(a)

    for e in l:
        if e.text.__contains__('2020'):
            year2020 = e
    try:
        linkElement = year2020.findNext('a')
        link = linkElement['href']
    except NameError:
        print("This company number doesn't exist")
        exit()

    print('Jaarrekening: ', link)
    download_file(link, './pdf/jaarrekening')
    print('File downloaded')
# creating a pdf file object
    pdfFileObj = open('./pdf/jaarrekening.pdf', 'rb')
# creating a pdf reader object
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# printing number of pages in pdf file
    print('Pages: ' + str(pdfReader.numPages))
    txtfile = open("Jaarrekening%s.txt"%number, 'w+', encoding="utf-8")

    for x in range(pdfReader.numPages):
        p = pdfReader.getPage(x)
        t = p.extractText()
        txtfile.write(t)
    txtfile.close()
# closing the pdf file object
    pdfFileObj.close()

    keywords = readFile('./txt/zoektermen.txt')

    with open('Jaarrekening%s.txt'%number)  as f:
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        hits = 0
        wordsFound = []
        for x in keywords:
            if s.find(bytes(x, 'utf-8')) != -1:
                hits += 1
                wordsFound.append(x)
    print('Number of keywords found:' + str(hits))
    print('Hits:')
# Open the file in read mode
    text = open("Jaarrekening%s.txt" %number, "r", encoding="utf-8")
# Create an empty dictionary
    d = dict()
    for w in wordsFound:
        d[w] = 0
# Loop through each line of the file
    for line in text:
    # Remove the leading spaces and newline character
        line = line.strip()
    # Convert the characters in line to
    # lowercase to avoid case mismatch
        line = line.lower()
    # Split the line into words
        words = line.split(" ")
    # Iterate over each word in line
        for word in words:
        # Check if the word is already in dictionary
            if word in d:
            # Increment count of word by 1
                d[word] = d[word] + 1
# Print the contents of dictionary

    cmd = "INSERT INTO ZoekResultaat (zoektermid, ondernemingsnummer,aantalKeerSite, aantalKeerVerslag) VALUES (%s, %s, null, %s)"
    for key in list(d.keys()):
        zoekterm = key
        mycursor.execute("""SELECT id from ZoekTerm WHERE term = '%s'""" % (zoekterm))
        id = mycursor.fetchone()
        kv = d[key]
        for row in id:
            idn = row
        if kv == 0:
            kv = 1
        val = (idn, number, kv)

        for row in id:
            print('id:', row)
        if d[key] != 0:
            print('term:', key, "\naantal:", d[key])
        else:
            d[key] = 1
            print('term:', key, "\naantal:", d[key])


        mycursor.execute(cmd, val)

    mydb.commit()
    txtfile.close()
    os.remove("Jaarrekening%s.txt" %number)
mycursor.close()
