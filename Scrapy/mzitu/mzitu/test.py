"""
Version: Python3.6
Author: Zzz
Time: 2019/4/23
"""
import asyncio
import datetime
import aiohttp
import random
import time
from aiomultiprocess import Pool
import pymongo
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

UserAgent_List = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]
header = {"UserAgent": random.choice(UserAgent_List),
          'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
          'Accept-Language': 'zh-CN,zh;q=0.9',
          'Referer': 'https://www.mzitu.com',
          }
file_path = r'G:\photo\scrapy'  #图片保存本地路径
MONGODB_SEVER = {'localhost': 27017}
client = pymongo.MongoClient('120.79.55.50', 27017)
db = client.testdb
col = db.MzituItem


def str_del(string):
    # 处理字符串
    ban = ['\\', '/', ':', '*', '', '"', '<', '>', '|', '?']
    for i in string:
        if i in ban:
            string = string.replace(i, '')
    return string


async def save_pic(result):
    #协程并发保存到本地
    img_title = result['title']
    img_urls = result['img_list']
    k = 1
    img_title = str_del(img_title)
    connector = aiohttp.TCPConnector(limit=60)
    file_paths = os.path.join(file_path, img_title)
    session = aiohttp.ClientSession(connector=connector)
    if os.path.exists(file_paths) is False:
        os.mkdir(file_paths)
        for img_url in img_urls:
            try:
                name = img_title + '(' + str(k) + ')'
                response = await session.get(url=img_url, headers=header, timeout=20)
                res_content = await response.read()

                file_name = '{}\{}.jpg'.format(file_paths, name)
                with open(file_name, 'wb') as f:
                    f.write(res_content)
                    print('下载' + img_url + '成功')
                    f.close()
                k += 1
            except Exception as e:
                print('保存失败', e)
    else:
        print(img_title)
    await session.close()


def deletDouble(s):
    l = len(s)
    delist = []
    k = 1
    for i in range(2900):
        for j in range(2900, l):
            if s[i] == s[j]:
                k += 1
                delist.append(s[i])

    return delist


async def get_col():
    async with Pool() as pool:
        i = col.find({})[150:180]
        result = await pool.map(save_pic, i)
        return result


def get_proxy():
    proxy = requests.get("http://127.0.0.1:5010/get/").text
    proxies = dict(http="{}".format(proxy), https="https://{}".format(proxy))
    return proxies


def save_pic1(result):
    #保存图片的数据库不用查重，在下载的时候根据题目筛选，下载未存在的文件
    img_title = result['title']
    img_urls = result['img_list']
    k = 1
    img_title = str_del(img_title)
    file_paths = os.path.join(file_path, img_title)
    if os.path.exists(file_paths) is False:
        os.mkdir(file_paths)
        for img_url in img_urls:
            try:
                name = img_title + '(' + str(k) + ')'
                response = requests.get(url=img_url, headers=header, timeout=20, stream=True)
                file_name = '{}\{}.jpg'.format(file_paths, name)
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                    print('下载' + img_url + '成功')
                    f.close()
                k += 1
                time.sleep(1)
            except Exception as e:
                print('保存失败', e)
    else:
        print(img_title)


def main():
    task = []
    j = 0
    '''
    #线程池的方式保存图片，经测试在线程数为10的时候下载会比较稳定但是速度比协程要慢
    #协程同时传入的任务数当大于10的时候会出现少量请求图片的错误，当大于500的时候协程内部报错select
    executor = ThreadPoolExecutor(max_workers=10)
    i= col.find({})[425:435]
    executor.map(save_pic1, i)
    '''
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    while True:
        startime = datetime.datetime.now()
        if j > 3000:
            print(j)
            break
        else:

            for i in col.find({})[j:j + 5]:
                task.append(asyncio.ensure_future(save_pic(i)))
            loop.run_until_complete(asyncio.wait(task))
            endtime = datetime.datetime.now()
            print((endtime - startime).seconds)

        j += 5

    loop.close()
if __name__ == '__main__':
    main()

    client.close()
