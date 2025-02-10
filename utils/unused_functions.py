import os
import requests
from bs4 import BeautifulSoup

# rectify：修改本地代理端口号
local_proxy_port = '10809'

proxies = {
    'http': f'http://127.0.0.1:{local_proxy_port}',
    'https': f'http://127.0.0.1:{local_proxy_port}',
}

def contains_prohibited_words(tag):
    prohibited_words = ['中国']
    for word in prohibited_words:
        if word in tag.text:
            return True
    return False

#只处理特定的 <li> 标签。
def remove_tags(soup):
    for li in soup.find_all('li'):
        if li.find_all('li'):
            continue  # If li contains other lis, skip it
        if contains_prohibited_words(li):
            with open("deleted_contents", 'a') as file:
                file.write("删除的标签内容:\n")
                file.write(li.prettify())
                file.write("\n")
            li.extract()
    return str(soup)


def get_content(file_path):  #从本地读取html文件
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content

#base_url:用于构建绝对url
def save_cache_data(html_content,base_url):

    soup = BeautifulSoup(html_content, 'lxml')
    dir_name = transfer_link_to_filename(base_url)
    # 创建一个目录来存储缓存资源
    cache_folder = os.path.join('cache',dir_name)

    os.makedirs(cache_folder, exist_ok=True)

    # 使用Session对象并提供基础URL   创建一个会话对象，可用于发送HTTP请求并保持会话状态
    session = requests.Session()
    session.base_url = base_url
    #常见的图片后缀格式
    extensions = [".png", ".jpg", ".JPEG","GIF","webp"]

    # 下载并缓存图片
    for img in soup.find_all('img'):
        # print("img",img)
        img_url = img['src']
        # 构建绝对URL  如果img_url / 开头，表示它是一个相对路径
        absolute_img_url = session.base_url + img_url if img_url.startswith('/') else img_url
        img_response = session.get(absolute_img_url, proxies=proxies)
        img_data = img_response.content     #图像的二进制数据
        # https://www.xxx.com/images/pic.jpg    -> pic.jpg

        img_name = os.path.basename(absolute_img_url)  #解决img标签下非图片的问题
        if any(img_name.endswith(ext) for ext in extensions):
            img_name = os.path.basename(img_name)
            img_path = os.path.join(cache_folder, img_name)
            print("img_path",img_path)
            if not os.path.exists(img_path):
                with open(img_path, 'ab') as img_file:
                    img_file.write(img_data)
            img['src'] = os.path.join(cache_folder, img_name)  # 更新为本地路径
        else:
            continue

    # # 保存修改后的HTML
    # with open('cached_html.html', 'w', encoding='utf-8') as file:
    #     file.write(soup.prettify())  #格式化HTML文档

def transfer_link_to_filename(base_url):
    filename_list = list(filter(None, base_url.split("/")))
    # print(filename_list)
    filename = filename_list[1]
    return filename
