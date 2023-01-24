import subprocess, time, os

def speedtest():
    url = "https://webcdn.m.qq.com/spcmgr/download/QQBrowser_Setup_Qqpcmgr_11.5.5240.400.exe"
    start_time = time.time()
    p = subprocess.Popen('./netspeedtest/wget -q -c %s -O tmp --no-proxy'%url)
    p.communicate()
    p.wait()
    end_time = time.time()
    total_time = end_time - start_time
    speed = 100 / total_time
    if os.path.exists('./tmp'):
        os.remove('./tmp')
    return speed
