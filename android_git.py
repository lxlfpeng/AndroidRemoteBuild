import os
import re
from git.repo import Repo

class GitCommand():
    def __init__(self, project_path=''):
            self.project_path = project_path

    def getChangeFiles(self,project_path=''):
        if len(project_path)==0:
            project_path=self.project_path
        print('Git目录:',project_path)
        repo = Repo(project_path)
        #尚未追踪的文件
        not_tracked_files=repo.untracked_files
        print('Git尚未追踪的文件:',not_tracked_files)
        # 仅列出尚未暂存的文件
        changedFiles = [ item.a_path for item in repo.index.diff(None) ]
        # 仅列出已暂存的文件
        changedFiles += [ item.a_path for item in repo.index.diff('Head') ]
        print('Git已更改的文件:',changedFiles)
        return changedFiles

    def getChangeFilesWithRe(self,project_path=''):
        if len(project_path)==0:
            project_path=self.project_path
        old_path=os.getcwd()
        os.chdir(project_path) 
        result=os.popen('git status --porcelain').read()
        print(result)
        new_files = re.compile("new file:   (\S+)").findall(result)
        modified_files = re.compile("modified:   (\S+)").findall(result)
        renamed_files = re.compile("R  (\S+)").findall(result)
        print("已修改的文件",renamed_files)
        deleted_files = re.compile("deleted:    (\S+)").findall(result)
        all_result=new_files+modified_files+deleted_files+deleted_files
        for file_name in all_result:
            file_name=file_name.replace('\"','')
        os.chdir(old_path) 
        return all_result


if __name__ == "__main__":
    git=GitCommand()
    diff=git.getChangeFiles(r'C:\Users\WIN10\Desktop\simpleproject')
    print(diff)

