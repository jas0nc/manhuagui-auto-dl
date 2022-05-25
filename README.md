fork from: manhuagui-dlr https://github.com/HSSLC/manhuagui-dlr

1) added ability to batch download from a list of urls.
2) the downloads will be transform into CBZ file format

best fit for use with Komga https://komga.org

To install python3 dependancy on SYnology. Run below command in ssh 
sudo -i
python3 -m ensurepip
python3 -m pip install --upgrade pip
python3 -m pip install bs4 requests lzstring Pillow

in order to start auto download in synology:
1) Go to Setting->task scheduler
2) Add schduled tast
3) General->
   Task name: manhuagui-auto-dl
   User: root
   Schedule->
   Run on the following days: daily
   Task Settings->
   Run Command: python3 /path/to/main.py
4) add the comic url into comic_url.txt
5) make sure the task is enabled, seat back, and wait, and ENJOY!!!.
