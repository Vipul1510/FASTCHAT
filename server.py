from email import message
from re import I
import threading
import socket
from database import *
import time
import sys

SERVER_ADDRESS = ('localhost', int(sys.argv[1]))
def timestamp():
	"""Used in function main()
	"""
	return str(int(sys.argv[1])-7680)+"$"+str(time.time()) # returns command embedded with time in string format

class Participant:
	"""This class is used for storing data for each client like username and socket but not password
	
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
		"""Constructor method
		"""
		self.username = username
		self.client_socket = client_socket
		self.thread=thread
		self.publickey=publickey


def send_to(participant, message: str,encd_type):
	"""This function is used to send messages to client when we have participant object along with encrypting using utf-8 or without any encryption (already sha256 or rsa encrypted)
	
	:param participant: particpant object to which message is to be sent
	:type participant: :class:`Participant`
	:param message: message to be sent to client
	:type message: string
	:param encd_type: type of encodin(utf-8)
	:type encd_type: string
	"""
	print("Sending message to "+participant.username)
	s=is_online(participant.username)		# Calls function from database to check whether user is online or not
	if not s:								# If user is not online storing messages in database
		msg_store(participant.username,message,0)	
	else:									# If user is online sending message to that user
		if encd_type=="None":
			participant.client_socket.send(message)
		else:
			participant.client_socket.send(message.encode())


def send(participant_name:str,message:str,encd_type=""):
	"""This function is used to send messages to client when we don't have object when we have only participant name, this function checks in the list of participants and finds the client socket and then sends a message.
	
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
			break

def receive_from(participant, encod_type:str ="", size: int = 1024):
	"""This function is used to receive a message only once from a client when we have object and to decrypt using utf-8 or just receiving without decryption
	"""
	if encod_type=="None":
		return participant.client_socket.recv(size)
	else:
 		return participant.client_socket.recv(size).decode()


def receive_from2(participant_name,encod_type:str="",size:int=1024):
	"""This function is used to receive a message only once from a client when we have participant name and it calls another function receive_from by passing socket
	"""
	for i in participants:
		if i.username==participant_name:
			return receive_from(i,encod_type,size)

def handle_command(participant, command):
	"""This function handles all the commands from the user

	:param participant: particpant object to which message is to be sent
	:type participant: :class:`Participant`
	:param command: unique strings for different work
	:type command: string
	"""
	print("Command by "+participant.username+": "+command)
	######################## /Send ###############################
	if command=="/Send":
		send(participant.username,'%DRT_MSG%')		# Sending initial command to server
		username2 = receive_from(participant)
		found=False
		for i in participants:
			if username2==i.username:
				send(participant.username,"%PUBKEY%"+i.publickey)
				found=True
				break
		if not found:
			send(participant.username,"%REPLY%-1")
		else:
			message=receive_from(participant,"None")
			send(username2,message,"None")
	########################## /Exit ###############################
	elif command == '/Exit':
		send(participant.username, '%QUIT%')		# Sending initial command to server
		participant.thread=None
	######################## /Creategrp ############################
	elif command=='/Creategrp':
		send(participant.username, '%CREATEGROUP%')		# Sending initial command to server
		groupname=receive_from(participant)
		a=group(groupname,participant.username,participant.publickey)
		if a==1:
			send(participant.username, 'Successfully created group '+groupname)
		else:
			send(participant.username, groupname+' already exists')
	######################## /Addmember #############################
	elif command=='/Addmember':
		admin_name=participant.username
		send(participant.username,'%ADDMEMBER%')		# Sending initial command to server
		groupname=receive_from(participant)
		membername=receive_from(participant)
		a=add_member(groupname,membername,admin_name)	# calls function from database
		send(participant.username,a)
		send(membername,"{"+groupname+"} ["+participant.username+"] You are added to this group")
	######################### /Sendgrp ##############################
	elif command=='/Sendgrp':
		send(participant.username,'%SENDGRP%')		# Sending initial command to server
		groupname=receive_from(participant)
		send_group(groupname,participant.username)
	########################## /Sendimg ##############################
	elif command=='/Sendimg':
		send(participant.username,"%SENDIMG%")		# Sending initial command to server
		username1=receive_from(participant)
		found=False
		for i in participants:
			if i.username==username1:
				send(participant.username,"%PUBKEY%"+i.publickey)
				found=True
				break
		if not found:
			send(participant.username,"NOT FOUND")
		else:
			reply=receive_from(participant)
			print(reply)
			if "Sorry" not in reply:
				size=int(float(reply.replace("Sending Image$","")))
				key=receive_from(participant,"None")
				print("received key")
				iv=receive_from(participant,"None")
				print("received iv")
				data=receive_from(participant,"None",size+1000)
				print("received data")
				send(username1,"%RECVIMG%")
				send(username1,"%SIZE%"+str(size))
				send(username1,key,"None")		# Sending key to server
				send(username1,iv,"None")		# Sending iv to server
				send(username1,data,"None")		# Sending encrypted image data to server
	########################### /kick ###############################
	elif command == '/kick':
		send(participant.username,"%REMOVE%")		# Sending initial command to server
		user=receive_from(participant)
		groupname=receive_from(participant)
		send(participant.username,remove_member(groupname,user,participant.username))
	######################### /Leavegrp ##############################
	elif command == '/Leavegrp':
		send(participant.username,"%LEAVEGRP%")		# Sending initial command to server
		groupname=receive_from(participant)
		b=leave_grp(groupname,participant.username)
		if b==-1:
			send(participant.username,("You are not there in group "+groupname))
		elif b==2:
			send(participant.username,"Please make other participant as admin and then leave")
		elif b==1:
			send(participant.username,("Successfully left the group "+groupname))
	######################### /OLDMSGS ##############################
	elif command=="/OLDMSGS":
		print("called no_pld_msgs")
		send(participant.username,"@"+str(no_old_msgs(participant.username)))
	########################## /OLDMSG ##############################
	elif command=="/OLDMSG":
		print("deleting old messages")
		result=msg_delete(participant.username)		# Calls function from database
		if result!=[]:								# If there are unread messages printing them
			send(participant.username,"Unread messages:")
			for i in result:
				send(participant.username,i[1],"None")
			send(participant.username,"")
	######################## /Deletegrp #############################
	elif command=="/Deletegrp":
		send(participant.username,"%DELGRP%")		# Sending initial command to server
		groupname=receive_from(participant)
		reply=delete_group(groupname,participant.username)
		if reply==-1:
			send(participant.username,"You are not there in group "+groupname)
		elif reply==1:
			send(participant.username,"Deleted group "+groupname+" successfully")
		else:
			send(participant.username,"You are not an admin in group "+groupname+", admin for this group is "+reply)
	####################### /Changeadmin ############################
	elif command == '/Changeadmin':
		send(participant.username,"%CHANGE_ADM%")		# Sending initial command to server
		groupname=receive_from(participant)
		user2=receive_from(participant)
		c=change_admin(groupname,participant.username,user2)
		if c==-1:
			send(participant.username,("You are not there in group "+groupname))
		elif c==-2:
			send(participant.username,(user2+" is not there in group "+groupname))
		elif c==1:
			send(participant.username,(user2+" is the admin for group "+groupname))
			send(user2,"{"+groupname+"} ["+participant.username+"] You are the admin for the group "+groupname)
		elif c==-3:
			send(participant.username,("You are not admin in group "+groupname))
	else:
		send(participant.username, '-- Invalid command')
	################################################################

