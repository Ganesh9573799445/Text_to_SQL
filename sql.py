import sqlite3
## Connect to sqlite
connection=sqlite3.connect("student.db")
#Create a cursor object to insert record, create table, retrieve
cursor=connection.cursor()
#create a table
table_info="""
create table student(name varchar(25),class varchar(25),
section varchar(25),marks int);
"""
cursor.execute(table_info)
#insert some more records
cursor.execute('''insert into student values('Ganesh','Data Science','A',90)''')
cursor.execute('''insert into student values('Dinesh','Data Science','B',100)''')
cursor.execute('''insert into student values('Narendra','Data Science','A',86)''')
cursor.execute('''insert into student values('Koushik','Devops','A',50)''')
cursor.execute('''insert into student values('Sachin','Devops','A',35)''')
#Display all the records
print("The inserted records are")
data=cursor.execute('''select * from student''')
for row in data:
    print(row)
#Close the connection
connection.commit()
connection.close