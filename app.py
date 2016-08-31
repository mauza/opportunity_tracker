from flask import Flask, render_template, request, json, session, redirect, url_for, g
import os
import sqlite3
from datetime import datetime

DATABASE = 'testDB.db'

app = Flask(__name__)
app.debug = True

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
        
def init_db(dbTable):
    with app.app_context():
        db = get_db()
        table = [dbTable,"ID","INTEGER PRIMARY KEY AUTOINCREMENT","Location","CHAR(30)","Department","CHAR(30)","Assigned","CHAR(30)","Priority","CHAR(30)","Status","CHAR(30)","Comments","TEXT","Created","DATE"]
        db.execute('CREATE TABLE if not exists {} ({} {},{} {},{} {},{} {},{} {},{} {},{} {},{} {})'.format(*table)) 
        db.commit()
    
@app.route("/")
def home():
    cur = get_db().execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cur.fetchall()
    info = []
    for table in tables:
        thisTable = []
        cur = get_db().execute('Select * from ' + table[0])
        names = [description[0] for description in cur.description]
        rows = cur.fetchall()
        thisTable.append(table)
        thisTable.append(names)
        thisTable.append(rows)
        info.append(thisTable)
    return render_template('index.html', info = info, active=info[0][0][0])
    
@app.route("/AddTable", methods=['POST'])
def addTable():
    table = request.form["tableName"]
    table = table.replace(" ","_")
    print(table)
    init_db(table)
    return redirect("/")
    
@app.route("/AddElement", methods=['POST'])
def addElement():
    table = request.form['table']
    location = request.form['location']
    department = request.form['department']
    assigned = request.form['assigned']
    priority = request.form['priority']
    status = request.form['status']
    comment = request.form['comments']
    date = str(datetime.now())
    db = get_db()
    db.execute('INSERT INTO {} (Location,Department,Assigned,Priority,Status,Comments,Created) VALUES (?,?,?,?,?,?,?)'.format(table),(location,department,assigned,priority,status,comment,date))
    db.commit()
    return redirect("/")
    
@app.route("/UpdateElement", methods=['POST'])
def UpdateElement():
    id = request.form['id']
    table = request.form['table']
    location = request.form['location']
    department = request.form['department']
    assigned = request.form['assigned']
    priority = request.form['priority']
    status = request.form['status']
    comment = request.form['comments']
    db = get_db()
    db.execute("UPDATE {} SET Location = '{}',Department = '{}',Assigned = '{}',Priority = '{}',Status = '{}',Comments = '{}' WHERE ID = '{}'".format(table,location,department,assigned,priority,status,comment,id))
    db.commit()
    return redirect("/")
    
@app.route("/edit/<table>/<id>")
def editElement(table, id):
    cur = get_db().execute("SELECT * FROM {} WHERE ID = '{}'".format(table,id))
    info = cur.fetchall()
    info = [table] + info
    return render_template('edit.html', info = info)
    
@app.route("/sort/<t>/<by>")
def sortTables(by, t):
    cur = get_db().execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence';")
    tables = cur.fetchall()
    info = []
    for table in tables:
        thisTable = []
        cur = get_db().execute('Select * from ' + table[0] + ' ORDER BY ' + by)
        names = [description[0] for description in cur.description]
        rows = cur.fetchall()
        thisTable.append(table)
        thisTable.append(names)
        thisTable.append(rows)
        info.append(thisTable)
    return render_template('index.html', info = info, active=t)
    

app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))

if __name__ == "__main__":
	app.run()

