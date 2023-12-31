import tkinter as tk
from tkinter import ttk

def show():
    name = name_va.get()
    print(f"查询{name}")
    data = [{'num': 524, 'writer': 'anson', 'name': 'i am the best', 'novel_id': 1},
            {'num': 563, 'writer': 'mike', 'name': 'the way', 'novel_id': 13}
        ]
    for i,v in enumerate(data):
        tree_view.insert('', i+1, values=(v['num'], v['writer'], v['name'], v['novel_id']))

def download():
    num = num_va.get()
    print(f"下载{num}")


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
tk.Button(button_frame, text='下载', font=(12), relief='flat',bg='#FAEBD7', width=8).pack(side=tk.LEFT, padx=10)

#设置表格
columns = ('num', 'writer', 'name', 'novel_id')
columns_value = ('序号', '作者', '书名', '书ID')
tree_view =  ttk.Treeview(root, height=18, show='headings', columns=columns)
#设置列名
tree_view.column('num', width=40, anchor='center')
tree_view.column('writer', width=40, anchor='center')
tree_view.column('name', width=40, anchor='center')
tree_view.column('novel_id', width=40, anchor='center')
#给列名设置显示的名字
tree_view.heading('num', text='序号')
tree_view.heading('writer', text='作者')
tree_view.heading('name', text='书名')
tree_view.heading('novel_id', text='书ID')
tree_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
root.mainloop()