def handle(participant: Participant):
	"""This function sends command to participant is participant is available 

	:param participant: particpant object to which message is to be sent
	:type participant: :class:`Participant`
	"""
	while participant.thread!=None:
		command = receive_from(participant)
		if command.startswith('/'):
			handle_command(participant, command)


def send_group(groupname,participant_name: str):
	"""This function sends messages in the group

	:param groupname: It denotes groupname in which message to be sent
	:type groupname: string
	:param participant_name: User name of the user who send message ih the group
	:type participant_name: string
	"""
	participants1=all_members(groupname,participant_name)		# Calls function from database
	string="%PUBKEY%"		
	if len(participants1)==0:
		send(participant_name,"%REPLY%You are not there in "+groupname)
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


def add_member(groupname,participant_name: str,admin_name: str):
	"""This function add participants in the group if admin gives the command

	:param groupname: Name of the group in which admin wants to add memeber
	:type groupname: string
	:param participant_name: username of the participant to be added in the group
	:type participant_name: string
	:param admin_name: Username of the admin
	:type admin_name: string
	"""
	p=None
	for i in participants:
		if i.username==participant_name:
			p=i
			break
	if p==None:
		return participant_name+" is not there at all"
	a=add_participants_to_grp(groupname,admin_name,p.username,p.publickey)		# Calls function from database
	if a==-1:
		return groupname+" doesn't exist"
	elif a==1:
		return participant_name+" is already there in "+groupname
	elif a==2:
		return "Successfully added "+participant_name+" to "+groupname
	else:
		return "You are not an admin in "+groupname


def remove_member(groupname,participant_name: str,admin_name:str):
	"""This function removes the given participant from the group

	:param groupname: Name of the group 
	:type groupname: string
	:param participant_name: username of the participant to be removed from the group
	:type participant_name: string
	:param admin_name: Username of the admin
	:type admin_name: string
	"""
	a=delete_participants_from_grp(groupname,admin_name,participant_name)	# Calls function from database
	if a==-1:
		return groupname+" doesn't exist"
	elif a==1:
		return "Successfully removed "+participant_name+" from "+groupname
	elif a==2:
		return participant_name+" is not there in "+groupname
	else:
		return "You are not an admin in "+groupname


def receive():
	"""Main loop. Add new clients, old clients in the chat room
	"""
	while True:
		client_socket, address = server.accept()
		print("Connected with "+str(address))
		msg=client_socket.recv(1024).decode()
		####################### /OLDUSER ############################
		if "/OLDUSER" in msg:
			list=msg.split("$")
			username=list[1]
			for i in participants:
				if i.username==username:
					i.client_socket=client_socket
					i.thread=1
					threading.Thread(target=handle, args=(i,)).start()
		####################### /NEWUSER ############################
		elif "/NEWUSER" in msg:
			list=msg.split("$")
			username=list[1]
			public_key=list[2]
			new=Participant(username,client_socket,1,public_key)
			participants.append(new)
			update_pubkey(username,public_key)
			threading.Thread(target=handle, args=(new,)).start()
		##############################################################


def main():
	"""This function is exclusively used for load balancing. Mainserver pings the server via this function
	"""
	while True:
		a=mainserver.recv(1024).decode()
		print(a)
		if a=='%FAST%':
			mainserver.send(timestamp().encode())
			

if __name__ == '__main__':
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mainserver=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	mainserver.connect(('localhost', 7680))		# Connecting to main server
	threading.Thread(target=main).start()		# Starting thread of main()
	server.bind(SERVER_ADDRESS)
	server.listen()
	participants = []
	print('Server is listening... ')
	threading.Thread(target=receive).start()	# Starting thread to receive
