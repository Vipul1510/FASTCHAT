from pickle import FALSE, GLOBAL
from re import A
import socket
import threading
from pathlib import Path
from colorama import Fore
import hashlib
import rsa
import csv
import sys
import signal
import multiprocessing
import os
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import time
from datetime import datetime

KEYSIZE = 16
BLOCKSIZE = 16
MAIN_SERVER_ADDRESS = ('localhost', 7680)
SERVER_ADDRESS1 = ('localhost', 7681)
SERVER_ADDRESS2 = ('localhost', 7682)
SERVER_ADDRESS3 = ('localhost', 7683)
SERVER_ADDRESS4 = ('localhost', 7684)
SERVER_ADDRESS5 = ('localhost', 7685)
######################## AES ENCRYPTION ##########################
def getKey(keysize):
	"""This function generates random number which we can use as encryption key in AES

	:param keysize: It denotes the size of key required
	"""
	key = os.urandom(keysize)
	return key

def getIV(blocksize):
	"""This function generates random number which we can use as encryption iv in AES

	:param blocksize: It denotes the size of iv required
	"""
	iv = os.urandom(blocksize)
	return iv

def encrypt_image(filename, key, iv):
	"""This function converts image into encrypted data using key and iv

	:param filename: The name of the image file
	:param key: key for encryption
	:param iv: iv for encryption
	"""
	with open(filename, "rb") as file1:
		data = file1.read()
		cipher = AES.new(key, AES.MODE_CBC, iv)
		ciphertext = cipher.encrypt(pad(data, BLOCKSIZE))
		return ciphertext

def decrypt_image(data, key, iv,filename):
	"""This function converts encrypted data back into image

	:param data: The encrypted data of image
	:param key: The key with encryption is done
	:param iv: The iv with which encryption is done
	:param filename: The final filename of the image
	"""
	cipher2 = AES.new(key, AES.MODE_CBC, iv)
	decrypted_data = unpad(cipher2.decrypt(data), BLOCKSIZE)
	with open(filename, "wb") as file:
		file.write(decrypted_data)
####################################################################
def Receive( servernumber:int,decode_type="",size: int = 1024):
	"""This function receives the message from the server

	:param servernumber: The denotes server number which is going to send message
	:paramdecode_type: Type of decoding
	:param size: Denotes size of message
	"""
	if decode_type=="":
		while True:
			msg=client_sockets[servernumber].recv(size)
			try:
				msg=msg.decode()
				if "NOT FOUND"==msg:
					return msg
			except:
				msg=rsa.decrypt(msg, privatekey)
				msg= msg.decode('utf-8')
			if "%PUBKEY%" in msg:
				msg=msg.replace("%PUBKEY%","")
				return msg
			elif "%REPLY%" in msg:
				return msg
			else:
				print(Fore.WHITE+msg)

def Receive_img(servernumber:int,size: int = 1024):
	"""This function is used to receive image from server

	:param servernumber: It denotes server number which is going to send message 
	:param size: size of message
	"""
	no_recv=0
	list=[]
	while True:
		msg=""
		if no_recv==2:
			msg=client_sockets[servernumber].recv(size)
		else:
			msg=client_sockets[servernumber].recv(1024)
		try:
			msg=msg.decode()
			if "%SIZE%" in msg:
				msg=msg.replace("%SIZE%","")
				size=int(msg)
			else:
				print(Fore.WHITE+msg)
		except:
			if no_recv!=2:
				msg=rsa.decrypt(msg, privatekey)
				try:
					msg= msg.decode('utf-8')
					print(Fore.WHITE+msg)
				except:
					no_recv+=1
					list.append(msg)			# appending key and iv in list
			else:
				try:
					msg=rsa.decrypt(msg, privatekey)
					msg= msg.decode('utf-8')
					print(Fore.WHITE+msg)
				except:
					no_recv+=1
					if no_recv==3:
						decrypt_image(msg, list[0], list[1],"image.png")	# Decrypting image
						return "Received image with filename image.png"

