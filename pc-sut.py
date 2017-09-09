#coding:utf-8

import sys
import urllib
import cookielib
import urllib2
import re
import json
#import image
#import cStringIO
#from PIL import Image
#import MySQLdb

reload(sys)
sys.setdefaultencoding("utf8")

loginurl='http://jwc.sut.edu.cn/ACTIONLOGON.APPPROCESS?mode=4'

class Sutjwcxx(object):

    def __init__(self, username, password):
        self.error = []
        self.allclass = {}
        self.allstu = []
        self.allmes = {}
        self.name = username
        self.password = password
        self.yzmurl='http://jwc.sut.edu.cn/ACTIONVALIDATERANDOMPICTURE.APPPROCESS'
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
    def login (self):
        #img = cStringIO.StringIO(urllib2.urlopen(self.yzmurl).read())
        picture = self.opener.open(self.yzmurl).read()
        local = open('f:/test/image.jpg', 'wb')
        local.write(picture)
        local.close()
        #image = Image.open(img)
        #image.show()
        yzm = raw_input('输入验证码： ')
        loginmessage=urllib.urlencode({
            'WebUserNO':self.name,
            'Password':self.password,
            'Agnomen':yzm,
            'submit.x': '30',
            'submit.y': '20'
        })
        headers={
            'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
            'Accept - Language':'zh - CN, zh;q = 0.8',
            'Connection':'keep - alive',
            'Content-Type':'text/html;charset=GBK',
            'User - Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        }
        req = urllib2.Request(loginurl, loginmessage)
        response = self.opener.open(req)
        page = response.read().decode("GBK")
        #print page
        if page.find(u"错误的用户名或者密码<br>") > 0:
            print "Error username or password."
            return
        if page.find(u"请输入正确的附加码<br>") > 0:
            print "Error Agnomen."
            return
        print 'Login Sucess!'

    def getClass(self):
        url = 'http://jwc.sut.edu.cn/ACTIONQUERYCLASSSTUDENT.APPPROCESS'
        #prams=urllib.urlencode({
        #    'DeptNO':'',
        #    'MajorNO':'',
        #    'ComeYear':'2017',
        #    'ClassNO':''
        #})
        response = self.opener.open(url)
        page = response.read().decode("GBK")
        #print page
        reg = '([0-9]{7})\[(.+)\]'
        com = re.compile(reg)
        find = re.findall(com, page)
        for each in find:
            classid, classname = each[0], each[1]
            self.allclass[str(classid)] = str(classname)
        #f=open('f:/test/sm.txt','w')
        #f.write(self.allclass[str(classid)])
        #f.close()
        #print self.allclass
    def getStudent(self):
        url='http://jwc.sut.edu.cn/ACTIONQUERYCLASSCET.APPPROCESS?mode=2&query=1'
        reg = '<td align="center" height="24" width="30" >([0-9L]{8,})</td>'
        com = re.compile(reg)
        for each in self.allclass:
            prams=urllib.urlencode({
                'DeptNO':'',
                'MajorNO':'',
                'ComeYear':'',
                'ClassNO':int(each),
            })
            req = urllib2.Request(url, prams)
            page = self.opener.open(req).read()
            find = re.findall(com, page)
            self.allstu += find
    def getxx(self):
        url='http://jwc.sut.edu.cn/ACTIONQUERYSTUDENTBYSTUDENTNO.APPPROCESS?mode=2'
        reg_id = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([0-9]{9}|[0-9]{9}L{0,})</td>'
        reg_year = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([0-9]{4})</td>'
        reg_name_nation = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5]{2,})</td>'
        reg_sex = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">(男|女)</td>'
        reg_major = u'<td width="28%" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5()]{2,})</td>'
        reg_class = u'<td height="31" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5()]{2,}[0-9]{2,}班)</td>'
        reg_sid = u'<td height="33" colspan="2" align="left" valign="middle" nowrap class="color-row">([0-9xX]{18})</td>'
        com_id = re.compile(reg_id)
        com_year = re.compile(reg_year)
        com_sex = re.compile(reg_sex)
        com_name_nation = re.compile(reg_name_nation)
        com_major = re.compile(reg_major)
        com_class = re.compile(reg_class)
        com_sid = re.compile(reg_sid)
        for index, each in enumerate(self.allstu):
            print "Start [" + str(index)  +  "] " + str(each),
            params = urllib.urlencode({ 'ByStudentNO' : str(each) })
            tempinfo = {}
            try:
                tempinfo['p'] = urllib2.urlopen('http://jwc.sut.edu.cn/ACTIONQUERYSTUDENTPIC.APPPROCESS?ByStudentNO=' + str(each)).read()
                response = self.opener.open(url,params)
                page = response.read().decode("GBK")
                tempinfo['id'] = re.findall(com_id, page)[0]
                tempinfo['year'] = re.findall(com_year, page)[0]
                tempinfo['sex'] = re.findall(com_sex, page)[0]
                tempinfo['name'], tempinfo['nation'] = re.findall(com_name_nation, page)
                tempinfo['major'] = re.findall(com_major, page)[1]
                tempinfo['class'] = re.findall(com_class, page)[0]
                tempinfo['sid'] = re.findall(com_sid, page)[0]
                self.allmes[each] = tempinfo
                print 'success.'
            except Exception, e:
                print e
                self.error.append(each)
                print 'fail.'
        f = open('f:/test/sm.txt', 'w')
        f.write(str(self.allmes))
        f.close()
        # def savesql(self, localhost, name, passwd, data, table):
        # db = MySQLdb.connect(localhost, name, passwd, data, charset="utf8")
        # sql = u"insert into " + str(table) + u"(stu_id, stu_name, stu_sex, stu_year, stu_nation, stu_city, stu_sid, stu_school, stu_major) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')"
        # cursor = db.cursor()
        # for each in self.allinfo:
        #   cursor.execute((sql % each['id'], each['name'],  each['sex'],  each['year'],  each['nation'],  each['city'],  each['sid'],  each['major'],  each['class']).encode("UTF-8"))
        # db.close()



if __name__ == '__main__':
    username = '*******'
    password = '*******'
    userlogin = Sutjwcxx(username, password)
    userlogin.login()
    userlogin.getClass()
    userlogin.getStudent()
    userlogin.getxx()