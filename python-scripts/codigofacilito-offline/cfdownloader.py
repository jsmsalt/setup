#!/usr/bin/env python3
from __future__ import unicode_literals
import youtube_dl
import requests
import urllib.request
import time
import re
from bs4 import BeautifulSoup
import sys
import json
import os
import string

class DownloadLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def download_hook(d):
    if d['status'] == 'finished':
        print('\rSe terminó de descargar...              ', end='\r')
    elif d['status'] == 'downloading':
        print('\rDescargando... %s (ETA: %s, VELOCIDAD: %s)            ' % (d['_percent_str'], d['_eta_str'], d['_speed_str']), end = '\r')

def validFilename(f):
    valid_chars = "-_.()[]áéíóúÁÉÍÓÚñÑ %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in f if c in valid_chars)

ydl_opts = {
    'outtmpl': '%(title)s-%(id)s.%(ext)s',
    'format': 'best',
    'logger': DownloadLogger(),
    'progress_hooks': [download_hook]
}

youtube_dl.utils.std_headers['Referer'] = "http://codigofacilito.com"


args = sys.argv
path = os.path.dirname(os.path.realpath(__file__))

if len(args) < 2:
    sys.exit('Curso no detectado...')
elif args[1].find('https://codigofacilito.com/cursos/') == -1:
    sys.exit('Curso no detectado...')

if len(args) == 3 and args[2] == '-t':
    text_only = True
else:
    text_only = False

s = requests.Session()
useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'

curso = dict()
headers = {'User-Agent': useragent, 'X-Requested-With': 'XMLHttpRequest'}
x = s.get(url=args[1], headers=headers)
if x.status_code != 200:
    sys.exit('Error...0')

# TITULO
soup = BeautifulSoup(x.content, "html.parser")
curso_titulo = soup.select('.box h1')[0].get_text()
curso['title'] = curso_titulo
curso['content'] = list()
json_file = path + '/json/' + curso['title'] + '.json'

if not os.path.isfile(json_file):
    # LOGIN
    print('Login...')
    data={
        'user[remember_me]': 'true',
        'user[email]': 'xxxx@gmail.com',
        'user[password]': '12345'
    }
    headers = {'User-Agent': useragent, 'X-Requested-With': 'XMLHttpRequest'}
    x = s.get(url="https://codigofacilito.com/users/sign_in")
    if x.status_code != 200:
        sys.exit('Error...1')
    token = re.search(r'csrf-token\" content=\"(.*?)\"', x.text).group(1)
    headers = {'User-Agent': useragent, 'x-csrf-token': token}
    x = s.post(url="https://codigofacilito.com/users/sign_in", data=data, headers=headers)

    # CONTENIDO
    content_list_headers = soup.select('a.load_remote')

    print('Extrayendo contenido...')

    id = 1
    last = 0
    for header in content_list_headers:
        htitle = header.select('.box')[0].get_text().replace("\n","").replace(".-"," - ")
        print(htitle)
        hlink = "https://codigofacilito.com"+header['href']

        headers = {'User-Agent': useragent, 'X-Requested-With': 'XMLHttpRequest'}
        x = s.get(url=hlink, headers=headers)
        if x.status_code != 200:
            sys.exit('Error...3')

        header_html = x.text.replace('\\\\\\', '').replace('\\"', '"').replace('\\\'', '\'').replace('\\n', '').replace('&nbsp;', '').replace('\\/', '/')
        header_html = re.search(r'html\(\"(.*?)\"\)', header_html).group(1)
        soup = BeautifulSoup(header_html, "html.parser")
        items = soup.select('a')
        childrens = list()

        for item in items:
            title = item.select('.box')[0].get_text()
            title_clean = re.search(r'([0-9]+)(\.- |\.-|- |-)(.*)', title)
            if title_clean:
                title = title_clean.group(3)
            print(' - ' + str(id) + ' - ' + title)
            link = "https://codigofacilito.com"+item['href']

            headers = {
                'User-Agent': useragent,
                'X-Requested-With': 'XMLHttpRequest',
                'accept': 'text/html, application/xhtml+xml'
            }
            x = s.get(url=link, headers=headers)
            if x.status_code != 200:
                sys.exit('Error...4')
            video = re.search(r'vimeo\.com\/video\/([0-9]+)\?', x.text)
            if video:
                video = video.group(1)
                type = "video"
            else:
                video = ""
                type = "text"

            childrens.append({"title": title, "link": link, "video": video, "type": type, "id": str(id)})
            last = id
            id += 1
        curso['content'].append({"title": htitle, "link": hlink, "type": "header", "childrens": childrens})

    curso['last'] = str(last)
    if not os.path.exists(path + '/json'):
        os.mkdir(path + '/json')

    with open(json_file, 'w') as js_file:
        json.dump(curso, js_file)
else:
    print('[DESCARGANDO CURSO]')
    js_file = open(json_file)
    json_str = js_file.read()
    curso_data = json.loads(json_str)

    folder_cursos = path + '/cursos'

    if not os.path.exists(folder_cursos):
        os.mkdir(folder_cursos)

    folder_curso = folder_cursos + '/' + validFilename(curso_data['title'])

    if not os.path.exists(folder_curso):
        os.mkdir(folder_curso)

    for item in curso_data['content']:
        if item['type'] == 'header':
            folder_unidad = folder_curso + '/' + validFilename(item['title'])

            if not os.path.exists(folder_unidad):
                os.mkdir(folder_unidad)

            for child in item['childrens']:
                if child['type'] == 'video' and text_only == False:
                    print('%s/%s: %s' % (child['id'], curso_data['last'], child['title']))
                    ydl_opts['outtmpl'] = folder_unidad + '/' + child['id'].zfill(3) + ' - ' + validFilename(child['title'])+'.%(ext)s'
                    ydl = youtube_dl.YoutubeDL(ydl_opts)
                    ydl.download(['http://player.vimeo.com/video/'+child['video']])
                elif child['type'] == 'text':
                    print('%s/%s: %s' % (child['id'], curso_data['last'], child['title']))
                    headers = {'User-Agent': useragent}
                    x = s.get(url=child['link'], headers=headers)
                    soup = BeautifulSoup(x.text, "html.parser")
                    articles = soup.select('article.paragraph')
                    if len(articles) > 0:
                        html = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>%s</title></head><body>%s</body></html>' % (child['title'], str(articles[0]))
                        filename = folder_unidad + '/' + child['id'].zfill(3) + ' - ' + validFilename(child['title']) + '.html'
                        if not os.path.isfile(filename):
                            with open(filename, "w") as html_file:
                                html_file.write(html)
