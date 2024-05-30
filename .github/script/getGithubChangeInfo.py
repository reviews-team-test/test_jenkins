import requests
import os
import json

logFile = 'githubResult.json'
excludeSuffLst = []

def getHeaders(access_token):
    # 设置头信息，包括使用access token进行认证
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "Accept": "application/vnd.github+json" 
    }
    return headers
# 获取两次提交之间的差异
def get_commit_diff(repo, commit_sha1, commit_sha2, token):
    url = f'https://api.github.com/repos/{repo}/compare/{commit_sha1}...{commit_sha2}'
    response = requests.get(url, headers=getHeaders(token))
    return response.json()
 
# 获取指定commit的文件列表
def get_commit_info(repo, commit_sha, token):
    url = f'https://api.github.com/repos/{repo}/commits/{commit_sha}'
    response = requests.get(url, headers=getHeaders(token))
    return response.json()
# 获取指定pr信息
def get_pull_info(repo, pull_number, token):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}'
    print(f'url is {url}')
    print(f'headers is {headers}')
    response = requests.get(url, headers=getHeaders(token))
    return response.json()

# 获取指定pr的commit信息
def get_pull_commit_info(repo, pull_number, token):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/commits'
    response = requests.get(url, headers=getHeaders(token))
    return response.json()

def get_pulls_files(repo, pull_number, token):
    url = f'https://api.github.com/repos/{repo}/pulls/{pull_number}/files'
    print(f'apiurl is {url}')
    response = requests.get(url, headers=getHeaders(token))
    if response.status_code == 200:
        return response.json()
    else:
        print(response.json())

# 写json文件
def writeJson(originInfo, infoType=dict):
    with open(logFile, "w+") as fout:
        if isinstance(originInfo, infoType):
            fout.write(json.dumps(originInfo, indent=4, ensure_ascii=False))
            
# 写json文件
def writeFile(originInfo, infoType=str):
    with open(logFile, "a+") as fout:
        if isinstance(originInfo, infoType):
            fout.write(originInfo+'\n')

def get_pr_files(repo, pull_number, token):
    try:
        originInfo = {}
        
        pfInfo = get_pulls_files(repo, pull_number, token)

        for fileTemp in pfInfo:
            originInfo[fileTemp['filename']] = {
                "a": [],
                "b": []
            }
            filePatch = fileTemp['patch']
            fileContent = filePatch.splitlines()
            for line in fileContent:
                if line.startswith("-"):
                    originInfo[fileTemp['filename']]["a"].append(line.lstrip("-"))
                elif line.startswith("+"):
                    originInfo[fileTemp['filename']]["b"].append(line.lstrip("+"))
                    
        writeJson(originInfo)
        return originInfo
    except Exception as e:
        print(f"[ERR]: 异常报错-{e}")


def get_change_files(repo, pull_number, token):
    try:
        originInfo = {}
        originInfoStr = ''
        pfInfo = get_pulls_files(repo, pull_number, token)
        for fileTemp in pfInfo:
            originInfo[fileTemp['filename']] = fileTemp['status']
            originInfoStr += fileTemp['filename'] + ':' + fileTemp['status'] + '\n'
            # writeFile(originInfo)
        print(originInfoStr)
        return originInfo
    except Exception as e:
        print(f"[ERR]: 异常报错-{e}")
        
def get_filterkey_info(content, keyLst, excludeSuffLst):
    strJson = {}
    if len(excludeSuffLst) != 0:
        for suffStr in excludeSuffLst:
            for fileName in list(content.keys()):
                if fileName.endswith(suffStr):
                    content.pop(fileName)
    for fileName, patchContent in content.items():
        if 'export' in keyLst or 'unset' in keyLst:
            for keyStr in keyLst:
                for actionType, actionTypePatchConten in patchContent.items():
                    for lineContent in actionTypePatchConten:
                        if keyStr in lineContent:
                            if keyStr not in list(strJson.keys()):
                                strJson[keyStr] = {}
                            if fileName not in list(strJson[keyStr].keys()):
                                strJson[keyStr][fileName] = {}
                            if actionType not in list(strJson[keyStr][fileName].keys()):
                                strJson[keyStr][fileName][actionType] = []
                            strJson[keyStr][fileName][actionType].append(lineContent)
        else:
                        for lineContent in patchContent['b']:
                            for keyStr in keyLst:
                                if keyStr in lineContent:
                                    if keyStr not in list(strJson.keys()):
                                        strJson[keyStr] = {}
                                    if fileName not in list(strJson[keyStr].keys()):
                                        strJson[keyStr][fileName] = []
                                    strJson[keyStr][fileName].append(lineContent)

    return strJson

def filter_keywords(repo, pull_number, token, keyLst, excludeSuffLst):
    content = get_pr_files(repo, pull_number, token)
    originInfo = {}
    with open(logFile, "w+") as fout:
        if isinstance(content, dict):
            originInfo = get_filterkey_info(content, keyLst, excludeSuffLst)
        fout.write(json.dumps(originInfo, indent=4, ensure_ascii=False))
    
    return originInfo

# if __name__ == '__main__':
#     import argparse
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--type", required=True, help="检查类型")
#     # parser.add_argument("--owner", required=True, help="拥有者")
#     parser.add_argument("--repo", required=True, help="所有者和存储库名称。 例如，octocat/Hello-World")
#     parser.add_argument("--SHA", required=False, help="commit sha")
#     parser.add_argument("--PRN", required=False, help="pr number")
#     parser.add_argument("--log", required=False, help="输出日志文件名")
#     parser.add_argument("--keys", required=False, help="要筛选的敏感词,多个使用逗号分隔")
#     parser.add_argument("--exclude", required=False, help="不进行敏感词筛选的文件后缀")
    
#     args = parser.parse_args()

#     if args.log:
#         logFile = args.log
#     if args.PRN:
#         pull_number = args.PRN
        
#     if args.type == 'get_change_files':
#         get_change_files(args.repo, pull_number)
#     if args.type == 'get_pr_files':
#         get_pr_files(args.repo, pull_number)
#     if args.type == 'filter_keys':
#         keyLst = args.keys.split(',')
#         if args.exclude:
#             excludeSuffLst = args.exclude.split(',')
#         filter_keywords(args.repo, pull_number, keyLst, excludeSuffLst)