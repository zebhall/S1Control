import socket

# Define the IP address and port to listen on
IP_ADDRESS = "192.168.137.47"
PORT = 55205

# Create a socket object and bind it to the IP address and port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Set the socket to capture packets in promiscuous mode
#sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
#sock.bind((IP_ADDRESS, PORT))
client = sock.accept()


# Continuously capture and print incoming packets
while True:
    packet, addr = sock.recvfrom(65565)
    print(packet)