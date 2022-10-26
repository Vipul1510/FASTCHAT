import socket
import select
import sys
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 
user_name=str(sys.argv[3])# user name for identifying admin without white spaces
password=str(sys.argv[4])#  password of the user without white spaces
file1=open("1user.txt","a")
file1.write(user_name+" "+password)
file1.close()
while True:
	# maintains a list of possible input streams 
	sockets_list = [sys.stdin, server]
	""" There are two possible input situations. Either the 
	user wants to give manual input to send to other people, 
	or the server is sending a message to be printed on the 
	screen. Select returns from sockets_list, the stream that 
	is reader for input. So for example, if the server wants 
	to send a message, then the if condition will hold true 
	below.If the user wants to send a message, the else 
	condition will evaluate as true"""

	read_sockets,write_socket, error_socket = select.select(sockets_list,[],[])
	for socks in read_sockets: 
		if socks == server: 
			message = socks.recv(2048) 
			print (message) 
		else: 
			message = sys.stdin.readline() 
			server.send(message.encode()) 
			sys.stdout.write("<You>")
			sys.stdout.write(message)
			sys.stdout.flush()
server.close()