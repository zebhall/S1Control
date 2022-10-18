# S1Control by ZH for PSS
global versionNum
global versionDate
versionNum = 'v0.0.1'
versionDate = '2022/10/18'


import socket
import xmltodict


global XRF_IP
global XRF_PORT
XRF_IP = '192.168.137.139'
XRF_PORT = 55204

s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def sendCommand(s, command):
    msg = '<?xml version="1.0" encoding="utf-8"?>'+ command
    msgData = b'\x03\x02\x00\x00\x17\x80'+len(msg).to_bytes(4,'little')+msg.encode('utf-8')+b'\x06\x2A\xFF\xFF'
    sent = s.sendall(msgData)
    if sent == 0:
        print('Error: XRF Socket disconnected')



s.connect((XRF_IP, XRF_PORT))

queryInstDef = '<Query parameter="Instrument Definition"/>'
queryLoginState = '<Query parameter="Login State"/>'
commandLogin = '<Command>Login</Command>'
#sendCommand(s, commandLogin)
#sendCommand(s, queryLoginState)
sendCommand(s, queryInstDef)



header = s.recv(10)
data_size = int.from_bytes(header[6:10], 'little')
data = s.recv(data_size)
footer = s.recv(4)


dataMod = data.decode("utf-8").replace('\n','').replace('\r','').replace('\t','')
msg = xmltodict.parse(dataMod)
print(msg)

s.close()