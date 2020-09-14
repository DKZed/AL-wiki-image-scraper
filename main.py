from bs4 import BeautifulSoup
from os import makedirs, path
from PIL import Image, ImageDraw, ImageFont
from requests import get
from urllib import request

wiki_url = 'https://azurlane.koumakan.jp'
ship_list_href = '/List_of_Ships'

response = get(wiki_url + ship_list_href)

tables = BeautifulSoup(response.text, "html.parser").find_all('table')


def add_text(ship_name, image_path):
    image = Image.open(image_path)
    font_size = 1
    font_path = path.join('font', 'Calibri.ttf')
    font = ImageFont.truetype(font_path, font_size)
    image_w, image_h = image.size

    rectangle = Image.new('RGB', (image_w, 20))
    rectangle_draw = ImageDraw.Draw(rectangle)
    rectangle_draw.rectangle([0, 0, image_w, 20], fill='black')

    while font.getsize(ship_name)[0] < image_w and font.getsize(ship_name)[1] < 20:
        font_size += 1
        font = ImageFont.truetype(font_path, font_size)
    font_size -= 1
    font = ImageFont.truetype(font_path, font_size)
    font_w, font_h = rectangle_draw.textsize(ship_name, font=font)
    rectangle_draw.text(((image_w-font_w)/2, (20-font_h)/2), ship_name, font=font, fill='white')

    combined = Image.new('RGB', (image_w, image_h + 20))
    combined.paste(image, (0, 0))
    combined.paste(rectangle, (0, image_h))

    combined.save(image_path)


def download_image(image_href, ship_name, is_icon, hull_type):
    image_link = wiki_url + image_href
    file_name = image_link.split('/')[-1]
    ship_name = ship_name.replace('/', '')
    directory = path.join('images', hull_type)
    # if is_icon:
    #     directory = path.join(directory, 'icon')
    # else:
    #     directory = path.join(directory, 'chibi')
    if not path.isdir(directory):
        makedirs(directory)
    print('Downloading to ' + directory)
    image_path = path.join(directory, file_name)
    request.urlretrieve(image_link, image_path)
    add_text(ship_name.replace('_', ' '), image_path)


def get_class(soup):
    if len(soup.body.findAll(text='Destroyer')) > 1:
        return 'DD'
    elif len(soup.body.findAll(text='Light Cruiser')) > 1:
        return 'CL'
    elif len(soup.body.findAll(text=['Heavy Cruiser', 'Large Cruiser'])) > 1:
        return 'CA'
    elif len(soup.body.findAll(text='Carrier')) > 1:
        return 'CV'
    elif len(soup.body.findAll(text=['Battleship', 'Battlecruiser'])) > 1:
        return 'BB'
    elif len(soup.body.findAll(text='Submarine')) > 1:
        return 'SV'
    else:
        return 'Other'


def get_icon(ship_name):
    image_response = get(wiki_url + ship_name)
    soup = BeautifulSoup(image_response.text, 'html.parser')
    img_tags = soup.find_all('img')
    urls = [img['src'] for img in img_tags]
    for url in urls:
        icon_string = ship_name + 'Icon'
        if icon_string in url and "thumb" not in url:
            download_image(url, ship_name, True, get_class(soup))


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
                # get_chibi(ship_name_href)
            except:
                print('Could not find href in row!')

