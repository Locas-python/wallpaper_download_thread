from urllib.request import urlopen
import re, logging
from threading import Thread
from queue import Queue


#下载器：根据链接（link） 下载图片，保存到 （filename）
def download_wallpaper(link, filename):
    with open(filename, 'wb') as file:
        data = urlopen(link).read()
        file.write(data)

# 线程：不断的从列队（links）取出图片链接，调用下载器
logging.basicConfig(
    level = logging.DEBUG,
    format = '[%(levelname)s] (%(threadName)s) %(message)s'
)
def worker(links):
    while True: # 守护线程不断地获取资源
        link = links.get()  # 获取资源，如果没有资源则一直等待
        filename = re.search('[\w_]+.png', link).group() # 提取文件名
        download_wallpaper(link, filename) # 下载图片
        logging.debug(f'downloading: {link} -> {filename}')
        links.task_done() # 告诉队列一个获取的资源已经处理完成，join()会等待资源处理完成

links = Queue()


# 启动两个线程
worker_num = 2
for i in range(worker_num):
    Thread(name=f'worker-{i}', target=worker, args=(links,), daemon=True).start()
    

# 首页有一系列图片链接，获取链接并加入列队
url = 'http://simpledesktops.com/browse/'
html = urlopen(url).read().decode('utf-8') # 下载html内容
imgs = re.findall(r'http://static.simpledesktops.com/uploads/desktops/[\w_/.]+?.png', html) # 正则表达式提取图片
for img in imgs:
    links.put(img) # 将资源放进队列
links.join() # 所有图片链接存放完成，等待处理结束