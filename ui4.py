import os
import re
import time
import tkinter as tk
from tkinter import ttk, messagebox

import parsel
import requests
import concurrent.futures
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import redis


def get_response_s(html_url):
    """
    获取网页的响应内容
    :param html_url: 网页链接
    :return: 网页的完整页面源码
    """
    # 使用 Edge 浏览器
    driver = webdriver.Edge()
    driver.get(html_url)
    try:
        # 使用 WebDriverWait 等待动态加载的内容出现
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bookinfo"))
        )
        # 获取包含动态加载内容的完整页面源码
        html_source = driver.page_source
        return html_source
    finally:
        # 关闭浏览器
        driver.quit()


def get_response(html_url):
    """
    发送请求函数
    :param html_url: 请求链接
    :return:response 响应对象
    """
    # 模拟浏览器headers请求头
    # headers = {
    #     # 用户代理 表示浏览器基本身份信息
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    # }
    headers = {'User-Agent': str(UserAgent().random)}
    # 发送请求
    response = requests.get(url=html_url, headers=headers)
    return response


def get_list(html_url):
    """
    获取各章节url/小说名
    :param html_url:小说目录页url
    :return:小说名，章节url
    """
    # 发送请求
    html_data = get_response(html_url).text
    # 提取小说名字
    name = re.findall('<span class="title">(.*?)</span>', html_data)[0]
    # 提取章节url
    url_list = re.findall('<dd><a href ="(.*?)">', html_data)
    return name, url_list


def get_content(html_url):
    """
    获取小说内容/小说每章标题
    :param html_url:小说章节url
    :return:每章标题,内容
    """
    response = get_response(html_url)
    # 将获取的html字符串数据转成可解析对象
    selector = parsel.Selector(response.text)
    # 提取标题
    title = selector.css('.reader h1::text').get()
    # print(title)
    # 提取内容
    content = '\n'.join(selector.css('#chaptercontent::text').getall())
    return title, content


def search(word):
    """
    搜索小说/作者
    :param word: 小说名/作者名
    :return: 包含搜索结果的列表
    """
    url = f'https://www.biqg.cc/s?q={word}'
    search_data = get_response_s(url)
    selector = parsel.Selector(search_data)
    divs = selector.css('.type_show .bookinfo')
    pre = '作者：'
    print(len(divs))
    data = []
    for div in divs:
        name = div.css('.bookname a::text').get()
        href = div.css('.bookname a::attr(href)').get()[len('/book/'):-1]
        author = div.css('.author::text').get()[len(pre):]
        d = {
            'href': href,
            'name': name,
            'author': author
        }
        data.append(d)
    global book_data
    book_data = data
    return data


book_data = []


def show():
    """
    显示查询结果
    :return: None
    """
    name = name_va.get()
    # 记录开始时间
    start_time = time.time()
    print(f"查询: {name}")
    # data = [{'num': 524, 'author': 'anson', 'name': 'i am the best', 'href': 1},
    #         {'num': 563, 'author': 'mike', 'name': 'the way', 'href': 13}
    #     ]
    data = search(name)
    for i, v in enumerate(data):
        tree_view.insert('', i + 1, values=(i + 1, v['author'], v['name'], v['href']))
        # 计算总共所需的时间差
    end_time = time.time()
    duration = end_time - start_time
    print(f'查询耗时：{duration:.2f}秒')


def save(name, title, content):
    """
    保存数据函数
    :param name: 小说名
    :param title: 章节名
    :param content: 内容
    :return: None
    """
    # 创建文件
    file = f'{name}\\'
    if not os.path.exists(file):
        os.mkdir(file)
    with open(file + title + '.txt', mode='a', encoding='utf-8') as f:
        """
        第一章 标题
            内容
        """
        f.write(title)
        f.write('\n')
        f.write(content)
        f.write('\n')


def download_sub(sub, book_title):
    # 下载子页面的函数
    url = f"https://www.biqg.cc/{sub}"
    # 构建完整的URL，子页面链接加在基础URL的末尾

    title, content = get_content(url)
    # 调用get_content函数，传入URL作为参数，获取子页面的标题和内容

    save(name=book_title, title=title, content=content)
    # 调用save函数，将书籍标题、子页面标题和内容作为参数，保存到文件中

    print(title)
    # 打印子页面的标题

