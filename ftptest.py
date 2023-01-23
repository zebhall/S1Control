from ftplib import FTP
import time

FTP_IP = '197.168.137.139'
FTP_PORT = 55000


ftp = FTP(FTP_IP, source_address=('197.168.137.47',53861))
ftp.set_debuglevel(2)
ftp.connect()
ftp.login()

# import socket
# s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
# s.connect((FTP_IP, FTP_PORT))
# print(s)
