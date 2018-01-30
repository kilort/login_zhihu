import requests
import re
import time
import http.cookiejar as cookielib

agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36'

headers = {'Host': 'www.zhihu.com',
           'Origin': 'https://www.zhihu.com',
           'Referer': 'https://www.zhihu.com',
           'User-Agent': agent
           }
sessions = requests.session()
#创建文件保存cookie信息并且应用他
sessions.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
try :
    sessions.cookies.load(ignore_discard =True)
except:
    print('cookies加载失败')


#提取知乎防止跨站攻击的防护码_xsrf
def get_xsrf():
    url = 'https://www.zhihu.com'
    req =requests.get(url,headers=headers)
    req.encoding='utf-8'
    try:
        pat = '<input type="hidden" name="_xsrf" value="(.*?)"/>'
        xsrf=re.compile(pat).findall(req.text)[0]
        return xsrf
    except:
        print('xsrf抓取失败，原因是',Exception)

#提取相应的验证码
def get_captcha():
    #这种创建验证码的看不懂,我理解为验证码的id是根据访问所需要加载的时间来随机生成的
    t = str(int(time.time()*1000))
    captcha_url = 'https://www.zhihu.com/captcha.gif?r=' + t + '&type=login'
    r = sessions.get(captcha_url,headers=headers)
    with open('captcha.jpg','wb') as f :
        try:
            f.write(r.content)
            f.close()
            print('请到文件根目录下查看captcha.jpg输入验证码')
            captcha =input('验证码：')
        except:
            print('验证码抓取失败，原因是',Exception)
            captcha=' '
        return captcha

def is_login():
    url = "https://www.zhihu.com/settings/profile"
    login = sessions.get(url, headers=headers, allow_redirects=False)
    if login.status_code == 200:
        title = re.compile('.*<title>(.*?)</title>.*').findall(login.text)
        print(title)
        return True
    else:
        return False


def login(password,username):
    _xsrf =get_xsrf()
    headers['X-Xsrftoken'] =_xsrf
    headers["X-Requested-With"] ="XMLHttpRequest"
    #判断是手机号码登录或者是email登录
    if '@' in username:
        email_login_url ='https://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': _xsrf,
            'password':password,
            'email':username,
        }
        login_page = sessions.post(url=email_login_url, data=postdata, headers=headers)
        #通过j查看login_page的json、文件来确认这次爬取是否需要验证码
        login_json = login_page.json()
        print(login_json)
        #r =1则表示需要填写验证码
        if login_json['r'] == 1:
            postdata['captcha'] = get_captcha()
            login_page = sessions.post(url=email_login_url, data=postdata, headers=headers)
            login_json = login_page.json()
            print(login_json['msg'])
        sessions.cookies.save()
    else:
        phone_login_url = "https://www.zhihu.com/login/phone_num"
        postdata = {
            '_xsrf':_xsrf,
            'password':password,
            'phone_num':username,
        }
        login_page = sessions.post(url=phone_login_url,data=postdata,headers=headers)
        login_json= login_page.json()
        print(login_json)
        if login_json['r']== 1:
            postdata['captcha']=get_captcha()
            login_page = sessions.post(url=phone_login_url, data=postdata, headers=headers)
            login_json = login_page.json()
            print(login_json['msg'])
        sessions.cookies.save()

'''
def is_login():
    url ='https://www.zhihu.com'
    response = sessions.get(url=url,headers=headers)
    if response.status_code == 200:
        print('登录成功')
        #pattern =
        #title =re.compile(pattern,re.S).findall(response.text)[0]
        print(len(response.text))
    else :
        print('登录失败')
'''

def main():
    if is_login():
        print('您已登录')
    else:
        username = input('username:')
        password = input('password:')
        login(password,username)


main()