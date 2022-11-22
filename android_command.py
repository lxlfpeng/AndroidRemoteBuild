import os
import re
import platform
from android_aapt_parse import ApkInfo

class MyGit():
    def __init__(self, project_path):
            self.project_path = project_path
    def getChangeFiles(self):
        os.chdir(self.project_path) 
        result=os.popen('git status').read()
        new_files = re.compile("new file:   (\S+)").findall(result)
        modified_file = re.compile("modified:   (\S+)").findall(result)
        all_result=new_files+modified_file
        for file_name in all_result:
            file_name=file_name.replace('\"','')

        return all_result

def domake():
    # 需要编译的工程地址
    project_path = r"C:\Users\peng\Desktop\remote"
    # jdk11的地址,为空则表示使用Java_Home配置的jdk版本进行编译
    jdk_11 = '-Dorg.gradle.java.home={}/jdk/linux_11'.format(os.getcwd())
    # 需要编译的模块名,为空则表示编译app这个module
    module_name = ''
    gradle = MyGradle(project_path, jdk_11, module_name)
    print('开始编译{} {} {}'.format(project_path, jdk_11, module_name))
    buildState = gradle.assembleDebug()
    if buildState == 0:
        print('编译成功!')
        adb = MyAdb()
        apk_path = gradle.get_apk_path(os.path.join(project_path, module_name))
        print('打包成功,Apk地址为:{}'.format(apk_path))
        if not apk_path is None:
            devices = adb.load_devices()
            print('获取到的已连接设备:{}'.format(str(devices)))
            for device in devices:
                install_status = adb.install_apk(device, apk_path)
                if install_status:
                    print('{} 设备安装成功!'.format(device))
                    apkinfo = ApkInfo(apk_path)
                    package = apkinfo.get_apk_package()
                    launch = apkinfo.get_apk_activity()
                    print('{}设备启动{}{}'.format(device, launch, devices))
                    launch_status = adb.launch_apk(package, launch, device)
                    if launch_status == 0:
                        print('{} 设备启动成功!'.format(device))
                    else:
                        print('{} 设备启动失败!'.format(device))
                else:
                    print('{} 设备安装失败!'.format(device))
    else:
        print('编译失败!')

if __name__ == "__main__":
   # 需要编译的工程地址
    project_path = r"/home/android/socialcontact/"
    # # jdk11的地址,为空则表示使用Java_Home配置的jdk版本进行编译
    # jdk_11 = '-Dorg.gradle.java.home={}/jdk/linux_11'.format(os.getcwd())
    # # 需要编译的模块名,为空则表示编译app这个module
    # module_name = ''
    # gradle = MyGradle(project_path, jdk_11, module_name)
    # print('开始编译{} {} {}'.format(project_path, jdk_11, module_name))
    # buildState = gradle.clean()
    # path=os.getcwd()
    # os.chdir(project_path)
    # os.system('./gradlew clean -Dorg.gradle.java.home={}/jdk/linux_11/'.format(path))
    gradlew=MyGradle(project_path,'11')
    print(gradlew.assembleDebug())
    # #需要编译的工程地址
    # project_path = r"C:\Users\peng\Desktop\remote"
    # # jdk11的地址,为空则表示使用Java_Home配置的jdk版本进行编译
    # jdk_11 = '-Dorg.gradle.java.home={}/jdk/jre'.format(os.getcwd())
    # # 需要编译的模块名,为空则表示编译app这个module
    # module_name = ''
    # gradle = MyGradle(project_path, jdk_11, module_name)
    # print('开始编译{} {} {}'.format(project_path, jdk_11, module_name))
    # buildState = gradle.assembleDebug()
    # if buildState == 0:
    #     print('编译成功!')
    #     adb = MyAdb()
    #     apk_path = gradle.get_apk_path(os.path.join(project_path, module_name))
    #     print('打包成功,Apk地址为:{}'.format(apk_path))
    #     if not apk_path is None:
    #         devices = adb.load_devices()
    #         print('获取到的已连接设备:{}'.format(str(devices)))
    #         for device in devices:
    #             install_status = adb.install_apk(device, apk_path)
    #             if install_status:
    #                 print('{} 设备安装成功!'.format(device))
    #                 apkinfo = ApkInfo(apk_path)
    #                 package = apkinfo.get_apk_package()
    #                 launch = apkinfo.get_apk_activity()
    #                 print('{}设备启动{}{}'.format(device, launch, devices))
    #                 launch_status = adb.launch_apk(package, launch, device)
    #                 if launch_status == 0:
    #                     print('{} 设备启动成功!'.format(device))
    #                 else:
    #                     print('{} 设备启动失败!'.format(device))
    #             else:
    #                 print('{} 设备安装失败!'.format(device))
    # else:
    #     print('编译失败!')
  
    # plat = platform.system().lower()
    # if plat == 'windows':
    #     print('windows系统')
    # elif plat == 'linux':
    #     print('linux系统')
    # os.chdir('./aapt/') 
    # result=os.popen(r'aapt.exe dump badging C:\Users\WIN10\Desktop\apk\release_aitd_block_3.9.9_2022-10-28.apk').read()    
    # print(result)
    #apkinfo = ApkInfo(r'C:\Users\WIN10\Desktop\apk\release_aitd_block_3.9.9_2022-10-28.apk')
    #print(apkinfo.get_luanch_activity())
    # myGit=MyGit(r'C:\Users\peng\Desktop\TqxdData')
    # result=myGit.getChangeFiles()
    # print(result)
    # os.chdir(r'C:\Users\peng\Desktop\TqxdData') 
    # result=os.popen('git status').read()
    # print(result)
    # match = re.compile("new file:   (\S+)").findall(result)
    # match2 = re.compile("modified:   \"(\S+)\"").findall(result)
    # print(match)
    # print(match2)
        