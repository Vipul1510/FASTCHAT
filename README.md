# FASTCHAT
## Implemented part:
1. Authentication in Sign In and Sign Up
	- Using a table in database to store username, password(encrypted using SH256), Public key and online status.
	- When user joins first time(i.e sign up) it's username, password and public key is added in the table
	- When user joins again (i.e sign in) then user's encrypted password is checked with stored password in the table if that matches then user joins back
	- 3 chances are given to try if passsword entered is wrong
	- When user leaves it's status is made offline in the table and when he/she joins back then status is made online again
2. Maintaining database
	- There are 3 tables in the database
	  - i)   clients
	  - ii)  grp_modified
	  - iii) msg_store
	- Table clients is used to store name, password , public key and online status as discussed above
	- Table grp_modified stores the groupname, admin name, participants in the group
	- Table msg_store stores undelivered messages for a fixed period of time 120 seconds(2 minutes) and delete messages from table when user comes online or when 120 seconds are passed
3. Direct message between 2 clients
	- When client-1 sends messsage to client-2 it follows following path:
	  	original message -> client-1 -> encryption with public key of client-2 -> server -> client-2 -> decryption with private key of client-2 -> original message
	- Images will also use same path 
4. Formation of group and group chatting
	- Group formation/creation is done by user who becomes admin of the group.
	- Groups are store in database in table grp_modified.
	- When a user wants to send message in group it follows following path
	  This path is followed for each member in the group except sender.
		original message -> client-1 -> encryption with public key of respective receiver in group -> server -> receiver -> decryption with private key of receiver -> original message
5. Provision of storing undelivered messages
	- When any user goes online and some other user sends message to user then these meassages are stored in table msg_store
	- When user comes online his/her name will be checked in table by server and undelivered messages will be delivered to user and deleted from the table
	- A message can stay in table maximum for 2 minutes if user not comes back in this time then that message of his/her is deleted permanently
6. E2E Encryption
	- This is done using RSA
	- When user join first time a public and private key is generated and saved in a username.csv file in the device and public key on server.
	- When user joins back then existing private and public keys are used from the file.
	- Whenever user-1 wants to send a message to user-2 then first user-1 asks public key of user-2 to server , then with that public key user-1 encrypts the message and sends to server then server sends that encrypted message to user-2 then user-2 decrpty the message using it's own private key . In this way E2E encryption is mentioned. 
7. Multiple servers and load Balancing
	- Added a mainserver and 5 normal servers of same kind.
	- When client want to send a message it follows following steps:
		- client interacts with mainserver to know which server has lower load
		- mainserver sends the server number which has less load (If load is same then arbitary between them)
		- client assigns it's work to that server
	- Procedure to check which server has less load:
		- Mainserver sends  a message (ping) to all 5 servers and get their replies
		- The server with fastest reply has the less load
8. Image sharing
	- Implemented image sharing in the direct chats
	- When user1 wants to send image then user1 has to give relative path to the image with respect to client.py
	- Image is encrypted using AES key and iv
	- User1 now sends Key (encrypted with rsa public key of user2), iv(encrypted with rsa public key of user2) and data(encrypted with key and iv) to server and server sends to user2
	- User2 receives Key, iv, data. User2 decrypts Key and iv with it's own private key and then decrypt the data using key and iv.
	- User2 sends data to file name image.png and that file will be created in the directory of file client.py
## TECHNOLOGY USED:
1. SH256: To encrypt password and store it into database of server
2. RSA: To ensure E2E encryption
3. postgresql: To maintain database
4. Python and socket library: To create servers and clients
5. AES Encryption and Decryption
## How to run code:
(Change localhost if you are working on different devices) 
1. Run python3 mainserver.py 
2. Run python3 server.py port_number 5 times (check port number inside the code and use port numbers in ascending order) 	
3. Run client.py
4. Give username and password
# Example of how to run code:
run first 7 lines on different terminal
1. python3 mainserver.py
2. python3 server.py 7681
3. python3 server.py 7682
4. python3 server.py 7683
5. python3 server.py 7684
6. python3 server.py 7685
7. python3 client.py 
USERNAME: XYZ
PASSWORD: ABC
## COMMANDS
/Send : Send message to another user

/Creategrp : Create a group

/Addmember : Add a user in a group

/Sendgrp : Send message on a group

/kick : Remove participant from a group

/Leavegrp : Leave a group

/Changeadmin : Change the admin of a group

/Sendimg : Send an image to another user

/Deletegrp : Delete a group

/Help : to see all the commands

/Exit : to exit from this terminal
