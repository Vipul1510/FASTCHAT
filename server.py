# Python program to implement server side of chat room. 
import socket 
import select
import sys 
import os
import psycopg2 as ps
from _thread import *
 
"""The first argument AF_INET is the address domain of the 
socket. This is used when we have an Internet Domain with 
any two hosts The second argument is the type of socket. 
SOCK_STREAM means that data or characters are read in 
a continuous flow."""

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# checks whether sufficient arguments have been provided

if len(sys.argv) != 3:
	print ("Correct usage: script, IP address, port number")
	exit() 

# takes the first argument from command prompt as IP address 
IP_address = str(sys.argv[1])
# takes second argument from command prompt as port number 
Port = int(sys.argv[2])
""" 
binds the server to an entered IP address and at the 
specified port number. 
The client must be aware of these parameters 
"""
server.bind((IP_address, Port))
#listens for 100 active connections. This number can be increased as per convenience.
server.listen(100) 
 

list_of_clients = [] 
def clientthread(conn, addr):
	# sends a message to the client whose user object is conn
	conn.send("Welcome to this chatroom!".encode())
	while True: 
		try:
			message = conn.recv(2048) 
			if message:
				"""prints the message and address of the 
				user who just sent the message on the server 
				terminal"""
				print ("<" + addr[0] + "> " + message)
				# Calls broadcast function to send message to all 
				message_to_send = "<" + addr[0] + "> " + message
				broadcast(message_to_send, conn)
			else:
				#message may have no content if the connection is broken, in this case we remove the connection
				remove(conn)
		except:
			continue

#Using the below function, we broadcast the message to all clients who's object is not the same as the one sending the message

def broadcast(message, connection, send_clients): 
	for clients in send_clients:
		if clients!=connection:
			try:
				clients.send(message.encode()) 
			except:
				clients.close()
				remove(clients) 
 
#The following function simply removes the object from the list that was created at the beginning of the program
def remove(connection): 
	if connection in list_of_clients: 
		list_of_clients.remove(connection)

db=ps.connect("All_users.db")
cursor=db.cursor()
cursor.execute('''CREATE TABLE USER_IDS(id PRIMARY TEXT,PASSWORD TEXT);''')

while True: 
	# Accepts a connection request and stores two parameters, conn which is a socket object for that user, and addr which contains the IP address of the client that just connected
	conn, addr = server.accept()
	#Maintains a list of clients for ease of broadcasting a message to all available people in the chatroom
	file1=open("1user.txt","r")
	str1=file1.readline()
	user=str1.split()[0]
	PASSWORD=str1.split()[1]
	os.remove("1user.txt")
	cursor.execute('''select decrypt(PASSWORD,decode('PASSWORD','escape'::text),'aes'::text) from user_ids where id=?''',user)
	found=False
	for i in cursor.fetchall():
		if i[0]==PASSWORD:
			found=True
		else:
			#error
	cursor.execute('''CREATE EXTENSION pgcrypto;''')
	if !(found):
		cursor.execute('''INSERT INTO USER_IDS(ID,PASSWORD) \ VALUES(?,?)''',str1.split(" ")[0],encrypt(PASSWORD,'PASSWORD','aes'))#crypt(str1.split[1],gen_salt("bf"))
	
	list_of_clients.append(conn)
	print (addr[0] + " connected")
	# creates and individual thread for every user that connects
	start_new_thread(clientthread,(conn,addr))     

conn.close() 
server.close()