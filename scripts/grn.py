from locust import HttpLocust, TaskSet, task
import Queue
from bs4 import BeautifulSoup
import re

class MyTaskSet(TaskSet):
    
    @task(1)
    def task_addSchedule(self):
        # ---------------LOGIN------------------
        try:
            data = self.locust.user_data_queue.get()
        except Queue.Empty:
            print('account data run out, test ended.')
            exit(0)
        loginInfo = {
            '_system':'1',
            '_account': data['username'],
            '_password': 'cybozu',
            'Content-Type':'application/x-www-form-urlencoded',
            'login-submit':'Login'
        }
        loginResult = self.client.post('/index', data=loginInfo)
        loginSoup = BeautifulSoup(loginResult.text,'lxml')
        token_csrf_ticket = loginSoup.find_all('input', attrs={'name': re.compile("(csrf_ticket)")})[0]['value']
        print "=============="+data['username']+" login end===================="

        # ---------------Click Add schedule icon------------------
        clickAddResult = self.client.get("/schedule/add?bdate=")
        clickAddSoup = BeautifulSoup(clickAddResult.text,"lxml")
        referer_key = clickAddSoup.find_all('input', attrs={'name': re.compile("(referer_key)")})[0]['value']
        uid = clickAddSoup.find_all('input', attrs={'name': re.compile("(uid)")})[0]['value']
        gid = clickAddSoup.find_all('input', attrs={'name': re.compile("(gid)")})[0]['value']
        bdate = clickAddSoup.find_all('input', attrs={'name': re.compile("(bdate)")})[0]['value']
        upload_ticket = clickAddSoup.find_all('input', attrs={'name': re.compile("(upload_ticket)")})[0]['value']
        print "=============="+data['username']+" Click Add schedule end===================="

        # ---------------Submit schedule------------------
        fileName = "test.txt"
        fileDataBinary = open(fileName, 'rb')
        bdateList = bdate.split('-')
        scheduleBody = {
            'csrf_ticket':token_csrf_ticket,
            'tab_name':'schedule/add',
            'bdate':bdate,
            'uid':uid,
            'gid':gid,
            'title':'locust_test_'+bdate,
            'start_year' :bdateList[0],
            'start_month':bdateList[1],
            'start_day':bdateList[2],
            'start_hour':'10',
            'start_minute':'0',
            'end_year':bdateList[0],
            'end_month':bdateList[1],
            'end_day':bdateList[2],
            'end_hour':'11',
            'end_minute':'0',
            'referer_key':referer_key,
            'selected_users_sUID':uid,
            'allow_file_attachment':'1',
            'upload_ticket':upload_ticket
        }
        addSchResult = self.client.post("/schedule/command_add",data=scheduleBody,files={'file':fileDataBinary})
        print "=============="+data['username']+" Submit schedule end===================="

        # ---------------LOGOUT------------------
        fileName = "test.txt"
        logout = {
            'logout':'Logout'
        }
        logoutResult = self.client.post("/command_logout")
        print "=============="+data['username']+" logout end===================="

class MyLocust(HttpLocust):
    task_set = MyTaskSet
    min_wait = 5000
    max_wait = 15000
    host = 'http://localhost/cgi-bin/cbgrn/grn.cgi'
    user_data_queue = Queue.Queue()
    for index in range(1,101):
        data = {
            "username": "user"+str(index)
        }
        user_data_queue.put_nowait(data)
