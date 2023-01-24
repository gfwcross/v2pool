from check import ping
from bench import speed
from merge import merge
from share import share
from rich import print
from rich.live import Live
from rich.table import Table
from rich.progress import track
import json
from rich.console import Console
import base64
import requests
import configparser
import os
import shutil
import time
from netspeedtest import sp

def speedtest_runner():
    table = Table()
    table.add_column('协议')
    table.add_column('节点名称')
    table.add_column('延迟')
    table.add_column('速度')
    
    obj = speed.benchmark()
    obj.__init__()
    results = []
    for i in track(range(0, len(live_nodes))):
        result = obj.run(live_nodes[i])
        _new_url = result[0]
        _id = live_nodes_id[i]
        _protocol = res['nodes'][_id]['protocol']
        _delay = res['nodes'][_id]['ping']
        _speed = result[2]
        _name = result[1]
        if (_speed is None) or (_name is None) or (_delay is None) or (_protocol is None):
            continue
        if _speed >= good:
            good_nodes.append(_new_url)
        if int(_delay) <= 300:
            low_delay_nodes.append(_new_url)
        table.add_row(_protocol, _name, _delay, "%.1f"%_speed)
        results.append({"url": _new_url, 
            "speed": _speed, 
            "delay": int(_delay), 
            "name": _name, 
            "protocol": _protocol})
        with open('./share/result.json', 'w', encoding = "utf-8") as f:
            json.dump(results, f, indent = 2, ensure_ascii=False)


if __name__ == '__main__':
    os.environ["NO_PROXY"] = '*'

    console = Console()

## 读取配置文件，转换为字典
    console.rule("[bold red]读取配置文件")
    config = configparser.ConfigParser()
    config.read('pref.ini')
    console.log(config._sections)


## 合并订阅链接
    console.rule("[bold red]获取 & 合并订阅链接")
    obj = merge.node_merge(console)
    links = obj.read_links()
    mixed = obj.convert(links)

## 写入到 all.txt，ping 测试（输出 out.json）
    console.rule("[bold red]可用性与真连接延迟测试")
    with open('./merge/all.txt', 'w') as f:
        f.write(mixed)
    if config.get("Preferences", "Pingtest") == "True":
        ping.check('./merge/all.txt')
        console.log('测试完成！')
    else:
        console.log('已跳过测试！')
    
    if os.path.exists('./out.json'):
        shutil.move('./out.json', './share/lite.json')
    with open('./share/lite.json', 'r', encoding = "utf-8") as f:
        res = json.load(f)
    live_nodes = []
    live_nodes_id = []
    for per in res["nodes"]:
        if per['isok']:
            live_nodes.append(per['link'])
            live_nodes_id.append(per['id'])
    all_nodes = ""
    for per in live_nodes:
        all_nodes += per + '\n'
    with open('./share/running.txt', 'w') as f:
        f.write(base64.b64encode(all_nodes.encode('utf-8')).decode('utf-8'))
    console.log("已导出可用节点至 ./share/running.txt")

## 测试本地速度
    console.rule("[bold red]本地互联网速度测试")
    localnetspeed = sp.speedtest()
    console.log("本地互联网速度：%.1f MB/s"%localnetspeed)
    mbps = int(localnetspeed * 8)
    if localnetspeed < 20: good = localnetspeed * 0.4 
    else: good = 8
    console.log("期望的节点速度: %.1f MB/s"%good)

## 打开json，跑 speedtest，输出为 result.json
    console.rule("[bold red]节点速度测试")
    good_nodes = low_delay_nodes = []
    
    if config.get("Preferences", "Speedtest") == "False":
        console.log("已跳过测试！")
    else:
        speedtest_runner()
    with open('./share/good.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(good_nodes).encode('utf-8')).decode('utf-8'))
    with open('./share/low_delay.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(low_delay_nodes).encode('utf-8')).decode('utf-8'))
    console.log("已导出速度优秀节点至 ./share/good.txt")
    console.log("已导出延迟优秀节点至 ./share/low_delay.txt")
    
    good_nodes_num = len(good_nodes)
    low_delay_nodes_num = len(low_delay_nodes)
    running_nodes_num = len(live_nodes)
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("节点总数", justify="center", style="dim", no_wrap=True)
    table.add_column("可用节点", justify="center", style="dim", no_wrap=True)
    table.add_column("速度优秀", justify="center", style="dim", no_wrap=True)
    table.add_column("延迟优秀", justify="center", style="dim", no_wrap=True)
    table.add_row(str(len(res["nodes"])), str(running_nodes_num), 
        str(good_nodes_num), str(low_delay_nodes_num))

## 节点共享
    console.rule("[bold red]节点共享：人人为我，我为人人")
    
    console.log("获取本地网络信息...")
    proxies = { "http": None, "https": None}
    try:
        r = requests.get("http://ip-api.com/json/", proxies=proxies)
    except:
        info = {'regionName': "未知", 'isp': "未知"}
    info = json.loads(r.text)
    local_ip = info['query']
    url = "http://opendata.baidu.com/api.php?query=%s&resource_id=6006&oe=utf8"%local_ip
    r = requests.get(url, proxies=proxies)
    detail = json.loads(r.text)['data'][0]['location']
    if (detail.find("移动") != -1): info['isp'] = "Chinamobile"
    if (detail.find("联通") != -1): info['isp'] = "Chinaunicom"
    if (detail.find("电信") != -1): info['isp'] = "Chinanet"

    running = share.transfersh('./share/running.txt')
    console.log("上传所有可用节点 ==> [bold red]%s[/bold red]"%running)
    good    = share.transfersh('./share/good.txt')
    console.log("上传速度优秀节点 ==> [bold red]%s[/bold red]"%good)
    delay   = share.transfersh('./share/low_delay.txt')
    console.log("上传延迟优秀节点 ==> [bold red]%s[/bold red]"%delay)
    result  = share.transfersh('./share/result.json')
    console.log("上传测速结果文件 ==> [bold red]%s[/bold red]"%result)

    sh = share.generatejson(running, running_nodes_num, good, 
        good_nodes_num, delay, result, mbps, 
        info['regionName'], info['isp'], detail)

    console.log("正在上传分享链接到云端...")
    bb = share.backblaze(
        "005dd61b9ce80da0000000001", 
        "K005kfqpEhTHh78tpCA1pjHDq7BvMwk", 
        "0d7d26114b59ccfe88500d1a")
    bb.get_auth()
    status = bb.upload_file("./%s"%sh)
    if (status):
        console.log("已生成分享链接到云端，感谢您的贡献！")
    else:
        console.log("上传失败，您仍然可以使用 transfer.sh 链接订阅。")

    console.log("按 Ctrl+C 退出程序或关闭窗口。")
# 一直等待
time.sleep(2147483647)

