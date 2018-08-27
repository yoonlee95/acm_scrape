from selenium import webdriver
from bs4 import BeautifulSoup
import json

conference_name = 'isca'

def init_webdriver():
  options = webdriver.ChromeOptions()
  options.add_argument('headless')
  options.add_argument('--ignore-certificate-errors')

  driver = webdriver.Chrome(chrome_options=options)
  return driver

def get_list_conf(html):
    conference_list_year = []
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        conf_info = {"name": link['title'], "link": link.get('href')}
        conference_list_year.append(conf_info)
    return conference_list_year

def get_article_links(driver, html):
  conf_article_links = []

  driver.get("https://dl.acm.org/"+html+"&preflayout=flat")
  driver.implicitly_wait(1)
  soup = BeautifulSoup(driver.page_source, 'html.parser')
  soup.find("table")

  for article_link in soup.find_all("tr"):
    if article_link.a != None:
      try:
        link = article_link.a["href"]
        if "citation.cfm?" in link and "&picked=prox" not in link:
          conf_article_links.append(link)
      except:
        pass
  return conf_article_links

conference_html = ""
with open(conference_name+"_acm_list.html", 'r') as myfile:
  conference_html = myfile.read()

Driver = init_webdriver()
conf_list_by_year = get_list_conf(conference_html)

article_links_by_year = {}
for conf in conf_list_by_year:
  print conf["name"]
  print conf["link"]
  article = get_article_links(Driver, conf["link"])
  article_links_by_year[conf["name"]] = article

with open(conference_name+'.json', 'w') as outfile:
    json.dump(article_links_by_year, outfile, indent=4)