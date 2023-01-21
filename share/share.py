import json
import uuid
import time
import base64
import requests
import os

# Create a file through Backblaze
# https://www.backblaze.com/b2/docs/

class backblaze:
    def __init__(self, application_keyid, application_key, bucket_id):
        self.application_key = application_key
        self.application_keyid = application_keyid
        self.bucket_id = bucket_id
        self.auth = None
        self.api_url = None
    
    def get_auth(self):
        # 获取认证信息
        id_and_key = '{}:{}'.format(self.application_keyid, self.application_key)
        basic_auth_string = 'Basic ' + base64.b64encode(bytes(id_and_key, encoding='utf-8')).decode('utf-8')
        headers = { 'Authorization': basic_auth_string }
        r = requests.get('https://api.backblazeb2.com/b2api/v2/b2_authorize_account', headers = headers)
        if r.status_code == 200:
            self.auth = r.json().get('authorizationToken')
            self.api_url = r.json().get('apiUrl')
            return True
        else:
            return False
    
    def upload_file(self, filename):
        # 上传文件 https://www.backblaze.com/b2/docs/uploading.html
        if self.auth == None:
            if not self.get_auth():
                return False
        headers = { 'Authorization': self.auth }
        r = requests.get(self.api_url + '/b2api/v2/b2_get_upload_url', headers = headers, params = { 'bucketId': self.bucket_id })
        upload_url = r.json().get('uploadUrl')
        upload_auth = r.json().get('authorizationToken')

        headers = { 'Authorization': upload_auth,  "Content-Type": "text/plain", "X-Bz-Content-Sha1": "do_not_verify" }
        with open(filename, 'rb') as f:
            singlename = os.path.basename(filename)
            content = f.read()
            r = requests.post(upload_url, headers = headers, data = content, params = { 'fileName': singlename })
        if r.status_code == 200:
            return True
        else:
            print(r.content, r.status_code)
            return False

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


def generatejson(running, running_num, good, good_num, 
    low_delay, resultjson, local_speed, region, isp):
    res = {
        "running": running,
        "running_num": running_num,
        "good": good,
        "good_num": good_num,
        "low_delay": low_delay,
        "resultjson": resultjson,
        "local_speed": local_speed,
        "region": region,
        "isp": isp,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "uploadTimestamp": int(time.time() * 1000)
    }
    # 随机生成一个 uuid
    filename = str(uuid.uuid4()) + ".json"
    with open(filename, 'w', encoding = "utf-8") as f:
        json.dump(res, f, indent = 4, ensure_ascii = False)
    return filename

if __name__ == '__main__':
    # bb = backblaze("005dd61b9ce80da0000000001", 
    #     "K005kfqpEhTHh78tpCA1pjHDq7BvMwk", 
    #     "0d7d26114b59ccfe88500d1a")
    # bb.get_auth()
    # bb.upload_file("./main.py")
    pass