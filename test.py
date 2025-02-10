from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_file():
    Tk().withdraw()  # 隐藏根窗口
    filename = askopenfilename()  # 打开文件选择对话框
    if filename:
        print("选择的文件是：", filename)

select_file()