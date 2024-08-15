from flask import *
from flask_cors import CORS
import mysql.connector as mysql
import os
import datetime
from fpdf import FPDF,HTMLMixin
class MyPDF(FPDF,HTMLMixin):
    pass
app=Flask(__name__)
CORS(app)
app.config["UPLOAD_FOLDER"]="./uploads"
app.secret_key="djjdjdjddj"
app.config["MAX_CONTENT_LENGTH"]=10*1024*1024
con=None
cur=None
def connect():
    global con
    global cur
    con=mysql.connect(host="localhost",user="root",password="",database="kattikeri")
    cur=con.cursor(dictionary=True)
def closeDB():
    global con
    con.close()
@app.route("/")
def home():
    return render_template("home.html")
@app.route("/login")
def loginpage():
    return render_template("login.html")
@app.route("/booking")
def booking():
    return render_template("booking.html")
@app.route("/chome")
def chome():
    return render_template("chome.html")
@app.route("/services")
def services():
    return render_template("services.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/api/login",methods=["GET"])
def login():
    global con
    global cur
    username=request.args.get("uname")
    password=request.args.get("password")
    print(f"{username} and {password}")
    connect()
    cur.execute("select * from users where username=%s and password=%s",(username,password))
    data=cur.fetchone()
    if(data!=None):
        print(data)        
        return jsonify({"status":"success","data":data})
    else:
        return jsonify({"status":"error"})

@app.route("/register")
def register():
    return render_template("register.html")
@app.route("/api/customer",methods=["GET","POST"],defaults={'id':0})
@app.route("/api/customer/<int:id>",methods=["GET","PUT","DELETE"])
def customer(id=None):
    global con
    global cur
    connect()
    print(request.method)
    if(request.method=="GET"):
        if(id==0):
            cur.execute("select * from customer")
            data=cur.fetchall()
            if(len(data)>0):
                return jsonify(data) 
            else:
                return jsonify({"data":""})
        else:
            cur.execute("select * from customer where cid=%s",(id,))
            data=cur.fetchone()
            return jsonify(data)
    elif(request.method=="POST"):
        name=request.form["name"]
        username=request.form["uname"]
        password=request.form["password"]
        address=request.form["address"]
        mobileno=int(request.form["mobileno"])
        gender=request.form["gender"]
        utype='customer'
        cur.execute("insert into customer(name,address,gender,mobileno) values(%s,%s,%s,%s)",(name,address,gender,mobileno))
        cur.execute("insert into users(username,password,type) values(%s,%s,%s)",(username,password,utype))
        con.commit()
        if(cur.rowcount>0):
            lasrowid=cur.lastrowid
            data={"status":"success","rows":lasrowid}
            return jsonify(data)
        else:
            data={"status":"error","rows":0}
            return jsonify(data)
@app.route("/logout")
def logout():
    return render_template('login.html')
@app.route("/api/services")
def service():
    connect()
    cur.execute("select * from service")
    data=cur.fetchall()
    closeDB()
    return jsonify(data)
@app.route("/bookedservicesPage")
def bookedservicesPage():
    return render_template("bookedservices.html")
@app.route("/ahome")
def ahome():
    return render_template("./admin/ahome.html")
@app.route("/report")
def report():
    return render_template("./admin/report.html")
@app.route("/paymentpage")
def paymentPage():
    return render_template("payment.html")
@app.route("/receipt")
def receipt():
    return render_template("receipt.html")
@app.route("/service")
def servicepage():
    return render_template("./admin/service.html")
@app.route('/serviceform')
def serviceform():
    return render_template('./admin/servicepage.html')
@app.route("/serviceedit/<int:id>")
def serviceEdit(id=None):
    global con
    global cur
    connect()
    cur.execute("select * from service where sid=%s",(id,))
    data=cur.fetchone()
    return render_template("./admin/servicepageedit.html",data=data)
@app.route("/api/service",methods=["GET","POST"],defaults={'id':0})
@app.route("/api/service/<int:id>",methods=["GET","PUT","DELETE"])
def service1(id=None):
    global con
    global cur
    print(request.method)
    connect()
    if(request.method=="GET"):
        print(f"id={id}")
        if(id==1000):
            cur.execute("select * from service")
            data=cur.fetchall()
            closeDB()
            return jsonify(data)
        elif(id==0):
            cur.execute("SELECT sid,sname,rate from service")
            data=cur.fetchall()
            closeDB()
            return jsonify(data)
        else:
            cur.execute("select * from service where sid=%s",(id,))
            data=cur.fetchone()
            closeDB()
            return jsonify(data)
    elif(request.method=="POST"):
        sname=request.form["sname"]
        rate=request.form["rate"]
        cur.execute("insert into service(sname,rate) values(%s,%s)",(sname,rate,))
        con.commit()
        if(cur.rowcount>0):
            lastrowid=cur.lastrowid
            closeDB()
            data={"status":"success","rowid":lastrowid}
            return jsonify(data)
        else:
            closeDB()
            data={"status":"error","rowid":0}
            return jsonify(data)   
    elif(request.method=="PUT"):
        sname=request.form["sname"]
        rate=request.form["rate"]
        print("id="+str(id))
        print("sname="+sname)
        print("rate="+rate)
        cur.execute("update service set sname=%s,rate=%s where sid=%s",(sname,rate,id))
        con.commit()
        if(cur.rowcount>0):
            lastrowid=cur.rowcount
            closeDB()
            data={"status":"success","rows":lastrowid}
            return jsonify(data)
        else:
            closeDB()
            data={"status":"error","rows":0}
            return jsonify(data)
    elif(request.method=="DELETE"):
        cur.execute("delete from service where sid=%s",(id,))
        con.commit()
        if(cur.rowcount>0):
            lastrowid=cur.rowcount
            closeDB()
            data={"status":"success","rows":lastrowid}
            return jsonify(data)
        else:
            closeDB()
            data={"status":"error","rows":0}
            return jsonify(data)
