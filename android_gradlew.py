import os
import platform

class AndroidGradle:
    def __init__(self, project_path, jdk_version='', module_name=''):
        """
        :param project_path:需要编译的工程地址
        :param jdk_version:为空则表示使用Java_Home配置的jdk版本进行编译
        :param module_name:需要编译的模块名,为空则表示编译app这个module
        """
        self.project_path = project_path
        self.jdk_path = self.get_jdk_path(jdk_version)
        if len(module_name) > 0:
            self.module_name = module_name+':'
        else:
            self.module_name = ''
        self.gradle_path = self.get_gradle()

    def get_gradle(self):
        plat = platform.system().lower()
        if plat == 'windows':
            return 'gradlew'
        elif plat == 'linux':
            gradlew_ptah=os.path.join(self.project_path,'gradlew')
            os.system('chmod +x {}'.format(gradlew_ptah))
            return './gradlew'

    def get_jdk_path(self,jdk_version):
        if len(jdk_version)==0 :
            return ''
        plat = platform.system().lower()
        if plat == 'windows':
            return  '-Dorg.gradle.java.home={}/jdk/win_11'.format(os.getcwd())
        elif plat == 'linux':
            if jdk_version=='11':
                os.system('chmod +x -R ./jdk/linux_11/bin')
                return  '-Dorg.gradle.java.home={}/jdk/linux_11'.format(os.getcwd())
   
    def execute_gradle_command(self, command,path=''):
        print('Gradle命令:',command)
        old_path=os.getcwd()
        if len(path) == 0:
            path = self.project_path
        os.chdir(path)
        result=os.system(command)
        os.chdir(old_path)  
        return result

    def clean(self, path=''):
        command='{} clean {}'.format(self.gradle_path, self.jdk_path)
        return self.execute_gradle_command(command,path)
  
    # 检查依赖并编译打包，debug、release环境的包都会打出来；
    def build(self, path=''):
        command='{} {}build %{}'.format(self.gradle_path,self.module_name, self.jdk_path)
        return self.execute_gradle_command(command,path) 
   
    # 编译并打Debug包
    def assembleDebug(self, path=''):
        command='{} {}assembleDebug {}'.format(self.gradle_path,self.module_name, self.jdk_path)
        return self.execute_gradle_command(command,path)==0
   
    # 编译并打Release的包
    def assembleRelease(self, path=''):
        command='{} {}assembleRelease {}'.format(self.gradle_path,self.module_name, self.jdk_path)
        return self.execute_gradle_command(command,path)        

   
    # Release模式打包并安装
    def installRelease(self, path=''):
        command='{} {}installRelease {}'.format(self.gradle_path,self.module_name, self.jdk_path)
        return self.execute_gradle_command(command,path)

    
    # Release模式打包并安装
    def installDebug(self, path=''):
        command='{} {}installDebug {}'.format(self.gradle_path,self.module_name, self.jdk_path)
        return self.execute_gradle_command(command,path)

    def get_apks_path(self, path):
        apks = []
        paths = os.walk(path)
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if file_name.endswith('.apk'):
                    # 获取文件路径
                    file_path = os.path.join(path, file_name)
                    apks.append(file_path)
        return apks

    def get_apk_path(self, path):
        paths = os.walk(path)
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if file_name.endswith('.apk'):
                    # 获取文件路径
                    return os.path.join(path, file_name)


    def find_all_apks(self, path):
        apks = []
        paths = os.walk(path)
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if file_name.endswith('.apk'):
                    # 获取文件路径
                    file_path = os.path.join(path, file_name)
                    apks.append(file_path)
        print('找到的Apk:',apks)
        return apks

    def find_single_apk(self, path):
        paths = os.walk(path)
        for path, dir_lst, file_lst in paths:
            for file_name in file_lst:
                if file_name.endswith('.apk'):
                    # 获取文件路径
                    print('找到的Apk:',os.path.join(path, file_name))
                    return os.path.join(path, file_name)

if __name__ == "__main__":
    project_path = r"C:\Users\WIN10\Desktop\socialcontact"
    gradlew=AndroidGradle(project_path,'11')
    gradlew.assembleDebug()
    #gradlew.assembleDebug()