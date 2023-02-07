import subprocess

def check(file_path):
    o = subprocess.Popen('./check/lite --config ./check/config.json --test {}'.format(file_path),
        stderr = subprocess.PIPE, stdout = subprocess.DEVNULL, shell = False)
    o.communicate()
    o.wait()
    return

if __name__ == '__main__':
    check('./check/all.txt')