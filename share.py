import gitlab, os
import requests, json
import uuid

# Create a file through Gitlab API
# https://docs.gitlab.com/ee/api/repository_files.html#create-new-file-in-repository

def uploadFile(file_path):
    auth_token = "glpat-FzgTKt-zJAsHxQUsQGDU"
    project_id = 42750275
    branch = "main"
    email = "user@gfwcross.tech"
    name = "GFWCross"
    gl = gitlab.Gitlab('https://gitlab.com', private_token=auth_token)
    try:
        gl.auth()
    except gitlab.exceptions.GitlabAuthenticationError as e:
        print(e)
        return 0
    
    with open(file_path, 'r') as my_file:
        file_content = my_file.read()
    
    try: 
        file_name = os.path.basename(file_path)
        project = gl.projects.get(project_id)
        f = project.files.create({'file_path': file_name,
                                    'branch': branch,
                                    'content': file_content,
                                    'author_email': email,
                                    'author_name': name,
                                    'commit_message': 'Upload'})
    except:
        return 0
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
    # 删除末尾回车
    res = r.text[:-1]
    return res

def generatejson(running, good, low_delay, resultjson, local_speed, local_isp):
    res = {
        "running": running,
        "good": good,
        "low_delay": low_delay,
        "resultjson": resultjson,
        "local_speed": local_speed,
        "local_isp": local_isp
    }
    # 随机生成一个 uuid
    filename = str(uuid.uuid4()) + ".json"
    with open(filename, 'w', encoding = "utf-8") as f:
        json.dump(res, f, indent = 4, ensure_ascii = False)
    return filename

if __name__ == '__main__':
    print(uploadFile("ea8d56fd-9b33-43b7-9289-f0788be16375.json"))