import github
import os
import json
def get_change_info(access_token, project_name, sha, logFile):
    try:
        g = github.Github(access_token)
        repo = g.get_repo(project_name)

        commit = repo.get_commit(sha)
        diff = commit.files

        originInfo = {}
        for file_diff in diff:
            originInfo[file_diff.filename] = {
                "a": [],
                "b": []
            }
            filePatch = file_diff.patch
            fileContent = filePatch.splitlines()
            for line in fileContent:
                if line.startswith("-      "):
                    originInfo[file_diff.filename]["a"].append(line.lstrip("-      "))
                elif line.startswith("+      "):
                    originInfo[file_diff.filename]["b"].append(line.lstrip("+      "))
           
        with open(logFile, "w") as fout:
            if isinstance(originInfo, dict):
                fout.write(json.dumps(originInfo, indent=4, ensure_ascii=False))
    except github.GithubException as e:
        print(f"Githun Api [ERR]: {e}")  
    except Exception as e:
        print(f"[ERR]: {e}")
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", required=True, help="拥有者")
    parser.add_argument("--repo", required=True, help="仓库名")
    parser.add_argument("--sha", required=True, help="查询sha")
    parser.add_argument("--logfile", required=False, help="输出日志文件名")
    args = parser.parse_args()
    
    access_token = os.getenv('GITHUB_ACCESS_TOKEN')
    project_name = args.owner+'/'+args.repo
    sha = args.sha
    logFile = "changeInfo.json"
    if args.logfile:
        logFile = args.logfile

    get_change_info(access_token, project_name, sha, logFile)