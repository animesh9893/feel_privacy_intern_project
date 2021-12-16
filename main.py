from flask import Flask,render_template,request, url_for, redirect
import json

import datetime
from dateutil import parser

# databse functions
from database import loginManager,updateMeetingLink,employeeDetail
from database import loginEmployee,deleteMeeting,changeSessionManager
from database import createMeeting,createManager,meetingListsManager
from database import createEmployee,bookMeeting,meetingDaysManager
from database import unbookMeeting,meetingDetail,managerDetail
from database import meetingDays, meetingList,managerMeeting
from database import bookedMeetingEmployee



app = Flask(__name__)

message = ""
code = 200


# basic home page
@app.route('/', methods=['GET', 'POST'])
def homePage():
    return redirect(url_for("loginPage"))

# login page for manager and employee
@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    global message
    global code
    print(message,code)
    return render_template("login.html",message=message,code=code)

# handle manager login
@app.route('/managerLogin', methods=['GET','POST'])
def managerLoginHandler():
    global message
    global code
    username = request.form.get("username")
    password = request.form.get("password")
    pin = request.form.get("pin")
    print(username,password,pin)
    resp = loginManager(str(username),str(password),pin)
    if resp["code"]==500:
        code = 500
        message = resp["message"]
        return redirect(url_for('loginPage'))
    print("login sucess",resp)
    return redirect(url_for('homeManager',manager_id=resp["manager_id"],session=resp["session"]))

# handle and show the meeting of manager
@app.route('/manager', methods=['GET', 'POST'])
def homeManager():
    global message
    global code
    session = request.args.get("session")
    manager_id = request.args.get("manager_id")
    meeting_day = request.args.get("meeting_day")
    if meeting_day!=None:
        meeting_day = parser.parse(meeting_day)

    print(session,manager_id)
    manager_meet = managerMeeting(manager_id)
    meeting_days = list(set(meetingDaysManager(manager_id)["data"]))
    manager_detail = managerDetail(manager_id,session)
    
    homeLink = "/manager?manager_id="+str(manager_id)+"&session="+session

    current_date_max = datetime.datetime.today()
    tomorrow = datetime.datetime.today()+datetime.timedelta(days=1)
    
    result = []
    meeting_days.sort()

    if meeting_day==None:
        meeting_day=meeting_days[0]

    for i in meeting_days:
        if i==current_date_max:
            result.append({"message":"Today","date":i})
        elif i==tomorrow:
            result.append({"message":"Tomorrow","date":i})
        else:
            result.append({"message":i.strftime("%d/%m/%Y"),"date":i})
    meeting_days = result

    meeting_list = meetingListsManager(manager_id,meeting_day)["data"]
    result = []
    for i in meeting_list:
        temp = i
        temp["timestamp"] = parser.parse(temp["timestamp"]).strftime("%H:%M")
        result.append(temp)
    meeting_list = result


    return render_template("home.html",
        manager_id=manager_id,manager_meet=manager_meet,
        meeting_days=meeting_days,manager_detail=manager_detail,
        homeLink=homeLink,meeting_list=meeting_list,session=session
    )

# manager meeting console
@app.route('/meetingManager', methods=['GET','POST'])
def meetingManager():
    session = request.args.get("session")
    manager_id = request.args.get("manager_id")
    meeting_id = request.args.get("meeting_id")

    meeting_detail = meetingDetail(int(meeting_id))["data"]
    meeting_detail["time"] = meeting_detail["timestamp"].strftime("%H:%M")
    meeting_detail["date"] = meeting_detail["timestamp"].strftime("%d/%m/%Y")

    return render_template('meeting.html',meeting_detail=meeting_detail,meeting_id=meeting_id,manager_id=manager_id,session=session)

# manager add meeting handler
@app.route('/addMeetingHandler', methods=['GET', 'POST'])
def addMeetingHandler():
    session = request.form.get("session")
    manager_id = int(request.form.get("manager_id"))
    time = parser.parse(request.form.get("time"))
    print(time,manager_id,session)
    resp = createMeeting(int(manager_id),time,session)
    return redirect(url_for('homeManager',manager_id=manager_id,session=session))
    # return render_template('addMeeting.html',manager_id=manager_id,session=session)

# manager add meeting handler
@app.route('/addMeeting', methods=['GET', 'POST'])
def addMeeting():
    session = request.args.get("session")
    manager_id = request.args.get("manager_id")
    return render_template('addMeeting.html',manager_id=manager_id,session=session)

# logout manager
@app.route('/logoutManager', methods=['GET', 'POST'])
def logoutManager():
    return redirect(url_for('homePage'))

# delete the meeting
@app.route('/deleteMeeting',methods=["GET","POST"])
def deleteMeetingHandler():
    session = request.form.get("session")
    manager_id = request.form.get("manager_id")
    meeting_id = request.form.get("meeting_id")
    pin = request.form.get("pin")
    resp = deleteMeeting(int(meeting_id),int(manager_id),session,int(pin))
    print(resp)
    if resp["code"]==500:
        return redirect(url_for('meetingManager',manager_id=manager_id,meeting_id=meeting_id,session=session))
    return redirect(url_for('homeManager',manager_id=manager_id,meeting_id=meeting_id,session=session))

