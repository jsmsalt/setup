import json
import youtube_dl
import re
import time
import os

homedir = os.path.expanduser("~")

ydl_opts = {
    'quiet': True,
    'no_warnings': True,
}

bookmarks = str(homedir)+'/.config/radiotray-ng/bookmarks.json'

while True:
    data = []
    change = False
    if os.path.isfile(bookmarks):
        with open(bookmarks) as json_file:  
            data = json.load(json_file)
            for g, group in enumerate(data):
                for s, station in enumerate(group['stations']):
                    r = re.findall(r"\((id|u)\:(.*?)\)", station['name'])

                    if r:
                        type = r[0][0]
                        channel = r[0][1]

                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:

                            if type == 'id':
                                url = 'https://www.youtube.com/channel/'+str(channel)+'/live'
                            else:
                                url = 'https://www.youtube.com/'+str(channel)+'/live'

                            info = None

                            try:
                                info = ydl.extract_info(url, download=False)
                            except:
                                print("An exception occurred: "+station['name'])

                            if info and info['url']:
                                if data[g]['stations'][s]['url'] != info['url']:
                                    data[g]['stations'][s]['url'] = info['url']
                                    change = True

        if change:
            with open(bookmarks, 'w') as json_save:  
                json.dump(data, json_save)

    time.sleep(60*20)