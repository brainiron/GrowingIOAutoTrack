#-*- coding=utf-8 -*-
import pandas as pd
import hashlib
import hmac
import time
import requests as req
import json

project_id = '97fd6815651f25fb'
publicKey = '06b3f5eb364f410eb7435a6940c4f431'
privateKey = '3bde47c09c534a0db10a4b2402d3cd46'
project_uid= 'z98jGyZP'

def authToken(secret, project, ai, tm):
    """计算 auth """
    message = ("POST\n/auth/token\nproject=" + project + "&ai=" + ai + "&tm=" + tm).encode('utf-8')
    signature = hmac.new(bytes(secret.encode('utf-8')), bytes(message), digestmod=hashlib.sha256).hexdigest()
    return signature

def getToken():
    tmStamp = str(round(time.time() * 1000))
    print ('使用时间戳 tm -> '+tmStamp)

    # 私钥、project uid , ai , tm
    authStr = authToken(privateKey, project_uid, project_id,tmStamp)
    print('authToken 计算 -> '+authStr)

    # header 中是 公钥
    header = {'X-Client-Id':publicKey}
    urlToken = 'https://www.growingio.com/auth/token?ai={ai}&project={project}&tm={tm}&auth={auth}'.format(
        ai=project_id,
        project=project_uid,
        tm=tmStamp,
        auth=authStr
        )
    # 
    token = req.post(urlToken,headers = header)
    print("token 请求返回 -> "+token.text)
    tokenReturn = json.loads(token.text)
    print('返回 token 啦 -> '+ tokenReturn['code'])
    return tokenReturn['code']

# 公钥、token
headerEvents = {'X-Client-Id':publicKey,'Authorization':getToken()}
print("header -> "+str(headerEvents))

def events():
    """创建事件级变量"""
    cstmUrl = 'https://www.growingio.com/v1/api/projects/{}/vars/events'.format(project_uid)
    with open('events.csv') as file:
        trackFile = pd.read_csv(file,encoding = "utf_8",index_col=0)
        for index,row in trackFile.iterrows():
            cstmData={
                'type':row['type'],
                'description':row['description'],
                'name':row['name'],
                'key':row['key']
                }
            print('data: ', cstmData)
            r = req.post(cstmUrl,headers=headerEvents,json=cstmData)
            print(r.text)
            print(r.status_code)

def getCstmEventsVariable():
    """获取事件级变量"""
    getCstmEventsUrl= 'https://www.growingio.com/v1/api/projects/{}/vars/events'.format(project_uid)
    requests = req.get(getCstmEventsUrl,headers = headerEvents)
    if(requests.status_code == 200):
        print('---------获取事件级变量-----------')
        events = pd.read_json(requests.text)
        events.to_csv("getEvents.csv")
        print('---------生成表格 getEvents.csv -----------')

def cstmEvents():
    """创建打点事件"""
    eventsUrl = 'https://www.growingio.com/v1/api/projects/{}/dim/events'.format(project_uid)
    listEvents = {}
    with open('getEvents.csv') as file:
        events = pd.read_csv(file,encoding = "utf_8",index_col=0)
        for index,row in events.iterrows():
            listEvents[row['name']] = {"key": row['key'],"id": row['id'], "name": row['name']}

        print(listEvents)

    with open('cstmEvents.csv') as file:
        trackFile = pd.read_csv(file,encoding = "utf_8",index_col=0)
        for index,row in trackFile.iterrows():
            var = print(row['cstm_cn'].split("、"))
            attrs = {}
            for key in var:
                attrs += listEvents[key]

            cstmData={
                'attrs':attrs,
                'type':row['type'],
                'description':row['description'],
                'name':index,
                'key':row['key']
                }
            
            print(cstmData)
            # r = req.post(eventsUrl,headers=headerEvents,json=cstmData)
            # print(r.text)
            # print(r.status_code)

  
# events()
# getCstmEventsVariable()
cstmEvents()