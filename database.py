import pymongo
import datetime
import random
import base64

myclient = None
mydb = None
meeting_col = None
manager_col = None
employee_col = None


# encode base64 encode
def encodeString(s):
	sample_string = str(s)
	string_byte = sample_string.encode("ascii")
	base64_bytes = base64.b64encode(string_byte)
	base64_string = base64_bytes.decode("ascii")
	return base64_string

# decode
def decodeString(s):
	base64_string = str(s)
	base64_bytes = base64_string.encode("ascii")
	sample_string_bytes = base64.b64decode(base64_bytes)
	sample_string = sample_string_bytes.decode("ascii")
	return sample_string

# connect to database
def connect():
	global myclient
	global mydb
	global meeting_col
	global manager_col
	global employee_col
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient["meetingManager"]
	meeting_col = mydb["meetings"]
	manager_col = mydb["manager"]
	manager_col = mydb["manager"]
	employee_col = mydb["employee"]

# utils end-------------------------

# meeting function ---------------------------

# gives the last meeting id
def lastMeetingId():
	global meeting_col
	if meeting_col == None:
		connect()
	result = []
	res = meeting_col.find().sort("meeting_id",-1).limit(1)
	for i in res:
		result.append(i)
	if len(result)==0:
		return 0
	try:
		return result[0]["meeting_id"]
	except:
		return 0

# check if date is valid or not
def dateIsValid(timestamp):
	current_time = datetime.datetime.now()
	if current_time>=timestamp:
		return False
	return True

# check if meeting data is valid or not
def meetingDataIsValid(data):
	global meeting_col
	if meeting_col == None:
		connect()
	result = []
	x = meeting_col.find({"meeting_id":data["meeting_id"]},{})
	for i in x:
		result.append(i)
	if len(result)!=0:
		print("Meeting id Exist")
		return False
	if not managerExist(data["manager_id"]):
		print("manager not Exist ")
		return False
	if not dateIsValid(data["timestamp"]):
		print("date is not Valid")
		return False
	return True

# create meeting
def createMeeting(manager_id,meet_time,session):
	data = {}
	global meeting_col
	if meeting_col == None:
		connect()
	x = manager_col.find({"manager_id":manager_id,"session":session},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"manager cred is wrong"
		}

	last_meeting_id = lastMeetingId()
	data["meeting_id"] = last_meeting_id+1
	data["manager_id"] = manager_id
	data["isBooked"] = False
	data["employee_id"] = None
	data["link"] = ""
	data["timestamp"] = meet_time
	if meetingDataIsValid(data):
		x = meeting_col.insert_one(data)
		print(x.inserted_id)
		data["code"]=200
		data["message"]=""
		return data

	data["code"]=500
	data["message"]="data is not valid"
	return data

