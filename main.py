#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@文件    :sign.py
@说明    :学习通签到Python版本 支持 普通签到/照片签到/手势签到/定位签到
@时间    :2021/03/10 20:35:26
@作者    :DanceDJ
@微信公众号    :给我一碗炒饭
@其他    :推荐使用云签到哦，在公众号查看，代码写了很多注释，希望可以帮到大家
@版本    :2.0
'''

import requests,json
import urllib.parse
from random import choices
import datetime,os,time
import emailUtil
session = requests.session()
requests.packages.urllib3.disable_warnings()

#用户配置！必须写！
setting={
    "account":'123456', #账号（手机号 ）「必填」
    "password":'123456', #密码 「必填」
    "sign":{
        "long":'1', #定位签到经纬度 「可空」
        "lat":'1', #定位签到经纬度 「可空」
        "address":'中国...', #定位签到显示的地址 「必填」
        "name":'姓名', #签到姓名 「必填」
        "img":['4c57ab8d2d25b6a60bcbd102a094b1b0'], #图片自定义之后再写，这里可以自己填入objectId列表就可以了，默认上传的图片是「图片加载失败」用来迷惑老师
        "sign_common":True, #是否开启普通签到 「True 开启 False 关闭」 默认开启，无需修改
        "sign_pic":False,    #是否开启照片签到 「True 开启 False 关闭」 默认开启，无需修改
        "sign_hand":True,   #是否开启手势签到 「True 开启 False 关闭」 默认开启，无需修改
        "sign_local":True,  #是否开启定位签到 「True 开启 False 关闭」 默认开启，无需修改
    },
    "other":{
        "count":5, #每门课程只检测前N个活动 避免因课程活动太多而卡住
        "sleep":60 #每次检测间隔时间（S）默认60秒 一分钟
    }
}

#乱七八糟的变量 不要动我
mycookie=""
myuid=""
courselist=[]
signType={ #拍照签到 1 普通签到 2 定位签到 5 手势签到 6
    1: '拍照签到',
    2: '普通签到',
    5: '定位签到',
    6: '手势签到',
}

#登录
def login(uname,code):
    global mycookie,myuid
    url="https://passport2-api.chaoxing.com/v11/loginregister?code="+code+"&cx_xxt_passport=json&uname="+uname+"&loginType=1&roleSelect=true"
    res=session.get(url)
    data = requests.utils.dict_from_cookiejar(session.cookies)
    mycookie=""
    for key in data:
        mycookie+=key+"="+data[key]+";"
    d=json.loads(res.text)
    if(d['mes']=="验证通过"):
        print(uname+"登录成功")
        url="https://sso.chaoxing.com/apis/login/userLogin4Uname.do"
        res=session.get(url)
        a=json.loads(res.text)
        if(a['result']==1):
            myuid=str(a['msg']['puid'])
            save_cookies(myuid,2)
            return 1
        else:
            print("获取uid失败")
    return 0
#获取同意请求头 包含Cookie
def getheaders():
    headers={"Accept-Encoding": "gzip",
    "Accept-Language": "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
    "Cookie": mycookie,
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 com.ssreader.ChaoXingStudy/ChaoXingStudy_3_4.8_ios_phone_202012052220_56 (@Kalimdor)_12787186548451577248",}
    return headers
#获取课程列表
def getcourse():
    global courselist
    url="http://mooc1-api.chaoxing.com/mycourse/backclazzdata?view=json&rss=1"
    headers=getheaders()
    if(headers==0):
        return 0
    res=requests.get(url,headers=headers)
    if('请重新登录' in res.text):
        print("Cookie已过期")
    else:
        d=json.loads(res.text)
        courselist=d['channelList']
        print("课程列表加载完成")
#普通签到
def sign1(aid,uid,name):
    name=urllib.parse.quote(name)
    url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId="+aid+"&uid="+uid+"&clientip=&latitude=-1&longitude=-1&appType=15&fid=0&name="+name
    headers=getheaders()
    if(headers==0):
        return 0
    res=requests.get(url,headers=headers)
    if(res.text=="success"):
        return 1
    else:
        return 0
#照片签到/手势签到
def sign2(aid,uid,oid,name):
    t=get_time()
    print(t+" 发现照片签到/手势签到")
    name=urllib.parse.quote(name)
    url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax?activeId="+aid+"&uid="+uid+"&clientip=&useragent=&latitude=-1&longitude=-1&appType=15&fid=0&objectId="+oid+"&name="+name
    headers=getheaders()
    if(headers==0):
        return 0
    res=requests.get(url,headers=headers)
    if(res.text=="success"):
        return 1
    else:
        return 0
#定位签到
def sign3(aid,uid,lat,long,name,address):
    t=get_time()
    print(t+" 发现定位签到")
    name=urllib.parse.quote(name)
    address=urllib.parse.quote(address)
    url="https://mobilelearn.chaoxing.com/pptSign/stuSignajax?name="+name+"&address="+address+"&activeId="+aid+"&uid="+uid+"&clientip=&latitude="+lat+"&longitude="+long+"&fid=0&appType=15&ifTiJiao=1"
    headers=getheaders()
    if(headers==0):
        return 0
    res=requests.get(url,headers=headers)
    if(res.text=="success"):
        return 1
    else:
        return 0
#获取签到类型
def get_sign_type(aid):
    url="https://mobilelearn.chaoxing.com/newsign/signDetail?activePrimaryId="+aid+"&type=1&"
    headers:{
      "User-Agent": "Mozilla/5.0 (iPad; CPU OS 13_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 ChaoXingStudy/ChaoXingStudy_3_4.3.2_ios_phone_201911291130_27 (@Kalimdor)_11391565702936108810"
    }
    res=requests.get(url,verify=False)
    d=json.loads(res.text)
    if(d['otherId']==0):
        if(d['ifPhoto']==1):
            return 1
        else:
            return 2
    elif(d['otherId']==2):
        if(d['ifRefreshEwm']==1):
            return 3
        else:
            return 4
    elif(d['otherId']==3):
        return 6
    elif(d['otherId']==4):
        return 5
    else:
        return 0
#统一签到入口
def sign(course, aid, uid, name):
    #拍照签到 1 普通签到 2 定位签到 5 手势签到 6
    activeType=get_sign_type(aid)
    if(activeType==1):
        images=setting['sign']['img']
        #未配置图片
        if(len(images)==0):
            signres=sign2(aid,uid,"",name)
        else:
            nowimg=choices(images)[0]
            signres=sign2(aid,uid,nowimg,name)
    elif(activeType==2):
        signres=sign1(aid,uid,name)
    elif(activeType==5):
        signres=sign3(aid,uid,setting['sign']['lat'],setting['sign']['long'],name,setting['sign']['address'])
    elif(activeType==6):
        signres=sign2(aid,uid,"",name)
    else:
        return -1
    # TODO 发送邮件
    if (signres == 1):
        teacherName = str(course['content']['course']['data'][0]['teacherfactor'])
        courseName = str(course['content']['course']['data'][0]['name'])
        signTypeStr = signType[activeType]
        emailUtil.mail('<'+ courseName +'>'+ teacherName +'课程'+ signTypeStr +'成功!', signTypeStr + '成功!')
        print(get_time() + '<'+ courseName +'>'+ teacherName +'课程'+ signTypeStr +'成功!')
    return signres
#获取用户活动列表
def gettask(course, courseId,classId,uid,cpi,name,sign_common,sign_pic,sign_hand,sign_local):
    try:
        url="https://mobilelearn.chaoxing.com/ppt/activeAPI/taskactivelist?courseId="+courseId+"&classId="+classId+"&uid="+uid+"&cpi="+cpi
        headers=getheaders()
        if(headers==0):
            return 0
        res=requests.get(url,headers=headers)
        d=json.loads(res.text)
        if(d['result']==1):
            activeList=d['activeList']
            count=0
            for active in activeList:
                status=active['status']
                activeType=active['activeType']
                aid=str(active['id'])
                if(status!=1):
                    return 0
                if(activeType==1 and sign_pic==True):
                    sign(course, aid,uid,name)
                if(activeType==2 and sign_common==True):
                    sign(course, aid,uid,name)
                if(activeType==5 and sign_local==True):
                    sign(course, aid,uid,name)
                if(activeType==6 and sign_hand==True):
                    sign(course, aid,uid,name)
                count+=1
                if(count>=setting['other']['count']):
                    break
    except Exception as e:
        print(e)
#获取时间
def get_time():
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day= today.day
    hour= today.hour
    minute= today.minute
    second= today.second
    if(month<10):
        month="0"+str(month)
    if(day<10):
        day="0"+str(day)
    date="["+str(year)+"."+str(month)+"."+str(day)+" "+str(hour)+":"+str(minute)+":"+str(second)+"]"
    return date
#初始化Cookies
def init_cookies():
    try:
        with open('cookies.txt','r') as f:
            data=f.read()
            f.close()
            if(len(data)<100):
                return 0
            return data
    except Exception as e:
        return 0
#初始化uid
def init_uid():
    try:
        with open('uid.txt','r') as f:
            data=f.read()
            f.close()
            if(len(data)<5):
                return 0
            return data
    except Exception as e:
        return 0
#初始化img
def init_img():
    print('你没有看错，我不想写了，时间紧迫，完了再更新图片上传')
#保存Cookies文件
def save_cookies(data,type):
    if(type==1):
        with open('cookies.txt','w') as f:
            f.write(data)
            f.close()
    else:
        with open('uid.txt','w') as f:
            f.write(str(data))
            f.close()
#初始化函数
def init():
    global mycookie,myuid
    if(setting['account']=="" or setting['password']==""):
        print("未进行账号配置")
        return 0
    cookies=init_cookies()
    uid=init_uid()
    if(cookies==0 or uid==0):
        res=login(setting['account'],setting['password'])
        if(res==0):
            print("登录失败，请检查账号密码")
        else:
            save_cookies(mycookie,1)
            getcourse()
    else:
        mycookie=cookies
        myuid=uid
        getcourse()
    return 1
#检测函数
def check():
    for course in courselist:
        # print(course)
        if('roletype' in course['content']):
            roletype=course['content']['roletype']
        else:
            continue
        if(roletype!=3):
            continue
        classId=str(course['content']['id'])
        courseId=str(course['content']['course']['data'][0]['id'])
        cpi=str(course['content']['cpi'])
        gettask(course, courseId,classId,myuid,cpi,setting['sign']['name'],setting['sign']['sign_common'],setting['sign']['sign_pic'],setting['sign']['sign_hand'],setting['sign']['sign_local'])

if __name__ == "__main__":
    res=init()
    if(res==1):
        print("初始化完成")
        while True:
            check()
            time.sleep(setting['other']['sleep'])