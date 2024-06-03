import getGithubChangeInfo
import os

# debian前缀检查
def debianPreCheck(repo, pull_number, token):
    resulyJson = getGithubChangeInfo.get_change_files(repo, pull_number, token)
    NoNeedPreFiles = ["debian/changelog", "debian/copyright", "debian/compat", "debian/source/format"]
    resultLst = []
    for file in resulyJson:
      # print(f'file is {file}')
      if file.startswith("debian/"):
        if file == 'debian/changelog':
          debianVersionCheck(repo, pull_number)
        if file not in NoNeedPreFiles:
          resultLst.append(file)
    if resultLst:
      writeCommentFile(f"[FAIL]: debian前缀检查不通过{resultLst}")
      exit(1)
    else:
      writeCommentFile("[PASS]: debian前缀检查通过")

# 敏感词检查
def debianKeyWordsCheck(repo, pr, token, keyLst, excludeSuffLst, logFile):
  try:
    resulyJson = getGithubChangeInfo.filter_keywords(repo, pr, token, keyLst, excludeSuffLst, logFile)
    showStr = '环境设置' if 'export' in keyLst else ''
    if resulyJson:
      writeCommentFile(f"[FAIL]: {showStr}敏感词检查不通过{list(resulyJson.keys())}")
      exit(1)
    else:
      writeCommentFile(f"[PASS]: {showStr}敏感词检查通过")
  except Exception as e:
    writeCommentFile(f"[ERR]: {showStr}异常报错-{e}")
    exit(1)
    
# debian/changelog版本检查
def debianVersionCheck():
    with os.popen("dpkg-parsechangelog -l debian/changelog -n 2 | awk -F'[()]' '{print $2}'|grep -v '^$\|^Task\|^Bug\|^Influence'|awk -F'-' '{print $1}'") as fin:
      versionLst = fin.readlines()
      if len(versionLst) == 2:
        version0 = versionLst[0].rstrip('\n')
        version1 = versionLst[1].rstrip('\n')
        if os.system(f'dpkg --compare-versions {version0} gt {version1}') == 0:
          writeCommentFile(f'[PASS]: 版本检查通过:{version0}|{version1}')
        else:
          writeCommentFile(f'[FAIL]: 版本检查不通过:{version0}|{version1}')
          exit(1)
      else:
        if len(versionLst) != 1:
          writeCommentFile(f'[ERR]: 版本检查异常:{versionLst}')
          exit(1)
        else:
          writeCommentFile(f'[PASS]: 版本检查通过:{versionLst}')

def writeCommentFile(commentMsg, commentType='body'):
  try:
    print(commentMsg)
    with open('comment.txt', "a+") as fout:
      fout.write(commentMsg+'\n')
  except Exception as e:
    print(f"[ERR]: writeCommentFile异常报错-{e}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="检查类型")
    # parser.add_argument("--repo", required=True, help="所有者和存储库名称。 例如，octocat/Hello-World")
    # parser.add_argument("--pr", required=True, help="pr number")
    # parser.add_argument("--token", required=True, help="github access token")
    parser.add_argument("--keys", required=False, help="查询关键字，逗号分隔")
    # parser.add_argument("--exclude", required=False, help="不进行敏感词筛选的文件后缀")
    parser.add_argument("--log", required=False, help="输出日志文件名")
    # parser.add_argument("--ref", required=False, help="commit sha")
    args = parser.parse_args()

    github_repository = os.getenv('GITHUB_REPOSITORY')
    github_token = os.getenv('GITHUB_TOKEN')
    github_job = os.getenv('GITHUB_JOB')
    pull_number = os.getenv('PULL_NUMBER')
    exclude_files = os.getenv('EXCLUDE_FILES')
    
    github_workflow_sha= os.getenv('GITHUB_WORKFLOW_SHA')
    github_ref_type = os.getenv('GITHUB_REF_TYPE')      
    html_url = getGithubChangeInfo.get_ref_runs(github_repository, github_workflow_sha, github_token)
    writeCommentFile(f"Debian检查:{html_url}")
    if args.type == 'pre-check':
      # head_ref = args.ref if args.ref else ''
      debianPreCheck(github_repository, pull_number, github_token)
    elif args.type == 'keys-check':
      keyLst = args.keys.split(",") if args.keys else []
      excludeSuffLst = exclude_files.split(',') if exclude_files else []
      # excludeSuffLst = args.exclude.split(',') if args.exclude else []
      logFile = args.log if args.log else 'githubResult.json'
      debianKeyWordsCheck(github_repository, pull_number, github_token, keyLst, excludeSuffLst, logFile)