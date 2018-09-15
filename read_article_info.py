from selenium import webdriver
from bs4 import BeautifulSoup
import json
import os
import urllib
import threading
import re

def download_file(path, download_url):

    download_dir = path
    options = webdriver.ChromeOptions()
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')


    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-setuid-sandbox')
    #options.add_argument('--disable-dev-shm-usage')
    #options.add_argument('--ignore-certificate-errors')
    # profile = {"plugins.always_open_pdf_externally": True}
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer
               "download.default_directory": download_dir , "download.extensions_to_open": "applications/pdf"}  

    print download_dir
    options.add_experimental_option("prefs", profile)
    driver = webdriver.Chrome(chrome_options=options)  # Optional argument, if not specified will search path.
    driver.get("https://dl.acm.org/"+download_url)

    for file in os.listdir(path):
        if file.endswith(".pdf"):
            #print file
            os.rename(os.path.join(path, file), path+"/paper.pdf")



    # web_file = urllib.urlopen("https://dl.acm.org/"+download_url)
    # local_file = open(path +'/paper.pdf', 'w')
    # local_file.write(web_file.read())
    # web_file.close()
    # local_file.close()

def init_webdriver():
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('--ignore-certificate-errors')

  driver = webdriver.Chrome(chrome_options=options)
  return driver

def get_abstract(soup):
    l = soup.find_all("div", style="display:inline")
    #print l[0].text
    #abstract_text = soup.find("div", id="abstract")
    try:
        abstract_text =  l[0].text
        if abstract_text is not None:
            return abstract_text.strip()
            #return abstract_text.getText().e
        else:
            print "failed to extract abstract ---->", soup.find("div", id="divmain").find("div").find("h1")
            return ""
    except:
        return ""
def get_bibilometers(soup):
    bibilometers = {}

    bibilometer_box = soup.find("div", id="divmain").find("td", class_="small-text")
    bibilometer_lines = bibilometer_box.getText().split("\n")
    bibilometer_lines = [x for x in bibilometer_lines if len(x) > 3]
   
    try: 
        bibilometers["CitationCount"] = int(bibilometer_lines[0].split(":")[1].replace(',',''))
    except:
        bibilometers["CitationCount"] = 0
    try: 
    	bibilometers["Downloads_cumulative"] = int(bibilometer_lines[1].split(":")[1].replace(',',''))
    except:
    	bibilometers["Downloads_cumulative"] = 0
    try:
        bibilometers["Downloads_12Months"] = int(bibilometer_lines[2].split(":")[1].replace(',',''))
    except:
        bibilometers["Downloads_12Months"] = 0
    try:
        bibilometers["Downloads_6Weeks"] = int(bibilometer_lines[3].split(":")[1].replace(',',''))
    except:
        bibilometers["Downloads_6Weeks"] = 0

    return bibilometers

def get_authors(soup):
    authors = []

    author_names = soup.find("div", id="divmain").find_all("a", title="Author Profile Page")
    for author_tag in author_names:
        author = {}
        author["Name"] = author_tag.string.strip()
	
	try:
            author["Affiliation"] = author_tag.parent.next_sibling.next_sibling.find("small").string.strip()
	except:
	    author["Affiliation"] = ""
        authors.append(author)

    return authors

def get_references(soup):
    references = []
    reference_box = soup.find("div", id="fback") \
                        .find("a",  attrs={'name':"references", 'class': 'small-text'}) \
                        .parent.next_sibling.next_sibling
    references_list = reference_box.find_all("tr")
    for reference in references_list:
        reference_dict = {}
        r_box =  reference.find_all("td")[2]
        r_box_a =  r_box.find_all("a")
        r_box_a_len = len(r_box_a)
        if r_box_a_len == 0:
            reference_dict["ArticleName"] = r_box.getText().strip()
        elif r_box_a_len == 1:
            baseaddress = "http://dl.acm.org/"
            reference_dict["ArticleName"] = r_box_a[0].getText().strip()
            reference_dict["ArticleHref"] = baseaddress + r_box_a[0]["href"]
        else:
            baseaddress = "http://dl.acm.org/"
            reference_dict["ArticleName"] = r_box_a[0].getText().strip()
            reference_dict["ArticleHref"] = baseaddress + r_box_a[0]["href"]
            reference_dict["DOIname"] = r_box_a[1].getText().strip()
            reference_dict["DOIhref"] = r_box_a[1]["href"]
        references.append(reference_dict)
    return references

def get_cited_by(soup):
    references = []
    reference_box = soup.find("div", id="fback") \
                        .find("a",  attrs={'name':"citedby", 'class': 'small-text'}) \
                        .parent.next_sibling.next_sibling
    references_list = reference_box.find_all("tr")
    for reference in references_list:
        reference_dict = {}
        r_box_a =  reference.find("a")
        baseaddress = "http://dl.acm.org/"
        reference_dict["ArticleName"] = r_box_a.getText().strip()
        reference_dict["ArticleHref"] = baseaddress + r_box_a["href"]
        references.append(reference_dict)
    return references

def get_published_year(soup):
    year_tag = soup.find("div", id="divmain").find("td", class_="small-text").parent.parent.parent.find_all("td")[1]
    #print year_tag
    y = re.sub('[^0-9]','', year_tag.getText())
    #return int(year_tag.getText().split(" ")[1])
    return int(y)
    

def get_title(soup):
    title_tag = soup.find("div", id="divmain").find("div").find("h1").text.encode('utf-8')
    print soup.find("div", id="divmain").find("div").find("h1").text.encode('utf-8')
    if title_tag is not None:
        #return title_tag.string.strip()
        return title_tag
    else:
         print "failed to extract title ---->", soup.find("div", id="divmain").find("div").find("h1")
def get_pdf_link(soup):
    links = soup.find("div", id="divmain").find_all("a", title="FullText PDF")
    if(len(links) == 1):
        #print links[0]['href']
        return links[0]['href']
    return None
def get_article_detail(driver, html, output):
  detail = {}

  print "https://dl.acm.org/"+html+"&preflayout=flat"
  driver.get("https://dl.acm.org/"+html+"&preflayout=flat")
  driver.implicitly_wait(1)
  soup = BeautifulSoup(driver.page_source, 'html.parser')

  detail["Link"] = "https://dl.acm.org/"+html+"&preflayout=flat"
  detail["Abstract"] = get_abstract(soup)
  detail["Bibilometrics"] = get_bibilometers(soup)
  detail["Authors"] = get_authors(soup)
  detail["References"] = get_references(soup)
  detail["Published"] = get_published_year(soup)
  detail["Title"] = get_title(soup)
  detail["Citedpaper"] = get_cited_by(soup)


  folder_name = html.split("cfm?id=")[1].strip()


  if not os.path.exists(output+folder_name):
      os.makedirs(output+folder_name)
  with open(output+folder_name+'/detail.json', 'w') as outfile:
      json.dump(detail, outfile, indent=4)

  # download pdf
  link =get_pdf_link(soup)
  if link != None:
    download_file("output/"+folder_name, link)

article_list = {}
article_list_file_name = 'isca.json'
with open(article_list_file_name, 'r') as f:
    article_list = json.load(f)

Driver = init_webdriver()

for conf, articles in article_list.iteritems():
    print conf
    
    for article in articles:
        get_article_detail(Driver, article, "isca/")
