from pickle import FALSE, GLOBAL
from re import A
import socket
import threading
from colorama import Fore
import hashlib
import rsa
import csv

SERVER_ADDRESS = ('localhost', 7880)
SERVER_ADDRESS1 = ('localhost', 7881)
SERVER_ADDRESS2 = ('localhost', 7882)
SERVER_ADDRESS3 = ('localhost', 7883)
SERVER_ADDRESS4 = ('localhost', 7884)
SERVER_ADDRESS5 = ('localhost', 7885)

def Receive(decode_type="", size: int = 1024):
	if decode_type=="":
		return client_socket.recv(size).decode()
	else:
 		return rsa.decrypt(client_socket.recv(size),privatekey)


def Send(message :str,encod_type:str=""):
	if encod_type=="":
		return client_socket.send(message.encode())
	elif encod_type=="NONE":
		return client_socket.send(message)


def Send_msg(message :str,pubkey2 :str):
	publicKeyReloaded = rsa.PublicKey.load_pkcs1(pubkey2.encode()) 
	client_socket.send(rsa.encrypt(message.encode(),publicKeyReloaded))


commands=["/Send",'/Exit','/Creategrp','/Addmember','/Sendgrp','/kick']
commands2=['%USER%','%PASS%','%TRYAGAIN%','%CONNECT%','%CREATEGROUP%',"%SENDGRP%","%ADDMEMBER%",'%QUIT%',"%DRT_MSG%","%REMOVE%","%GET OUT%"]

def handle_server_instruction(message):

	if message == '%USER%':
		Send(username)
	
	elif message == '%PASS%':
		Send(hashlib.sha256(password.encode()).hexdigest())
	
	elif message == '%TRYAGAIN%':
		password2=input(Fore.RED+'Try again:(\n'+Fore.GREEN+"Password: "+Fore.WHITE)
		Send(hashlib.sha256(password2.encode()).hexdigest())

	elif message=='%CONNECT%':
		threading.Thread(target=write).start()
	
	elif message == '%CREATEGROUP%':
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname)
		threading.Thread(target=write).start()

	elif message=="%SENDGRP%":
		groupname=input(Fore.GREEN+"GROUPNAME:\n"+Fore.RED+"$ "+Fore.BLUE)
		Message=input(Fore.GREEN+"MESSAGE:\n"+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname)
		mem=Receive()
		#print(Fore.WHITE+Receive())
		n=mem.count("@")
		l=mem.split("@")
		if n==0:
			print(Fore.WHITE+mem)
		else:
			for i in range(n):
				Send_msg("{"+groupname+"}"+"["+username+"]"+Message,l[i])
		threading.Thread(target=write).start()

	elif message=="%ADDMEMBER%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		member=input(Fore.GREEN+'NAME OF THE PERSON TO BE ADDED:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname)
		Send(member)
		print(Fore.WHITE+Receive())
		threading.Thread(target=write).start()
	
	elif message == '%QUIT%':
		print(Fore.RED+'Exiting...')
		client_socket.close()
		exit(0)
	
	elif message =="%DRT_MSG%":
		username2 = input(Fore.GREEN+"User name to which message is to be sent: \n"+Fore.RED+"$ "+Fore.BLUE)
		message = input(Fore.GREEN+"Message: \n"+Fore.RED+"$ "+Fore.BLUE)
		Send(username2)
		a=Receive()
		if a!="-1":
			Send_msg(username+" : "+message,a)
		else:
			print(Fore.WHITE+username2+" is not there")
		threading.Thread(target=write).start()
	
	elif message=="%REMOVE%":
		username_frnd = input(Fore.GREEN+"User name to be removed: \n"+Fore.RED+"$ "+Fore.BLUE)
		grp_name=input(Fore.GREEN+"From which group user to be removed: \n"+Fore.RED+"$ "+Fore.BLUE)
		Send(username_frnd)
		Send(grp_name)
		threading.Thread(target=write).start()
	
	elif message=="%GET OUT%":
		return 0
	else:
		print(Fore.WHITE+"Received unknown instruction "+message+" from server\n"+Fore.RED+"$ ")


def receive():
	"""Pool messages from server (runs in separate thread)"""
	while True:
		try:
			message=client_socket.recv(1024)
			try:
				dec_message = message.decode('utf-8')
			except:
				message=rsa.decrypt(message, privatekey)
				dec_message= message.decode('utf-8')
			if dec_message.startswith('%'):
				handle_server_instruction(str(dec_message))
				#if handle_server_instruction(str(dec_message))==0:
				#	return
			else:
				if dec_message=='-- Connected to server!':
					print(dec_message)
					publickey, privatekey = rsa.newkeys(1024)
					publicKeyPkcs1PEM = publickey.save_pkcs1().decode()
					privateKeyPkcs1PEM = privatekey.save_pkcs1().decode()
					filename=f"{username}.csv"
					with open(filename, 'w', newline='') as file:
						writer = csv.writer(file)
						writer.writerow([publicKeyPkcs1PEM])
						writer.writerow([privateKeyPkcs1PEM])
					client_socket.send(publicKeyPkcs1PEM.encode())
				elif dec_message=='Thanks for coming back!':
					print(dec_message)
					filename=f"{username}.csv"
					with open(filename, 'r') as file:
						csvreader = csv.reader(file)
						i=0
						for row in csvreader:
							if i==0:
								x=row[0]
								publickey=rsa.PublicKey.load_pkcs1(x.encode())
							if i==1:
								y=row[0]
								privatekey = rsa.PrivateKey.load_pkcs1(y.encode())
							i=i+1
				else:
					print(Fore.WHITE+message.decode()+Fore.RED+"\n$ ",end='')
		except OSError:
			print('An error occurred!')
			client_socket.close()
			break


def write():
	"""Hold open input for sending messages (runs in separate thread)"""
	while True:
		message=input(Fore.RED+"$ ")
		if message in commands:
			Send(message)
			break   


if __name__ == '__main__':
	try:
		username = input(Fore.GREEN+"Username: "+Fore.WHITE)
		password = input(Fore.GREEN+"Password: "+Fore.WHITE)
		publickey=1
		privatekey=1
		global client_sockets
		client_sockets=[]
		client_sockets[0].connect(SERVER_ADDRESS)
		client_sockets[1].connect(SERVER_ADDRESS1)
		client_sockets[2].connect(SERVER_ADDRESS2)
		client_sockets[3].connect(SERVER_ADDRESS3)
		client_sockets[4].connect(SERVER_ADDRESS4)
		client_sockets[5].connect(SERVER_ADDRESS5)
		client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect(SERVER_ADDRESS)
	except ConnectionRefusedError:
		print(Fore.WHITE+'Could not connect to the server. Exiting...')
		exit(1)
	receive_thread = threading.Thread(target=receive())
	receive_thread.start()