from ftplib import FTP
import ftplib
import os
import sys
import time
class FTPDownload:
    """
        ftp自动下载、自动上传脚本，可以递归目录操作
    """

    def __init__(self, host, port=21):
        """ 初始化 FTP 客户端
        参数:
                 host:ip地址

                 port:端口号
        """
        # print("__init__()---> host = %s ,port = %s" % (host, port))

        self.host = host
        self.port = port
        self.ftp = FTP()
        # 重新设置下编码方式
        self.ftp.encoding = 'utf-8'
        if not os.path.exists('./ftplib/'):
           os.makedirs('./ftplib/')
        self.log_file = open("./ftplib/log.txt", "a")
        # 需要忽略的下载目录
        self.ignore_dir_list = ['build', '.git', '.gradle', '.idea']

    def login(self, username, password):
        """ 初始化 FTP 客户端
            参数:
                  username: 用户名

                 password: 密码
            """
        try:
            # 0主动模式 1 #被动模式
            self.ftp.set_pasv(True)
            # 打开调试级别2，显示详细信息
            # self.ftp.set_debuglevel(2)

            self.debug_print('开始尝试连接到 %s' % self.host)
            self.ftp.connect(self.host, self.port)
            self.debug_print('成功连接到 %s' % self.host)

            self.debug_print('开始尝试登录到 %s' % self.host)
            self.ftp.login(username, password)
            self.debug_print('成功登录到 %s' % self.host)

            self.debug_print(self.ftp.welcome)
        except Exception as err:
            self.deal_error("FTP 连接或登录失败 ，错误描述为：%s" % err)

    def is_same_size(self, local_file, remote_file):
        """判断远程文件和本地文件大小是否一致

           参数:
             local_file: 本地文件

             remote_file: 远程文件
        """
        try:
            self.ftp.voidcmd('TYPE I')
            remote_file_size = self.ftp.size(remote_file)
        except Exception as err:
            self.debug_print("remote_file->Size获取失败：%s" % err)
            remote_file_size = -1

        try:
            local_file_size = os.path.getsize(local_file)
        except Exception as err:
            self.debug_print("local_file->Size获取失败：%s" % err)
            local_file_size = -1

        self.debug_print('local_file_size:%d  , remote_file_size:%d' % (local_file_size, remote_file_size))
        if remote_file_size == local_file_size:
            return 1
        else:
            return 0

    def download_file(self, local_file, remote_file):
        """从ftp下载文件
            参数:
                local_file: 本地文件

                remote_file: 远程文件
        """
        self.debug_print("download_file()---> local_path = %s ,remote_path = %s" % (local_file, remote_file))

        try:
            self.debug_print('>>>>>>>>>>>>下载文件 %s ... ...' % local_file)
            buf_size = 1024
            file_handler = open(local_file, 'wb')
            self.ftp.retrbinary('RETR %s' % remote_file,file_handler.write, buf_size)
            file_handler.close()
        except Exception as err:
            self.debug_print('下载文件出错，出现异常：%s ' % err)
            return

    def download_file_tree(self, local_path, remote_path):
        """从远程目录下载多个文件到本地目录
                       参数:
                         local_path: 本地路径

                         remote_path: 远程路径
                """
        print("download_file_tree()--->  local_path = %s ,remote_path = %s" %(local_path, remote_path))
        try:
            self.ftp.cwd(remote_path)
        except Exception as err:
            self.debug_print('远程目录%s不存在，继续...' %remote_path + " ,具体错误描述为：%s" % err)
            return False

        if not os.path.isdir(local_path):
            self.debug_print('本地目录%s不存在，先创建本地目录' % local_path)
            os.makedirs(local_path)

        self.debug_print('切换至目录: %s' % self.ftp.pwd())
        remote_files = self.ftp.nlst()
        for file in remote_files:
            remote_file_path = os.path.join(remote_path, file)
            local_file_path = os.path.join(local_path, file)
            # if os.path.isdir(remote_file_path):
            #     #self.DownLoadFileTree( Local, file )
            #     print('dir--文件夹:-->'+file+"==路径:==>"+remote_file_path)
            #     self.download_file_tree(local_file_path, remote_file_path)
            # else:
            #     print('file--文件名:-->'+file+"==路径:==>"+remote_file_path)
            #     #self.download_file(local_file_path, remote_file_path)
            try:
                # 打开路径没问题，类型是文件夹
                self.ftp.cwd(remote_file_path)
                # print('dir--文件夹:-->'+file+"==路径:==>"+remote_file_path)
                if not file in self.ignore_dir_list:
                    self.download_file_tree(local_file_path, remote_file_path)
                # 由于已经打开了目录因此需要返回上一级目录
                self.ftp.cwd('..')
            except ftplib.error_perm:
                if not os.path.exists(local_file_path):
                    # 文件不存在直接下载
                    self.download_file(local_file_path, remote_file_path)
                else:
                    # 文件已存在
                    same = self.is_same_size(local_file_path, remote_file_path)
                    #判断文件是否被修改
                    if not same:
                        print('需要下载文件:'+remote_file_path)
                        self.download_file(local_file_path, remote_file_path)
        return True

    def make_remote_dirs(self,target_dir):
        old_dir=self.ftp.pwd()  
        part_path = target_dir.split('/')
        for path in part_path:
            try:
                self.ftp.cwd(path)
            except Exception as e:
                self.ftp.mkd(path)
                self.ftp.cwd(path)
        self.ftp.cwd(old_dir)

    def upload_file(self, local_file, remote_file):
        print("远端上传地址:",remote_file)
        """从本地上传文件到ftp

           参数:
             local_path: 本地文件

             remote_path: 远程文件
        """
        if not os.path.isfile(local_file):
            self.debug_print('%s 不存在' % local_file)
            return

        if self.is_same_size(local_file, remote_file):
            self.debug_print('跳过相等的文件: %s' % local_file)
            return

        buf_size = 1024
        file_handler = open(local_file, 'rb')
        self.ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
        file_handler.close()
        self.debug_print('上传: %s' % local_file + "成功!")

    def upload_file_tree(self, local_path, remote_path):
        """从本地上传目录下多个文件到ftp
           参数:

             local_path: 本地路径

             remote_path: 远程路径
        """
        if not os.path.isdir(local_path):
            self.debug_print('本地目录 %s 不存在' % local_path)
            return
        try:
            self.ftp.cwd(remote_path)
            self.debug_print('切换至远程目录: %s' % self.ftp.pwd())
        except ftplib.error_perm:
            self.ftp.mkd(remote_path)
            self.ftp.cwd(remote_path)
            self.debug_print('远程目录不存在,创建并切换目录: %s' % self.ftp.pwd())

        local_name_list = os.listdir(local_path)
        for local_name in local_name_list:
            src = os.path.join(local_path, local_name)
            if os.path.isdir(src):
                try:
                    self.ftp.mkd(local_name)
                except Exception as err:
                    self.debug_print("目录已存在 %s ,具体错误描述为：%s" %(local_name, err))
                self.debug_print("upload_file_tree()---> 上传目录： %s" % local_name)
                self.upload_file_tree(src, local_name)
            else:
                self.debug_print("upload_file_tree()---> 上传文件： %s" % local_name)
                self.upload_file(src, local_name)
        self.ftp.cwd("..")

    def close(self):
        """ 退出ftp
        """
        self.debug_print("close()---> FTP退出")
        self.ftp.quit()
        self.log_file.close()

    def debug_print(self, s):
        """ 打印日志
        """
        self.write_log(s)

    def deal_error(self, e):
        """ 处理错误异常
            参数：
                e：异常
        """
        log_str = '发生错误: %s' % e
        self.write_log(log_str)
        sys.exit()

    def write_log(self, log_str):
        """ 记录日志
            参数：
                log_str：日志
        """
        time_now = time.localtime()
        date_now = time.strftime('%Y-%m-%d', time_now)
        format_log_str = "%s ---> %s \n " % (date_now, log_str)
        print(format_log_str)
        self.log_file.write(format_log_str)

    def load(self,ip,port,name,pwd,path):
         my_ftp = MyFTP(ip, port)
         my_ftp.login(name,pwd)
         my_ftp.download_file_tree(path, r"\app\src\main")
         my_ftp.close()

if __name__ == "__main__":
    my_ftp = FTPDownload("172.16.5.3", 2121)
    my_ftp.login("peng", "5652")

    # 下载单个文件
    #my_ftp.download_file("./myufc/build.gradle", "/App/build.gradle")

    # 下载目录
    my_ftp.download_file_tree(r"C:\Users\peng\Desktop\remote", "/")

    # 上传单个文件
    # my_ftp.upload_file("G:/ftp_test/Release/XTCLauncher.apk", "/App/AutoUpload/ouyangpeng/I12/Release/XTCLauncher.apk")

    # 上传目录
    #my_ftp.upload_file_tree("./zhangsan/Screenshots/", "/ll/")

    # 关闭连接
    my_ftp.close()
