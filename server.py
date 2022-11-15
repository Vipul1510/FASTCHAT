from email import message
from re import I
import threading
import socket
from database import *
import rsa
import cryptocode

ENCODING = 'utf-8'
SERVER_ADDRESS = ('127.0.0.1', 15665)


class Participant:
	def __init__(self, username: str,password: str,client_socket: socket):
		self.username = username
		self.password=password
		self.client_socket = client_socket
		


class group:
	def __init__(self,admin,group_name):
		self.members=[]
		self.admins=[admin]
		self.group_name=group_name


def send_to(participant_socket, message: str,username: str):
	print("Sending message to "+username+" : "+message)
	if message==None:
		print("Message to be sent is None")
	else:
		participant_socket.send(message.encode(ENCODING))


def send(participant_name:str,message:str):
	for i in participants:
		if i.username==participant_name:
			send_to(i,message)


def receive_from(participant: Participant, encod_type:str =ENCODING, size: int = 1024):
	if encod_type=="":
		return participant.client_socket.recv(size).decode()
	else:
 		return participant.client_socket.recv(size).decode(encod_type)


def handle_command(participant, command):
	print("Command by "+participant.username+": "+command)
	if command=="/Send":
		send_to(participant,'%DRT_MSG%')
		username = receive_from(participant)
		message=receive_from(participant)
		send(username,participant.username+": "+message)
	elif command == '/Exit':
		send_to(participant, '%QUIT%')
		participant.client_socket.close()
	# admin commands
	elif command=='/Creategrp':
		send_to(participant, '%CREATEGROUP%')
		k=receive_from(participant)
		if k in list(map(lambda p: p.group_name, groups)):
			send_to(participant, k+' already exists')
		else:
			g=group(participant.username,k)
			groups.append(g)
			send_to(participant, 'Successfully created group '+k)
	elif command=='/Addmember':
		admin_name=participant.username
		send_to(participant,'%ADDMEMBER%')
		groupname=receive_from(participant)
		membername=receive_from(participant)
		a=add_member(groupname,membername,admin_name)
		send_to(participant,a)
	elif command=='/Sendgrp':
		send_to(participant,'%SENDGRP%')
		group_name=receive_from(participant)
		message=receive_from(participant)
		a=send_group(group_name,message,participant.username)
		send_to(participant,a)
	elif command == '/kick':
		send_to(participant,"%REMOVE%")
		user=receive_from(participant)
		grp_name=receive_from(participant)
		send_to(participant,remove_member(grp_name,user,participant.username))
	else:
		send_to(participant, '-- Invalid command')


def handle(participant: Participant):
	while True:
		command = receive_from(participant)
		if command.startswith('/'):
			handle_command(participant, command)


def send_group(group_name,message:str,participant_name: str):
	Group=None
	for i in groups:
		if group_name==i.group_name:
			Group=i
			break
	if Group==None:
		return "You are not there in "+group_name
	participant=None
	for i in Group.members+Group.admins:
		if i==participant_name:
			participant=i
	if participant==None:
		return "You are not there in "+group_name
	for i in participants:
		found=False
		if i.username in Group.members+Group.admins and i.username!=participant_name:
			found=True
		if found:
			send_to(i,"["+group_name+"] "+participant_name+": "+message)
	return "Sent"


def add_member(group_name,participant_name: str,admin_name: str):
	Admin=None
	participant=None
	for i in participants:
		if i.username==participant_name:
			participant=i
		if i.username==admin_name:
			Admin=i
	if participant==None:
		return "Participant doesn't exist at all"
	if Admin==None:
		return "You are not there at all"
	Group=None
	for i in groups:
		if group_name==i.group_name:
			Group=i
			break
	if Group==None:
		return group_name+" doesn't exist"
	admin_found=False
	for i in Group.admins:
		if i==Admin.username:
			admin_found=True
			break
	if not admin_found:
		return "You are not an admin in "+group_name
	for i in Group.members:
		if(i==participant.username):
			return participant_name+" is already there in "+group_name
	for i in Group.admins:
		if(i==participant.username):
			return participant_name+" is already there in "+group_name
	Group.members.append(participant_name)
	return "Successfully added "+participant_name+" to "+group_name


def remove_member(group_name,participant_name: str,admin_name:str):
	Group=None
	for i in groups:
		if i.group_name==group_name:
			Group=i
			break
	if Group==None:
		return group_name+" doesn't exist"
	if admin_name not in Group.admins:
		return "You are not an admin in "+group_name
	if participant_name not in Group.members:
		return "This participant is not there in "+group_name
	Group.members.remove(participant_name)
	return "Successfully removed "+participant_name+" from "+group_name


def receive():
	"""
	Main loop, add new clients to the chat room
	"""
	while True:
		client_socket, address = server.accept()
		print("Connected with "+str(address))
		client_socket.send('%USER%'.encode(ENCODING))
		username = client_socket.recv(1024).decode(ENCODING)
		client_socket.send('%PASS%'.encode(ENCODING))
		password = client_socket.recv(1024).decode(ENCODING)
		###############
		a=sign_in_up(username,password)
		while True:
			if a==1:
				print(username+" joined back")
				send_to(client_socket,'%CONNECT%',username)
				thread = threading.Thread(target=handle, args=(participant,))
				thread.start()
				break
			elif a==0:
				print("New participant: "+username)
				send_to(client_socket, '-- Connected to server!',username)
				send_to(client_socket,'%CONNECT%')
				thread = threading.Thread(target=handle, args=(new_participant,))
				thread.start()
				break
			elif a==-1:
				print('Connection attempt with existing username: '+username)
				client_socket.send('%TRYAGAIN%'.encode(ENCODING))
				password2 = client_socket.recv(1024).decode(ENCODING)
				a=sign_in_up(username,password2)


if __name__ == '__main__':
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind(SERVER_ADDRESS)
	server.listen()
	participants = []
	groups=[]
	print('Server is listening... ')
	open_database()
	receive()