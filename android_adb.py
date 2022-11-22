import os
import platform

class AndroidAdb:
    # def __init__(self, need_local=False):
    #     """
    #     :param adb_path:adb位置,未设置则使用系统默认的adb
    #     """
    #     self.adb_path = self.get_adb()
    #     print(self.adb_path)
    #     # if len(adb_path)==0:
    #     #     self.adb_path=''
        
    #     # self.project_path = project_path
    #     # self.jdk_path = self.get_jdk_path(jdk_version)
    #     # if len(module_name) > 0:
    #     #     self.module_name = module_name+':'
    #     # else:
    #     #     self.module_name = ''
    #     # self.gradle_path = self.get_gradle()

    # def get_adb(self):
    #     plat = platform.system().lower()
    #     if plat == 'windows':
    #         return 'adb.exe'
    #     elif plat == 'linux':
    #         return './adb'

    def load_devices(self):
        """
        通过adb获取连接的设备
        """
        result = os.popen('adb devices').read()
        result = result.replace('List of devices attached', '')
        devices = result.split('device')
        devices_name = []
        for device in devices:
            device = device.replace('\n', '').replace('\t', '')
            if len(device) != 0 and device != None:
                devices_name.append(device)
        print('adb连接的设备:',devices_name)
        return devices_name

    def install_apk(self, device, apk_path):
        if not os.path.exists(apk_path):
            print('安装失败,文件不存在:',device+'==>'+apk_path)
            return False
        print('正在安装:',device+'==>'+apk_path)
        result = os.popen('adb -s %s install %s' % (device, apk_path)).read()
        if 'Success' in result:
            print('安装成功:',device+'==>'+apk_path)
            return True
        print('安装失败,进行覆盖安装:',device+'==>'+apk_path)
        # 进行覆盖安装
        result = os.popen('adb -s %s install -r %s' %(device, apk_path)).read()
        if 'failed' in result:
            print('覆盖安装失败:',device+'==>'+apk_path)
            return False
        elif 'Success' in result:
            print('覆盖安装成功:',device+'==>'+apk_path)
            return True

    def launch_apk(self, package_name, launch_name, device):
        print('启动App:','package_name=>'+package_name+' launch_name=>'+launch_name+' device=>'+device)
        return os.system('adb -s '+device+' shell am start -n '+package_name+'/'+launch_name+'')==0
    
if __name__ == "__main__":
    adb=AndroidAdb()
    devices=adb.load_devices()
    for device in devices:
        adb.install_apk(device, r'C:\Users\WIN10\Desktop\socialcontact\app\build\outputs\apk\debug\debug_aitd_block_4.0.0_2022-11-15.apk')
        result=adb.launch_apk('com.huke.socialcontact', 'com.huke.socialcontact.ui.activity.me.SplashActivity', device)
        print(result)