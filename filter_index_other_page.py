import time
import os
import requests
from bs4 import BeautifulSoup
import webbrowser

# 设置全局变量
write_file_path = ""
path = "BBC_Other_Index.html"
blacklist_path = 'blacklist.txt'
prohibited_words_path = "prohibited_words.txt"


def get_index_html(url, port):  # 爬虫获取html
    proxies = {
        'http': f'http://127.0.0.1:{port}',
        'https': f'http://127.0.0.1:{port}',
    }
    response = requests.get(url, proxies=proxies)

    if response.status_code == 200:
        with open(path, "w", encoding="utf-8") as file:
            file.write(response.text)
        print("HTML 内容已保存到 BBC_Other_Index 文件中")
    else:
        print("获取HTML失败，状态码为：", response.status_code)


def write_html(file_path, file_content, prefix, write_or_not):
    count = 1
    full_file_path = os.path.join(file_path, f"{prefix}{count}.html")

    while os.path.exists(full_file_path):
        count += 1
        full_file_path = os.path.join(file_path, f"{prefix}{count}.html")

    file_name = f"{prefix}{count}.html"

    if write_or_not == 1:
        with open(full_file_path, 'w', encoding='utf-8') as file:
            file.write(file_content)
        print("处理后的网页写入到：", file_name)
    return full_file_path


# 对<li>标签的不同情况进行细分，以适应主页不同板块结构
def remove_tags_with_prohibited_words(soup, prohibited_words):
    # <li>下<span>标签过滤
    for span in soup.find_all('span'):
        if any(word in span.get_text() for word in prohibited_words):
            parent_li = span.find_parent('li')
            if parent_li:
                with open("deleted_contents", 'a') as file:
                    file.write("删除的标签内容:\n")
                    file.write(parent_li.prettify())
                    file.write("\n")
                parent_li.extract()

    # <li>下<a><p>标签过滤
    for li in soup.find_all('li'):
        h3_tag = li.find('h3')
        a_tag = li.find('a')
        p_tag = li.find('p')
        if (a_tag and any(word in a_tag.get_text() for word in prohibited_words)) or (
                p_tag and any(word in p_tag.get_text() for word in prohibited_words)):
            with open("deleted_contents", 'a') as file:
                file.write("删除的标签内容:\n")
                file.write(li.prettify())
                file.write("\n")
            li.extract()

    # 热看板块过滤
    target_class = 'bbc-iinl4t euhul101'
    divs = soup.find_all('div', class_=target_class)
    for div in divs:
        for li in div.find_all('li'):
            a_tag = li.find('a')
            if a_tag and any(word in a_tag.get_text() for word in prohibited_words):
                with open("deleted_contents", 'a') as file:
                    file.write("删除的标签内容:\n")
                    file.write(li.prettify())
                    file.write("\n")
                li.extract()
    return soup


# 将txt转为列表，黑名单和敏感词导入可用
def import_file_to_list(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file.readlines()]
            return lines
    except FileNotFoundError:
        print("文件未找到！")
        return []


# 根据blacklist.txt，删除href标签，不可能修改源码，测试的时候可以用
def remove_href(html_content, href_to_remove):
    for black_href in hrefs_to_remove:  # 遍历黑名单

        # 找到所有带有指定href的标签
        tags_with_href = soup.find_all(href=black_href)

        # 从BeautifulSoup对象中删除这些标签
        for tag in tags_with_href:
            tag.decompose()

    # 返回修改后的HTML内容
    return str(soup)

if __name__ == '__main__':
    start_time = time.time()
    get_index_html("https://www.bbc.com/zhongwen/simp/topics/ck2l9z0em07t", 17890)  # 爬取网页 -国际主页

    with open(path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'lxml')  # 创建Beautiful Soup对象

    hrefs_to_remove = import_file_to_list(blacklist_path)  # 将敏感链接文件转为列表
    prohibited_words = import_file_to_list(prohibited_words_path)  # 将敏感词文件转为列表
    # prohibited_words = ['中国', '俄乌战争']  # 敏感词列表

    soup = remove_tags_with_prohibited_words(soup, prohibited_words)  # 返回处理后的soup

    modified_html = str(soup)  # 将BeautifulSoup对象转换回字符串

    save_path = write_html(write_file_path, modified_html, "mod", 1)
    webbrowser.open(save_path)

    end_time = time.time()
    duration = end_time - start_time
    print("程序运行时长：", duration, "秒")
