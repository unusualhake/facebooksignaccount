#coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import multiprocessing
from multiprocessing import Pool
import sys,os
import time
import requests
from xvfbwrapper import Xvfb
import threading
from colour_print import *
reload(sys)
sys.setdefaultencoding( "utf-8" )
##### global define####
driver_mail = None
driver1_sign = None
usr_agent_list=None
proxy_list=None
static_proxy_list = None
######################

xvfb = Xvfb(width=1280,height=720)
xvfb.start()
from random import Random
def get_passwd(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str
def get_name():
	str = ''
	chars = ["wang","gao","qian","zhao","li","zhou","wu","liu"]
	names = ["nan","dong","xi","bei","shang","xia","zuo","you","jin","mu",'shui',"huo","tu"]
	length = len(chars) - 1
	random = Random()
	str = chars[random.randint(0, length)]
	name = names[random.randint(0, length)]
	return str,name

def save_page(name,driver):
	f = open(name,"w")
	f.write(driver.page_source)
	f.close()
def get_mail():
	url = "https://10minutemail.net/"
	try:
		driver_mail.get(url)
		time.sleep(0.5)
		element = driver_mail.find_element_by_xpath('//*[@class="mailtext"]')
		return  element.get_attribute("value")
	except:
		print "error"
def get_code():
	clicknum = 0
	print "try get safe code..."
	while "registration@facebookmail.com" not in driver_mail.page_source:
		try:
			driver_mail.find_element_by_link_text("Refresh this page.").click()
		except:
			driver_mail.refresh()
		time.sleep(3)
		print "try %s S..."%str(clicknum)
		save_page("code.html",driver_mail)
		clicknum = clicknum + 1
		if clicknum>5:
			break
	save_page("mail.html",driver_mail)
	code_txt = driver_mail.find_element_by_xpath('//*[@id="mailbox-table"]//tr[3]/td[2]').text
	code =  code_txt.split(" ")[0]
	print "get code : " +code
	return code 
def init(num):
	global driver1_sign
	global driver_mail
	global usr_agent_list
        global proxy_list
	global static_proxy_list
	dcap = dict(DesiredCapabilities.PHANTOMJS)
#	print "get usranget is : "+ usr_agent_list[num]
	print "get proxy    is : "+ proxy_list[num]
	dcap["phantomjs.page.settings.userAgent"] = usr_agent_list[num]
	service_args = ['--proxy=%s'%static_proxy_list[num]]
	service_arg = ['--proxy=%s'%static_proxy_list[num]]
	service_arg.append("--proxy-auth=smt:smt2017")
	service_args.append("--proxy-auth=smt:smt2017")
	service_args.append('--ignore-ssl-errors=true') ##忽略https错误
	driver1_sign = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_args)
	driver1_sign.set_page_load_timeout(40)
	driver_mail = webdriver.PhantomJS(desired_capabilities=dcap,service_args=service_arg)
	driver_mail.set_page_load_timeout(40)
def read_file(name,flag):
	result = list()
        f = open(name,'r')
        for line in open(name):
                line = f.readline().replace("\r\n","").replace("\n","")
                result.append(line)
        f.close()
	if flag:
		from random import Random
		random = Random()
		random.shuffle(result)
        return result
def save_acc(mail,passwd):
	
	print UseStyle("save the account: "+mail+"  "+passwd,   fore = 'purple')
	r = open("fb_acc.txt","a")
	r.write(mail+"+"+passwd+"\r\n")
	r.close()

def load_file(i):
	global usr_agent_list
	global proxy_list
	global static_proxy_list
	usr_agent_list = read_file("usragent.txt",True)
	proxy_list     = read_file("proxy.txt",True)
	static_proxy_list = read_file("proxy.txt",True)
