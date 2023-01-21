import json
from datetime import datetime
from rich import print
from rich.console import Console
import requests
import time

class node_merge:

    def __init__(self, console):
        self.console = console

    def read_links(self):
        # 读取配置文件
        with open('./merge/config.json', 'r') as f:
            conf = json.load(f)
        
        # 遍历所有的链接
        links = []
        for per in conf:
            if per['update_method'] != 'auto':
                if per['id'] == 0:
                    per['url'] = 'https://gcore.jsdelivr.net/gh/pojiezhiyuanjun/freev2/{}clash.yml'.format(datetime.now().strftime('%m%d'))
                if per['id'] == 7:
                    per['url'] = 'https://nodefree.org/dy/{}.txt'.format(datetime.now().strftime('%Y%m/%Y%m%d'))
                if per['id'] == 8:
                    per['url'] = 'https://clashnode.com/wp-content/uploads/{}.txt'.format(datetime.now().strftime('%Y/%m/%Y%m%d'))
                self.console.log("更新链接 ", per['id'], " \t--> ", per['url'])
            links.append(per['url'])

        time.sleep(1)
        self.console.log("欲合并的订阅链接列表: ", links)
        time.sleep(1)
        # 更新 json 文件
        with open('./merge/config.json', 'w') as f:
            json.dump(conf, f, indent = 4)
        return links

    def convert(self, sub):
        api_url = 'https://api.v1.mk/sub?target=mixed&url='
        for url in sub:
            api_url += '|' + url
        api_url += '&insert=false'

        # 请求 api
        self.console.log("请求链接: ", api_url)
        try: 
            r = requests.get(api_url)
        except:
            self.console.log("请求失败, 未知错误")
            return None
        if r.status_code == 200:
            self.console.log("成功请求, 长度 %d "%len(r.text))
            return r.text
        else:
            self.console.log("请求失败, 状态码", r.status_code)
            return None

if __name__ == '__main__':
    console = Console()
    obj = node_merge(console)
    links = obj.read_links()
    obj.convert(links)