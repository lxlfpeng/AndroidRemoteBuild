#pip install pyftpdlib
from pyftpdlib.authorizers import DummyAuthorizer
from  pyftpdlib.handlers  import FTPHandler
from  pyftpdlib.servers import FTPServer
import threading
import time
# perm权限选项
# 读取权限：

# "e" =更改目录（CWD，CDUP命令）
# "l" =列表文件（LIST，NLST，STAT，MLSD，MLST，SIZE命令）
# "r" =从服务器检索文件（RETR命令）
# 写入权限：

# "a" =将数据追加到现有文件（APPE命令）
# "d" =删除文件或目录（DELE，RMD命令）
# "f" =重命名文件或目录（RNFR，RNTO命令）
# "m" =创建目录（MKD命令）
# "w" =将文件存储到服务器（STOR，STOU命令）
# "M"=更改文件模式/权限（SITE CHMOD命令）
# "T"=更改文件修改时间（SITE MFMT命令）
def ftp_server(username, password, directory):
    """
    启动一个ftp的server进程

    :param username: 需要添加用户的用户名
    :param password: 用户的密码
    :param directory: 用户的家目录，也就是FTP服务器的数据目录
    :return:
    """
    try:
        # 实例化DummyAuthorizer来创建ftp用户
        authorizer = DummyAuthorizer()
        # 参数：用户名，密码，目录，权限
        authorizer.add_user(username, password, directory, perm="elradfmw")

        # 匿名登录
        # authorizer.add_anonymous(directory)
    except OSError as e:
        if "Address already in use" in e:
            print("21号端口被占用")

    # 初始化ftp句柄
    handler = FTPHandler
    handler.authorizer = authorizer

    # 添加被动端口范围
    #handler.passive_ports = range(2000, 2400)

    # 启动server，本地执行，监听21号端口（参数：IP，端口，handler）
    server = FTPServer(('0.0.0.0', 2121), handler)
    server.serve_forever()

class FtpServerThread(threading.Thread):

    def __init__(self, username, password, directory, port=2121, perm='elradfmw'):
        """
        启动一个ftp的server进程
        :param username: 需要添加用户的用户名
        :param password: 用户的密码
        :param directory: FTP服务器的数据目录
        """        
        threading.Thread.__init__(self)
        try:
            # 实例化DummyAuthorizer来创建ftp用户
            authorizer = DummyAuthorizer()
            # 参数：用户名，密码，目录，权限
            authorizer.add_user(username, password, directory, perm)
            # 允许匿名登录
            # authorizer.add_anonymous(directory)
        except OSError as e:
            if "Address already in use" in e:
                print("21号端口被占用")
        # 初始化ftp句柄
        handler = FTPHandler
        handler.authorizer = authorizer
        # 添加被动端口范围
        #handler.passive_ports = range(2000, 2400)
        # 启动server，本地执行，监听21号端口（参数：IP，端口，handler）
        self.server = FTPServer(('0.0.0.0', port), handler)

    def run(self):
        """
        开启ftp服务
        """
        self.server.serve_forever()

    def stop(self):
        """
        关闭ftp服务
        """
        self.server.close_all()

if __name__ == '__main__':
   #ftp_server(username="peng", password="5652", directory=r"C:\Users\WIN10\Desktop\socialcontact")
    ftp_server = FtpServerThread(username="peng", password="5652", directory=r"C:\Users\WIN10\Desktop\JavaDemo")
    ftp_server.start()
    print("================>")
    time.sleep(10)
    ftp_server.stop()