def meetingExist(meeting_id):
	global meeting_col
	if meeting_col==None:
		connect()
	result = []
	x = meeting_col.find({"meeting_id":meeting_id},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return False
	return True

def isBooked(meeting_id):
	global meeting_col
	if meeting_col==None:
		connect()
	result = []
	x = meeting_col.find({"meeting_id":meeting_id},{})
	for i in x:
		result.append(i)
	if len(result)==0 or result[0]["isBooked"]==True:
		return True
	return False
# meeting function end ---------------------------





# manager function start ---------------------

def changeSessionManager(manager_id,session):
	global manager_col
	if manager_col == None:
		connect()
	if not managerExist(managerExist):
		return {
			"code":500,
			"message":"Manager not exist"
		}
	manager_col.update_one({"manager_id":manager_id,"session":session},{"$set":{"session":str(random.getrandbits(128))}})
	return {
		"code":200,
		"message":""
	}
# gives the last manager id
def lastManagerId():
	global manager_col
	if manager_col == None:
		connect()
	result = []
	res = manager_col.find().sort("manager_id",-1).limit(1)
	for i in res:
		result.append(i)
	if len(result)==0:
		return 0
	try:
		return result[0]["manager_id"]
	except:
		return 0
	# return 0

# check if same username present
def managerUsernameExist(username):
	global manager_col
	if manager_col == None:
		connect()
	x = manager_col.find({"username":username},{})
	result = []
	for i in x:
		result.append(i)
	if len(result)==0:
		return False
	return True

# create manager
def createManager(username,password,email="",pin=123):
	data = {}
	global manager_col
	if manager_col == None:
		connect()
	if managerUsernameExist(username):
		return {"code":500,"message":"user Exist"}
	last_manager_id = lastManagerId()
	hash_key = random.getrandbits(128)
	data["session"] = str(hash_key)
	data["username"] = username
	data["password"] = encodeString(password)
	data["email"] = email
	data["meeting"] = []
	data["pin"] = encodeString(pin)
	data["manager_id"] = last_manager_id+1
	manager_col.insert_one(data)
	return {
		"code":200,
		"message":"",
		"manager_id":last_manager_id+1,
		"username":username,
		"session":str(hash_key)
	}

# login manager
def loginManager(username,password,pin):
	global manager_col
	if manager_col == None:
		connect()
	result = []
	x=manager_col.find({"username":username},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return {
			"code":500,
			"message":"Invalid user"
		}
	if password!=decodeString(result[0]["password"]):
		return {
			"code":500,
			"message":"Invalid password"
		}
	if str(pin)!=decodeString(result[0]["pin"]):
		return {
			"code":500,
			"message":"Invalid PIN"
		}
	hash_key = str(random.getrandbits(128))
	manager_col.update_one({"manager_id":result[0]["manager_id"]},{"$set":{"session":hash_key}})
	return {
		"code":200,
		"message":"",
		"manager_id":result[0]["manager_id"],
		"session": hash_key
	}

# check if manager exist or not
def managerExist(_id):
	global manager_col
	if manager_col==None:
		connect()
	result = []
	x= manager_col.find({"manager_id":_id},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return False
	return True

def deleteMeeting(meeting_id,manager_id,session,pin):
	global meeting_col
	global manager_col
	if manager_col == None:
		connect()
	x = manager_col.find({"manager_id":manager_id,"session":session,"pin":encodeString(pin)},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"manager cred is wrong"
		}
	x = meeting_col.find({"meeting_id":meeting_id},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"meeting not found"
		}
	if result[0]["isBooked"]==True:
		return {
			"code":500,
			"message":"meeting is already book"
		}
	query = {"meeting_id":meeting_id}
	meeting_col.delete_many(query)
	return {
		"code":200,
		"message":""
	}

def updateMeetingLink(meeting_id,manager_id,session,link):
	global meeting_col
	global manager_col
	if manager_col == None:
		connect()
	x = manager_col.find({"manager_id":manager_id,"session":session},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"manager cred is wrong"
		}
	x = meeting_col.find({"meeting_id":meeting_id},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"meeting not found"
		}
	meeting_col.update_one({"meeting_id":meeting_id},{"$set":{"link":link}})
	return {
		"code":200,
		"message":""
	}

def managerMeeting(manager_id):
	global meeting_col
	global manager_col
	if manager_col == None:
		connect()
	x = manager_col.find({"manager_id":int(manager_id)},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"manager cred is wrong"
		}
	x = meeting_col.find({"manager_id":int(manager_id)},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"meeting not found"
		}
	return {
		"code":200,
		"message":"",
		"data":result
	}

def meetingDaysManager(manager_id):
	manager_id = int(manager_id)

	global meeting_col
	if meeting_col==None:
		connect()
	x = meeting_col.find({"manager_id":manager_id},{})
	result = []
	for i in x:
		result.append(i["timestamp"].date())
	return {
		"code":200,
		"message":"",
		"data":result
	}


def meetingListsManager(manager_id,day):
	manager_id = int(manager_id)

	global meeting_col
	if meeting_col==None:
		connect()

	lower = datetime.datetime.combine(day, datetime.datetime.min.time())
	upper = datetime.datetime.combine(day, datetime.datetime.max.time())

	x = meeting_col.find({"timestamp":{"$lte":upper,"$gte":lower},"manager_id":manager_id})
	# date = date.replace(minute=59, hour=23, second=59, year=2018, month=6, day=1)
	result = []
	for i in x:
		i["timestamp"] = i["timestamp"].isoformat()
		del i["_id"]
		result.append(i)
	return {
		"code":200,
		"message":"",
		"data":result
	}

def managerDetail(manager_id,session):
	manager_id = int(manager_id)
	global manager_col
	if manager_col == None:
		connect()
	x = manager_col.find({"manager_id":manager_id,"session":session},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"manager cred is wrong"
		}
	return {
		"code":500,
		"message":"",
		"data":result[0]
	}









# mangaer function end --------------

# employee function start

# check if same username present
def employeeUsernameExist(username):
	global employee_col
	if employee_col == None:
		connect()
	x = employee_col.find({"username":username},{})
	result = []
	for i in x:
		result.append(i)
	if len(result)==0:
		return False
	return True

def lastEmployeeId():
	global employee_col
	if employee_col == None:
		connect()
	result = []
	res = employee_col.find().sort("employee_id",-1).limit(1)
	for i in res:
		result.append(i)
	if len(result)==0:
		return 0
	try:
		return result[0]["employee_id"]
	except:
		return 0
	# return 0

def createEmployee(username,password,email="",pin=123):
	data = {}
	global employee_col
	if manager_col == None:
		connect()
	if employeeUsernameExist(username):
		return {"code":500,"message":"user Exist"}
	last_employee_id = lastEmployeeId()
	hash_key = random.getrandbits(128)
	data["session"] = str(hash_key)
	data["username"] = username
	data["password"] = encodeString(password)
	data["email"] = email
	data["pin"] = encodeString(pin)
	data["meeting"] = []
	data["employee_id"] = last_employee_id+1
	employee_col.insert_one(data)
	return {
		"code":200,
		"message":"",
		"employee_id":last_employee_id+1,
		"username":username,
		"session":str(hash_key)
	}


def employeeDetail(employee_id,session):
	employee_id = int(employee_id)
	global manager_col
	if employee_col == None:
		connect()
	x = employee_col.find({"employee_id":employee_id,"session":session},{})
	result = []
	for i in x:
		result.append(i)
	if len(result) == 0:
		return {
			"code":500,
			"message":"employee cred is wrong"
		}
	return {
		"code":500,
		"message":"",
		"data":result[0]
	}




# login employee
def loginEmployee(username,password,pin):
	global employee_col
	if employee_col == None:
		connect()
	result = []
	x=employee_col.find({"username":username},{})
	for i in x:
		result.append(i)
	if password!=decodeString(result[0]["password"]):
		return {
			"code":500,
			"message":"Invalid password"
		}
	if str(pin)!=decodeString(result[0]["pin"]):
		return {
			"code":500,
			"message":"Invalid PIN"
		}
	hash_key = str(random.getrandbits(128))
	employee_col.update_one({"employee_id":result[0]["employee_id"]},{"$set":{"session":hash_key}})
	return {
		"code":200,
		"message":"",
		"employee_id":result[0]["employee_id"],
		"session": hash_key
	}

# check if employee exist or not
def employeeExist(_id):
	global employee_col
	if employee_col==None:
		connect()
	result = []
	x= employee_col.find({"employee_id":_id},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return False
	return True

def bookMeeting(meeting_id,employee_id,session):
	global meeting_col
	global employee_col
	if meeting_col==None:
		connect()
	if not meetingExist(meeting_id):
		return {
			"code":500,
			"message":"meeting is not exist"
		}
	if isBooked(meeting_id):
		return {
			"code":500,
			"message":"meeting is already booked"
		}
	result = []
	x= employee_col.find({"employee_id":employee_id,"session":session},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return {
			"code":500,
			"message":"session is wrong"
		}
	meeting_col.update_one({"meeting_id":meeting_id},{"$set":{"isBooked":True,"employee_id":employee_id}})
	meeting_array = result[0]["meeting"]
	meeting_array.append(meeting_id)

	employee_col.update_one({"employee_id":employee_id,"session":session},{"$set":{"meeting":list(set(meeting_array))}})

	return {
		"code":200,
		"message":"meeting is booked"
	}

def unbookMeeting(meeting_id,employee_id,session):
	global meeting_col
	global employee_col
	if meeting_col==None:
		connect()
	if not meetingExist(meeting_id):
		return {
			"code":500,
			"message":"meeting is not exist"
		}
	if not isBooked(meeting_id):
		return {
			"code":500,
			"message":"meeting is not booked"
	}
	result = []
	x= employee_col.find({"employee_id":employee_id,"session":session},{})
	for i in x:
		result.append(i)
	if len(result)==0:
		return {
			"code":500,
			"message":"session is wrong"
	}
	meeting_array = result[0]["meeting"]
	if meeting_id in meeting_array:
		meeting_array.remove(meeting_id)
		meeting_col.update_one({"meeting_id":meeting_id},{"$set":{"isBooked":False,"employee_id":None}})
		employee_col.update_one({"employee_id":employee_id,"session":session},{"$set":{"meeting":list(set(meeting_array))}})
	else:
		return {
			"code":500,
			"message":"meeting is not booked by employee"
		}
	return {
		"code":200,
		"message":"meeting is unbooked"
	}

def meetingDetail(meeting_id):
	global meeting_col
	if meeting_col==None:
		connect()
	x = meeting_col.find({"meeting_id":int(meeting_id)})
	result = []
	for i in x:
		result.append(i)
	if len(result)==0:
		return {
			"code":500,
			"message":"meeting is not exist"
		}
	return {
		"code":200,
		"message":"",
		"data":result[0]
	}

def meetingDays():
	global meeting_col
	if meeting_col==None:
		connect()
	x = meeting_col.find({"isBooked":False},{})
	result = []
	for i in x:
		result.append(i["timestamp"].date())
	return {
		"code":200,
		"message":"",
		"data":result
	}

def meetingList(day):
	global meeting_col
	if meeting_col==None:
		connect()

	lower = datetime.datetime.combine(day, datetime.datetime.min.time())
	upper = datetime.datetime.combine(day, datetime.datetime.max.time())

	x = meeting_col.find({"timestamp":{"$lte":upper,"$gte":lower},"isBooked":False})
	# date = date.replace(minute=59, hour=23, second=59, year=2018, month=6, day=1)
	result = []
	for i in x:
		i["timestamp"] = i["timestamp"].isoformat()
		del i["_id"]
		if i["isBooked"]==False:
			result.append(i)
	return {
		"code":200,
		"message":"",
		"data":result
	}

def bookedMeetingEmployee(employee_id,session):
	global employee_col
	global meeting_col
	if employee_col==None:
		connect()
	x = employee_col.find({"employee_id":employee_id,"session":session})
	result = []
	for i in x:
		result.append(i)
	if len(result)==0:
		return {
			"code":500,
			"message":"user not exist",
			"data":[]
		}
	x = meeting_col.find({"employee_id":employee_id,"isBooked":True})
	result = []
	for i in x:
		temp = i
		del temp["_id"]
		result.append(temp)
	if len(result)==0:
		return {
			"code":500,
			"message":"user not booked",
			"data":[]
		}
	return {
			"code":200,
			"message":"",
			"data":result
	}

# meetingList((datetime.datetime.now()+datetime.timedelta(days=2)).date())
# meetingDays()
# meetingList

# print(usernameExist("animesh"))


# print(lastManagerId())
# print(createEmployee("animesh","123","animeshshrivatri",123))
# print(bookMeeting(1,1,"24669372921244178510641233504811020965"))
# print(meetingDetail(1,1,"24669372921244178510641233504811020965"))
# print(lastManagerId())
# print(loginManager("animesh","123",123))
# print(managerExist(2))

# print(deleteMeeting(1213122,2,"282354524227274623474917139303590445778",123))

# print(updateMeetingLink(1,2,"260489321422829745203857524119916801137","Adasdasd"))

# print(bookedMeetingEmployee(1,"218717808582800295034267231205088425588"))