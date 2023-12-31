import re
import requests
import parsel
import os
import concurrent.futures

"""
1、发送请求 utl
2、获取数据 response
3、解析数据 提取所需内容
    re正则表达式：直接对字符串数据进行解析 
        re.findall('什么数据','什么地方') 从什么地方，去找什么数据
        # 提取标题
        title = re.findall('<h1 class="wap_none">(.*?)</h1>', response.text)[0]
        print(title)
        # 提取内容
        context=re.findall('<div id="chaptercontent" class="Readarea ReadAjax_content">(.*?)</div>',response.text,re.S)[0].replace('<br /><br />','\n')
        print(context)
    css选择器: 根据标签属性提取数据
        .reader h1::text 类名为.reader下面h1标签里的一个文本
        # 将获取的html字符串数据转成可解析对象
        selector = parsel.Selector(response.text)
        # 提取标题
        title = selector.css('.reader h1::text').get()
        print(title)
        # 提取内容
        context = '\n'.join(selector.css('#chaptercontent::text').getall())
        print(context)
    xpath节点提取：据标签节点提取数据
4、保存数据
"""


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
    print(title)
    # 提取内容
    content = '\n'.join(selector.css('#chaptercontent::text').getall())
    return title, content


def save(name, title, content):
    """
    保存数据函数
    :param name: 小说名
    :param title: 章节名
    :param content: 内容
    :return:
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


def get_novel_id(html_url):
    """
    获取小说id
    :param html_url:  分类的链接
    :return:
    """
    # 发送请求
    novel_data = get_response(html_url=html_url).text
    selector = parsel.Selector(novel_data)
    href = selector.css('.blocks ul li a::attr(href)').getall()
    href = [i[1:-1] for i in href]
    print(href)
    return href


def main(html_url):
    """
    :param html_url:
    :return:
    """
    # # 获取章节标题，内容
    # title, content = get_content(html_url=html_url)
    # # 保存文件
    # save(name, title, content)
    href = get_novel_id(html_url=html_url)
    for novel_id in href:
        novel_url = f'https://www.biqg.cc/{novel_id}/'
        name, url_list = get_list(html_url=novel_url)
        print(name)
        for url in url_list:
            index_url = 'https://www.biqg.cc/' + url
            # 获取章节标题，内容
            title, content = get_content(html_url=index_url)
            # 保存文件
            save(name, title, content)


if __name__ == '__main__':
    # url = 'https://www.biqg.cc/book/86926/'
    # # 获取小说名，各章节url
    # name, url_list = get_list(html_url=url)
    # # 多线程爬取
    # exe = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    # for url in url_list:
    #     index_url = 'https://www.biqg.cc/' + url
    #     exe.submit(main, index_url)
    # exe.shutdown()
    html_url = 'https://www.biqg.cc/top/'
    main(html_url)
