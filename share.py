# glpat-9PY3LxeTz5P_BtYcHjtL

import gitlab, os
import requests, json

# Create a file through Gitlab API
# https://docs.gitlab.com/ee/api/repository_files.html#create-new-file-in-repository

def uploadFile(auth_token,project_id,file_path,branch,email,name):
        gl = gitlab.Gitlab('https://gitlab.com', private_token=auth_token)
        gl.auth()
        with open(file_path, 'r') as my_file:
            file_content = my_file.read()
        file_name = os.path.basename(file_path)
        project = gl.projects.get(project_id)
        f = project.files.create({'file_path': file_name,
                                  'branch': branch,
                                  'content': file_content,
                                  'author_email': email,
                                  'author_name': name,
                                  'commit_message': 'Upload'})
        return 1

def transfersh(file_path):
    # https://transfer.sh/
    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        try: 
            requests.packages.urllib3.disable_warnings()
            r = requests.post('https://transfer.sh/', files={filename:f}, verify=False)
        except:
            return "Error"
    return r.text

def generatejson(running, good, low_delay, resultjson, local_speed, local_isp):
    res = {
        "running": running,
        "good": good,
        "low_delay": low_delay,
        "resultjson": resultjson,
        "local_speed": local_speed,
        "local_isp": local_isp
    }
    with open('./share_result.json', 'w') as f:
        json.dump(res, f, indent = 4, ensure_ascii=False)

if __name__ == '__main__':
    print(transfersh("./running.txt"))