@app.route("/api/upload",methods=["POST"])
def paymentupload():
    file=request.files['file']
    time=datetime.datetime.now()
    file.save(os.path.join(app.config["UPLOAD_FOLDER"],time.strftime("%d%m%Y%H%M%S")+file.filename))
    return jsonify({"msg":"success","filename":time.strftime("%d%m%Y%H%M%S")+file.filename})
@app.route("/api/bookservice",methods=["POST"])
def bookservice():
    global con
    global cur
    bdate=request.form["bdate"]
    tamt=request.form["tamt"]
    totalpeople=request.form["totalpeople"]
    entance=request.form["entrance"]
    cid=request.form["cid"]
    filename=request.form["filename"]
    #print(bdate+"\ntamt="+str(tamt)+"\n"+cid+"\n"+filename+"\ntp="+totalpeople+"\nent="+entance+"\n")
    sids=request.form["sids"]
    speople=request.form["speople"]
    samt=request.form["samt"]
    lstsid=sids.split(",")
    lstspeople=speople.split(",")
    lstsamt=samt.split(",")
    connect()
    cur.execute("insert into booking(bdate,userid,ticketamt,filename,totalpeople,entrance,status) values(%s,%s,%s,%s,%s,%s,%s)",(bdate,cid,tamt,filename,totalpeople,entance,'na'))
    bid=cur.lastrowid
    for i in range(0,len(lstsid)-1):
        sid=int(lstsid[i])
        people=int(lstspeople[i])
        amt=int(lstsamt[i])
        cur.execute("insert into booked_services(bid,sid,noofpersons,amt) values(%s,%s,%s,%s)",(bid,sid,people,amt))
    con.commit()
    closeDB()
    return jsonify({"msg":"booked"})
@app.route("/api/report")
def reportData():
    global con
    global cur
    connect()
    cur.execute("select bid,date_format(bdate,'%d/%m/%y') as bdate,userid,ticketamt,entrance,totalpeople,filename,status from booking where status='na' order by bdate desc")
    data=cur.fetchall()
    print(data)
    closeDB()
    return jsonify(data)
@app.route("/api/approvepayment/<int:bid>")
def approve(bid=None):
    global con
    global cur
    connect()
    cur.execute("update booking set status='a' where bid=%s",(bid,))
    con.commit()
    closeDB()
    return jsonify({"msg":"approved"})
@app.route("/api/rejectpayment/<int:bid>")
def reject(bid=None):
    global con
    global cur
    connect()
    cur.execute("delete from booked_services where bid=%s",(bid,))
    cur.execute("delete from booking where bid=%s",(bid,))
    closeDB()
    return jsonify({"msg":"rejected"})
@app.route("/api/customerorders/<string:userid>")
def customerorders(userid=None):
    global con
    global cur
    connect()
    cur.execute("select bid,date_format(bdate,'%d/%m/%y') as bdate,userid,ticketamt,entrance,totalpeople,filename,status from booking where userid=%s order by bdate desc",(userid,))
    data=cur.fetchall()
    print(data)
    closeDB()
    return jsonify(data)
@app.route("/printreceipt/<bid>")
def printreceipt(bid=None):
    global con
    global cur
    connect()
    cur.execute("select bid,date_format(bdate,'%d/%m/%y') as bdate,userid,ticketamt,entrance,totalpeople,filename,status from booking where bid=%s",(bid,))
    data=cur.fetchone()
    src=os.path.join(app.config["UPLOAD_FOLDER"],"entrance.jpg")
    output=f"<img src='{src}' width='500' height='100'/><br />"
    output=output+"<h1 align='center'>KattiKeri Jamkhandi Udyanavana</h1>"
    output=output+"<h3 align='center'>Payment Receipt<br/>"
    output=output+f"<b align='center'>Ticekt ID:{data['bid']}</b><br />"
    output=output+f"<b align='center'>Date:{data['bdate']}</b><br />"
    output=output+f"<b align='center'>User:{data['userid']}</b><br />"
    output=output+f"<b align='center'>Number of People:{data['totalpeople']}</b><br />"
    output=output+f"<b align='center'>Ticekt Amt:{data['ticketamt']}</b><br />"
    output=output+f"<b align='center'>Entrance Fees:{data['entrance']}</b><br />"
    totalamt=int(data["ticketamt"])+int(data["entrance"])
    output=output+f"<b align='center'>Total Amount:{totalamt}</b></h3>"
    cur.execute("select s.sid,sname,rate,noofpersons,amt from service s,booked_services bs where s.sid=bs.sid and bs.bid=%s",(bid,))
    data1=cur.fetchall()
    closeDB()
    slno=1
    output=output+"<h3 align='center'>Booked Services are as follows</h3>"
    output=output+"<table border='1' align='center'><tr><th>SLNO</th><th>Service Name</th><th>Rate</th><th>Number of persons</th><th>Amount</th></tr>"
    for s in data1:
        output=output+f"<tr align='center'><td>{slno}</td><td>{s['sname']}</td><td>{s['rate']}</td><td>{s['noofpersons']}</td><td>{s['amt']}</td></tr>"
        slno=slno+1
    output=output+"</table>"
    pdf=MyPDF()
    pdf.add_page()
    pdf.write_html(output)
    pdf.output('receipt.pdf','F')
    return send_from_directory('./','receipt.pdf')
