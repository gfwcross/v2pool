import subprocess, os, re, json, socket, base64

global country_dict

def test_per_node(url):
    # 调用 stairspeedtest 测试
    obj = subprocess.Popen(["./bench/stairspeedtest"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    obj.stdin.write(bytes(url, encoding='gbk'))
    obj.communicate()
    code = obj.wait()
    if (code != 0):
        return None
    
    # 寻找文件夹下最新的日志文件
    path = "./bench/logs"
    lists = os.listdir(path)
    lists.sort(key=lambda x:os.path.getmtime((path+"\\"+x)))
    file_new = os.path.join(path, lists[-1])
    
    inbound = None
    outbound = None
    speed = None

    # 读取日志文件，获取结果
    with open(file_new, 'r', encoding = 'utf-8') as f:
        log = f.read()
        # 遍历每一行，寻找 GEOIP 和 速度信息
        for line in log.splitlines():
            geoip_find = line.find('Fetched GeoIP data: ')
            speed_find = line.find('Average speed: ')
            if (geoip_find != -1 and inbound == None and outbound == None):
                inbound = line[geoip_find + 20:]
                continue
            if (geoip_find != -1 and inbound != None and outbound == None):
                outbound = line[geoip_find + 20:]
                continue
            if (speed_find != -1):
                speed = re.findall("\d+\.?\d*", line[speed_find + 15 : speed_find + 22])[0]
                if (line[speed_find + 15 : speed_find + 22].find('K') != -1):
                    speed = float(speed) * 0.001
                else:
                    speed = float(speed)
    
    return inbound, outbound, speed

def isp_translate(isp):
    isp_dict = {
        "Cloudflare": "CF",
        "Google": "谷歌云",
        "Amazon": "AWS",
        "Microsoft": "Azure"
    }
    for i in isp_dict:
        if (isp.find(i) != -1):
            return isp_dict[i]
    return isp

def country_translate(country):

    with open('./bench/country.json', 'r', encoding = 'utf-8') as f:
        country_dict = json.load(f)[0]
    if (country in country_dict):
        return country_dict[country]


def give_name(inboundip, bound1, bound2):
    # 未知情况
    if (bound1 == bound2 == None):
        return "Unknown"
    if (bound1 == None):
        return country_translate(bound2.get('country_code')) + ' ' + isp_translate(bound2.get('isp'))
    if (bound2 == None):
        return country_translate(bound1.get('country_code')) + ' ' + isp_translate(bound1.get('isp'))

    # 若 inboundip 为域名，则获取域名的 ip 地址
    if (re.match(r'.*[a-zA-Z]+.*', inboundip)):
        inboundip = socket.gethostbyname(inboundip)

    # 判定出入口节点
    inbound = outbound = None
    if (inboundip == bound1.get('ip')):
        # bound1 为入口节点
        inbound = bound1
        outbound = bound2
    else:
        inbound = bound2
        outbound = bound1

    # 直连节点
    if (inbound.get('ip') == outbound.get('ip')):
        return country_translate(inbound.get('country_code')) + inbound.get('isp')

    # CF CDN 节点
    if (inbound.get('isp').find('Cloudflare') != -1):
        return 'CF > ' + \
            country_translate(outbound.get('country_code')) + isp_translate(outbound.get('isp'))

    # 中转节点
    return country_translate(inbound.get('country_code')) + ' -> ' + \
        country_translate(outbound.get('country_code')) + isp_translate(outbound.get('isp'))

def rename_node(bound1, bound2, origin_url):
    # 获取前缀协议名称
    prefix = origin_url[0 : origin_url.find('://')]
    
    if (prefix == 'ss'):
        # ss://method:password@server:port#name
        serverip = origin_url[origin_url.find('@') + 1 : origin_url.find(':')] 
        new_name = give_name(serverip, bound1, bound2)
        new_url = origin_url[: origin_url.find('#') + 1] + new_name
        return new_url, new_name
    
    if (prefix == 'ssr'):
        # ssr://server:port:protocol:method:obfs:password_base64/?params_base64#name
        serverip = origin_url[origin_url.find('//') + 2 : origin_url.find(':')]
        new_name = give_name(serverip, bound1, bound2)
        new_url = origin_url[: origin_url.find('#') + 1] + new_name
        return new_url, new_name
    
    if (prefix == 'vmess'):
        # vmess://base64(json)
        json_str = base64.b64decode(origin_url[origin_url.find('//') + 2 :]).decode('utf-8')
        json_dict = json.loads(json_str)
        serverip = json_dict.get('add')
        new_name = give_name(serverip, bound1, bound2)
        json_dict['ps'] = new_name
        new_url = "vmess://" + base64.b64encode(json.dumps(json_dict).encode('utf-8')).decode('utf-8')
        return new_url, new_name
    
    if (prefix == 'trojan'):
        # trojan://password@server:port#name
        serverip = origin_url[origin_url.find('@') + 1 : origin_url.find(':')]
        new_name = give_name(serverip, bound1, bound2)
        new_url = origin_url[: origin_url.find('#') + 1] + new_name
        return new_url, new_name
        
def run(url):
    # 测速
    result = test_per_node(url)
    if (result[0] == None):
        bound1 = None
    else:
        bound1 = json.loads(result[0])
    if (result[1] == None):
        bound2 = None
    else:
        bound2 = json.loads(result[1])
    speed = result[2]

    # 重命名节点
    result = rename_node(bound1, bound2, url)
    new_url = result[0]
    new_name = result[1]
    return new_url, new_name, speed


def init_country():
    with open('./bench/country.json', 'r', encoding = 'utf-8') as f:
        country_dict = json.load(f)[0]

if __name__ == '__main__':
    with open('./bench/country.json', 'r', encoding = 'utf-8') as f:
        country_dict = json.load(f)[0]
