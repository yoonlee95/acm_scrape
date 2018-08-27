from selenium import webdriver
from bs4 import BeautifulSoup
import json
import os
import urllib
import threading

def download_file(path, download_url):
    web_file = urllib.urlopen(download_url)
    local_file = open(path +'/paper.pdf', 'w')
    local_file.write(web_file.read())
    web_file.close()
    local_file.close()

def init_webdriver():
  options = webdriver.ChromeOptions()
  options.add_argument('headless')
  options.add_argument('--ignore-certificate-errors')

  driver = webdriver.Chrome(chrome_options=options)
  return driver

def get_abstract(soup):
    abstract_text = soup.find("div", id="abstract")
    if abstract_text is not None:
        return abstract_text.getText()
    else:
        return ""
def get_bibilometers(soup):
    bibilometers = {}

    bibilometer_box = soup.find("div", id="divmain").find("td", class_="small-text")
    bibilometer_lines = bibilometer_box.getText().split("\n")
    bibilometers["CitationCount"] = int(bibilometer_lines[1].split(":")[1].replace(',',''))
    bibilometers["Downloads_cumulative"] = int(bibilometer_lines[2].split(":")[1].replace(',',''))
    bibilometers["Downloads_12Months"] = int(bibilometer_lines[3].split(":")[1].replace(',',''))
    bibilometers["Downloads_6Weeks"] = int(bibilometer_lines[4].split(":")[1].replace(',',''))
    return bibilometers

def get_authors(soup):
    authors = []

    author_names = soup.find("div", id="divmain").find_all("a", title="Author Profile Page")
    for author_tag in author_names:
        author = {}
        author["Name"] = author_tag.string.strip()
        author["Affiliation"] = author_tag.parent.next_sibling.next_sibling.find("small").string.strip()
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
    return int(year_tag.getText().split(" ")[0])

def get_title(soup):
    title_tag = soup.find("div", id="divmain").find("div").find("h1")
    return title_tag.string.strip()

def get_article_detail(driver, html):
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
  #   download_file("output/"+folder_name,)

  if not os.path.exists("output/"+folder_name):
      os.makedirs("output/"+folder_name)
  with open("output/"+folder_name+'/detail.json', 'w') as outfile:
      json.dump(detail, outfile, indent=4)

article_list = {}
article_list_file_name = 'isca.json'
with open(article_list_file_name, 'r') as f:
    article_list = json.load(f)

Driver = init_webdriver()

for conf, articles in article_list.iteritems():
    print conf
    for article in articles:
        get_article_detail(Driver, article)