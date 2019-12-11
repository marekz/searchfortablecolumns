import mysql.connector
import os
from datetime import datetime
import csv

startTime = datetime.now()
database = "mydbtoserach"

db = mysql.connector.connect(host="localhost",
    user="rootuserforexample",
    passwd="passwd_tadam",
    db=database
)

path_to_project = "/home/myuser/site/searc/vendor/folder"

i = 0
final_data = {}

cur = db.cursor(buffered=True)

# check if exist element form array in any files
# if yes, than remove element from array
# if no, its mean column is maybe not necesarry and check to remove
def checkColumnInTable(file_list, table, column_list):
    # print("Try to find in table: {0}\ncolumns: {1}\nFile list: ".format(table, column_list))
    for file in file_list:
        with open(file, 'r') as f:
            for line in f:
                for i in column_list:
                    if str(i) in line:
                        column_list.remove(str(i))
    if len(column_list) > 0:
        final_data[table] =  column_list
        

# Find in project files
# scan all files in project and find in files with table name 
# after this, find in founded files column name
# if coumn name dosent exist in file, its is propably the column is not used in serwis.
def findInProjectFiles(table, column_list):
    file_list = []
    for folder, dirs, files in os.walk(path_to_project):
        for file in files:
            if file.endswith('.php'):
                fullpath = os.path.join(folder, file)
                with open(fullpath, 'r') as f:
                    try:
                        for line in f:
                            table_string = "'{0}'".format(table)
                            if table_string in line:
                                if fullpath not in file_list:
                                    file_list.append(fullpath)


                    except UnicodeDecodeError:
                        pass
                    #     print("Wrong codeing style in file...") 
                    #     print(" --- {}".format(fullpath))
    if len(file_list) > 0:
        checkColumnInTable(file_list, table, column_list)


def returnHistoryColumn(table):
    sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='{0}' AND TABLE_NAME='{1}';".format(database, table)
    cur2 = db.cursor()
    column_list = []
    cur2.execute(sql)
    for (COLUMN_NAME) in cur2:
        if 'id' != COLUMN_NAME[0]:
            column_list.append(COLUMN_NAME[0])
    findInProjectFiles(table, column_list)

cur.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='{0}'").format(database)

for (TABLE_NAME) in cur:
    table = TABLE_NAME[0]
    if "history" in table: 
        i = i + 1
        returnHistoryColumn(table)

cur.close()

print(final_data)

endTime = datetime.now()

execution_time = endTime - startTime

print("-------------- Execution time: {0}".format(execution_time))

w = csv.writer(open("output.csv", "w"))

for key, val in final_data.items():
    w.writerow([key, val])