def download():
    # 记录开始时间
    start_time = time.time()

    # 作为下载的基础URL
    url = 'https://www.biqg.cc/book/'

    # 从num_va中获取用户输入的值，并将其转换为整数类型。然后将其减去1并赋值给变量num。
    num = int(num_va.get()) - 1
    global book_data

    # 从book_data列表中根据索引num获取对应元素的href值，并赋值给变量href。
    href = book_data[num]['href']
    book_title, url_list = get_list(url + href)
    print(f'开始下载：《{book_title}》')
    print("===================")

    # 使用concurrent.futures.ThreadPoolExecutor创建线程池，512，并将其赋值给executor。
    with concurrent.futures.ThreadPoolExecutor(max_workers=512) as executor:

        # 创建一个空列表futures，用于存储线程的返回结果。
        futures = []
        for sub in url_list:
            # 检查Redis队列的长度，如果超过阈值，则等待一段时间
            while redis_client.llen('sub_urls') >= MAX_QUEUE_SIZE:
                time.sleep(1)

            # 将子页面链接sub添加到Redis队列'sub_urls'的左侧。
            redis_client.lpush('sub_urls', sub)

            # 使用executor.submit方法将download_sub_redis函数提交给线程池，传入参数book_title，并将返回的future对象添加到futures列表中。
            futures.append(executor.submit(download_sub_redis, book_title))

        for future in concurrent.futures.as_completed(futures):
            # 使用concurrent.futures.as_completed遍历futures列表中的future对象。
            try:
                future.result()
                # 获取future对象的结果，阻塞当前线程直到结果可用

            except Exception as e:
                print(f'An error occurred: {e}')

    print("===================")
    print(f'《{book_title}》下载完成')

    # 计算总共所需的时间差
    end_time = time.time()
    duration = end_time - start_time
    print(f'下载《{book_title}》完成，耗时：{duration:.2f}秒')

    messagebox.showinfo("下载完成", f"《{book_title}》下载完成\n耗间：{duration:.2f}秒")


def download_sub_redis(book_title):
    # 使用Redis队列下载子页面的函数
    while True:
        # 检查Redis队列的长度，如果为空，则退出循环
        if redis_client.llen('sub_urls') == 0:
            break

        # 从Redis队列中获取子页面链接，使用rpop方法从右侧取出一个元素
        sub = redis_client.rpop('sub_urls')
        if not sub:
            break

        # 将子页面链接从bytes类型解码为字符串类型
        sub = sub.decode('utf-8')
        download_sub(sub, book_title)
        # 调用download_sub函数，传入子页面

# 设置最大队列长度
MAX_QUEUE_SIZE = 10000


# 创建Redis连接
redis_client = redis.Redis(host='127.0.0.1', port=6379)
try:
    # 尝试连接Redis服务器
    redis_client.ping()
    print("Redis连接成功！")
except redis.exceptions.ConnectionError:
    print("Redis连接失败！")

def on_treeview_click(event):
    # 获取所点击项的序号
    item = tree_view.focus()
    values = tree_view.item(item, 'values')
    num_va.set(values[0])


# 创建界面
root = tk.Tk()
# 变量
name_va = tk.StringVar()
num_va = tk.StringVar()
# 设置界面大小
root.geometry('500x500+500+200')
# 设置标题
root.title('小说下载器')

# 名字作者输入框
search_frame = tk.Frame(root)
search_frame.pack(pady=20)  # 设置上边距
tk.Label(search_frame, text='书名 作者', font=('宋体', 15)).pack(side=tk.LEFT, padx=10)
tk.Entry(search_frame, textvariable=name_va).pack(side=tk.LEFT)

# 序号输入框
download_frame = tk.Frame(root)
download_frame.pack(pady=10)  # 设置上边距
tk.Label(download_frame, text='序号', font=('宋体', 15)).pack(side=tk.LEFT, padx=33)
tk.Entry(download_frame, textvariable=num_va).pack(side=tk.LEFT)

# 查询下载
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text='查询', font=(12), relief='flat', bg='#FAEBD7', width=8, command=show).pack(side=tk.LEFT,
                                                                                                         padx=10)
tk.Button(button_frame, text='下载', font=(12), relief='flat', bg='#FAEBD7', width=8, command=download).pack(
    side=tk.LEFT, padx=10)

# 设置表格
columns = ('num', 'writer', 'name', 'novel_id')
columns_value = ('序号', '作者', '书名', '书ID')
tree_view = ttk.Treeview(root, height=18, show='headings', columns=columns)
# 设置列名
tree_view.column('num', width=1, anchor='center')
tree_view.column('writer', width=30, anchor='center')
tree_view.column('name', width=90, anchor='center')
tree_view.column('novel_id', width=5, anchor='center')
# 给列名设置显示的名字
tree_view.heading('num', text='序号')
tree_view.heading('writer', text='作者')
tree_view.heading('name', text='书名')
tree_view.heading('novel_id', text='书ID')
tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 绑定点击事件
tree_view.bind('<ButtonRelease-1>', on_treeview_click)

# 滚动条
vsb = ttk.Scrollbar(root, orient="vertical", command=tree_view.yview)
vsb.pack(side=tk.RIGHT, fill=tk.Y)
tree_view.configure(yscrollcommand=vsb.set)

root.mainloop()
