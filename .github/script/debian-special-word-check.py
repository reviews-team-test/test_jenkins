import getGithubChaneInfo
import json

def readJsonFile(filepath):
    with open(filepath, 'r', encoding="utf-8") as fin:
        content = json.load(fin)
    return content
  
def getFilterInfo(keyLst, shaDict):
  filterInfo = {}
  for keyStr in keyLst:
    for key, value in shaDict.items():
        if value['b']:
          for strContent in value["b"]:
              if keyStr in strContent:
                if keyStr not in list(filterInfo.keys()):
                    filterInfo[keyStr] = {}
                if key not in list(filterInfo[keyStr].keys()):
                    filterInfo[keyStr][key] = []
                filterInfo[keyStr][key].append(strContent)

  # with open('filterInfo.json', "w") as fout:
  #     if isinstance(filterInfo, dict):
  #         fout.write(json.dumps(filterInfo, indent=4, ensure_ascii=False))
  if filterInfo:
    print(f"[ERR]: 存在敏感词{list(filterInfo.keys())}")
    exit(1)
  
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="查询项目名称")
    parser.add_argument("--token", required=True, default="at", help="github access token")
    parser.add_argument("--sha", required=True, help="查询哈希值")
    parser.add_argument("--keys", required=True, help="查询关键字，逗号分隔")
    args = parser.parse_args()
    
access_token = args.token
project_name = args.project
sha = args.sha
keyLst = args.keys.split(",")

logFile = "changeInfo.json"
getGithubChaneInfo.get_change_info(access_token, project_name, sha, logFile)
try:
  shaDict = readJsonFile("changeInfo.json")
  getFilterInfo(keyLst, shaDict)
except Exception as e:
  print(f"[ERR]: 异常报错-{e}")
  exit(1)
