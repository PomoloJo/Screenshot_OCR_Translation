# ocr小软件第二版_v2.2_20210113

from aip import AipOcr
import tkinter.filedialog
import tkinter.messagebox
import tkinter
import json
import winreg
import win32ui
import os
from PIL import ImageGrab
from BaiduTransAPIforPython3 import baidutrans
from functions import screenshot_2
import configparser
import pyperclip


# 读取配置文件
config = configparser.ConfigParser()
ini_address = './config.ini'
if not os.path.exists(ini_address):
    config.add_section('HOTKEY')
    config.set('HOTKEY', 'capture', 'q')
    config.set('HOTKEY', 'capture_trans', 'w')
    config.add_section('BaiduAipOcr')
    config.set('BaiduAipOcr', 'app_id', 'None')
    config.set('BaiduAipOcr', 'api_key', 'None')
    config.set('BaiduAipOcr', 'secret_key', 'None')
    config.add_section('BaiduTransAPI')
    config.set('BaiduTransAPI', 'app_id', 'None')
    config.set('BaiduTransAPI', 'secret_key', 'None')
    config.add_section('ClipSetting')
    config.set('ClipSetting', 'mode', '1')
    config.write(open('config.ini', 'w'))
    config.read(ini_address, encoding="utf-8")
else:
    config.read(ini_address, encoding="utf-8")

'''
    !!! 这样读取，用户修改以后可能要重启软件才能生效 !!!
'''
APP_ID = config['BaiduAipOcr']['APP_ID']
API_KEY = config['BaiduAipOcr']['API_KEY']
SECRET_KEY = config['BaiduAipOcr']['SECRET_KEY']
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

TRANS_ID = config['BaiduTransAPI']['app_id']
TRANS_SKEY = config['BaiduTransAPI']['secret_key']
trans_id_skey = (TRANS_ID, TRANS_SKEY)


