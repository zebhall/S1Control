import socket
import time
import os
import threading

XRF_FTP_IP = '192.168.137.139'
XRF_FTP_PORT = 55000

xrfsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
xrfsocket.connect((XRF_FTP_IP, XRF_FTP_PORT))
xrfsocket.setblocking(False)


def sendCommand(s:socket, data):
    s.send(data)
    print(f'sent {data}')

def recvData(s:socket):
    data = s.recv(1024)#.replace(b"\x00", b"")
    #data = data.decode()
    print(f'recv {data}')
    return data


# XRF Listen Loop Functions

def xrfListenLoopThread_Start(event):
    global listen_thread
    listen_thread = threading.Thread(target=xrfListenLoop)
    listen_thread.daemon = True
    listen_thread.start()

def xrfListenLoop():
    while True:
        try:
            recvData(xrfsocket)
        except socket.error:
            pass
        time.sleep(0.05)



weird_blank_deadfeed_packet = b"\x00\x00\x00\x00\xed\xfe\xad\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
txt_weird_blank_deadfeed_packet = weird_blank_deadfeed_packet.hex()
get_cmd_file = b"\x24\x4f\x57\x20\x32\x31\x2c\x20\x42\x72\x75\x6b\x65\x72\x43\x6f\x6d\x6d\x61\x6e\x64\x46\x69\x6c\x65\x2e\x43\x4d\x44\x0d"
get_file_list_root = b"\x24\x46\x57\x20\x31\x36\x2c\x20\x3a\x0d\x47\x65\x74\x46\x69\x6c\x65\x4c\x69\x73\x74\x20\x5c\x2a\x2e\x2a"    # $FW 16, :GetFileList \*.*
get_file_status_geoexpl_aen = b"\x24\x46\x57\x20\x34\x30\x2c\x20\xd9\x0d\x47\x65\x74\x46\x69\x6c\x65\x53\x74\x61\x74\x75\x73\x20\x5c\x42\x52\x55\x4b\x45\x52\x5c\x47\x65\x6f\x45\x78\x70\x6c\x6f\x72\x61\x74\x69\x6f\x6e\x2e\x61\x65\x6e"


xrfListenLoopThread_Start(None)
print('listen loop started')
time.sleep(1)

sendCommand(xrfsocket, weird_blank_deadfeed_packet)   
time.sleep(2)
sendCommand(xrfsocket, get_cmd_file)
time.sleep(2)
sendCommand(xrfsocket, get_file_list_root)
time.sleep(2)
sendCommand(xrfsocket, get_file_status_geoexpl_aen)
time.sleep(2)



xrfsocket.close()



