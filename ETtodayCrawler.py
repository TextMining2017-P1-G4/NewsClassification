# coding=utf-8

import os
import re
import itertools
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime


def get_catogories_map():
    
    catogories = {
        'politics': ['政治'],
        'finance': ['財經'],
        'entertainment': ['影劇'],
        'sports': ['體育'],
        'society': ['社會'],
        'local': ['地方'],
        'world': ['國際', '大陸'],
        'lifestyle': ['消費', '生活'],
        'health': ['健康'],
        'travel': ['旅遊'],
        'odd': ['新奇', '寵物'],
    }
    
    website = 'http://www.ettoday.net/news/news-list-2017-05-09-9.htm'
    r = requests.get(website)
    soup = BeautifulSoup(r.content, 'lxml')
    node = soup.select('div.part_menu_2')
    
    def parse_catogory_id(keyword):
        pat = re.compile(r'<li>.+{}.+</li>'.format(keyword))
        href, = pat.findall(str(node[0]))
        pat = re.compile(r'href="/news/news-list-2017-05-09-(.+).htm"')
        catogory_id, = pat.findall(href)
        return catogory_id
        
    def gen_catogories_id_map(iterable):
        for c, k in iterable:
            catogory_ids = list(map(parse_catogory_id, k))
            yield (c, catogory_ids)
        
    return dict(list(gen_catogories_id_map(catogories.items())))



def get_categories_news_href(catogories_map):
    
    def gen_traceback_date():
        date = datetime.datetime(2017, 5, 10)
        date_step = datetime.timedelta(days=1)
        while True:
            yield date.year, date.month, date.day
            date -= date_step
            
    
    def get_news_href(website):
        r = requests.get(website)
        soup = BeautifulSoup(r.content, 'lxml')
        node = soup.select('div.part_list_2')
        pat = re.compile(r'<h3>.+</h3>')
        news = pat.findall(str(node[0]))
        pat = re.compile(r'href="(.+?)"')
        hrefs = list(map(pat.findall, news))
        hrefs = list(itertools.chain.from_iterable(hrefs))
        return hrefs
    
    
    def get_category_news_href(category_ids):
        
        #N = 6000
        N = 100

        collected_hrefs = []
        next_date = gen_traceback_date()
        
        while len(collected_hrefs) < N:
            website_template = ('http://www.ettoday.net/news/news-list' + \
                                '-{}-{}-{}-{}.htm').format
            y, m, d = next(next_date)
            
            websites = [website_template(y, m, d, cid) for cid in category_ids]
            hrefs = [get_news_href(w) for w in websites]
            hrefs = list(itertools.chain.from_iterable(hrefs))
            collected_hrefs += hrefs
            collected_hrefs = list(set(collected_hrefs))
        
        return collected_hrefs
    
    return dict([(c, get_category_news_href(cids))
                 for c, cids in catogories_map.items()])



def parse_news(website):
    r = requests.get(website)
    soup = BeautifulSoup(r.content, 'lxml')
    #print(soup)
    
    title_node = soup.select('.title')
    #print(title_node)
    title_xml = str(title_node[0])
    title_soup = BeautifulSoup(title_xml, 'lxml')
    title = list(title_soup.stripped_strings)

    story_node = soup.select('div.story')
    pat = re.compile(r'<p>.+</p>')
    story_xmls = pat.findall(str(story_node[0]))
    story_xmls = list(filter(lambda t: 'iframe' not in t, story_xmls))
    story_xmls = list(filter(lambda t: u'記者' not in t, story_xmls))
    story_xmls = list(filter(lambda t: u'img' not in t, story_xmls))
    story_soup = BeautifulSoup(''.join(story_xmls), 'lxml')
    story = list(story_soup.stripped_strings)
    
    texts = title + story
    
    return texts



if __name__ == '__main__':
    
    import os
    import sys
    import getopt
    
    def usage():
        print('    Usage:')
        print('        -F    Folder name for creating folder to reposit news.')
        print('        -N    Number of news for each catogory.')
    

    if len(sys.argv) <= 1:
        print('{} -h'.format(sys.argv[0]))
        usage()
        sys.exit(2)
        
    
    try:
        opt_list, args = getopt.getopt(sys.argv[1:], 'F:N:')
    except (getopt.GetoptError, msg):
        print('{} -h'.format(sys.argv[0]))
        usage()
        sys.exit(2)
        
        
    for o, a in opt_list:
        if o in ('-F'):
            train_data_folder = a
        if o in ('-N'):
            N = a

        
    print(N)
    catogories_map = get_catogories_map()
    catogories_news_hrefs_map = get_categories_news_href(catogories_map)
    
    os.system('mkdir {}'.format(train_data_folder))
    for cc, hrefs in catogories_news_hrefs_map.items():
        
        category_folder = os.path.join(train_data_folder, cc)
        os.system('mkdir {}'.format(category_folder))
        
        et_home = 'http://www.ettoday.net'
        websites = [urljoin(et_home, h) for h in hrefs]
        news_ids = [h.strip('.htm').split('/')[-1] for h in hrefs]
        
        for news_id, website in zip(news_ids, websites):
            try:
                news_text = '\n'.join(parse_news(website))
                filename = os.path.join(category_folder, news_id)
                with open(filename, 'w') as f:
                    f.write(news_text)
                    f.write('\n')
            except:
                print('{}-{}'.format(cc, news_id))