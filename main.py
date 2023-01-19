from check import ping
from bench import speed
from pretest import merge
from rich import print
from rich.live import Live
from rich.table import Table
import json
from rich.console import Console
import base64
import speedtest

if __name__ == '__main__':
    console = Console()

    # 合并订阅链接
    console.rule("[bold red]获取 & 合并订阅链接")

    all_links = merge.read_links()
    mixed = merge.convert(all_links)

    # 写入到 all.txt，用于 ping 测试（输出 out.json）
    console.rule("[bold red]可用性与真连接延迟测试")
    with open('./check/all.txt', 'w') as f:
        f.write(mixed)
    ping.check('./check/all.txt')

    console.print('测试完成！\n')
    
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

    # 测试本地速度
    console.rule("[bold red]本地互联网速度测试")
    # st = speedtest.Speedtest()
    # st.get_best_server()
    # local_speed = st.download() / 1024 / 1024 / 8
    # console.print("本地互联网速度：[bold red]%.1f MB/s[/bold red]" % local_speed)
    
    good = 5
    # if (local_speed < 10):
    #     good = local_speed * 0.5

    console.print("\n\n")

    # 打开json，跑 speedtest
    console.rule("[bold red]节点速度测试")
 
    good_nodes = []
    low_delay_nodes = []

    table = Table()
    table.add_column('协议')
    table.add_column('节点名称')
    table.add_column('延迟')
    table.add_column('速度')
    speed.init_country()
    with Live(table, refresh_per_second=4) as live:
        for i in range(0, len(live_nodes)):
            result = speed.run(live_nodes[i])
            _new_url = result[0]
            _id = live_nodes_id[i]
            _protocol = res['nodes'][_id]['protocol']
            _delay = res['nodes'][_id]['ping']
            _speed = result[2]
            _name = result[1]
            if _speed == None or _name == None or _delay == None or _protocol == None:
                continue
            if _speed >= good:
                good_nodes.append(_new_url)
            if int(_delay) <= 250:
                low_delay_nodes.append(_new_url)
            table.add_row(_protocol, _name, _delay, "%.1f"%_speed)
    
    with open('./good.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(good_nodes).encode('utf-8')).decode('utf-8'))
    with open('./low_delay.txt', 'w') as f:
        f.write(base64.b64encode('\n'.join(low_delay_nodes).encode('utf-8')).decode('utf-8'))
    
    console.print("已导出速度优秀节点至 ./good.txt\n")
    console.print("已导出延迟优秀节点至 ./low_delay.txt\n")

    # 节点共享
    console.rule("[bold red]节点共享：人人为我，我为人人")
    

