import urllib.request

pdf_path = ""


def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()


download_file('http://cdn.staatsbladmonitor.be/2021pdf/2021-10900345.pdf', "jaarrekening")