# Give 4 inputs while running the program id(str),password(str),int,int
# Rough model for databasing 
import psycopg2
import sys
name=sys.argv[1]
passw=sys.argv[2]
age=int(sys.argv[3])
number=int(sys.argv[4])


# USELESS part starts :)
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
conn = psycopg2.connect(
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cursor          = conn.cursor()
name_Database   = "Projfds"
sqlCreateDatabase = "CREATE DATABASE "+name_Database+";"
myNewDB="poiuy"
sqlCreateDatabase =f"SELECT 'CREATE DATABASE {myNewDB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{myNewDB}')"
cursor.execute(sqlCreateDatabase)
conn.commit()
print("Database created successfully........")
# USELESS part ends :(


# Creating table if it is not there
# NAME = ID
# COUNTRY = PASSWORD
# AGE and SALARY are other things :o
sql = '''CREATE TABLE IF NOT EXISTS RTYuyfu(
   NAME TEXT NOT NULL PRIMARY KEY,
   COUNTRY PASSWORD NOT NULL,
   AGE FLOAT,
   SALARY FLOAT    
)'''
cursor.execute(sql)

  
# Display whole table
cursor.execute("SELECT * FROM RTYuyfu")
print(cursor.fetchall())
print("previous over")
conn.commit()


# check whether name is already present or not
sql134 = 'SELECT * FROM RTYuyfu WHERE name=%s;'
cursor.execute(sql134,[name])
result = cursor.fetchone()
print(result) # Wrote for our conven

if result!=None:
   print('Name already exists')
   print('Enter 1 for password change else 0')
   a=input(int)
   if a:
   # To update password
      print("Enter old password")
      old_pass=input(str)
      if old_pass==result[1]:
         print("Enter new password")
         new_pass=input(str)
         insert_stmt1 = "INSERT INTO RTYuyfu (NAME, COUNTRY,\
AGE, SALARY) VALUES (%s, %s, %s, %s) ON CONFLICT (NAME) DO UPDATE SET country = Excluded.country;"
      data = [(name, new_pass, age,number)]
      cursor.executemany(insert_stmt1, data)
else:
   insert_stmt2 = f"""CREATE EXTENSION IF NOT EXISTS pgcrypto;
   INSERT INTO RTYuyfu (NAME, COUNTRY,\
AGE, SALARY) VALUES ('{name}', crypt('{passw}', gen_salt('bf')), {age},{number}) ON CONFLICT (NAME) DO NOTHING;"""
#"crypt({passw}, gen_salt('bf'))"  ::: To be used later
   cursor.execute(insert_stmt2)

  
# Display whole table again to see changes
cursor.execute("SELECT * FROM RTYuyfu")
print(cursor.fetchall())
  

conn.commit()
conn.close()