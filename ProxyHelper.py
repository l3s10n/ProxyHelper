#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from socket import error
import threading
import time
import requests
import re

type="https" # http or https

class ProxyServerTest:
    def __init__(self):
        # 本地socket服务
        self.ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def getRandomProxy(self):
        if type == "http":
            url = "http://127.0.0.1:5010/get/"
        elif type == "https":
            url = "http://127.0.0.1:5010/get/?type=https"
        else:
            print('[*' + self.getTime() + ']: Type Error')
            exit()
        try:
            proxy = requests.get(url).json()["proxy"].split(":")
            proxy[1] = int(proxy[1])
        except:
            print('[*' + self.getTime() + ']: ' + f"No {type} proxiy can be used")
            exit()
        # return ['10.162.89.147', 8000]
        return proxy

    # 非阻塞获取socket的返回值
    def socketReadHelper(self, socket):
        socket.setblocking(False)
        try:
            data = socket.recv(8192)
        except:
            data = b""
        socket.setblocking(True)
        return data

    def isFirstPartResponse(self, reponse):
        # 通过头部和数据体判断当前报文是否只是第一部分

        hasBody = False

        headerPart = reponse.split(b'\r\n\r\n')[0]
        bodyPart = reponse.split(b'\r\n\r\n')[1]

        headers = headerPart.split(b'\r\n')
        for header in headers:
            r = re.search("(.*):(.*)", header.decode(), re.M|re.I)
            if r:
                if r.group(1) == "Content-Type" or r.group(1) == "Transfer-Encoding":
                    hasBody = True
        if hasBody and bodyPart==b'':
            return True
        else:
            return False

    def getTime(self):
        return time.asctime(time.localtime(time.time()))

    def run(self):
        try:
            # 本地服务IP和端口
            self.ser.bind(('127.0.0.1', 8081))
            # 最大连接数
            self.ser.listen(50)
        except error as e:
            print('[*' + self.getTime() + ']: ' + "The local service : " + str(e))
            return '[*' + self.getTime() + ']: ' + "The local service : " + str(e)

        while True:
            try:
                # 接收客户端数据
                client, addr = self.ser.accept()
                print('[*' + self.getTime() + ']: ' + 'Accept %s connect' % (addr,))
                data = client.recv(8192)
                if not data:
                    break
                print('[*' + self.getTime() + ']: Accept data from client...')
            except error as e:
                print('[*' + self.getTime() + ']: ' + "Local receiving client : " + str(e))
                return '[*' + self.getTime() + ']: ' + "Local receiving client : " + str(e)

            while True:
                # 将从客户端接收数据转发给代理服务器，直到拿到代理服务器的返回报文之前不断重试
                mbsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                proxyip = self.getRandomProxy()
                print('[*' + self.getTime() + ']: ' + "Now proxy ip:" + str(proxyip))
                prip = proxyip[0]
                prpo = proxyip[1]
                try:
                    mbsocket.settimeout(3)
                    mbsocket.connect((prip, prpo))
                    mbsocket.send(data)
                    data_1 = mbsocket.recv(8192)
                except Exception as e:
                    print('[*' + self.getTime() + ']: ' + "Cannot connect proxy server")
                    print('[*' + self.getTime() + ']: ' + "Use other proxy to RE_Connect...")
                    continue
            
                if data_1[0:4]!=b'HTTP':
                    print('[*' + self.getTime() + ']: ' + "Illegal response")
                    print('[*' + self.getTime() + ']: ' + "Use other proxy to RE_Connect...")
                    continue

                if type == "http":
                    print('[*' + self.getTime() + ']: ' + "Got response from proxy server")
                    if self.isFirstPartResponse(data_1):
                        # 代理服务器返回报文时，有可能先返回返回报文的头部，再返回返回报文的内容
                        print('[*' + self.getTime() + ']: ' + "This is only first part")
                        try:
                            data_2 = mbsocket.recv(8192)
                        except:
                            print('[*' + self.getTime() + ']: ' + "Cannot get second part")
                            print('[*' + self.getTime() + ']: ' + "Use other proxy to RE_Connect...")
                            continue
                        print('[*' + self.getTime() + ']: ' + "Got second part response from proxy server")
                        print('[*' + self.getTime() + ']: ' + "Send response to client")
                        client.send(data_1)
                        client.send(data_2)
                    else:
                        print('[*' + self.getTime() + ']: ' + "Send response to client")
                        client.send(data_1)
            
                if type == "https":
                    # 如果是https，要建立起隧道、进行TLS的交互，再之后才能发送和接受数据
                    print(data_1)
                    print('[*' + self.getTime() + ']: ' + "Https tunnel established")
                    client.send(data_1)
                    TLSMessageC = b""
                    TLSMessageS = b""
                    print('[*' + self.getTime() + ']: ' + "Communicate through https tunnel")
                    while True:
                        try:
                            TLSMessageC = self.socketReadHelper(client)
                            TLSMessageS = self.socketReadHelper(mbsocket)

                            if TLSMessageC != b"":
                                mbsocket.send(TLSMessageC)
                            if TLSMessageS != b"":
                                client.send(TLSMessageS)
                        except:
                            print('[*' + self.getTime() + ']: ' + 'Something wrong in communicating through https tunnel...')
                            break

                        # 获取TLS报文的类型，看是否是分手报文（TLS报文的第一个字节标识了TLS报文的类型）
                        if (len(TLSMessageC) >=1 and TLSMessageC[0]==21) or (len(TLSMessageS) >=1 and TLSMessageS[0]==21):
                            break

                print('[*' + self.getTime() + ']: ' + "One proxy over")
                break

            # 关闭连接
            client.close()
            mbsocket.close()

def main():
    print('''*Atuhor : lesion.





__________                              ___ ___         .__                       
\______   \_______  _______  ______.__./   |   \   ____ |  | ______   ___________ 
 |     ___/\_  __ \/  _ \  \/  <   |  /    ~    \_/ __ \|  | \____ \_/ __ \_  __ \
 |    |     |  | \(  <_> >    < \___  \    Y    /\  ___/|  |_|  |_> >  ___/|  | \/
 |____|     |__|   \____/__/\_ \/ ____|\___|_  /  \___  >____/   __/ \___  >__|   
                              \/\/           \/       \/     |__|        \/       






    ''')

    try:
        pst = ProxyServerTest()
        # 多线程
        t = threading.Thread(target=pst.run, name='LoopThread')
        print('[*]Waiting for connection...')
        # 关闭多线程
        t.start()
        t.join()
    except Exception as e:
        print("[-]main : " + str(e))
        return "[-]main : " + str(e)

if __name__ == '__main__':
    main()
