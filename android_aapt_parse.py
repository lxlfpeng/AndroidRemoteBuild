import os
import re
import platform

class ApkInfo:
    def __init__(self, apk_path):
        """
        通过apk包获取apk信息
        :param apk_path:apk路径 
        """
        self.apk_path = apk_path
        self.aapt_path = self.get_aapt()

    @staticmethod
    def get_aapt():
        plat = platform.system().lower()
        if plat == 'windows':
            return 'aapt2.exe'
        elif plat == 'linux':
            os.system('chmod +x ./aapt/aapt2')
            return './aapt2'
     
    def get_apk_size(self):
        """
        得到apk的文件大小
        :return: 
        """
        size = round(os.path.getsize(self.apk_path) / (1024 * 1000), 2)
        return str(size) + "M"

    def aapt_dump_package_info(self):
        """
        获取apk包的信息
        :return: 
        """
        os.chdir('./aapt/')
        result = os.popen("{} dump badging {}".format(self.aapt_path,self.apk_path))
        apk_info = result.buffer.read().decode('utf-8')
        os.chdir(os.path.abspath('..'))
        return  apk_info              

    def get_apk_base_info(self):
        """
        获取apk包的基本信息
        :return: 
        """
        result = self.aapt_dump_package_info()
        match = re.compile(
            "package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(result)
        if not match:
            raise Exception("can't get packageinfo")
        package_name = match.group(1)
        version_code = match.group(2)
        version_name = match.group(3)
        return package_name, version_name, version_code

    def get_apk_name(self):
        """
        获取apk名字
        :return:
        """
        result = self.aapt_dump_package_info()

        # 此处的apk包名我是取得中文名称。具体信息可以在dos下用aapt查看详细信息后，修改正则获取自己想要的name
        match = re.compile(
            "application-label-zh-CN:'([\u4e00-\u9fa5_a-zA-Z0-9-\S]+)'").search(result)
        if match is not None:
            return match.group(1)

    def get_luanch_activity(self):
        """
        得到启动类
        :return:
        """
        result = self.aapt_dump_package_info()
        match = re.compile("launchable-activity: name='(\S+)'").search(result)
        if match is not None:
            return match.group(1)

    def get_apk_package(self):
        """
        得到包名
        :return:
        """        
        result = self.aapt_dump_package_info()
        package_str = re.findall('package: name=\'.*?\'', result)
        package_name = package_str[0].replace('\'', '').split('=')[1]
        return package_name

if __name__ == "__main__":
    apkinfo = ApkInfo(r'C:\Users\WIN10\Desktop\apk\release_aitd_block_3.9.9_2022-10-28.apk')
    print(apkinfo.aapt_dump_package_info())
    print(apkinfo.get_apk_base_info())
    print(apkinfo.get_apk_name())
    print(apkinfo.get_luanch_activity())
    print(apkinfo.get_apk_package())    
    print(apkinfo.get_apk_size())

