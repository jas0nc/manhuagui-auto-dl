# Development by HSSLCreative & Jas0n
# Date: 2021/4/1

import requests, os, time, re
from get import get
from PIL import Image
from zipfile import ZipFile
import shutil
import pathlib

def downloadCh(url, config_json=None):
    def downloadPg(url, e, m, counter):
        h = {'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://tw.manhuagui.com/',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}
        #單頁最大重試次數
        for i in range(1):
            try:
                res = requests.get(url, params={'e':e, 'm':m}, headers = h, timeout=10)
                res.raise_for_status()
            except:
                #print('頁面 %s 下載失敗: %s 重試中...' % (url, res.status_code), end='')
                #print('等待1秒...')
                #每次重試間隔
                #time.sleep(1)
                continue
            ##filename = str(counter) + '_' + os.path.basename(url)
            filename = os.path.basename(url)
            file = open(filename,'wb')
            for chunk in res.iter_content(100000):
                file.write(chunk)
            file.close()
            #轉檔 調整為False將不會轉檔
            if True:
                output_filename = filename + '.jpg'
                src_filename = os.path.join('..', '..', 'jpg', cname, output_filename)
                im = Image.open(filename)
                im.save(src_filename, 'jpeg')
            #轉檔結束
            return
        #print('超過重試次數 跳過此檔案')
        return False
    j = get(url)
    if not j:
        return False
    bname = j['bname']
    cname = j['cname']

    os.chdir(pathlib.Path(__file__).parent.absolute())

    def replacenum(matched):
        value = int(matched.group('value'))
        return " " + str('{:03d}'.format(value)) + " "
    padded_cname = re.sub('(?P<value>\d+)',replacenum,cname)
    padded_cname = re.sub(r'[\\/:*?"<>|]', '_', padded_cname)
    cname = padded_cname

    CBZfilename = re.sub(r'[\\/:*?"<>|]', '_', bname)+' - '+padded_cname+'.CBZ'
    missingpage = 0

    chdir(os.path.join('temp',re.sub(r'[\\/:*?"<>|]', '_', bname), 'jpg', cname))
    os.chdir(os.path.join('..', '..'))
    chdir(os.path.join('raw', cname))
    length = j['len']
    print(' '+'下載 %s 中 共%s頁' % (CBZfilename, length))
    e = j['sl']['e']
    m = j['sl']['m']
    path = j['path']
    i = 1

    for filename in j['files']:
        pgUrl = 'https://i.hamreus.com' + path +  filename
        output_filename = filename + '.jpg'
        src_filename = os.path.join('..', '..', 'jpg', cname, output_filename)
        if os.path.isfile(src_filename):
            print (' '+' '+src_filename+" - File exist, skip")
        else:
            print(' '+' '+os.path.basename(pgUrl)+" - Downloading                                        ")
            #每話間隔2秒
            print('  '+'延遲1秒...                                                                        ')
            print('  下載 %s: %s/%s' % (CBZfilename, i, length), end='\r')
            if (downloadPg(pgUrl, e, m, i) == False):
            	missingpage += 1
            	print(' '+' cannot download: '+os.path.basename(pgUrl)+" - missing page +1				")
            time.sleep(1)
        i += 1
    os.chdir(pathlib.Path(__file__).parent.absolute())
    chdir(os.path.join('CBZ', re.sub(r'[\\/:*?"<>|]', '_', bname)))

    z = 1
    if missingpage == 0 and length != 0:
        # create a ZipFile object
        zipObj = ZipFile(CBZfilename, 'w')
        for filename in j['files']:
            # Add file to the zip
            output_filename = filename + '.jpg'
            jpglocation = os.path.join('..','..','temp', re.sub(r'[\\/:*?"<>|]', '_', bname), 'jpg', cname, output_filename)
            zipObj.write(jpglocation, str(z).zfill(3)+'.jpg')
            z += 1
        # close the Zip File
        zipObj.close()
        print (' '+CBZfilename+" - is Created									")
    else:
        print (' '+CBZfilename+" - download failed, "+str(missingpage)+" pages are missing				")

    # remove files
    os.chdir(pathlib.Path(__file__).parent.absolute())
    if os.path.isfile(os.path.join('CBZ',re.sub(r'[\\/:*?"<>|]', '_', bname),CBZfilename)):
        jpgfolder = os.path.join('temp', re.sub(r'[\\/:*?"<>|]', '_', bname), 'jpg', cname)
        rawfolder = os.path.join('temp', re.sub(r'[\\/:*?"<>|]', '_', bname), 'raw', cname)
        shutil.rmtree(jpgfolder, ignore_errors=True, onerror=None)
        shutil.rmtree(rawfolder, ignore_errors=True, onerror=None)
    return True

def chdir(ds):
    dlist = ds.split(os.path.sep)
    for d in dlist:
        if not os.path.exists(d) and not os.path.isdir(d):
            os.mkdir(d)
        os.chdir(d)