def main(i,num):
	load_file(i)
	init(num)
	url = "https://www.facebook.com"
	print "get fb homepage..."
	try:
		driver1_sign.get(url)
	except:
		print "get fbhome timeout..."
	time.sleep(1)
	if  "firstname" not in driver1_sign.page_source:
		print "fb home is null,return.."
		return
	print "get mail..."
	mail = get_mail()
	print "get mail : "+mail
	name1,name2 = get_name()
	print "get name :"+name1+"  "+name2
	print "send name ..."
	driver1_sign.find_element_by_xpath('//*[@name="firstname"]').send_keys(name1)
	driver1_sign.find_element_by_xpath('//*[@name="lastname"]').send_keys(name2)
	driver1_sign.find_element_by_xpath('//*[@name="reg_email__"]').send_keys(mail)
	time.sleep(1)
	driver1_sign.find_element_by_xpath('//*[@name="reg_email_confirmation__"]').send_keys(mail)
	passwd = get_passwd()
	print "passwd is : "+passwd
	driver1_sign.find_element_by_xpath('//*[@name="reg_passwd__"]').send_keys(passwd)
	try:
		driver1_sign.find_element_by_xpath('//*[@name="birthday_year"]').click()
		time.sleep(2)
		driver1_sign.find_element_by_xpath('//*[@value="1992"]').click()
		time.sleep(1)
	except:
		print "click fail"
	print "select sex..."
	driver1_sign.find_element_by_xpath('//*[@name="sex"][1]').click()
	time.sleep(1)
	driver1_sign.find_element_by_xpath('//*[@name="websubmit"]').click()
	time.sleep(16.1)
	if len(driver1_sign.page_source) <200000:
		print "length is too small,wait..."                   
		time.sleep(2.1)
	if "code_in_cliff" not in driver1_sign.page_source :
		printf("need check,sign fail... ")
		save_page("sign_fail.html",driver1_sign)
		return
	save_page("sign.html",driver1_sign)
	code = get_code()
	print "submit the code..."
	try:
		driver1_sign.find_element_by_xpath('//*[@id="code_in_cliff"]').send_keys(code)
	except:
		driver1_sign.find_element_by_xpath('//*[@class="inputtext _55r1"]').send_keys(code)
	time.sleep(1.2)
	print "click confirm button..."
	try:
		driver1_sign.find_element_by_xpath('//*[@name="confirm"]').click()
	except:
		print "click confirm button timeout..."
		time.sleep(3.1)
		save_page("signed.html",driver1_sign)
	time.sleep(2.1)
	save_acc(mail,passwd)
	print "sign sucess..."
	print "over..."
def printf(str):
	print UseStyle(str,fore = 'red')
def print_green(str):
         print UseStyle(str,fore = 'green')
def print_all(str,colour):
	print UseStyle(str,fore = colour)
def get_proxy(i):
	print_all("get proxy...","green")
	r=open("list%s.txt"%str(i),"w")
        r.close()
        data = requests.get("http://www.httpdaili.cn:8082/private/query?dingdanhao=ips92486658220170914hkljh&num=500&selectall=true")
	r = open("list%s.txt"%str(i),"a")
        r.write(data.content)
	r.close()
def start(i):
	num = 0
#	print "start work..."
	#get_proxy(i)
	while(1):
		print_green("%d  :try %s s to get fb"%(i,str(num)))
		if num >40:
			printf("num over 50,retry again")
			#num = 0
			return
	#		get_proxy(i)
		try:
			main(i,num)
		except Exception,e:
			print e
		finally:
			num = num + 1
			try:
				driver1_sign.quit()
				driver_mail.quit()
			except:
				print "close driver fail..."
if __name__ == "__main__":
	threads = []
	p = Pool()
	print UseStyle("start work...",   fore = 'green')
	for i in range(int(sys.argv[1])):
		multiprocessing.Process(target = start, args = (i,)).start()
		time.sleep(2.1)
		#p.apply_async(start, args=(i,))
	#p.close()
    	#p.join()
	xvfb.stop()
