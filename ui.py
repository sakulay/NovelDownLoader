import re
import tkinter as tk
from tkinter import ttk

import parsel
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_response_s(html_url):
    # 使用 Chrome 浏览器
    driver = webdriver.Chrome()
    driver.get(html_url)
    try:
        # 使用 WebDriverWait 等待动态加载的内容出现
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "type_show"))
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
    headers = {
        # 用户代理 表示浏览器基本身份信息
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    # 发送请求
    response = requests.get(url=html_url, headers=headers)
    return response

def get_list(html_url):
    # 发送请求
    html_data = get_response(html_url).text
    # 提取小说名字
    name = re.findall('<span class="title">(.*?)</span>', html_data)[0]
    # 提取章节url
    url_list = re.findall('<dd><a href ="(.*?)">', html_data)
    return name, url_list

def get_content(html_url):
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
    name = name_va.get()
    print(f"查询{name}")
    # data = [{'num': 524, 'author': 'anson', 'name': 'i am the best', 'href': 1},
    #         {'num': 563, 'author': 'mike', 'name': 'the way', 'href': 13}
    #     ]
    data = search(name)
    for i,v in enumerate(data):
        tree_view.insert('', i+1, values=(i+1, v['author'], v['name'], v['href']))

def download():
    url = 'https://www.biqg.cc/book/'
    num = int(num_va.get()) - 1
    global book_data
    print(book_data[num]['href'])
    href = book_data[num]['href']
    book_title,url_list = get_list(url + href)
    print(book_title)
    for sub in url_list:
        print("================")
        url1 = f"https://www.biqg.cc/{sub}"
        title, content = get_content(url1)
        print(title)
        print(content)


#创建界面
root = tk.Tk()
#变量
name_va = tk.StringVar()
num_va = tk.StringVar()
#设置界面大小
root.geometry('500x500+500+200')
#设置标题
root.title('小说下载器')

#名字作者输入框
search_frame = tk.Frame(root)
search_frame.pack(pady=20)#设置上边距
tk.Label(search_frame, text='书名 作者', font=('宋体', 15)).pack(side=tk.LEFT, padx=10)
tk.Entry(search_frame, textvariable=name_va).pack(side=tk.LEFT)

#序号输入框
download_frame = tk.Frame(root)
download_frame.pack(pady=10)#设置上边距
tk.Label(download_frame, text='序号', font=('宋体', 15)).pack(side=tk.LEFT, padx=33)
tk.Entry(download_frame, textvariable=num_va).pack(side=tk.LEFT)

#查询下载
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
tk.Button(button_frame, text='查询', font=(12), relief='flat',bg='#FAEBD7', width=8, command=show).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text='下载', font=(12), relief='flat',bg='#FAEBD7', width=8, command=download).pack(side=tk.LEFT, padx=10)

#设置表格
columns = ('num', 'writer', 'name', 'novel_id')
columns_value = ('序号', '作者', '书名', '书ID')
tree_view =  ttk.Treeview(root, height=18, show='headings', columns=columns)
#设置列名
tree_view.column('num', width=1, anchor='center')
tree_view.column('writer', width=30, anchor='center')
tree_view.column('name', width=90, anchor='center')
tree_view.column('novel_id', width=5, anchor='center')
#给列名设置显示的名字
tree_view.heading('num', text='序号')
tree_view.heading('writer', text='作者')
tree_view.heading('name', text='书名')
tree_view.heading('novel_id', text='书ID')
tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#滚动条

vsb = ttk.Scrollbar(root, orient="vertical", command=tree_view.yview)
vsb.pack(side=tk.RIGHT, fill=tk.Y)
tree_view.configure(yscrollcommand=vsb.set)
root.mainloop()