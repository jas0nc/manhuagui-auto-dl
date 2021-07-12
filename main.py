#!/usr/local/bin/python3
# Development by HSSLCreative & Jas0n
# Date: 2021/4/1

import re, time, bs4, requests, lzstring, os
from download import downloadCh, chdir
from generate_config import generate_config
import pathlib
import shutil

check_re = r'^https?://([a-zA-Z0-9]*\.)?manhuagui\.com/comic/([0-9]+)/?'
request_url = 'https://tw.manhuagui.com/comic/%s'
host = 'https://tw.manhuagui.com'
comic_list = 'comic_url.txt'

def main():
    print('僅供學術研究交流使用，勿作為商業用途')
    ##while True:
    ##    print('輸入URL:')
    ##    #格式:https://*.manhuagui.com/comic/XXXXX
    ##    #是否進入章節都沒關係
    ##    #例如https://*.manhuagui.com/comic/XXXXX/XXXXX.html也行
    ##    #反正要得只有id
    ##    url = input()
    print('workdir: '+str(pathlib.Path(__file__).parent.absolute()))
    os.chdir(pathlib.Path(__file__).parent.absolute())
    with open(comic_list) as my_comic_url:
        my_comic = list(my_comic_url)
        my_comic_url.close()
        new_comic = my_comic
        for line in my_comic:
            os.chdir(pathlib.Path(__file__).parent.absolute())
            url = line
            while True:
                try:
                    checked_id = re.match(check_re, url).group(2)
                    break
                except:
                    print('無效的網址')
                    continue
            try:
                res = requests.get(request_url % checked_id)
                res.raise_for_status()
            except:
                print('錯誤:可能是沒網路或被ban ip?')
                return
            bs = bs4.BeautifulSoup(res.text, 'html.parser')
            title = bs.select('.book-title h1')[0]
            print('標題: %s - %s' % (title.text, url) )
            authors_link = bs.select('a[href^="/author"]')
            authors = []
            for author in authors_link:
                authors.append(author.text)
            authors = '、'.join(authors)
            coverlink = bs.select('.hcover img')
            coverlink = [x['src'] for x in coverlink][0]
            #print(coverlink)
            description = bs.select('div#intro-cut')[0]
            #print(description)
            status = bs.select('.status span')[0]
            #print(status)
            config_json = generate_config(title.text, authors, coverlink, url, description.text, status.text)
            links = bs.select('.chapter-list a')
            if not links:
                links = bs4.BeautifulSoup(lzstring.LZString().decompressFromBase64(bs.select('#__VIEWSTATE')[0].attrs.get('value')), 'html.parser').select('.chapter-list a')
            links.reverse()
            ch_list = []
            for link in links:
                ch_list.append([link.attrs['title'], link.attrs['href']])
            ##print('編號 對應名稱')
            ##for ch_index in range(len(ch_list)):
            ##    ch = ch_list[ch_index]
            ##    print(str(ch_index).ljust(4), ch[0])
            ##print('輸入上列編號(ex:輸入1-2 5-8 10 將會下載編號 1, 2, 5, 6, 7, 8, 10 的章節)')
            ##choose_chs = input()
            ##tmp = re.findall(r'[0-9]+\-?[0-9]*', choose_chs)
            ##choose_block_list = []
            config_writed = False
            ##for block in tmp:
            ##    try:
            ##        block = block.split('-')
            ##        for i in range(len(block)):
            ##            block[i] = int(block[i])
            ##            if block[i] > len(ch_list) or block[i] < 0:
            ##                raise Exception('out of range')
            ##        if len(block) >= 2:
            ##            if block[1] < block[0]:
            ##                block[0], block[1] = block[1], block[0]
            ##            choose_block_list.append([block[0], block[1]])
            ##        else:
            ##            choose_block_list.append([block[0], block[0]])
            ##    except:
            ##        continue
            ##for area in choose_block_list:
            ##    block = ch_list[area[0]:area[1]+1]
            ##    for ch in block:
            allchdownloaded = True
            for ch in ch_list:
                bname = title.text
                cname = ch[0]
                def replacenum(matched):
                    value = int(matched.group('value'))
                    return " " + str('{:03d}'.format(value)) + " "
                padded_cname = re.sub('(?P<value>\d+)',replacenum,cname)
                padded_cname = re.sub(r'[\\/:*?"<>|]', '_', padded_cname)
                cname = padded_cname

                CBZfilename = re.sub(r'[\\/:*?"<>|]', '_', bname)+' - '+padded_cname+'.CBZ'
                os.chdir(pathlib.Path(__file__).parent.absolute())
                chdir(os.path.join('CBZ', re.sub(r'[\\/:*?"<>|]', '_', bname)))
                if config_json:
                    if not os.path.isfile('config.json'):
                        with open(os.path.join('config.json'), 'w', encoding='utf-8') as config:
                            config.write(config_json)
                            print (' '+'config_json'+" - is created")
                if not os.path.isfile('cover.jpg'):
                    response = requests.get(coverlink)
                    file = open("cover.jpg", "wb")
                    file.write(response.content)
                    file.close()
                    print (' '+'cover.jpg'+" - is created")
                if os.path.isfile(CBZfilename):
                    print (' '+CBZfilename+" - File exist, skip")
                else:
                    allchdownloaded = False
                    if not config_writed:
                        downloadCh(host + ch[1], config_json)
                    else:
                        downloadCh(host + ch[1])
                        config_writed = True
                    #每話間隔2秒
                    print(' '+'延遲2秒...')
                    time.sleep(2)
            if allchdownloaded:
                bname = title.text
                # remove temp folder
                os.chdir(pathlib.Path(__file__).parent.absolute())
                tempfolder = os.path.join('temp', re.sub(r'[\\/:*?"<>|]', '_', bname))
                if os.path.isdir(tempfolder):
                    shutil.rmtree(tempfolder)
                print (bname+" - All chapters are downloaded, next")
                #每漫畫間隔2秒
                print('延遲2秒...')
                time.sleep(2)
                #move complete series to the end of url file
                new_comic.append(new_comic.pop(new_comic.index(line)))
                os.chdir(pathlib.Path(__file__).parent.absolute())
                with open(comic_list, 'w') as f:
                    for item in new_comic:
                        f.write("%s" % item)
main()

#各話間會延遲5秒 各頁間會延遲1秒
#防止被ban ip
#目前延遲數值是保守值 可自行依注解更改
#反正執行後就能afk了
