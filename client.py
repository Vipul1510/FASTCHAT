from pickle import FALSE, GLOBAL
from re import A
import socket
import threading
from traceback import print_tb
import colorama
from colorama import Fore
from sa import *
import os
import hashlib
import rsa
import csv

SERVER_ADDRESS = ('localhost', 7889)
# SERVER_ADDRESS1 = ('127.0.0.1', 15661)
# SERVER_ADDRESS2 = ('127.0.0.1', 15662)
# SERVER_ADDRESS3 = ('127.0.0.1', 15663)
# SERVER_ADDRESS4 = ('127.0.0.1', 15664)
ENCODING = 'utf-8'


def receive_from(client_socket, decode_type:str =ENCODING, size: int = 1024):
	if decode_type=="":
		return client_socket.recv(size).decode()
	else:
 		return client_socket.recv(size).decode(decode_type)


def Send(client_socket, message :str,encod_type:str =ENCODING):
	if encod_type=="":
		return client_socket.send(message.encode())
	elif encod_type=="NONE":
		return client_socket.send(message)
	else:
 		return client_socket.send(message.encode(ENCODING))


def Send_msg(client_socket, message :str,publickey:int):
	Send(client_socket,encrypt(message,publickey),"NONE")


commands=["/Send",'/Exit','/Creategrp','/Addmember','/Sendgrp','/kick']
def handle_server_instruction(message):
	if len(message)<2:
		print(Fore.WHITE+"Received unknown instruction "+message+" from server")
	if message[0]!="%" or message[len(message)-1]!="%":
		print(Fore.WHITE+"Received unknown instruction "+message+" from server")

	if message == '%USER%':
		Send(client_socket,username)
	
	elif message == '%PASS%':
		Send(client_socket,hashlib.sha256(password.encode(ENCODING)).hexdigest())

	elif message=='%CONNECT%':
		threading.Thread(target=write).start()
	
	elif message == '%CREATEGROUP%':
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(client_socket,groupname)
		threading.Thread(target=write).start()

	elif message=="%SENDGRP%":
		groupname=input(Fore.GREEN+"GROUPNAME:\n"+Fore.RED+"$ "+Fore.BLUE)
		Message=input(Fore.GREEN+"MESSAGE:\n"+Fore.RED+"$ "+Fore.BLUE)
		Send(client_socket,groupname)
		Send(client_socket,Message)
		print(Fore.WHITE+receive_from(client_socket))
		threading.Thread(target=write).start()

	elif message=="%ADDMEMBER%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		member=input(Fore.GREEN+'NAME OF THE PERSON TO BE ADDED:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(client_socket,groupname)
		Send(client_socket,member)
		print(Fore.WHITE+receive_from(client_socket))
		threading.Thread(target=write).start()
	
	elif message == '%TRYAGAIN%':
		password2=input(Fore.RED+'TRYAGAIN\n'+Fore.GREEN+"Password: "+Fore.WHITE)
		Send(client_socket,hashlib.sha256(password2.encode(ENCODING)).hexdigest())
	
	elif message == '%QUIT%':
		print(Fore.RED+'Exiting...')
		client_socket.close()
		exit(0)
	
	elif message =="%DRT_MSG%":
		username_frnd = input(Fore.GREEN+"User name to which message is to be sent: \n"+Fore.RED+"$ "+Fore.BLUE)
		message = input(Fore.GREEN+"Message: \n"+Fore.RED+"$ "+Fore.BLUE)
		Send(client_socket,username_frnd)
		Send(client_socket,message)
		threading.Thread(target=write).start()
	
	elif message=="%REMOVE%":
		username_frnd = input(Fore.GREEN+"User name to be removed: \n"+Fore.RED+"$ "+Fore.BLUE)
		grp_name=input(Fore.GREEN+"From which group user to be removed: \n"+Fore.RED+"$ "+Fore.BLUE)
		Send(client_socket,username_frnd)
		Send(client_socket,grp_name)
		threading.Thread(target=write).start()
	elif message=="%GET OUT%":
		return 0
	else:
		print(Fore.WHITE+"Received unknown instruction "+message+" from server\n"+Fore.RED+"$ ")


def receive():
	z=0
	"""Pool messages from server (runs in separate thread)"""
	while True:
		try:
			message = client_socket.recv(1024).decode(ENCODING)
			if message.startswith('%'):
				if handle_server_instruction(str(message))==0:
					return
			else:
				if message=='-- Connected to server!':
					publicKey, privateKey = rsa.newkeys(1024)
				msg=message.split(":",1)
				if z==0:
					aa=1
					#print(Fore.WHITE+msg[0]+": "+decrypt(msg[1],privatekey))
				else:
					print(Fore.WHITE+message+Fore.RED+"\n$ ",end='')
				z+=1
		except OSError:
			print('An error occurred!')
			client_socket.close()
			break


def write():
	"""Hold open input for sending messages (runs in separate thread)"""
	while True:
		message=input(Fore.RED+"$ ")
		if message in commands:
			Send(client_socket,message)
			break   


if __name__ == '__main__':
	try:
		username = input(Fore.GREEN+"Username: "+Fore.WHITE)
		password = input(Fore.GREEN+"Password: "+Fore.WHITE)
		client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# client_sockets=[]
		# for i in range(5):
		# 	client_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		client_socket.connect(SERVER_ADDRESS)
		# client_sockets[0].connect(SERVER_ADDRESS)
		# client_sockets[0].connect(SERVER_ADDRESS1)
		# client_sockets[0].connect(SERVER_ADDRESS2)
		# client_sockets[0].connect(SERVER_ADDRESS3)
		# client_sockets[0].connect(SERVER_ADDRESS4)
	except ConnectionRefusedError:
		print(Fore.WHITE+'Could not connect to the server. Exiting...')
		exit(1)
	receive_thread = threading.Thread(target=receive)
	receive_thread.start()