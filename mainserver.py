import socket
import threading
import time
from database import *

SERVER_ADDRESS = ('localhost', 7680)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SERVER_ADDRESS)
server.listen()
participant=[]
servers=list()

def connections():
	""" Add client_socket to the list of participant
	"""
	while True:
		client_socket, address = server.accept()	# Accepts the connection
		participant.append(client_socket)		# Add participant's client socket in the list participant 
		threading.Thread(target=recieve,args=(client_socket,)).start()	# start thread for this client_socket

def optserver():
	"""This function is used to server which has less work. It is base for the load balancing in the program
	"""
	t=100
	index="0"
	for i in servers:
		k=time.time()				# Initial time
		i.send('%FAST%'.encode())	# Pings the server
		B=i.recv(1024).decode()		
		list=B.split("$")
		if t>float(list[1])-k:		# Finds server which responds fast
			t=float(list[1])-k
			index=list[0]
	print(index)
	return index					# returns the server which has less load that is server which responds fast

def recieve(clientsocket):
	"""This is the main receive function of mainserver. This provides server which has less load, checks sign in and sign up
	"""
	while True:
		try:
			a=clientsocket.recv(1024).decode()		# Receive command from client
			print(a)
			if a=="/OPTSERVER":						
				clientsocket.send(str(optserver()).encode())
			elif "/USER" in a:
				list=a.split("$")
				username=list[1]
				password=list[2]
				for i in range(3):
					d=int(float(is_online(username)))
					reply=sign_in_up(username,password)   # calls function from database module
					if reply==0:
						print("Sending -- Connected to server!")
						clientsocket.send("-- Connected to server!".encode())
						break
					elif reply==1:
						print("Sending Thanks for coming back!")		
						clientsocket.send(("Thanks for coming back!"+str(d)).encode())
						break
					elif reply==-1 and i<2:
						clientsocket.send("TRY AGAIN".encode())
					elif i==2:
						clientsocket.send("TRY AGAIN".encode())
						participant.remove(clientsocket)
			elif "/Exit" in a:
				exit_user(a.replace("/Exit",""))
				participant.remove(client_socket)
				return
			elif "/EXIT"==a:
				participant.remove(client_socket)
				return
		except:
		    break

def del_old_msgs():
	"""This fuction deletes the undelivered messages from the database after specified amount of time (Here 120 seconds)
	"""
	while True:
		time.sleep(120)
		print("deleting old messages....")
		deletion_of_old_msgs()			# Calls function from database

if __name__ == '__main__':
	open_database()			# Initiating database fastchat and creating required tables
	for i in range(5):
		client_socket, address = server.accept()
		servers.append(client_socket)
	threading.Thread(target=connections).start()	# Starting thread for connections
	threading.Thread(target=del_old_msgs).start()	# Starting thread for deletion of old messages from database
