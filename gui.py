# gui.py
import time
import sys
from tkinter.filedialog import askopenfilename
from bs4 import BeautifulSoup
import webbrowser
import tkinter as tk
from urllib.parse import urlparse
from ttkbootstrap import Style
from filter_index_page import write_html
from filter_index_page import get_index_html,remove_tags_with_prohibited_words
from filter_index_page import import_file_to_list,get_save_path



############# global variable settings ###########################
window_width = 400
window_height = 200
close_action_performed=False  #检测是否点击了关闭或者取消按钮
global_test_url = ""  # 初始化全局变量url值 为空
hrefs_to_remove = []
blacklist_path = './utils/forbidden_words_cover.txt'
prohibited_words_path = './utils/forbidden_words_cover.txt'
write_file_path = "./modified/"   # 过滤后网页写入位置
local_save_path = "./save_webpages"  # 爬取网页保存到本地的位置

# 在原文件基础上追加   gai
def save_bid_words(forbidden_words):
    # 指定要保存违禁词的文本文件名
    filename = "forbidden_words.txt"
    # 将用户输入的违禁词按空格分割成列表，并去除可能的空白字符
    new_words_list = forbidden_words.split()
    # 读取原有文件中的违禁词并存入集合，以便快速检查重复
    existing_words = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # 去除每行的前后空白字符和换行符
                word = line.strip()
                if word:  # 确保不为空
                    existing_words.add(word)
    except FileNotFoundError:
        pass

    # 打开文件，准备追加新的违禁词
    with open(filename, 'a', encoding='utf-8') as file:
        for word in new_words_list:
            # 如果违禁词不在原有文件中，则追加到文件末尾
            if word not in existing_words:
                file.write(word + '\n')
            #     print(f"违禁词 '{word}' 已添加。")
            # else:
            #     print(f"违禁词 '{word}' 已存在，未添加。")

# 覆盖原文件
def save_bid_words_and_cover(forbidden_words):

    # 将用户输入的违禁词按空格分割成列表，并去除可能的空白字符
    new_words_list = forbidden_words.split()
    # 打开文件，准备填写新的违禁词
    with open(blacklist_path, 'w', encoding='utf-8') as file:
        for word in new_words_list:
            file.write(word + '\n')

def save_searched_url(url):
    # 指定要保存网址的文本文件名
    filename = "searched_urls.txt"

    # 读取原有文件中的url并存入集合，以便快速检查重复
    existing_words = set()
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # 去除每行的前后空白字符和换行符
                word = line.strip()
                if word:  # 确保不为空
                    existing_words.add(word)
    except FileNotFoundError:
        pass

    with open(filename, 'a', encoding='utf-8') as file:
        if url not in existing_words:
            file.write(url + '\n')
            print(f"url '{url}' 已添加。")
        else:
            print(f"url'{url}' 已存在，未添加。")
    # 可选：确认网址写入成功
    # print(f"网址已保存到文件：{filename}")

def complete_url_scheme(url):  #规范url
    # 解析URL，检查是否包含scheme
    parsed_url = urlparse(url)
    # 如果没有scheme，则添加默认的http方案
    if not parsed_url.scheme:
        url = 'http://' + url  # 或者使用 'https://'

    return url

# 待更新
def is_valid_url(url):
    # 尝试解析URL
    result = urlparse(url)
    # 检查URL是否包含网络位置部分
    if not all([result.scheme, result.netloc]):
        # 如果没有scheme或netloc，则认为URL无效，抛出异常
        return False
    return True

def check_inputs(url,forbid):
    # 假设 entry.get() 和 entry2.get() 是两个方法，返回用户输入的字符串
    strip_url = url.strip()  # 使用 .strip() 去除字符串两端的空格
    strip_forbid = forbid.strip()
    # url = complete_url_scheme(url)
    if not strip_url or not strip_forbid :
        return 0
    if is_valid_url(url)==0:
        print("无效的网址格式！请重新输入")
        return 0,0
    return url,forbid