# update the meeting link
@app.route('/changeLink',methods=["GET","POST"])
def changeLink():
    # password = request.form.get("password")
    session = request.form.get("session")
    manager_id = request.form.get("manager_id")
    meeting_id = request.form.get("meeting_id")
    link = request.form.get("link")
    resp = updateMeetingLink(int(meeting_id),int(manager_id),str(session),str(link))
    print(meeting_id,manager_id,session,link)
    return redirect(url_for('meetingManager',manager_id=manager_id,meeting_id=meeting_id,session=session))

# user functions --------
# handle manager login
@app.route('/employeeLogin', methods=['GET','POST'])
def employeeLoginHandler():
    global message
    global code
    username = request.form.get("username")
    password = request.form.get("password")
    pin = request.form.get("pin")
    print(username,password,pin)
    resp = loginEmployee(str(username),str(password),pin)
    if resp["code"]==500:
        code = 500
        message = resp["message"]
        return redirect(url_for('loginPage'))
    print("login sucess",resp)
    return redirect(url_for('homeEmployee',employee_id=resp["employee_id"],session=resp["session"]))

# handle and show the meeting of manager
@app.route('/employee', methods=['GET', 'POST'])
def homeEmployee():
    global message
    global code
    session = request.args.get("session")
    employee_id = request.args.get("employee_id")
    meeting_day = request.args.get("meeting_day")
    if meeting_day!=None:
        meeting_day = parser.parse(meeting_day)

    employee_meet = meetingDays()
    meeting_days = list(set(meetingDays()["data"]))
    employee_detail = employeeDetail(int(employee_id),session)
    
    homeLink = "/employee?employee_id="+str(employee_id)+"&session="+session

    current_date_max = datetime.datetime.today()
    tomorrow = datetime.datetime.today()+datetime.timedelta(days=1)
    
    result = []
    meeting_days.sort()

    if meeting_day==None:
        meeting_day=meeting_days[0]

    for i in meeting_days:
        if i==current_date_max:
            result.append({"message":"Today","date":i})
        elif i==tomorrow:
            result.append({"message":"Tomorrow","date":i})
        else:
            result.append({"message":i.strftime("%d/%m/%Y"),"date":i})
    meeting_days = result

    meeting_list = meetingList(meeting_day)["data"]
    result = []
    for i in meeting_list:
        temp = i
        temp["timestamp"] = parser.parse(temp["timestamp"]).strftime("%H:%M")
        result.append(temp)
    meeting_list = result


    return render_template("homeEmployee.html",
        employee_id=employee_id,meeting_days=meeting_days,
        employee_detail=employee_detail,
        homeLink=homeLink,meeting_list=meeting_list,session=session
    )

# manager meeting console
@app.route('/meetingEmployee', methods=['GET','POST'])
def meetingEmployee():
    session = request.args.get("session")
    employee_id = request.args.get("employee_id")
    meeting_id = request.args.get("meeting_id")

    meeting_detail = meetingDetail(int(meeting_id))["data"]
    meeting_detail["time"] = meeting_detail["timestamp"].strftime("%H:%M")
    meeting_detail["date"] = meeting_detail["timestamp"].strftime("%d/%m/%Y")

    return render_template('meetingEmployee.html',
        meeting_detail=meeting_detail,meeting_id=meeting_id,
        employee_id=employee_id,session=session
    )

@app.route('/bookMeeting', methods=['GET','POST'])
def bookMeetingHandler():
    session = request.args.get("session")
    employee_id = request.args.get("employee_id")
    meeting_id = request.args.get("meeting_id")
    print(bookMeeting(int(meeting_id),int(employee_id),session))
    print(session,employee_id,meeting_id)
    return redirect(url_for('homeEmployee',employee_id=employee_id,session=session))

@app.route('/unbookMeeting', methods=['GET','POST'])
def unbookMeetingHandler():
    session = request.args.get("session")
    employee_id = request.args.get("employee_id")
    meeting_id = request.args.get("meeting_id")
    unbookMeeting(int(meeting_id),int(employee_id),session)

    return redirect(url_for('bookMeetingList',employee_id=employee_id,session=session))

@app.route('/bookMeetingList', methods=['GET','POST'])
def bookMeetingList():
    session = request.args.get("session")
    employee_id = request.args.get("employee_id")
    meeting_id = request.args.get("meeting_id")

    meeting_list = bookedMeetingEmployee(int(employee_id),session)
    print(meeting_list["data"])
    meeting_list = meeting_list["data"]
    result = []
    for i in meeting_list:
        temp = i
        temp["timestamp"] = temp["timestamp"].strftime("%H:%M")
        result.append(temp)
    meeting_list = result
    print(meeting_list)
    return render_template('bookMeetingEmployee.html',
        employee_id=employee_id,session=session,meeting=meeting_list
    )


if __name__ == '__main__':
    app.run(host='localhost', port=8080)




