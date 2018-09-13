import json
import requests
import re
import time
import threading
import queue
from lxml import etree
from requests.exceptions import RequestException


# 创建FIFO
contains = queue.Queue()

# 创建线程数
thread_nums = 5


def get_one_page(url):

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text      
        return None
    except RequestException:
        return None


def parese_one_page(response):

    rehtml = etree.HTML(response)
    name = rehtml.xpath('//p[@class="name"]/a//text()')
    star = rehtml.xpath('//p[@class="star"]//text()')
    time = rehtml.xpath('//p[@class="releasetime"]//text()')
    score1 = rehtml.xpath('//i[@class="integer"]//text()')
    score2 = rehtml.xpath('//i[@class="fraction"]//text()')               
    print(name, star, time, score1, score2)

    for item in range(len(name)):
        yield{
            'name': name[item],
            'star': star[item].strip()[3:],
            'time': time[item][5:],
            'score': score1[item]+score2[item]
        }


def write_to_file(item):
    
    with open('猫眼2-5_thread.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False)+'\n')


def worker():
    
    global contains
    while not contains.empty():
        url = contains.get()
        response = get_one_page(url)
        for item in parese_one_page(response):
            write_to_file(item)


if __name__ == '__main__':
    start = time.clock()

    # 建立一个线程池，添加FIFO
    threads = []
    for i in range(2):
        url = 'http://maoyan.com/board/4?offset=' + str(i * 10)
        contains.put(url)

    # 开始所有线程
    for i in range(thread_nums):
        thread = threading.Thread(target=worker)
        thread.start()
        threads.append(thread)

    # 阻塞调用线程，等待线程结束
    for thread in threads:
        thread.join()

    end = time.clock()
    print('time', end-start)
