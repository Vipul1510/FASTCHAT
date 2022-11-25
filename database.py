import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

# It creates a new database 
def open_database():
    """This function creates database and all required tables. This function is called when main server is initiated
    """
    # Credentials to login into postgresql
    conn = psycopg2.connect(
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    # Checking if database already exists or not
    name_Database   = "fastchat"
    query=f"""SELECT datname FROM pg_database WHERE datname='{name_Database}';"""
    cursor.execute(query)
    result=cursor.fetchall()
    if result==[]:
        sqlCreateDatabase = f"""CREATE DATABASE {name_Database};"""
        cursor.execute(sqlCreateDatabase)
    conn.commit()
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = "DROP TABLE IF EXISTS Clients ;"
    cursor.execute(sql)
    sql = "DROP TABLE IF EXISTS grp_modified;"
    cursor.execute(sql)
    sql = "DROP TABLE IF EXISTS msg_stack ;"
    cursor.execute(sql)
    # Creating table clients which keeps all details of clients including whether user's status of online or offline
    sql = '''CREATE TABLE IF NOT EXISTS Clients(
   NAME TEXT NOT NULL PRIMARY KEY,
   PASSWORD TEXT NOT NULL,
   IS_ONLINE FLOAT,
   PUBLIC_KEY TEXT   
    )'''
    cursor.execute(sql)
    # Creates table grp_modified which stores the groupname,admin name and participants
    sql = '''CREATE TABLE IF NOT EXISTS grp_modified(
        GRPNAME TEXT NOT NULL,
        ADMIN TEXT NOT NULL,
        Participants TEXT NOT NULL,
        PublicKey TEXT NOT NULL,
        CONSTRAINT pk_grp_modified PRIMARY KEY(GRPNAME,ADMIN,Participants,PublicKey)  
        )'''
    cursor.execute(sql)
    sql = '''CREATE TABLE IF NOT EXISTS msg_stack(
   TO_name TEXT NOT NULL,
   MSG bytea NOT NULL,
   Is_image INT,
   time_stamp INT,
   CONSTRAINT pk_msg_stack PRIMARY KEY(TO_name,MSG,time_stamp)  
   )'''
    cursor.execute(sql)
    conn.commit()
    print("Database initiated........")

# Sign in and Sign Up 
def sign_in_up(name,passw):
    """This function takes care of authentication by storing username and encrypted password in table 'clients' and also keeps track of user is online or not along with public key of the user.

    :param name: It denotes username
    :param passw: It denotes password of the respective username 
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    # check whether name is already present or not
    sql134 = 'SELECT * FROM Clients WHERE name=%s;'
    cursor.execute(sql134,[name])
    result = cursor.fetchone()
    is_online=1
    # If name is already present (i.e old user) then checks encrypted password matches with encrypted input password  
    if result!=None:
        if passw==result[1]:
            insert_stmt2 = f"""UPDATE Clients SET IS_ONLINE=1 WHERE name='{name}';"""
            cursor.execute(insert_stmt2)
            conn.commit()
            return 1
        else:
            return -1
    # If new user joins then adds username, password and public key to the database
    else:
        insert_stmt2 = f"""INSERT INTO Clients (NAME, PASSWORD,\
IS_ONLINE) VALUES ('{name}', '{passw}', {is_online}) ON CONFLICT (NAME) DO NOTHING;"""
        cursor.execute(insert_stmt2)
        conn.commit()
        return 0

# Update public key
def update_pubkey(name,publicKey):
    """This function adds public key to the respective username in the table 'clients'

    :param name: It denotes username
    :param publicKey: It denotes public key of the respective username
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    insert_stmt2 = f"""UPDATE Clients SET PUBLIC_KEY='{publicKey}' WHERE name='{name}';"""
    cursor.execute(insert_stmt2)
    conn.commit()

# Get public key (It returns public key of given member)
def get_public_key(name):
    """This function gives public key of the given username

    :param name: It denotes username
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = 'SELECT * FROM Clients WHERE name=%s;'
    cursor.execute(sql134,[name])
    result = cursor.fetchone()
    if result!=None:
        return result[3]        # Return public key
    else:
        return -1               # If name not exists return -1

# Group Creation
def group(groupname,admin,publickey):
    """This function adds groupname, admin name and publickey of admin in table grp_modified

    :param groupname: It denotes group name of the new group which user wants to create
    :param admin: It denotes the user who is creating the group
    :param publickey:  It denotes the public key of admin
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    # Checks if already groupname is existing or not
    sql=f'''SELECT grpname FROM grp_modified WHERE GRPNAME='{groupname}';'''
    cursor.execute(sql)
    result=cursor.fetchall()
    # If group name is new then insert groupname, admin in the table
    if result==[]:
        insert_stmt1 = "INSERT INTO grp_modified (GRPNAME, ADMIN,Participants, PublicKey) VALUES (%s, %s,%s,%s)ON CONFLICT (GRPNAME,ADMIN,Participants, PublicKey) DO NOTHING;"
        data = [(groupname,admin,admin,publickey)]
        cursor.executemany(insert_stmt1, data)
        return 1
    else:
        return -1

# Add participants to the group
def add_participants_to_grp(grpname,admin,new_participant,publickey):
    """This function adds groupname, admin name, username and publickey of username in table grp_modified

    :param groupname: It denotes group name in which admin wants to add new participant
    :param admin: It denotes the admin of the group
    :param new_participant: It denotes the username 
    :param publickey:  It denotes the public key of admin
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result==None:
        return -1      # There is no group having group name as grpname 
    elif result[1]!=admin:
        return result[1]      # user is not admin type=str
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{new_participant}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result!=None:
        return(1)       # new_participant already exists 
    elif result==None:
        insert_stmt1 = f"INSERT INTO grp_modified (GRPNAME, ADMIN,Participants, PublicKey) VALUES ('{grpname}', '{admin}','{new_participant}','{publickey}');"
        cursor.execute(insert_stmt1)
        conn.commit
        return 2           # Done successfully 

# Delete participants from the group
def delete_participants_from_grp(grpname,admin,member):
    """This function deletes the username from the group if fuction is called by admin

    :param grpname: It denotes group name from which admin has to delete participant
    :param admin: It denotes admin of the group
    :param member: It denotes the member to which admin wants to kick out
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()

    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result==None:
        return -1      # There is no group having group name as grpname 
    elif result[1]!=admin:
        return result[1]       # user is not admin 
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{member}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result==None:
        return(2)       # No participant named member in the group
    elif result!=None:
        insert_stmt1 = f"DELETE FROM grp_modified WHERE Participants='{member}';"
        cursor.execute(insert_stmt1)
        conn.commit
        return 1         # Deleted successfully   

# Delete group
def delete_group(grpname,admin):
    """This function deletes all rows containing group name

    :param grpname: It denotes the group name which admin wants to delete
    :param admin: It denotes the group admin
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result==None:
        return -1      # There is no group having group name as grpname 
    elif result[1]!=admin:
        return result[1]       # user is not admin 
    elif result!=None:
        insert_stmt1 = f"DELETE FROM grp_modified WHERE GRPNAME='{grpname}';"
        cursor.execute(insert_stmt1)
        conn.commit
        return 1         # Deleted successfully  

# When user wants to leave a group
def leave_grp(grpname,name):
    """This function helps user to leave a specific group.

    :param grpname: It denotes the group which user wants to leave
    :param name: It denotes the username of user
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{name}';"
    cursor.execute(sql134)
    result = cursor.fetchall()
    if result==[]:
        return -1      # There is no group having group name as grpname 
    elif result[0][1]==name:
        return 2       # user is admin 
    elif result!=None:
        insert_stmt1 = f"DELETE FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{name}';"
        cursor.execute(insert_stmt1)
        conn.commit
        return 1 

# When admin wants to change the post of admin
def change_admin(grpname,admin,new_admin):
    """This function helps the admin to change another user to to admin

    :param grpname: It denotes the group name for which admin to be changed
    :param admin: It denotes the username of existing admin
    :param new_admin: It denotes the username of new admin
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{admin}';"
    cursor.execute(sql134)
    cursor.execute(sql134)
    result = cursor.fetchall()
    if result==[]:
        return -1      # There is no group having group name as grpname 
    elif result[0][1]==admin:
        sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{new_admin}';"
        cursor.execute(sql134)
        result = cursor.fetchall()
        if result==[]:
            return -2
        else:
            stmt = f"""UPDATE grp_modified SET admin='{new_admin}' WHERE admin='{admin}' AND grpname='{grpname}';"""
            cursor.execute(stmt)
            return 1       # Done successfully
    else:
        return -3     # user is part of grp but not admin
    
# When user becomes offline bool is_online becomes 0
def exit_user(username):
    """This function changes online status of user to offline while leaving

    :param username: It denotes the username who is exiting (Going offline)
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    # sets is_online status to zero
    stmt = f"""UPDATE Clients SET IS_ONLINE=0 WHERE name='{username}';"""
    cursor.execute(stmt)
    conn.commit()

# store messages when user(receiver) is offline
def msg_store(username,msg,is_image):
    """This function stores the messages when receiver are offline

    :param username: It denotes offline user's name 
    :param msg: It denotes the message which will be saved in database 
    :param is_image: It denotes whether given message is an image or not
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    insert_stmt1 = "INSERT INTO msg_stack (TO_name,MSG,Is_image,time_stamp) VALUES ( %s,%s,%s,%s)ON CONFLICT (TO_name,MSG,time_stamp) DO NOTHING;"
    data = [(username,msg,is_image,time.time()-19800)]
    cursor.executemany(insert_stmt1, data)
    conn.commit

# delete msg if user comes online after sending it to the user
def msg_delete(username):
    """This fuction return one message of a user when he/she comes online and delete then from the table

    :param: It denotes the username who came online
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = f"""SELECT * from msg_stack WHERE TO_name='{username}';"""
    cursor.execute(sql)
    result = cursor.fetchall()
    sql = f"""DELETE from msg_stack WHERE TO_name='{username}' ;"""
    cursor.execute(sql)
    conn.commit
    return result

# Returns number of undelivered msgs
def no_old_msgs(username):
    """This functions returns number of undelivered messages when the user comes onlne

    :param username: It denotes the username of client
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = f"""SELECT * from msg_stack WHERE TO_name='{username}';"""
    cursor.execute(sql)
    result = cursor.fetchall()
    print(len(result),"#$% no of old messages")
    return len(result)

# returns all the members in the group
def all_members(groupname,name):
    """This function returns all members present in a group

    :param groupname: It denotes the groupname 
    :param name: It denotes the user name who want this information
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    # Checks if user with username 'name' present in that group or not
    sql=f'''SELECT * FROM grp_modified WHERE GRPNAME='{groupname}' AND Participants='{name}';'''
    cursor.execute(sql)
    result=cursor.fetchall()
    #print(result)
    if result==[]:
        return []
    sql=f'''SELECT Participants, PublicKey FROM grp_modified WHERE GRPNAME='{groupname}';'''
    cursor.execute(sql)
    result=cursor.fetchall()
    if result==[]:
        return []
    return result

# deletion of msgs after 30 seconds
def deletion_of_old_msgs():
    """This function deletes all messages which are in database for more than 120 seconds time
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql=f"""DELETE from msg_stack WHERE time_stamp <= '{int(time.time()-19920)}'"""
    cursor.execute(sql)

# returns online / offline status of user
def is_online(name):
    """This function returns the online/offline status of the user

    :param name: It denotes the username of client
    """
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql134 = 'SELECT * FROM Clients WHERE name=%s;'
    cursor.execute(sql134,[name])
    result = cursor.fetchall()
    if result==[]:
        return 2
    else:
        return result[0][2]