def run_gui():

    def import_file():
        try:
            filename = askopenfilename()  # 打开文件选择对话框
            if filename:
                data = ''
                print("选择的文件是：", filename)
                if not filename.endswith('.txt'):
                    raise ValueError("文件后缀必须为'.txt'")
                with open(filename, 'r') as file:
                    for line in file:
                        line = line.strip()  # 去除行尾换行符和空白字符
                        data += line + ' '
                    # 将数据放入左边的输入框
                    entry2.delete(0, 'end')  #删除输入框中的文本内容
                    entry2.insert('end', data)
        except FileNotFoundError:
            print("文件未找到")
        except ValueError as e:
            print("错误：", str(e))

    def get_base_url_and_bid_words():  #获取网址并赋值给 global_base_url
        # try:
        global global_test_url
        global_test_url = entry.get()
        forbidden_words = entry2.get()
        global_base_url,forbidden_words = check_inputs(global_test_url,forbidden_words)
        if global_test_url and forbidden_words :
            save_searched_url(global_base_url)
            save_bid_words_and_cover(forbidden_words)
            print("您输入的网址是：", global_base_url)
            print("要过滤的违禁词:", forbidden_words)
            runs()
            # root.destroy()
        else:
            print("网址/违禁词为空,请检查后重新输入")
        # 待完善
        # except Exception as e:
        #     print(e)
    def on_button_press(event): # 在绑定回车键事件时，会自动传递一个event参数给事件处理函数
        # print(event)
        get_base_url_and_bid_words()

    def cancel():
        print("取消按钮被点击")
        global close_action_performed
        close_action_performed=True
        # 在这里执行取消操作
        root.destroy()  # 关闭窗口

    def close_window():
        print("程序正在关闭...")
        global close_action_performed
        close_action_performed = True
        root.destroy()

    root = tk.Tk()
    root.title("获取网址")
    style = Style()
    #['cyborg', 'journal', 'darkly', 'flatly', 'clam', 'alt', 'solar', 'minty', 'litera', 'united', 'xpnative', 'pulse
    style.theme_use('sandstone')
    # 获取屏幕宽度和高度
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 计算窗口左上角坐标使其居中
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    label1 = tk.Label(root, text="请输入您要访问的完整网址：")
    label1.place(relx=0.5, rely=0.1, anchor=tk.CENTER)  # 放在高度的10%位置

    label2 = tk.Label(root, text="请输入要过滤的违禁词(按空格间隔)：")
    label2.place(relx=0.5, rely=0.4, anchor=tk.CENTER)  # 放在高度的40%位置

    entry = tk.Entry(root, width=40)  # 设置输入框的宽度
    entry.place(relx=0.5, rely=0.2, anchor=tk.CENTER)  # 放在高度的20%位置

    entry2 = tk.Entry(root, width=40)  # 设置输入框的宽度
    entry2.place(relx=0.5, rely=0.5, anchor=tk.CENTER)  # 放在高度的50%位置

    select_file = tk.Button(root, text="选择", command=import_file)
    select_file.place(relx=0.9, rely=0.5, anchor=tk.CENTER)

    # 添加确认按钮
    button_confirm = tk.Button(root, text="确认", command=get_base_url_and_bid_words)
    button_confirm.place(relx=0.4, rely=0.7, anchor=tk.CENTER)

    # root.bind("<Return>", on_button_press)
    root.bind("<Return>", on_button_press)

    # 绑定<WM_DELETE_WINDOW>事件到close_window函数
    root.protocol("WM_DELETE_WINDOW", close_window)
    # 添加取消按钮
    button_cancel = tk.Button(root, text="取消", command=cancel)
    button_cancel.place(relx=0.6, rely=0.7, anchor=tk.CENTER)

    # 设置窗口位置和大小
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    root.mainloop()

def runs():
    global hrefs_to_remove
    flag = close_action_performed
    if not flag:  # 未关闭
        global_base_url = global_test_url
        # print("global_base_url", global_base_url)

        #page_save_path:爬取的页面保存在本地的路径
        page_save_path = get_save_path(base_url=global_base_url,path=local_save_path,suffix=1)
        # print("page_save_path:", page_save_path)

        full_write_file_path = get_save_path(base_url= global_base_url,path=write_file_path,suffix=0)
        # print("full_write_file_path:",full_write_file_path)
        start_time = time.time()
        get_index_html(global_base_url,page_save_path)  # 爬取网页

        with open(page_save_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        soup = BeautifulSoup(html_content, 'lxml')  # 创建Beautiful Soup对象

        hrefs_to_remove = import_file_to_list(blacklist_path)  # 将敏感链接文件转为列表
        prohibited_words = import_file_to_list(prohibited_words_path)  # 将敏感词文件转为列表
        print("hrefs_to_remove",hrefs_to_remove)
        print("prohibited_words",prohibited_words)
        # prohibited_words = ['中国', '俄乌战争']  # 敏感词列表

        soup = remove_tags_with_prohibited_words(soup, prohibited_words)  # 返回处理后的soup

        modified_html = str(soup)  # 将BeautifulSoup对象转换回字符串

        save_path = write_html(full_write_file_path, modified_html, "mod", 1)
        webbrowser.open(save_path)

        end_time = time.time()
        duration = end_time - start_time
        print("程序运行时长：", duration, "秒")
    else:
        sys.exit()



