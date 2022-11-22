import json
from flask import Flask, request
from ftp_client import FTPDownload
from android_gradlew import AndroidGradle
from android_adb import AndroidAdb
from android_aapt_parse import ApkInfo
import os
import shutil
import datetime

#由于涉及到权限的操作因此请用root权限执行该脚本
app = Flask(__name__)
@app.route('/webhook', methods=['POST'])
def webhook():
    starttime = datetime.datetime.now()
    response_data={}
    response_data['code']=0
    #获取query参数request.args.get('user_name'))
    post_data = json.loads(request.data)

    local_path=os.path.join(post_data['remote_dir'],post_data['project_name'])
    #fpt配置
    ftp = FTPDownload(post_data['ftpHost'],int(post_data['ftpPort']) )
    ftp.login(post_data['ftpName'], post_data['ftpPwd'])     
    #下载工程代码
    if post_data['fullLoad']:
        print('全量下载代码')
        #全量下载
        try:
            shutil.rmtree(local_path)
        except :
            print('删除文件错误')
        ftp.download_file_tree(local_path, "/")
    else:
        print('增量下载代码:',post_data['diffFiles'])
        #增量下载
        for file in  post_data['diffFiles']:
            ftp.download_file(os.path.join(local_path,file), file)     

    if not len(post_data['backApkPath'])>0:
        ftp.close()

    gradle=AndroidGradle(local_path,module_name=post_data['moudleName'],jdk_version=post_data['jdkVersion'])
    #清理工程
    if post_data['needClean']:
        gradle.clean()
        print('clean代码成功')
    
    #编译Apk
    if post_data['needBuild']:
        buildState = gradle.assembleDebug()
        print('assembleDebug执行成功' if buildState else 'assembleDebug执行失败')
        if not buildState :
            response_data['code']=1
            response_data['msg']='编译失败'
            return json.dumps(response_data)           
   
    #获取Apk地址
    apk_path=gradle.find_single_apk(local_path)
    if apk_path ==None:
        response_data['code']=2
        response_data['msg']='未找到Apk文件'
        return json.dumps(response_data)
    print('获取到的Apk地址为:',apk_path)
   
    #上传Apk
    if len(post_data['uploadUrl'])>0:
        print('将应用上传到分发平台中去')
        response_data['remotePath']=''

    #安装Apk    
    if  post_data['needInstallApk']:
        adb=AndroidAdb()
        devices=adb.load_devices()
        apkinfo = ApkInfo(apk_path)
        package = apkinfo.get_apk_package()
        launch = apkinfo.get_luanch_activity()
        for device in devices:
            install_status = adb.install_apk(device, apk_path)
            if install_status:
                adb.launch_apk(package, launch, device)

     #回传Apk
    if len(post_data['backApkPath'])>0:
        ftp.make_remote_dirs(post_data['backApkPath'])
        backApkPath=os.path.join(post_data['backApkPath'],os.path.split(apk_path)[1])
        ftp.upload_file(apk_path, backApkPath)
        response_data['backApkPath']=backApkPath
        ftp.close()

    
    #计算耗时
    endtime = datetime.datetime.now()
    response_data['useTime']=(endtime - starttime).seconds
    response_data['msg']='success'
    return json.dumps(response_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)