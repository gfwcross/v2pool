import json, sys
from datetime import datetime
from rich import print
from rich.panel import Panel
from rich.text import Text
import requests


def read_links():
    # 读取配置文件
    with open('./pretest/config.json', 'r') as f:
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
            print("更新链接 ", per['id'], " \t--> ", per['url'])
        links.append(per['url'])

    print("\n欲合并的订阅链接列表: ", links)

    # 更新 json 文件
    with open('./pretest/config.json', 'w') as f:
        json.dump(conf, f, indent = 4)

    return links

def convert(sub):
    api_url = 'https://api.v1.mk/sub?target=mixed&url='
    for url in sub:
        api_url += '|' + url
    api_url += '&insert=false'

    # 请求 api
    print("\n请求链接: ", api_url)
    try: 
        r = requests.get(api_url)
    except:
        print("\n请求失败, 未知错误")
        return None
    if r.status_code == 200:
        print("成功请求\n\n")
        return r.text
    else:
        print("\n 请求失败, 状态码", r.status_code)
        return None

if __name__ == '__main__':
    convert(read_links())

