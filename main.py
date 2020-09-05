from bs4 import BeautifulSoup
from os import makedirs, path
from requests import get
from urllib import request

wiki_url = 'https://azurlane.koumakan.jp'
ship_list_href = '/List_of_Ships'

response = get(wiki_url + ship_list_href)

tables = BeautifulSoup(response.text, "html.parser").find_all('table')


def download_image(image_href, ship_name, is_icon):
    image_link = wiki_url + image_href
    file_name = image_link.split('/')[-1]
    ship_name = ship_name.replace('/', '')
    directory = path.join('images', ship_name)
    if is_icon:
        directory = path.join(directory, 'icon')
    else:
        directory = path.join(directory, 'chibi')
    if not path.isdir(directory):
        makedirs(directory)
    print('Downloading to ' + directory)
    request.urlretrieve(image_link, path.join(directory, file_name))


def get_icon(ship_name):
    image_response = get(wiki_url + ship_name)
    soup = BeautifulSoup(image_response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags]
    for url in urls:
        icon_string = ship_name + 'Icon'
        if icon_string in url and "thumb" not in url:
            download_image(url, ship_name, True)


def get_chibi(ship_name):
    image_response = get(wiki_url + ship_name + '/Gallery#Retrofit')
    soup = BeautifulSoup(image_response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags]
    has_retrofit = False
    chibi_string_kai = ship_name + 'KaiChibi'
    chibi_string = ship_name + 'Chibi'
    for url in urls:
        if chibi_string_kai in url:
            has_retrofit = True
    for url in urls:
        if has_retrofit and chibi_string_kai in url:
            download_image(url, ship_name, False)
        elif not has_retrofit and chibi_string in url:
            download_image(url, ship_name, False)


for table in tables:
    table_body = table.find_all('tbody')
    for body in table_body:
        table_rows = body.find_all('tr')
        for row in table_rows:
            try:
                ship_name_href = row.next_element.contents[0].attrs['href']
                get_icon(ship_name_href)
                get_chibi(ship_name_href)
            except:
                print('Could not find href in row!')

