# 被ocr_test.py以及v2.0调用

import tkinter
import tkinter.filedialog
import win32con, win32gui, win32print, win32api


# 获取缩放后的分辨率
def get_screen_size():
    w = win32api.GetSystemMetrics (0)
    h = win32api.GetSystemMetrics (1)
    return w, h


# 获取真实的分辨率
def get_real_size():
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h


class MyCapture:
    def __init__(self, png, win):
        # 变量X和Y用来记录鼠标左键按下的位置
        self.X = tkinter.IntVar(value=0)
        self.Y = tkinter.IntVar(value=0)

        self.selectPosition = None
        # 屏幕尺寸
        screenWidth, screenHeight = get_real_size()
        # 创建顶级组件容器
        self.top = tkinter.Toplevel(win, width=screenWidth, height=screenHeight)
        # 不显示最大化、最小化按钮
        self.top.overrideredirect(True)
        self.canvas = tkinter.Canvas(self.top, bg='white', width=screenWidth, height=screenHeight)
        # 显示全屏截图，在全屏截图上进行区域截图
        self.img = tkinter.PhotoImage(file=png)
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        # Button表示一个按钮事件，1代表鼠标左键，2中键，3右键
        # bind-all是全局绑定，通常用于全局快捷键
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
        # 当鼠标左键抬起时代表截图结束，销毁顶层容器
        self.top.destroy()