def Send(message :str,servernumber:int,encod_type:str=""):
	"""This function sends message from client to server

	:param message: Message to be sent
	:param servernumber: It denotes server number to which message to be sent
	:param encod_type: Type of encoding
	"""
	if encod_type=="":
		return client_sockets[servernumber].send(message.encode())
	elif encod_type=="None":
		return client_sockets[servernumber].send(message)


def Send_msg(message :str,pubkey2 :str,servernumber:int):
	"""This function sends rsa encrypted messages to the server

	:param message: Message to be sent
	:param pubkey2: Public key of receiver
	:param servernumber: It denotes server number to which message to be sent
	"""
	publicKeyReloaded = rsa.PublicKey.load_pkcs1(pubkey2.encode())
	client_sockets[servernumber].send(rsa.encrypt(message.encode(),publicKeyReloaded))

# Commands used to carry out different form of chatting
commands=["/Send",'/Creategrp','/Addmember','/Sendgrp','/kick','/Leavegrp','/Changeadmin','/Sendimg',"/Deletegrp"]
commands2=['%CREATEGROUP%',"%SENDGRP%","%ADDMEMBER%",'%QUIT%',"%DRT_MSG%","%REMOVE%"]

def handle_server_instruction(message,r):
	"""It handles the commands given by user on terminal

	:param message: It denotes message which contain command
	:param r: It denotes the less load having server number 
	"""
	global username
	########################### CREATEGROUP #############################
	if message == '%CREATEGROUP%':
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		with open(f"{username}.csv", 'a') as file:
				writer = csv.writer(file)
				writer.writerow(["You : Tried to create group '" +groupname+"'"])
		Send(groupname,r)
		threading.Thread(target=write).start()
	########################### DELETEGROUP #############################
	elif message=="%DELGRP%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname,r)
		threading.Thread(target=write).start()
	########################### SENDGROUP #############################
	elif message=="%SENDGRP%":
		groupname=input(Fore.GREEN+"GROUP NAME:\n"+Fore.RED+"$ "+Fore.BLUE)
		Message=input(Fore.GREEN+"MESSAGE:\n"+Fore.RED+"$ "+Fore.BLUE)
		with open(f"{username}.csv", 'a') as file:
				writer = csv.writer(file)
				writer.writerow([ "You {"+groupname+"}: "+Message])
		Send(groupname,r)
		mem=Receive(r)
		n=mem.count("@")
		if "%REPLY%" in mem:
			mem=mem.replace("%REPLY%","")
			print(Fore.WHITE+mem)
		elif n==0:
			print(Fore.WHITE+mem)
		else:
			l=mem.split("@")
			for i in range(n):
				Send_msg("{"+groupname+"} "+"["+username+"] "+"("+str(datetime.fromtimestamp(int(time.time())))+") "+Message,l[i],r)
		threading.Thread(target=write).start()
	########################### SENDIMG #############################
	elif message=="%SENDIMG%":
		path=os.getcwd()
		username2 = input(Fore.GREEN+"USER NAME: \n"+Fore.RED+"$ "+Fore.BLUE)
		client_sockets[r].send(username2.encode())
		pubkey2=Receive(r)
		if pubkey2=="NOT FOUND":
			print(username2+" is not there at all")
		else:
			file_name=input(Fore.GREEN+"FILE NAME:\n"+Fore.RED+"$ "+Fore.BLUE)
			totalpath=path+"/"+file_name
			exists=Path(totalpath).exists()
			if not exists:
				print(Fore.WHITE+"File not found")
				Send("Sorry",r)
			else:
				Send("Sending Image"+"$"+str(3*os.path.getsize(totalpath)),r)
				key= getKey(KEYSIZE)
				iv = getIV(BLOCKSIZE)
				data=encrypt_image(file_name, key, iv)
				Send(rsa.encrypt(key,rsa.PublicKey.load_pkcs1(pubkey2.encode())),r,"None")
				time.sleep(0.1)
				Send(rsa.encrypt(iv,rsa.PublicKey.load_pkcs1(pubkey2.encode())),r,"None")
				time.sleep(0.1)
				Send(data,r,"None")
				print(Fore.WHITE+"Sent image")
		threading.Thread(target=write).start()
	########################### ADDMEMBER #############################
	elif message=="%ADDMEMBER%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		member=input(Fore.GREEN+'USER NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		with open(f"{username}.csv", 'a') as file:
				writer = csv.writer(file)
				writer.writerow(["You : Tried to add '"+member+"' to group '" +groupname+"'"])
		Send(groupname,r)
		Send(member,r)
		threading.Thread(target=write).start()
	########################### LEAVEGROUP #############################
	elif message=="%LEAVEGRP%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname,r)
		threading.Thread(target=write).start()
	########################### CHANGE ADMIN #############################
	elif message=="%CHANGE_ADM%":
		groupname=input(Fore.GREEN+'GROUP NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		username1=input(Fore.GREEN+'USER NAME:\n'+Fore.RED+"$ "+Fore.BLUE)
		Send(groupname,r)
		Send(username1,r)
		threading.Thread(target=write).start()
	############################# QUIT ###############################
	elif message == '%QUIT%':
		client_sockets[r].close()
		client_sockets[0].close()
		sys.exit(0)
	########################### DRT MSG #############################
	elif message =="%DRT_MSG%":
		username2 = input(Fore.GREEN+"USER NAME: \n"+Fore.RED+"$ "+Fore.BLUE)
		message = input(Fore.GREEN+"MESSAGE: \n"+Fore.RED+"$ "+Fore.BLUE)
		Send(username2,r)
		a=Receive(r)
		if "%REPLY%" in a:
			a=a.replace("%REPLY%","")
			if a=="-1":
				with open(f"{username}.csv", 'a') as file:
					writer = csv.writer(file)
					writer.writerow([username2+" is not there"])
				print(Fore.WHITE+username2+" is not there")
		elif a!="-1":
			with open(f"{username}.csv", 'a') as file:
				writer = csv.writer(file)
				writer.writerow(["You ["+username2+"]: "+message])
			Send_msg("["+username+"] "+"("+str(datetime.fromtimestamp(int(time.time())))+") "+message,a,r)
		threading.Thread(target=write).start()
	########################### REMOVE #############################
	elif message=="%REMOVE%":
		username_frnd = input(Fore.GREEN+"USER NAME: \n"+Fore.RED+"$ "+Fore.BLUE)
		grp_name=input(Fore.GREEN+"GROUP NAME: \n"+Fore.RED+"$ "+Fore.BLUE)
		with open(f"{username}.csv", 'a') as file:
				writer = csv.writer(file)
				writer.writerow(["You : Tried to remove '"+username_frnd+"' from group '"+grp_name+"'"])
		Send(username_frnd,r)
		Send(grp_name,r)
		threading.Thread(target=write).start()
	else:
		print(Fore.WHITE+"Received unknown instruction "+message+" from server\n"+Fore.RED+"$ ")

def receive2(r):
	"""Fuction which receives from server (used as a helper function)
	"""
	msg=10
	while True:
		message=client_sockets[r].recv(1024).decode()
		if message[0]=="@":
			msglist=message[1:]
			msg=int(msglist)
			break
	return msg

def receive3(r):
	"""Function which receives from server and decypt it
	"""
	a=True
	while a:
		message=client_sockets[r].recv(1024)
		try:
			message=rsa.decrypt(message, privatekey).decode()
			print(message)
			a=False
		except:
			print(message.decode())

def receive(r):
	"""Pool messages from server (runs in separate thread)
	
	:param r: It denotes the server number which is going to send message to client
	"""
	while True:
		try:
			message=client_sockets[r].recv(1024)
			try:
				dec_message = message.decode('utf-8')
			except:
				message=rsa.decrypt(message, privatekey)
				dec_message= message.decode('utf-8')
			if dec_message.startswith('%'):
				if dec_message=="%RECVIMG%":
					s=Receive_img(r)
					print(Fore.WHITE+s+Fore.RED+"\n$ ",end='')
				else:
					handle_server_instruction(str(dec_message),r)
			else:
				with open(filename, 'a') as file:
						writer = csv.writer(file)
						writer.writerow([message.decode()])
				print(Fore.WHITE+message.decode()+Fore.RED+"\n$ ",end='')
		except OSError:
			print('An error occurred!')
			client_sockets[0].close()
			break

def smalltime():
	"""Helper function to get the server number which has least load
	"""
	client_sockets[0].send("/OPTSERVER".encode())
	a=client_sockets[0].recv(1024).decode()
	return int(a)

def write():
	"""Hold open input for sending messages (runs in separate thread)
	"""
	while True:
		message=input(Fore.RED+"$ ")
		if message in commands:
			a=smalltime()
			Send(message,a)
			return
		elif message=="/Help":
			print("/Send : Send message to another user")
			print("/Creategrp : Create a group")
			print("/Addmember : Add a user in a group")
			print("/Sendgrp : Send message on a group")
			print("/kick : Remove participant from a group")
			print("/Leavegrp : Leave a group")
			print("/Changeadmin : Change the admin of a group")
			print("/Sendimg : Send an image to another user")
			print("/Deletegrp : Delete a group")
			print("/Help : to see all the commands")
			print("/Exit : to exit from this terminal")
		elif message=="/Exit":
			client_sockets[0].send(("/Exit"+username).encode())
			for i in range(5):
				Send(message,i+1)
			break


def handler(signum, frame):
	"""This function exits the user when ctrl+C is pressed on terminal
	"""
	client_sockets[0].send(("/Exit"+username).encode())
	for i in range(5):
		Send("/Exit",i+1)
	sys.exit(0)


if __name__ == '__main__':
	try:
		username = input(Fore.GREEN+"Username: "+Fore.WHITE)
		password = input(Fore.GREEN+"Password: "+Fore.WHITE)
		publickey=1
		privatekey=1
		global client_sockets
		client_sockets=[]
		for i in range(6):
			client_sockets.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
		client_sockets[0].connect(MAIN_SERVER_ADDRESS)	# Connecting client with main server

		for k in range(3): # 3 chances to give correct password
			client_sockets[0].send(("/USER$"+username+"$"+hashlib.sha256(password.encode()).hexdigest()).encode())
			reply=client_sockets[0].recv(1024).decode()	# Encrypting password and sending to server and getting reply
			if reply=="TRY AGAIN":
				if k==2:
					print(Fore.RED+"Sorry, So many attempts failed!")
				else:
					password=input(Fore.RED+'Try again:(\n'+Fore.GREEN+"Password: "+Fore.WHITE)
			else:
				print(reply)
				## SIGN IN CASE
				if "Thanks for coming back!"in reply:
					print(Fore.GREEN+"##########################################################")
					print("################# WELCOME TO FAST CHAT ###################")
					print("##########################################################"+Fore.RED)
					print("/Send : Send message to another user")
					print("/Creategrp : Create a group")
					print("/Addmember : Add a user in a group")
					print("/Sendgrp : Send message on a group")
					print("/kick : Remove participant from a group")
					print("/Leavegrp : Leave a group")
					print("/Changeadmin : Change the admin of a group")
					print("/Sendimg : Send an image to another user")
					print("/Deletegrp : Delete a group")
					print("/Help : to see all the commands")
					print("/Exit : to exit from this terminal"+Fore.WHITE)
					if reply[len(reply)-1]=="1":
						print("Already session is active")
						client_sockets[0].send(("/EXIT").encode())
						break
					filename=f"{username}.csv"		
					totalpath="./"+filename
					exists=Path(totalpath).exists()
					if not exists:		# Checking if csv file exists with username.csv or not
						print("You cannot join again from other device")
						client_sockets[0].send(("/Exit"+username).encode())
						break
					with open(filename, 'r') as file:
						csvreader = csv.reader(file)
						i=0
						j=False
						for row in csvreader:	# Reading undelivered messages and printing hostory
							if i==0:
								x=row[0]
								publickey=rsa.PublicKey.load_pkcs1(x.encode())
							elif i==1:
								y=row[0]
								privatekey = rsa.PrivateKey.load_pkcs1(y.encode())
							elif i>=2:
								if i==2:
									print("Old Messages :")
									if row[0]!="Unread messages:":
										j=True
										print(row[0])
								else:
									if row[0]!="Unread messages:":
										j=True
										print(row[0])
							i+=1
						if j:
							print("Finished Old messages")
					####################### CONNECTING TO 5 SERVERS #########################
					client_sockets[1].connect(SERVER_ADDRESS1)
					client_sockets[2].connect(SERVER_ADDRESS2)
					client_sockets[3].connect(SERVER_ADDRESS3)
					client_sockets[4].connect(SERVER_ADDRESS4)
					client_sockets[5].connect(SERVER_ADDRESS5)
					for i in range(5):
						receive_thread = threading.Thread(target=receive,args=(i+1,)).start()
					for j in range(5):
						client_sockets[j+1].send(("/OLDUSER$"+username).encode())
					########################### Undelivered msgs ###########################
					client_sockets[0].send("/OPTSERVER".encode())
					serverno=int(float(client_sockets[0].recv(1024).decode()))
					client_sockets[serverno].send("/OLDMSG".encode())#########################################################################
				## SIGN UP CASE
				elif reply=="-- Connected to server!":
					print(Fore.GREEN+"##########################################################")
					print("################# WELCOME TO FAST CHAT ###################")
					print("##########################################################"+Fore.RED)
					print("/Send : Send message to another user")
					print("/Creategrp : Create a group")
					print("/Addmember : Add a user in a group")
					print("/Sendgrp : Send message on a group")
					print("/kick : Remove participant from a group")
					print("/Leavegrp : Leave a group")
					print("/Changeadmin : Change the admin of a group")
					print("/Sendimg : Send an image to another user")
					print("/Deletegrp : Delete a group")
					print("/Help : to see all the commands")
					print("/Exit : to exit from this terminal"+Fore.WHITE)
					client_sockets[1].connect(SERVER_ADDRESS1)
					client_sockets[2].connect(SERVER_ADDRESS2)
					client_sockets[3].connect(SERVER_ADDRESS3)
					client_sockets[4].connect(SERVER_ADDRESS4)
					client_sockets[5].connect(SERVER_ADDRESS5)
					for i in range(5):
						receive_thread = threading.Thread(target=receive,args=(i+1,)).start()
					publickey, privatekey = rsa.newkeys(1024)
					publicKeyPkcs1PEM = publickey.save_pkcs1().decode()
					privateKeyPkcs1PEM = privatekey.save_pkcs1().decode()
					filename=f"{username}.csv"
					with open(filename, 'w', newline='') as file:	# Creatinf new file and writing public and private key in it
						writer = csv.writer(file)
						writer.writerow([publicKeyPkcs1PEM])
						writer.writerow([privateKeyPkcs1PEM])
					file.close()
					for i in range(5):
						client_sockets[i+1].send(("/NEWUSER$"+username+"$"+publicKeyPkcs1PEM).encode())
				threading.Thread(target=write).start()
				break
	
	except ConnectionRefusedError:
		print(Fore.WHITE+'Could not connect to the server. Exiting...')
		exit(1)
	signal.signal(signal.SIGINT, handler)	# exiting if client uses ctrl+C
