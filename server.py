from email import message
from re import I
import threading
import socket
from database import *
import time
import sys
SERVER_ADDRESS = ('localhost', sys.argv[1])


class Participant:
	"""
	This class is used for storing data for each client like username and socket but not password
	
	:param username: user name of the client which is unique
	:type username: string
	:param client_socket: client socket to which server should communicate to the client
	:type client_socket: socket
	:param thread: receiving thread for requests sent by client
	:type thread: Thread
	:param publickey: RSA public key of client but saved as a string
	:type publickey: string
	"""
	def __init__(self, username: str,client_socket,thread,publickey):
		"""
		Constructor method
		"""
		self.username = username
		self.client_socket = client_socket
		self.thread=thread
		self.publickey=publickey


def send_to(participant, message: str,encd_type):
	"""
	This function is used to send messages to client when we have participant object along with encrypting using utf-8 or without any encryption (already sha256 or rsa encrypted)
	
	:param participant: particpant object to which message is to be sent
	:type participant: :class:`Participant`
	:param message: message to be sent to client
	:type message: string
	:param encd_type: type of encodin(utf-8)
	:type encd_type: string
	"""
	print("Sending message to "+participant.username)
	if encd_type=="None":
		participant.client_socket.send(message)
	else:
		participant.client_socket.send(message.encode())


def send(participant_name:str,message:str,encd_type=""):
	"""
	This function is used to send messages to client when we don't have object when we have only participant name, this function checks in the list of participants and finds the client socket and then sends a message.
	
	:param participant_name: name of the particpant to which message is to be sent
	:type participant_name: string
	:param message: message to be sent to client
	:type message: string
	:param encd_type: type of encodin(utf-8)
	:type encd_type: string
	"""
	for i in participants:
		if i.username==participant_name:
			send_to(i,message,encd_type)


def receive_from(participant, encod_type:str ="", size: int = 1024):
	"""
	This function is used to receive a message only once from a client when we have object and to decrypt using utf-8 or just receiving without decryption
	"""
	if encod_type=="None":
		return participant.client_socket.recv(size)
	else:
 		return participant.client_socket.recv(size).decode()


def receive_from2(participant_name,encod_type:str="",size:int=1024):
	"""
	This function is used to receive a message only once from a client when we have participant name and it calls another function receive_from by passing socket
	"""
	for i in participants:
		if i.username==participant_name:
			return receive_from(i,encod_type,size)

def handle_command(participant, command):

	print("Command by "+participant.username+": "+command)
	if command=="/Send":
		send(participant.username,'%DRT_MSG%')
		username2 = receive_from(participant)
		found=False
		for i in participants:
			if username2==i.username:
				send(participant.username,i.publickey)
				found=True
				break
		if not found:
			send(participant.username,"-1")
		else:
			message=receive_from(participant,"None")
			send(username2,message,"None")
	elif command == '/Exit':
		send(participant.username, '%QUIT%')
		exit_user(participant.username)
		participant.thread=None
		participant.client_socket.close()
	elif command=='/Creategrp':
		send(participant.username, '%CREATEGROUP%')
		grp_name=receive_from(participant)
		a=group(grp_name,participant.username,participant.publickey)
		if a==1:
			send(participant.username, 'Successfully created group '+grp_name)
		else:
			send(participant.username, grp_name+' already exists')
	elif command=='/Addmember':
		admin_name=participant.username
		send(participant.username,'%ADDMEMBER%')
		groupname=receive_from(participant)
		membername=receive_from(participant)
		a=add_member(groupname,membername,admin_name)
		send(participant.username,a)
	elif command=='/Sendgrp':
		send(participant.username,'%SENDGRP%')
		group_name=receive_from(participant)
		send_group(group_name,participant.username)
	elif command == '/kick':
		send(participant.username,"%REMOVE%")
		user=receive_from(participant)
		grp_name=receive_from(participant)
		send(participant.username,remove_member(grp_name,user,participant.username))
	else:
		send(participant.username, '-- Invalid command')


def handle(participant: Participant):
	while participant.thread!=None:
		command = receive_from(participant)
		if command.startswith('/'):
			handle_command(participant, command)

#completed
def send_group(group_name,participant_name: str):
	participants1=all_members(group_name,participant_name)
	string=""
	if len(participants1)==0:
		send(participant_name,"You are not there in "+group_name)
		return
	for j in range(len(participants1)):
		if participants1[j][0]==participant_name:
			participants1.pop(j)
			break
	for j in participants1:
		string+=j[1]+"@"
	send(participant_name,string)
	for i in range(len(participants1)):
		msg=receive_from2(participant_name,"None")
		send(participants1[i][0],msg,"None")
	send(participant_name,"Sent")
#completed

#completed
def add_member(group_name,participant_name: str,admin_name: str):
	p=None
	for i in participants:
		if i.username==participant_name:
			p=i
			break
	if p==None:
		return participant_name+" is not there at all"
	a=add_participants_to_grp(group_name,admin_name,p.username,p.publickey)
	if a==-1:
		return group_name+" doesn't exist"
	elif a==1:
		return participant_name+" is already there in "+group_name
	elif a==2:
		return "Successfully added "+participant_name+" to "+group_name
	else:
		return "You are not an admin in "+group_name
#completed


#completed
def remove_member(group_name,participant_name: str,admin_name:str):
	a=delete_participants_from_grp(group_name,admin_name,participant_name)
	if a==-1:
		return group_name+" doesn't exist"
	elif a==1:
		return "Successfully removed "+participant_name+" from "+group_name
	elif a==2:
		return participant_name+" is not there in "+group_name
	else:
		return "You are not an admin in "+group_name
#completed

def receive():
	"""
	Main loop, add new clients to the chat room
	"""
	while True:
		client_socket, address = server.accept()
		print("Connected with "+str(address))
		client_socket.send('%USER%'.encode())
		username = client_socket.recv(1024).decode()
		client_socket.send('%PASS%'.encode())
		password = client_socket.recv(1024).decode()
		###############
		a=sign_in_up(username,password)
		for i in range(4):
			if i==3:
				client_socket.send('%GET OUT%'.encode())
				break
			print("while loop",a)
			if a==1:
				print(username+" joined back")
				participant=None
				for i in participants:
					if i.username==username:
						i.client_socket=client_socket
						participant=i
						send(username, 'Thanks for coming back!')
						send(username,'%CONNECT%')
						participant.thread = threading.Thread(target=handle, args=(participant,))
						participant.thread.start()
						break
				break
			elif a==0:
				print("New participant: "+username)
				new_participant=Participant(username,client_socket,None,None)
				participants.append(new_participant)
				send(username, '-- Connected to server!')
				send(username,'%CONNECT%')
				pubkey=client_socket.recv(1024).decode()
				update_pubkey(username,pubkey)
				new_participant.publickey=pubkey
				new_participant.thread = threading.Thread(target=handle, args=(new_participant,))
				new_participant.thread.start()
				break
			elif a==-1:
				print('Connection attempt with existing username: '+username)
				client_socket.send('%TRYAGAIN%'.encode())
				password2 = client_socket.recv(1024).decode()
				print(password2)
				a=sign_in_up(username,password2)


if __name__ == '__main__':
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(SERVER_ADDRESS)
	server.listen()
	participants = []
	print('Server is listening... ')
	open_database()
	receive()