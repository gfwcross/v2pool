from check import ping
from bench import speed
from pretest import merge
from rich import print
from rich.live import Live
from rich.table import Table
from rich.progress import track
import json
from rich.console import Console
import base64
import speedtest
import share
import requests
import configparser
import os

def speedtest_runner():
    if config.get("Preferences", "Speedtest") == "False":
        return

    table = Table()
    table.add_column('协议')
    table.add_column('节点名称')
    table.add_column('延迟')
    table.add_column('速度')
    speed.init_country()

    for i in track(range(0, len(live_nodes))):
        result = speed.run(live_nodes[i])
        _new_url = result[0]
        _id = live_nodes_id[i]
        _protocol = res['nodes'][_id]['protocol']
        _delay = res['nodes'][_id]['ping']
        _speed = result[2]
        _name = result[1]
        if _speed is None or _name is None or _delay is None or _protocol is None:
            continue
        if _speed >= good:
            good_nodes.append(_new_url)
        if int(_delay) <= 250:
            low_delay_nodes.append(_new_url)
        table.add_row(_protocol, _name, _delay, "%.1f"%_speed)
        results.append({"url": _new_url, 
            "speed": _speed, 
            "delay": int(_delay), 
            "name": _name, 
            "protocol": _protocol})
        with open('./result.json', 'w') as f:
            json.dump(results, f, indent = 2, ensure_ascii=False)


if __name__ == '__main__':

    console = Console()

## 读取配置文件，转换为字典
    console.rule("[bold red]读取配置文件")
    config = configparser.ConfigParser()
    config.read('pref.ini')
    print(config._sections, "\n")


## 合并订阅链接
    console.rule("[bold red]获取 & 合并订阅链接")
    all_links = merge.read_links()
    mixed = merge.convert(all_links)

## 写入到 all.txt，ping 测试（输出 out.json）
    console.rule("[bold red]可用性与真连接延迟测试")
    with open('./check/all.txt', 'w') as f:
        f.write(mixed)
    if config.get("Preferences", "Pingtest") == "True":
        ping.check('./check/all.txt')
        console.print('测试完成！\n')
    else:
        console.print('已跳过测试！\n')
    with open('./out.json', 'r', encoding = "utf-8") as f:
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
    with open('./running.txt', 'w') as f:
        f.write(base64.b64encode(all_nodes.encode('utf-8')).decode('utf-8'))
    
    console.print("已导出可用节点至 ./running.txt\n")

## 测试本地速度
    console.rule("[bold red]本地互联网速度测试")
    # st = speedtest.Speedtest()
    # st.get_best_server()
    # local_speed = st.download() / 1024 / 1024 / 8
    # console.print("本地互联网速度：[bold red]%.1f MB/s[/bold red]" % local_speed)
    good = 5
    # if (local_speed < 10):
    #     good = local_speed * 0.5
    console.print("\n\n")

## 打开json，跑 speedtest，输出为 result.json
    console.rule("[bold red]节点速度测试")
 
    good_nodes = []
    low_delay_nodes = []
    results = []

    speedtest_runner()

    with open('./good.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(good_nodes).encode('utf-8')).decode('utf-8'))
    with open('./low_delay.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(low_delay_nodes).encode('utf-8')).decode('utf-8'))
    
    console.print("已导出速度优秀节点至 ./good.txt\n")
    console.print("已导出延迟优秀节点至 ./low_delay.txt\n")

## 节点共享
    console.rule("[bold red]节点共享：人人为我，我为人人")
    
    console.print("获取本地网络信息...")
    proxies = { "http": None, "https": None}
    r = requests.get("http://ip-api.com/json/?lang=zh-CN", proxies=proxies)
    info = json.loads(r.text)
    isp_translator = { "Chinanet": "电信", "Chinaunicom": "联通", "Chinamobile": "移动"}
    if info['isp'] in isp_translator:
        info['isp'] = isp_translator[info['isp']]
    console.print("地区：[bold red]%s[/bold red]" % info['regionName'])
    console.print("运营商：[bold red]%s[/bold red]" % info['isp'])

    running = share.transfersh('./running.txt')
    console.print("上传所有可用节点 ==> [bold red]%s[/bold red]"%running)
    good    = share.transfersh('./good.txt')
    console.print("上传速度优秀节点 ==> [bold red]%s[/bold red]"%good)
    delay   = share.transfersh('./low_delay.txt')
    console.print("上传延迟优秀节点 ==> [bold red]%s[/bold red]"%delay)
    result  = share.transfersh('./result.json')
    console.print("上传测速结果文件 ==> [bold red]%s[/bold red]"%result)

    sh = share.generatejson(running, good, delay, result, "...", info['regionName'] + info['isp'])
    status = share.uploadFile("./%s"%sh)
    if (status):
        console.print("已生成分享链接到云端，感谢您的贡献！")
    else:
        console.print("上传失败，您仍然可以使用 transfer.sh 链接订阅。")