# 主窗体，继承tkinter.Tk
class MyWin(tkinter.Tk):
    def __init__(self):
        super(MyWin, self).__init__()
        # 窗口布局
        # win = tkinter.Tk()
        self.title('Ocr&Translation_v2.1')
        self.geometry('900x600')

        # 初始化tfw几何信息与颜色与透明度
        self.tfw_geo_info = (0, 0, 0, 0)
        self.color = 255
        self.alpha = 0.3

        self.frame_left = tkinter.Frame(self)
        self.button_input = tkinter.Button(self.frame_left, width=25, height=3, text='打开图片并识别', command=self.process)
        self.button_output = tkinter.Button(self.frame_left, width=25, height=3, text='输出为txt', command=self.textOutput)
        self.button_capture = tkinter.Button(self.frame_left, width=25, height=3, command=self.buttonCaptureClick)
        self.button_capture['text'] = '截图识别\n快捷键（区分大小写） Ctrl+'+config['HOTKEY']['CAPTURE']
        self.button_trans = tkinter.Button(self.frame_left, width=25, height=3, text='翻译', command=self.trans)
        self.button_captureAndTrans = tkinter.Button(self.frame_left, width=25, height=3, command=self.captureAndTrans)
        self.button_captureAndTrans['text'] = '截图识别并翻译\n快捷键（区分大小写） Ctrl+'+config['HOTKEY']['CAPTURE_TRANS']
        self.button_clear = tkinter.Button(self.frame_left, width=25, height=3, text='清空所有内容', command=self.clearAll)
        self.button_tfw = tkinter.Button(self.frame_left, width=25, height=3, text='透明悬浮窗模式（测试）', command=self.floatingWindow)
        self.button_setting = tkinter.Button(self.frame_left, width=25, height=3, text='设置', command=self.setting)
        self.text_1 = tkinter.Text(self)
        self.text_2 = tkinter.Text(self)

        self.frame_left.pack(side='left', anchor='w', fill='y')
        self.text_1.pack(anchor='ne', fill='both', expand='yes')
        self.text_2.pack(anchor='ne', fill='both', expand='yes')
        self.button_input.pack(side='top', anchor='nw', fill='x')
        self.button_output.pack(side='top', anchor='nw', fill='x')
        self.button_capture.pack(side='top', anchor='nw', fill='x')
        self.button_trans.pack(side='top', anchor='nw', fill='x')
        self.button_captureAndTrans.pack(side='top', anchor='nw', fill='x')
        self.button_clear.pack(side='top', anchor='nw', fill='x')
        self.button_tfw.pack(side='top', anchor='nw', fill='x')
        self.button_setting.pack(side='top', expand='yes', anchor='sw', fill='x')


        # bind-all是全局绑定，通常用于全局快捷键
        # bind和bind-all第二个参数是事件，需要如下修改
        self.order_ctrl_1 = '<Control-{}>'.format(config['HOTKEY']['CAPTURE'])
        self.order_ctrl_2 = '<Control-{}>'.format(config['HOTKEY']['CAPTURE_TRANS'])

        self.bind_all(self.order_ctrl_1, lambda event: self.buttonCaptureClick())
        self.bind_all(self.order_ctrl_2, lambda event: self.captureAndTrans())

    # 找到桌面绝对路径
    def getDesktopPath(self):
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]

    # 读取图片
    def getFileContent(self, fpath):
        with open(fpath, 'rb') as fp:
            return fp.read()

    # 打开图片处理
    def process(self):
        try:
            fpath = tkinter.filedialog.askopenfilename(
                title='选择图片',
                filetypes=[('PIC', '*.png *.jpg *jpeg'), ('All Files', '*')]
            )
            image = self.getFileContent(fpath)
            te = client.basicAccurate(image)  # string
            te = json.dumps(te)  # unicode
            te = json.loads(te)  # utf8?
            for i in te["words_result"]:
                self.text_1.insert("insert", (str(i["words"] + "\n")))  # "insert"表示从当前光标处插入
        except Exception as e:
            tkinter.messagebox.showinfo('提示', '识别失败，请检查网络环境和“设置”选项中的“OCRAPI”')
            print(type(e), e)

    # 输出为txt
    def textOutput(self):
        try:
            if self.text_1.get('0.0', 'end') == '\n':
                tkinter.messagebox.showinfo('提示', '无法输出，文本内容为空！')
            else:
                dlg = win32ui.CreateFileDialog(0)
                dlg.SetOFNInitialDir(self.getDesktopPath())
                flag = dlg.DoModal()
                if flag == 1:
                    if '.txt' in dlg.GetPathName():
                        f = open(dlg.GetPathName(), 'w')
                    else:
                        f = open(dlg.GetPathName() + '.txt', 'w')
                    print(self.text_1.get('0.0', 'end'), file=f)
                    tkinter.messagebox.showinfo('提示', '处理完成')
                    f.close()
                else:
                    print("取消另存为...")
        except Exception as e:
            print(type(e), e)

    # 截图识别
    def buttonCaptureClick(self):
        try:
            # 最小化主窗口
            self.state('icon')
            # sleep(0.1)
            filename = 'temp.png'
            x, y = screenshot_2.get_real_size()
            im = ImageGrab.grab((0, 0, x, y))
            im.save(filename)
            # 显示全屏幕截图
            w = screenshot_2.MyCapture(filename, self)
            self.button_capture.wait_window(w.top)
            # text.set(str(w.selectPosition))
            x1, x2, y1, y2 = w.selectPosition
            im2 = im.crop((x1, y1, x2, y2))
            im2.save('temp_2.png')
            # 截图结束，恢复主窗口，并删除临时的全屏幕截图文件
            image = self.getFileContent('temp_2.png')
            te = client.basicAccurate(image)  # string
            te = json.dumps(te)  # unicode
            te = json.loads(te)  # utf8?
            for i in te["words_result"]:
                self.text_1.insert("insert", (str(i["words"] + "\n")))  # "insert"表示从当前光标处插入
            im2.close()
            im.close()
            self.state('normal')
            os.remove(filename)
            os.remove('temp_2.png')
            if config['ClipSetting']['mode'] == '2':
                pyperclip.copy(self.text_1.get('0.0', 'end'))
        except Exception as e:
            tkinter.messagebox.showinfo('提示', '识别失败，请检查网络环境和“设置”选项中的“OCRAPI”')
            print(type(e), e)

    # 翻译
    def trans(self):
        try:
            if self.text_1.get('0.0', 'end') == '\n':
                tkinter.messagebox.showinfo('提示', '内容为空！')
            else:
                te = baidutrans(trans_id_skey, (self.text_1.get('0.0', 'end')))
                for i in te["trans_result"]:
                    self.text_2.insert("insert", (str(i["dst"] + "\n")))
                if config['ClipSetting']['mode'] == '3':
                    pyperclip.copy(self.text_2.get('0.0', 'end'))
        except Exception as e:
            tkinter.messagebox.showinfo('提示', '翻译失败，请检查网络环境和“设置”选项中的“TRANSAPI”')
            print(type(e), e)

    # 截图识别并翻译
    def captureAndTrans(self):
        self.text_1.delete('0.0', 'end')
        self.text_2.delete('0.0', 'end')
        self.buttonCaptureClick()
        self.trans()

    # 清空所有内容
    def clearAll(self):
        self.text_1.delete('0.0', 'end')
        self.text_2.delete('0.0', 'end')

    # 透明浮窗模式
    def floatingWindow(self):
        self.tfw = tkinter.Toplevel(self, width=450, height=300)
        self.tfw['background']='#00BFFF'
        self.tfw.attributes("-alpha", self.alpha)
        # True隐藏所有边框，包括最大化、最小化、关闭按钮, False取消隐藏
        self.tfw.overrideredirect(True)
        self.tfw.title('transparent floating window (测试阶段)')
        # 主界面最小化的同时，将焦点和窗口都锁定到tfw，就可以隐藏主界面，又不会丢失tfw找不回来
        self.state('icon')
        self.tfw.grab_set()  # 窗口锁定在tfw上
        self.tfw.focus_set()  # 焦点锁定在tfw上
        # (已弃用)截获并修改右上角自带红色关闭按钮的功能，导向自定义功能
        # self.tfw.protocol('WM_DELETE_WINDOW', self.closeTfw)

        # 鼠标动作绑定
        self.tfw.bind('<ButtonPress-1>', self.startMoveB1)
        self.tfw.bind('<ButtonRelease-1>', self.stopMoveB1)
        self.tfw.bind('<B1-Motion>', self.onMotionB1)
        self.tfw.bind('<Double-Button-1>', self.captureDoubleClick)

        self.tfw.bind('<B3-Motion>', self.onMotionB3)
        self.tfw.bind('<ButtonRelease-3>', self.stopMoveB3)
        self.tfw.bind('<Double-Button-3>', self.closeTfw)

        self.tfw.bind('<ButtonPress-2>', self.startMoveB2)
        self.tfw.bind('<B2-Motion>', self.onMotionB2)

    # 按下鼠标中键,记录初始位置
    def startMoveB2(self, event):
        self.x = event.x_root
        self.y = event.y_root

    # 鼠标中键改变tfw颜色和透明度，暂无保存到配置文件的功能
    def onMotionB2(self, event):
        try:
            # 这里必须记录下鼠标点击时的self.x不能直接event.x_root，不然会因为刚开始时窗口和屏幕都位于(0,0)而拖不动窗口
            self.delta_x = int((event.x_root - self.x)/32)
            self.delta_y = int((event.y_root - self.y)/32)
            if 0 < self.color + self.delta_y < 255:
                self.color += self.delta_y
                self.tfw['background'] = '#%02x%02x%02x' % (0, self.color, 255)
            if 0.1 < self.alpha + self.delta_x/128 < 0.7:
                self.alpha += self.delta_x/128
                self.tfw.attributes('-alpha', self.alpha)
        except Exception as e:
            print(type(e), e)

    # 绑定到了右键双击，退出tfw
    def closeTfw(self, event):
        # 重新显示主界面
        self.deiconify()
        # 破坏tfw实现退出
        self.tfw.destroy()

    # 窗口移动事件，有bug，因为鼠标和窗口都属于event，所以会不断互相干扰，拖拽时产生振动
    # 原因发现了，要用event.x_root：
    #   相对于应用程序左上角的位置,左键点击的位置是 event.x, event.y
    #   相对于屏幕左上角的位置,左键点击的位置是 event.x_root, event.y_root
    def startMoveB1(self, event):
        self.x = event.x
        self.y = event.y

    def onMotionB1(self, event):
        try:
            # 这里必须记录下鼠标点击时的self.x不能直接event.x，不然会因为刚开始时窗口和屏幕都位于(0,0)而拖不动窗口
            self.delta_x = event.x_root - self.x
            self.delta_y = event.y_root - self.y
            self.tfw.geometry("+{}+{}".format(self.delta_x, self.delta_y))
        except Exception as e:
            print(type(e), e)

    def stopMoveB1(self, event):
        self.x = None
        self.y = None
        # 获取tfw几何信息
        self.tfw_geo_info = (self.tfw.winfo_x(), self.tfw.winfo_y(), self.tfw.winfo_width(), self.tfw.winfo_height())

    def onMotionB3(self, event):
        try:
            self.delta_x = self.tfw.winfo_pointerx() - self.tfw.winfo_rootx()
            self.delta_y = self.tfw.winfo_pointery() - self.tfw.winfo_rooty()
            self.tfw.geometry("{}x{}".format(self.delta_x, self.delta_y))
        except Exception as e:
            print(type(e), e)

    def stopMoveB3(self, event):
        self.tfw_geo_info = (self.tfw.winfo_x(), self.tfw.winfo_y(), self.tfw.winfo_width(), self.tfw.winfo_height())

    # 双击后把透明浮窗所在区域截图截出来
    def captureDoubleClick(self, event):
        try:
            # 隐藏窗口
            self.tfw.withdraw()
            filename = 'temp.png'
            x, y = screenshot_2.get_real_size()
            im = ImageGrab.grab((0, 0, x, y))
            im.save(filename)
            x, y, w, h = self.tfw_geo_info
            im2 = im.crop((x, y, x+w, y+h))
            im2.save('temp_2.png')
            # 截图结束，识别
            image = self.getFileContent('temp_2.png')
            te = client.basicAccurate(image)  # string
            te = json.dumps(te)  # unicode
            te = json.loads(te)  # utf8?
            self.clearAll()
            for i in te["words_result"]:
                self.text_1.insert("insert", (str(i["words"] + "\n")))  # "insert"表示从当前光标处插入
            im2.close()
            im.close()
            # 恢复tfw，并删除临时的全屏幕截图文件
            os.remove(filename)
            os.remove('temp_2.png')
            if config['ClipSetting']['mode'] == '2':
                pyperclip.copy(self.text_1.get('0.0', 'end'))
            self.tfw.deiconify()
        except Exception as e:
            tkinter.messagebox.showinfo('提示', '识别失败，请检查网络环境和“设置”选项中的“OCRAPI”')
            self.tfw.destroy()
            self.deiconify()
            print(type(e), e)

    # 设置的弹出窗口
    def setting(self):
        self.top = tkinter.Toplevel(self, width=900, height=600)
        self.top.resizable(0, 0)  # 锁定窗体大小
        # 只能弹出一个窗口，且必须关闭才能处理原窗口
        self.top.grab_set()  # 窗口锁定在top上
        self.top.focus_set()  # 焦点锁定在top上
        # True隐藏包括按钮在内的边框, False取消隐藏
        self.top.overrideredirect(False)
        self.top.title('setting(测试阶段)')

        # 快捷键设置区域
        self.label_frame_key = tkinter.LabelFrame(self.top, text='更改快捷键')
        # 截图识别快捷键
        self.content_key_1 = tkinter.StringVar()
        self.key_capture_1 = self.button_capture['text'].split('+', -1)
        self.content_key_1.set(self.key_capture_1[-1])
        self.entry_setting_key_1 = tkinter.Entry(self.label_frame_key, textvariable=self.content_key_1, state='readonly')
        #self.entry_setting_key_1.insert("insert", key_capture_1[-1])
        # 给输入框绑定按键监听事件<Key>为监听任何按键 <Key-x>监听其它键盘，如大写的A<Key-A>、回车<Key-Return>
        self.entry_setting_key_1.bind('<Key>', func=self.changeKey_1)
        self.label_setting_key_1 = tkinter.Label(self.label_frame_key, text='更改截图识别快捷键: Ctrl + ')

        # 截图识别翻译快捷键
        self.content_key_2 = tkinter.StringVar()
        self.key_capture_2 = self.button_captureAndTrans['text'].split('+', -1)
        self.content_key_2.set(self.key_capture_2[-1])
        self.entry_setting_key_2 = tkinter.Entry(self.label_frame_key, textvariable=self.content_key_2, state='readonly')
        #self.entry_setting_key_2.insert("insert", key_capture_2[-1])
        self.entry_setting_key_2.bind('<Key>', func=self.changeKey_2)
        self.label_setting_key_2 = tkinter.Label(self.label_frame_key, text='更改截图识别并翻译快捷键: Ctrl + ')

        # OCRAPI设置区域
        self.label_frame_api_ocr = tkinter.LabelFrame(self.top, text='更改OCRAPI')
        # 修改ocr_app_id
        self.content_ocrapi_id = tkinter.StringVar()
        self.content_ocrapi_id.set(config['BaiduAipOcr']['APP_ID'])
        self.entry_ocrapi_id = tkinter.Entry(self.label_frame_api_ocr, textvariable=self.content_ocrapi_id, width=35)
        self.label_ocrapi_id = tkinter.Label(self.label_frame_api_ocr, text='APP_ID: ')
        # 修改ocr_api_key
        self.content_ocrapi_key = tkinter.StringVar()
        self.content_ocrapi_key.set(config['BaiduAipOcr']['API_KEY'])
        self.entry_ocrapi_key = tkinter.Entry(self.label_frame_api_ocr, textvariable=self.content_ocrapi_key, width=35)
        self.label_ocrapi_key = tkinter.Label(self.label_frame_api_ocr, text='API_KEY: ')
        # 修改ocr_secret_key
        self.content_ocrapi_skey = tkinter.StringVar()
        self.content_ocrapi_skey.set(config['BaiduAipOcr']['SECRET_KEY'])
        self.entry_ocrapi_skey = tkinter.Entry(self.label_frame_api_ocr, textvariable=self.content_ocrapi_skey, width=35)
        self.label_ocrapi_skey = tkinter.Label(self.label_frame_api_ocr, text='SECRET_KEY: ')

        # TRANSAPI设置区域
        self.label_frame_api_trans = tkinter.LabelFrame(self.top, text='更改TRANSAPI')
        # 修改ocr_app_id
        self.content_transapi_id = tkinter.StringVar()
        self.content_transapi_id.set(config['BaiduTransAPI']['app_id'])
        self.entry_transapi_id = tkinter.Entry(self.label_frame_api_trans, textvariable=self.content_transapi_id, width=35)
        self.label_transapi_id = tkinter.Label(self.label_frame_api_trans, text='APP_ID: ')
        # 修改ocr_secret_key
        self.content_transapi_skey = tkinter.StringVar()
        self.content_transapi_skey.set(config['BaiduTransAPI']['secret_key'])
        self.entry_transapi_skey = tkinter.Entry(self.label_frame_api_trans, textvariable=self.content_transapi_skey, width=35)
        self.label_transapi_skey = tkinter.Label(self.label_frame_api_trans, text='SECRET_KEY: ')

        # 粘贴板设置区域
        self.label_frame_clip = tkinter.LabelFrame(self.top, text='粘贴板功能设置')
        self.v = tkinter.IntVar()
        self.v.set(config['ClipSetting']['mode'])
        self.button_clip_1 = tkinter.Radiobutton(self.label_frame_clip, text='Null', value=1, variable=self.v)
        self.button_clip_2 = tkinter.Radiobutton(self.label_frame_clip, text='截图识别自动复制',value=2, variable=self.v)
        self.button_clip_3 = tkinter.Radiobutton(self.label_frame_clip, text='翻译完成自动复制',value=3, variable=self.v)

        # 确定按键
        self.button_change = tkinter.Button(self.top, text='确认修改',
                                           width=10, height=1,
                                           command=self.buttonChangeClick)


        # 显示窗体
        self.label_frame_key.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=tkinter.EW)
        # 以下属于label_frame_key
        self.label_setting_key_1.grid(row=0, column=0, ipadx=10, ipady=5)
        self.entry_setting_key_1.grid(row=0,column=1)
        self.label_setting_key_2.grid(row=1, column=0, ipadx=10, ipady=5)
        self.entry_setting_key_2.grid(row=1, column=1)

        self.label_frame_api_ocr.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tkinter.EW)
        # 以下属于label_frame_api_ocr
        self.label_ocrapi_id.grid(row=0, column=0, ipadx=10, ipady=5)
        self.entry_ocrapi_id.grid(row=0, column=1)
        self.label_ocrapi_key.grid(row=1, column=0, ipadx=10, ipady=5)
        self.entry_ocrapi_key.grid(row=1, column=1)
        self.label_ocrapi_skey.grid(row=2, column=0, ipadx=10, ipady=5)
        self.entry_ocrapi_skey.grid(row=2, column=1)

        self.label_frame_api_trans.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky=tkinter.EW)
        # 以下属于label_frame_api_trans
        self.label_transapi_id.grid(row=0, column=0, ipadx=10, ipady=5)
        self.entry_transapi_id.grid(row=0, column=1)
        self.label_transapi_skey.grid(row=1, column=0, ipadx=10, ipady=5)
        self.entry_transapi_skey.grid(row=1, column=1)

        self.label_frame_clip.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky=tkinter.EW)
        # 以下属于label_frame_api_trans
        self.button_clip_1.grid(row=0, column=0, ipadx=10, ipady=5)
        self.button_clip_2.grid(row=0, column=1, ipadx=10, ipady=5)
        self.button_clip_3.grid(row=0, column=2, ipadx=10, ipady=5)

        self.button_change.grid(row=4, column=1)


    # 在控制台显示监听到的按键并改变为当前值
    def changeKey_1(self, ke):
        if 48 <= ke.keycode <= 57 or 65 <= ke.keycode <= 90:
            self.content_key_1.set(ke.char)
        # 分别是按键别名，按键对应的字符，按键的唯一代码，用于判断按下的是哪个键</class></key></button-1>
        print(" ke.keysym: ", ke.keysym, " ke.char: ", ke.char, " ke.keycode: ", ke.keycode)

    # 在控制台显示监听到的按键并改变为当前值
    def changeKey_2(self, ke):
        if 48 <= ke.keycode <= 57 or 65 <= ke.keycode <= 90:
            self.content_key_2.set(ke.char)
        # 分别是按键别名，按键对应的字符，按键的唯一代码，用于判断按下的是哪个键</class></key></button-1>
        print(" ke.keysym: ", ke.keysym, " ke.char: ", ke.char, " ke.keycode: ", ke.keycode)

    # 按下确认键
    def buttonChangeClick(self):
        try:
            # 修改界面快捷键提示
            self.button_capture['text'] = '截图识别\n快捷键ctrl+' + self.content_key_1.get()
            self.button_captureAndTrans['text'] = '截图识别并翻译\n快捷键ctrl+' + self.content_key_2.get()
            # 修改config配置文件
            self.order_ctrl_1 = '<Control-{}>'.format(self.content_key_1.get())
            self.order_ctrl_2 = '<Control-{}>'.format(self.content_key_2.get())
            config.set('HOTKEY', 'capture', self.content_key_1.get())
            config.set('HOTKEY', 'capture_trans', self.content_key_2.get())
            config.set('BaiduAipOcr', 'app_id', self.content_ocrapi_id.get())
            config.set('BaiduAipOcr', 'api_key', self.content_ocrapi_key.get())
            config.set('BaiduAipOcr', 'secret_key', self.content_ocrapi_skey.get())
            config.set('BaiduTransAPI', 'app_id', self.content_transapi_id.get())
            config.set('BaiduTransAPI', 'secret_key', self.content_transapi_skey.get())
            config.set('ClipSetting', 'mode', str(self.v.get()))
            config.write(open(ini_address, "w+", encoding="utf-8"))
            # 函数绑定后不会随着变量改变而自动刷新，需要重新绑定
            self.bind_all(self.order_ctrl_1, lambda event: self.buttonCaptureClick())
            self.bind_all(self.order_ctrl_2, lambda event: self.captureAndTrans())
        except Exception as e:
            print(type(e), e)


def main():
    win = MyWin()
    win.mainloop()


if __name__ == '__main__':
    main()
