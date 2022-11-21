from email import message
from re import I
import threading
import socket
from database import *
import rsa
import cryptocode

ENCODING = 'utf-8'
SERVER_ADDRESS = ('localhost', 7889)


class Participant:
	def __init__(self, username: str,client_socket: socket,thread):
		self.username = username
		self.client_socket = client_socket
		self.thread=thread
		#self.publickey=publickey


def send_to(participant_socket, message: str,username: str):
	print("Sending message to "+username+" : "+message)
	if message==None:
		print("Message to be sent is None")
	else:
		participant_socket.send(message.encode(ENCODING))


def send(participant_name:str,message:str):
	for i in participants:
		if i.username==participant_name:
			send_to(i.client_socket,message,i.username)


def receive_from(participant, encod_type:str =ENCODING, size: int = 1024):
	if encod_type=="":
		return participant.client_socket.recv(size).decode()
	else:
 		return participant.client_socket.recv(size).decode(encod_type)


def handle_command(participant, command):
	print("Command by "+participant.username+": "+command)
	if command=="/Send":
		send(participant.username,'%DRT_MSG%')
		username = receive_from(participant)
		message=receive_from(participant)
		send(username,participant.username+": "+message)
	elif command == '/Exit':
		send(participant.username, '%QUIT%')
		exit_user(participant.username)
		participant.thread=None
		participant.client_socket.close()

	# Admin commands
	elif command=='/Creategrp':
		send(participant.username, '%CREATEGROUP%')
		grp_name=receive_from(participant)
		a=group(grp_name,participant.username,)
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
		message=receive_from(participant)
		a=send_group(group_name,message,participant.username)
		send(participant.username,a)
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
def send_group(group_name,message:str,participant_name: str):
	participants=all_members(group_name)
	if len(participants)==0:
		return "You are not there in "+group_name
	for i in participants:
		if i!=participant_name:
			send_to(i.username,"["+group_name+"] "+participant_name+": "+message)
	return "Sent message in "+group_name
#completed

#completed
def add_member(group_name,participant_name: str,admin_name: str):
	a=add_participants_to_grp(group_name,admin_name,participant_name)
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
		client_socket.send('%USER%'.encode(ENCODING))
		username = client_socket.recv(1024).decode(ENCODING)
		client_socket.send('%PASS%'.encode(ENCODING))
		password = client_socket.recv(1024).decode(ENCODING)
		###############
		a=sign_in_up(username,password)
		for i in range(4):
			if i==3:
				client_socket.send('%GET OUT%'.encode(ENCODING))
				break
			print("while loop",a)
			if a==1:
				print(username+" joined back")
				participant=None
				for i in participants:
					if i.username==username:
						i.client_socket=client_socket
						participant=i
						break
				send(username, 'Thanks for coming back!')
				send(username,'%CONNECT%')
				participant.thread = threading.Thread(target=handle, args=(participant,))
				participant.thread.start()
				break
			elif a==0:
				print("New participant: "+username)
				new_participant=Participant(username,client_socket,None)
				participants.append(new_participant)
				send(username, '-- Connected to server!')
				send(username,'%CONNECT%')
				new_participant.thread = threading.Thread(target=handle, args=(new_participant,))
				new_participant.thread.start()
				break
			elif a==-1:
				print('Connection attempt with existing username: '+username)
				client_socket.send('%TRYAGAIN%'.encode(ENCODING))
				password2 = client_socket.recv(1024).decode(ENCODING)
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