import json
import os
from urllib.parse import unquote
from http.server import HTTPServer, BaseHTTPRequestHandler
import android_command
from ftplib_download import MyFTP

class RequestHandler(BaseHTTPRequestHandler):
    def _writeheaders(self):
        print(self.path)
        print(self.headers)

    def do_Head(self):
        self._writeheaders()

    def do_GET(self):
        print('get请求:')
        self._writeheaders()
        MyFTP("172.16.5.3", 2121).load("172.16.5.3", 2121,"peng", "5652",r"C:\Users\peng\Desktop\remote\app\src\main")
        print('拉取完毕')
        os.getcwd
        android_command.domake()
        print('打包完毕')
        return "打包完成啦"
       # self.wfile.write(str(self.headers))

    def do_POST(self):
        self._writeheaders()
        data = self.rfile.read(int(self.headers['content-length']))
        data = unquote(str(data, encoding='utf-8'))
        json_obj = json.loads(data)
        print(json_obj)


if __name__ == "__main__":
    addr = ('', 7000)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()