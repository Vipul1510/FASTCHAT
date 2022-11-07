import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def open_database():
    conn = psycopg2.connect(
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    #cursor          = conn.cursor()
    # name_Database   = "Projfds"
    # sqlCreateDatabase = "CREATE DATABASE "+name_Database+";"
    # myNewDB="poiuy"
    # sqlCreateDatabase =f"SELECT 'CREATE DATABASE {myNewDB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{myNewDB}')"
    # cursor.execute(sqlCreateDatabase)
    #conn.commit()
    print("Database created successfully........")
####################################

def sign_in_up(name,passw):
    conn = psycopg2.connect(
    user='postgres',
    password='postgres',
    host='localhost',
    port= '5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor          = conn.cursor()
    #name_Database   = "Projfds"
    #sqlCreateDatabase = "CREATE DATABASE "+name_Database+";"
    #myNewDB="poiuy"
    #sqlCreateDatabase =f"SELECT 'CREATE DATABASE {myNewDB}' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '{myNewDB}')"
    #cursor.execute(sqlCreateDatabase)
    #conn.commit()
    #print("Database created successfully........")


    
    if cursor != None:
        sql = '''CREATE TABLE IF NOT EXISTS RTYuyfu(
   NAME TEXT NOT NULL PRIMARY KEY,
   COUNTRY TEXT NOT NULL,
   AGE FLOAT,
   SALARY FLOAT    
)'''
        cursor.execute(sql)
    # check whether name is already present or not
        sql134 = 'SELECT * FROM RTYuyfu WHERE name=%s;'
        cursor.execute(sql134,[name])
        result = cursor.fetchone()
        print(result) # Wrote for our conven
        age=0
        number =100000000
        if result!=None:
            if passw==result[1]:
                return 1
            else:
                return -1
        else:
            insert_stmt2 = f"""INSERT INTO RTYuyfu (NAME, COUNTRY,\
AGE, SALARY) VALUES ('{name}', '{passw}', {age},{number}) ON CONFLICT (NAME) DO NOTHING;"""
            cursor.execute(insert_stmt2)
            conn.commit()
            return 0
        """if result!=None:
        print('Name already exists')
        print('Enter 1 for password change else 0')
        a=input(int)
        if a==1:
   # To update password
            print("Enter old password")
            old_pass=input(str)
            if old_pass==result[1]:
                print("Enter new password")
                new_pass=input(str)
                insert_stmt1 = "INSERT INTO RTYuyfu (NAME, COUNTRY,\
AGE, SALARY) VALUES (%s, %s, %s, %s) ON CONFLICT (NAME) DO UPDATE SET country = Excluded.country;"
                data = [(name, new_pass, age,number)]
                cursor.executemany(insert_stmt1, data)"""
        
        insert_stmt2 = f"""INSERT INTO RTYuyfu (NAME, COUNTRY,\
AGE, SALARY) VALUES ('{name}', '{passw}', {age},{number}) ON CONFLICT (NAME) DO NOTHING;"""
#"crypt({passw}, gen_salt('bf'))"  ::: To be used later
        cursor.execute(insert_stmt2)
        conn.commit()