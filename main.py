#!/usr/bin/env python3
from operator import itemgetter

__author__ = 'soon'

import sys
import urllib.request
from bs4 import BeautifulSoup
from bs4.element import Tag
from shutil import copyfile
import os
import asyncio

class Item:

    def __init__(self, soup):
        self._name = ''
        self._image = ''
        self._price = ''

        self.parse(soup)

    def parse(self, tag):
        """
        Parses Item from the following table (comments starts with # are not parts of table):

        <table class="li nol" itemscope="itemscope" itemtype="http://schema.org/Product">
            <tbody>
                <tr itemscope="itemscope" itemtype="http://schema.org/Offer" itemprop="offers">
                    <td class="pic lt" style="width:142px">
                        <a href="javascript:;" onclick="return toVI(event);" class="pic" _sp="p4634.c0.m14.l1262" r="1">

                            # This is the image of the item

                            <img itemprop="image" src="http://thumbs1.ebaystatic.com/m/mBo7aAX7xsNG4HflO4Yk89Q/140.jpg" alt="Zippo 207, Street Chrome Finish Lighter, Full Size">

                        </a>
                    </td>
                    <td class="details">
                        <div class="ttl">

                            # This is the name of the item

                            <a href="http://www.ebay.com/itm/Zippo-207-Street-Chrome-Finish-Lighter-Full-Size-/121382771024?pt=LH_DefaultDomain_0&amp;hash=item1c42fa1950" itemprop="name" title="Zippo 207, Street Chrome Finish Lighter, Full Size" class="v4lnk" _sp="p4634.c0.m14.l1262" r="1">
                                Zippo 207, Street Chrome Finish Lighter, Full Size
                            </a>

                        </div>
                        <div>
                        </div>
                        <div class="dynamic dynSgCol">
                            <div class="s1 emptyDiv">
                                <div class="mWSpc">
                                </div>
                                &nbsp;
                            </div>
                        </div>
                        <div class="anchors">
                            <div class="g-nav group">
                                <div class="mi-l">
                                    <div>
                                        <a class="pll ppr" id="v4-21" href="javascript:;" onmouseover="return gallery(event, {&quot;item&quot;:&quot;121382771024&quot;,&quot;offset&quot;:null,&quot;images&quot;:3,&quot;version&quot;:0,&quot;href&quot;:null});">
                                            Увеличить
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </td>
                    <td class="trs">
                    </td>
                    <td class="pay">
                    </td>
                    <td class="bids">
                        <img src="http://q.ebaystatic.com/aw/pics/ru/ru/bin_15x54.gif" alt="Купить сейчас" title="Купить сейчас">
                    </td>

                    # This is the price of the item

                    <td class="prices g-b" itemprop="price">
                        US $8,20
                    </td>

                    <td class="time  rt">
                        <b class="hidlb">Осталось времени:</b><span>26дн.&nbsp;12ч.&nbsp;34мин.</span>
                    </td>
                </tr>
            </tbody>
        </table>
        """
        assert isinstance(tag, Tag)

        self.name = tag.find('a', itemprop="name")
        self.image = tag.find('img', itemprop="image")
        self.price = tag.find('td', itemprop="price").text

    def to_html(self):
        """

        """
        item = BeautifulSoup()
        item = item.new_tag('div')
        item['class'] = 'item'

        item.append(self.image)
        item.append(self.name)
        item.append(self.price)

        return item

    #region Properties

    @property
    def name(self):
        """
        Returns <a> tag with name and link of the item
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def image(self):
        """
        Returns <img> tag with image of the item
        """
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def price(self):
        return self._price
        
    @price.setter
    def price(self, value):
        self._price = value 

    #endregion


def parse_from_url(url):
    page = urllib.request.urlopen(url)
    return BeautifulSoup(page.read())


def get_image_url_from_item_details_url(url):
    soup = parse_from_url(url)

    return soup.find(id='icImg')['src']


def get_items(soup):
    """
    Finds the following html (comments starts with # are not parts of html) in the soup and loads item from it:

    <div id="lvc" class="lview">
        <a name="item1c42fa1950"> </a>
        <table class="li nol" itemscope="itemscope" itemtype="http://schema.org/Product">

            # First item

        </table>
        <a name="item540cdd123b"> </a>
        <table class="li nol" itemscope="itemscope" itemtype="http://schema.org/Product">

            # Second item

        </table>

        # And so on...

    </div>

    :param soup:
    :return: Iterator of Items
    """
    assert isinstance(soup, BeautifulSoup)

    div_items = soup.find('div', id='lvc')

    return map(Item, div_items.find_all('table', class_="li nol"))


def create_css():

    soup = BeautifulSoup()

    css = soup.new_tag('style', type='text/css')
    css.append('''
     div.item {
        margin: 10px;
        padding: 10px;

        -webkit-transition: all 200ms linear;
        -o-transition: all 200ms linear;
        -moz-transition: all 200ms linear;
        -ms-transition: all 200ms linear;
        -kthtml-transition: all 200ms linear;
        transition: all 200ms linear;
     }

     div.item:hover {
        -webkit-box-shadow: 0px 0px 10px 10px #CCC;
        -moz-box-shadow: 0px 0px 10px 10px #CCC;
        box-shadow: 0px 0px 10px 10px #CCC;
        -webkit-transition: all 200ms linear;
        -o-transition: all 200ms linear;
        -moz-transition: all 200ms linear;
        -ms-transition: all 200ms linear;
        -kthtml-transition: all 200ms linear;
        transition: all 200ms linear;
     }
    ''')

    soup.append(css)

    return soup


def generate_default_html():
    """
    Generates default html page for items
    :return: BeautifulSoup object
    """

    soup = BeautifulSoup("<!DOCTYPE html>")

    html = soup.new_tag('html')

    head = soup.new_tag('head')
    head.append(create_css())
    html.append(head)

    html.append(soup.new_tag('body'))

    items = soup.new_tag('div')
    items['class'] = 'items'

    html.body.append(items)

    soup.append(html)

    return soup


def load_image(url, path):
    r = urllib.request.urlretrieve(url)
    copyfile(r[0], path)


def load_item(item, directory):
    image_url = get_image_url_from_item_details_url(item.name['href'])

    _, extension = os.path.splitext(image_url)

    image_name = item.name['title'].replace('/', '-')
    image_path = os.path.join(directory, image_name) + '.' + extension
    load_image(image_url, image_path)

    return None, (image_name, item.price)


def get_next_url(soup):
    next_url = soup.find('td', class_='next')
    try:
        return 'http://stores.ebay.com' + next_url.contents[0]['href']
    except KeyError:
        return None


def get_pages(start_url):
    while start_url is not None:
        soup = parse_from_url(start_url)
        yield soup
        start_url = get_next_url(soup)


def process_page(page, folder, filename):
    items = list(get_items(page))
    loaded_items = map(lambda item: load_item(item, folder), items)

    with open(filename, 'w') as f:
        for i, item in enumerate(loaded_items):
            print('Processing {0:3} of {1}'.format(i + 1, len(items)))

            task, data_to_write = item

            f.write('{0:>90}\t:\t{1}\n'.format(data_to_write[0], data_to_write[1]))


def main(argv):
    folder = './out'

    if not os.path.isdir(folder):
        os.mkdir(folder)

    # argv = ["", "http://stores.ebay.com/Mrs-Shoppe/Zippo-Lighters-/_i.html?rt=nc&_fsub=7335370010&_sid=29140120&_sticky=1&_trksid=p4634.c0.m14&_sop=2&_sc=1"]

    tasks = []


    # for page_number, page in enumerate(get_pages(argv[1])):
    #     print('Running thread for {0} page'.format(page_number))

    page = parse_from_url(argv[1])
    process_page(page, folder, os.path.join(folder, argv[2]))

if __name__ == '__main__':
    main(sys.argv)


