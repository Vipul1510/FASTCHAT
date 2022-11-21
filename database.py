import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# It opens new database if not exists
def open_database():
    conn = psycopg2.connect(
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    name_Database   = "fastchat"
    query=f"""SELECT datname FROM pg_database WHERE datname='{name_Database}';"""
    cursor.execute(query)
    result=cursor.fetchall()
    print(result)
    if result==[]:
        sqlCreateDatabase = f"""CREATE DATABASE {name_Database};"""
        cursor.execute(sqlCreateDatabase)
    conn.commit()
    print("Database created successfully........")

# Sign in and Sign Up
def sign_in_up(name,passw):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS Clients(
   NAME TEXT NOT NULL PRIMARY KEY,
   PASSWORD TEXT NOT NULL,
   IS_ONLINE FLOAT,
   EXTRA FLOAT    
    )'''
    cursor.execute(sql)
    # check whether name is already present or not
    sql134 = 'SELECT * FROM Clients WHERE name=%s;'
    cursor.execute(sql134,[name])
    result = cursor.fetchone()
        #print(result) # Wrote for our conven
    is_online=1
    number =100000000
    if result!=None:
        if passw==result[1]:
            return 1
        else:
            return -1
    else:
        insert_stmt2 = f"""INSERT INTO Clients (NAME, PASSWORD,\
IS_ONLINE, EXTRA) VALUES ('{name}', '{passw}', {is_online},{number}) ON CONFLICT (NAME) DO NOTHING;"""
        cursor.execute(insert_stmt2)
        conn.commit()
        return 0

# Group Creation
def group(groupname,admin):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql=f'''SELECT grpname FROM grp_modified WHERE GRPNAME='{groupname}';'''
    cursor.execute(sql)
    result=cursor.fetchall()
    if result==None:
        sql = '''CREATE TABLE IF NOT EXISTS grp_modified(
        GRPNAME TEXT NOT NULL,
        ADMIN TEXT NOT NULL,
        Participants TEXT NOT NULL,
        CONSTRAINT pk_grp_modified PRIMARY KEY(GRPNAME,ADMIN,Participants)  
        )'''
        cursor.execute(sql)
        conn.commit
        insert_stmt1 = "INSERT INTO grp_modified (GRPNAME, ADMIN,Participants) VALUES (%s, %s,%s)ON CONFLICT (GRPNAME,ADMIN,Participants) DO NOTHING;"
        data = [(groupname,admin,admin)]
        cursor.executemany(insert_stmt1, data)
        return 1
    else:
        return -1


# Add participants to the group
def add_participants_to_grp(grpname,admin,new_participant):
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
        return -1      # There is no group having group name as grpname type=int
    elif result[1]!=admin:
        return result[1]       # user is not admin type=str
    sql134 = f"SELECT * FROM grp_modified WHERE GRPNAME='{grpname}' AND Participants='{new_participant}';"
    cursor.execute(sql134)
    result = cursor.fetchone()
    if result!=None:
        return(1)       # new_participant already exists type=int
    elif result==None:
        insert_stmt1 = f"INSERT INTO grp_modified (GRPNAME, ADMIN,Participants) VALUES ('{grpname}', '{admin}','{new_participant}');"
        cursor.execute(insert_stmt1)
        conn.commit
        return 2           # Done successfully type=int


# Delete participants from the group
def delete_participants_from_grp(grpname,admin,member):
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
        return -1      # There is no group having group name as grpname type=int
    elif result[1]!=admin:
        return result[1]       # user is not admin type=str
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


# When user becomes offline bool is_online becomes 0
def exit_user(username):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    stmt = f"""UPDATE Clients SET IS_ONLINE=0 WHERE name='{username}';"""
    cursor.execute(stmt)
    conn.commit()

# stores msg
def msg_store(username,msg,is_image):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS msg_stack(
   TO_name TEXT NOT NULL,
   MSG TEXT NOT NULL,
   Is_image INT,
   time_stamp TIMESTAMP,
   CONSTRAINT pk_msg_stack PRIMARY KEY(TO_name,MSG,time_stamp)  
   )'''
    cursor.execute(sql)
    conn.commit
    from datetime import datetime  
    timestamp = 1625309472.357246 
    date_time = datetime.fromtimestamp(timestamp)
    now  = datetime.now() 
    str_date_time = date_time.strftime("%Y-%D-%M %H:%M:%S")
    insert_stmt1 = "INSERT INTO msg_stack (TO_name,MSG,Is_image,time_stamp) VALUES ( %s,%s,%s,%s)ON CONFLICT (TO_name,MSG,time_stamp) DO NOTHING;"
    data = [(username,msg,is_image,now)]
    cursor.executemany(insert_stmt1, data)
    conn.commit


# delete msgs if user comes online after sending it to the user
def msg_delete(username):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = f"""SELECT * from msg_stack WHERE TO_name='{username}'"""
    cursor.execute(sql)
    result = cursor.fetchall()
    sql = f"""DELETE from msg_stack WHERE TO_name='{username}'"""
    cursor.execute(sql)
    conn.commit
    return result

# returns all the members in the group
def all_members(groupname):
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql=f'''SELECT Participants FROM grp_modified WHERE GRPNAME='{groupname}';'''
    cursor.execute(sql)
    result=cursor.fetchall()
    if result==None:
        return []
    return result


# deletion of msgs after 120 seconds
def deletion_of_old_msgs():
    conn = psycopg2.connect(
    database="fastchat",
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    sql = f"""SELECT * from msg_stack"""
    cursor.execute(sql)
    result = cursor.fetchall()
    for i in result:
        print(i[3],type(i[3]))
        from datetime import datetime     
        now  = datetime.now() 
        duration = now - i[3]  
        duration_in_s = duration.total_seconds() 
        print(duration_in_s)
        if duration_in_s>120:
            sql = f"""DELETE from msg_stack WHERE TO_name='{i[0]}' AND MSG='{i[1]}' """
            cursor.execute(sql)