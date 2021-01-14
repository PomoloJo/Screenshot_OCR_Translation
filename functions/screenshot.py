# 没有被调用

import tkinter
import tkinter.filedialog
import os
from PIL import ImageGrab
from tkinter import StringVar
import win32con, win32gui, win32print, win32api


# 创建tkinter主窗口
root = tkinter.Tk()
# 指定主窗口位置与大小
root.geometry('200x80+400+300')
# 不允许改变窗口大小
root.resizable(False, False)


def get_screen_size():
    """获取缩放后的分辨率"""
    w = win32api.GetSystemMetrics (0)
    h = win32api.GetSystemMetrics (1)
    return w, h


def get_real_size():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h


class MyCapture:
    def __init__(self, png):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)

        self.selectPosition = None
        # 屏幕尺寸
        screenWidth = root.winfo_screenwidth()
        screenHeight = root.winfo_screenheight()
        # 创建顶级组件容器
        self.top = tkinter.Toplevel(root, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.img = tkinter.PhotoImage(file=png)
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        self.canvas.bind('<Button-1>', self.onLeftButtonDown)
        self.canvas.bind('<B1-Motion>', self.onLeftButtonMove)
        self.canvas.bind('<ButtonRelease-1>', self.onLeftButtonUp)
        self.canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    # 鼠标左键按下的位置
    def onLeftButtonDown(self, event):
        self.X.set(event.x)
        self.Y.set(event.y)
        # 开始截图
        self.sel = True

    # 鼠标左键移动，显示选取的区域
    def onLeftButtonMove(self, event):
        if not self.sel:
            return
        global lastDraw
        try:
            # 删除刚画完的图形，要不然鼠标移动的时候是黑乎乎的一片矩形
            self.canvas.delete(lastDraw)
        except Exception as e:
            print(type(e), e)
        lastDraw = self.canvas.create_rectangle(self.X.get(), self.Y.get(), event.x, event.y, outline='black')

    # 获取鼠标左键抬起的位置，保存区域截图
    def onLeftButtonUp(self, event):
        self.sel = False
        try:
            self.canvas.delete(lastDraw)
        except Exception as e:
            pass
        # sleep(0.1)
        # # 考虑鼠标左键从右下方按下而从左上方抬起的截图
        myleft, myright = sorted([self.X.get(), event.x])
        mytop, mybottom = sorted([self.Y.get(), event.y])
        self.selectPosition = (myleft, myright, mytop, mybottom)
        self.top.destroy()


text = StringVar()
text.set('nodata')


def buttonCaptureClick():
    # 最小化主窗口
    root.state('icon')
    # sleep(0.1)

    filename = 'temp.png'
    x, y = get_real_size()
    im = ImageGrab.grab((0, 0, x, y))
    im.save(filename)
    #im.close()
    # 显示全屏幕截图
    w = MyCapture(filename)
    buttonCapture.wait_window(w.top)
    #text.set(str(w.selectPosition))
    x1, x2, y1, y2 = w.selectPosition
    im2 = im.crop((x1, y1, x2, y2))
    im2.save('temp_2.png')
    im2.close()
    im.close()
    # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件
    root.state('normal')
    os.remove(filename)


label = tkinter.Label(root, textvariable=text)
label.place(x=10, y=30, width=160, height=20)
label.config(text='New test')
buttonCapture = tkinter.Button(root, text='截图', command=buttonCaptureClick)
buttonCapture.place(x=10, y=10, width=160, height=20)
# 启动消息主循环
# root.update()
root.mainloop()