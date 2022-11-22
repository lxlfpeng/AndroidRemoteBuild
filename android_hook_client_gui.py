import tkinter as tk
from tkinter.filedialog import askdirectory
import os
from android_git import GitCommand
import json
import requests
from android_adb import AndroidAdb
from android_aapt_parse import ApkInfo
import socket
from ftp_server import FtpServerThread
import time


class MakeApkGui:

    def __init__(self):
        # 设置默认参数
        if not os.path.exists('./android/setting.json'):
            self.create_default_setting()
        # 读取配置参数
        json_setting = open('./android/setting.json', encoding="utf-8")
        self.request_data  = json.load(json_setting)
        # 读取已修改的文件
        self.request_data ['diffFiles'] = GitCommand(self.request_data['local_project_path']).getChangeFiles()
        # ftp服务器连接相关设置
        self.request_data['ftpHost'] = self.get_host_ip()
        #开启ftpserver
        self.create_and_run_ftp()
       
    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height,
                                (screenwidth - width)/2, (screenheight - height)/2)
        root.geometry(size)

    def make_input_item(self, frame, label, defalut_value):
        frame_back = tk.Frame(frame)
        input_value = tk.StringVar()
        input_value.set(defalut_value)
        tk.Label(frame_back, text=label, font=(
            'Arial', 14), width=12).pack(side='left')
        tk.Entry(frame_back, textvariable=input_value, font=(
            'Arial', 14), width=35).pack(side='right', fill='x')
        frame_back.pack()
        return input_value

    def make_checbox_ui(self,frame,label,defalut_value,column):
        checked_value = tk.IntVar()
        checked_value.set(defalut_value)
        tk.Checkbutton(frame, text=label, variable=checked_value,
                       onvalue=1, offvalue=0).grid(row=0, column=column)
        return checked_value

    def selectPath(self):
        selected_path = askdirectory()
        self.diff_files.set(GitCommand(selected_path).getChangeFiles())
        self.dir_path.set(selected_path)
        self.remote_dir_value.set(self.request_data['remote_dir'])
        self.request_data['local_project_path'] = selected_path
        self.ftp_server.stop()
        self.create_and_run_ftp()
      #   remote_dir= os.path.join(os.path.split(self.request_data['remote_dir'])[0],os.path.basename(selected_path))
      #   self.request_data['remote_dir']=remote_dir
      #   self.remote_dir_value.set(remote_dir)

    def make_seeting_ui(self):
        # 实例化object，建立窗口window
        window = tk.Tk()
        # 第2步，给窗口的可视化起名字
        window.title('拉取代码并编译')
        # 居中显示窗口并设置大小
        self.center_window(window, 600, 700)
        
        # 显示被更改的数据
        self.diff_files = tk.StringVar()
        self.diff_files.set(self.request_data['diffFiles'])  # 为变量var2设置值
        diff_list = tk.Listbox(window, listvariable=self.diff_files, width=600)
        diff_list.pack()
        
        # 路径选择
        files_fream = tk.Frame(window)
        files_fream.pack()
        self.dir_path = tk.StringVar()
        self.dir_path.set(self.request_data['local_project_path'])
        tk.Label(files_fream, text='本地路径:', font=(14)).grid(row=0, column=0)
        tk.Entry(files_fream, textvariable=self.dir_path,width=60).grid(row=0, column=1)
        tk.Button(files_fream, text='路径选择', command=lambda: self.selectPath()).grid(row=0, column=2)

        # hook地址
        self.webhook_api_value=self.make_input_item(window, 'WebhookApi:', self.request_data['webhook_api'])

        # 远端存储目录
        self.remote_dir_value = self.make_input_item(window, '远端存储目录:', self.request_data['remote_dir'])

        # ftp地址
        self.ftp_host_value =self.make_input_item(window, 'FtpHost:', self.request_data['ftpHost'])

        # 端口
        self.ftp_port_value = self.make_input_item(window, 'FtpPort:', self.request_data['ftpPort'])

        # 用户名
        self.ftp_name_value = self.make_input_item(window, 'FtpName:', self.request_data['ftpName'])

        # 密码
        self.ftp_pwd_value = self.make_input_item(window, 'FtpPwd:', self.request_data['ftpPwd'])

        # 编译模块
        self.app_module_value =self.make_input_item(window, '编译模块:', self.request_data['moudleName'])

        # JDK版本
        self.app_jdk_value =self.make_input_item(window, 'JDK版本:', self.request_data['jdkVersion'])
        
        # 分发地址
        self.app_distribute_value =self.make_input_item(window, '分发地址:', self.request_data['uploadUrl'])

        # Apk回传目录
        self.app_back_value = self.make_input_item(window, 'Apk回传目录:', self.request_data['backApkPath'])

        # 编译选择功能
        checkbox_group = tk.Frame(window)
        checkbox_group.pack()

        #是否全量拉取代码    
        self.full_load_check_value =self.make_checbox_ui(checkbox_group,'是否全量拉取',self.request_data['fullLoad'] if 1 else 0,0)
        
        #是否需要clean工程
        self.clean_project_check_value =self.make_checbox_ui(checkbox_group,'是否清理工程',self.request_data['needClean'] if 1 else 0,1)
        
        #是否需要编译项目
        self.build_project_check_value =self.make_checbox_ui(checkbox_group,'是否编译工程',self.request_data['needBuild'] if 1 else 0,2)
        
        #是否在远程运行apk
        self.run_app_check_value =self.make_checbox_ui(checkbox_group,'是否运行工程',self.request_data['needInstallApk'] if 1 else 0,3)

        log_box = tk.Frame(window, height=10)
        log_box.pack()
        # 日志
        self.text_log = tk.Text(log_box, height=10)
        self.text_log.pack()
        # 创建text和scrollbar组件
  
        self.text_log.pack(side=tk.LEFT, fill=tk.X)
        scr = tk.Scrollbar(log_box)
        scr.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定text和scrollbar（以下是关键）
        self.text_log["yscrollcommand"] = scr.set
        scr["command"] = self.text_log.yview    

        # 给下面部分添加按钮
        submit = tk.Button(window, text="发送并保存配置", width=50,
                           height=2, command=lambda: self.post_submit())
        submit.pack()

        # 主窗口循环显示
        window.mainloop()

    def insert_log(self,log_tag,log_value):
         self.text_log.insert("end", log_tag+': '+log_value+"\n")

    def get_host_ip(self):
        """
        获取本机的ip地址
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip


    def create_default_setting(self):
        request_data = {}
        request_data['local_project_path'] = r'C:\Users\WIN10\Desktop\socialcontact'
        request_data['remote_dir'] = '/home/'
        request_data['webhook_api'] = 'http://192.168.52.137:5000/webhook'
        # 已修改过的文件
        request_data['diffFiles'] = GitCommand(
            request_data['local_project_path']).getChangeFiles()
        # ftp服务器连接相关设置
        request_data['ftpHost'] = self.get_host_ip()
        request_data['ftpPort'] = 2121
        request_data['ftpName'] = "peng"
        request_data['ftpPwd'] = "5652"
        request_data['jdkVersion']='11'
        # 是否全量更新
        request_data['fullLoad'] = False
        # 是否进行清理
        request_data['needClean'] = True
        # 是否进行编译
        request_data['needBuild'] = False
        # 需要编译的模块名
        request_data['moudleName'] = 'app'
        # 上传分发平台的链接(为空则不上传)
        request_data['uploadUrl'] = ''
        # 回传APK保存路径,为空则不回传(必须要传本地已存在的目录)
        request_data['backApkPath'] = '/libs/'
        # 是否需要安装APk
        request_data['needInstallApk'] = False
        if not os.path.exists('./android'):
            os.makedirs('./android')
        with open('./android/setting.json', "w", encoding='utf-8') as file:
            file.write(str(json.dumps(request_data)))

    def save_setting(self):
        # 保存配置文件
        if not os.path.exists('./android'):
            os.makedirs('./android')
        with open('./android/setting.json', "w", encoding='utf-8') as file:
            file.write(str(json.dumps(self.request_data)))       

    def get_apk_path(self,path):
        paths = os.walk(path)
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if file_name.endswith('.apk'):
                    # 获取文件路径
                    return os.path.join(path, file_name)


    def post_submit(self):
        self.make_requset_param()
        self.save_setting()
        # 发送网络请求
        print(json.dumps(self.request_data))
        self.insert_log('网络请求参数',json.dumps(self.request_data))
        response = requests.post(url=self.request_data['webhook_api'], headers={
                                 'Content-Type': 'application/json'}, data=json.dumps(self.request_data))
        self.insert_log('网络请求结果',response.text)
        response_data = json.loads(response.text)
        if response_data['code'] == 0 and len(self.request_data['backApkPath']) > 0:
            apk_path = os.path.join(
                self.request_data['local_project_path'], response_data['backApkPath'].strip('/'))
            adb = AndroidAdb()
            devices = adb.load_devices()
            apkinfo = ApkInfo(apk_path)
            package = apkinfo.get_apk_package()
            launch = apkinfo.get_luanch_activity()
            for device in devices:
                install_status = adb.install_apk(device, apk_path)
                if install_status:
                    adb.launch_apk(package, launch, device)

    def make_requset_param(self):
        self.request_data['jdkVersion']=self.app_jdk_value.get()
        self.request_data['webhook_api'] = self.webhook_api_value.get()
        self.request_data['ftpHost'] = self.ftp_host_value.get()
        self.request_data['remote_dir'] = self.remote_dir_value.get()
        self.request_data['project_name'] =os.path.basename(self.request_data['local_project_path'])
        self.request_data['ftpPort'] = self.ftp_port_value.get()
        self.request_data['ftpName'] = self.ftp_name_value.get()
        self.request_data['ftpPwd'] = self.ftp_pwd_value.get()
        self.request_data['moudleName'] = self.app_module_value.get()
        self.request_data['uploadUrl'] = self.app_distribute_value.get()
        self.request_data['backApkPath'] = self.app_back_value.get()
        self.request_data['fullLoad'] = self.full_load_check_value.get() == 1
        self.request_data['needClean'] = self.clean_project_check_value.get() == 1
        self.request_data['needBuild'] = self.build_project_check_value.get() == 1
        self.request_data['needInstallApk'] = self.run_app_check_value.get() == 1
        self.request_data['diffFiles'] = GitCommand(self.request_data['local_project_path']).getChangeFiles()

    def create_and_run_ftp(self):
        # 开启ftp服务器
        self.ftp_server = FtpServerThread(username=self.request_data['ftpName'], password=self.request_data['ftpPwd'],
                                     directory=self.request_data['local_project_path'], port=self.request_data['ftpPort'])
        self.ftp_server.start()



if __name__ == '__main__':

    # 展示界面
    apkGui = MakeApkGui()

    apkGui.make_seeting_ui()


