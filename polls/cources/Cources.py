import threading

import requests
import execjs
import re
import json
import time
from polls.cources.models import *
from pony.orm import *

from bs4 import BeautifulSoup as bs

domin = 'http://zjxy.hnhhlearning.com'
homeUrl = 'http://zjxy.hnhhlearning.com/Home'
learningUrl = 'http://zjxy.hnhhlearning.com/Study/Learning?'
learningMediaLiUrl = 'http://zjxy.hnhhlearning.com/Study/Learning/MediaLi?'
testHistory = 'http://zjxy.hnhhlearning.com/Study/ExamList/TestHistory'
testIndex = 'http://zjxy.hnhhlearning.com/Study/ExamList/TestIndex'
formalIndex = 'http://zjxy.hnhhlearning.com/Study/ExamList/Index'

passExam = 'http://zjxy.hnhhlearning.com/Study/Exam?epaId='
sumbQuestion = 'http://zjxy.hnhhlearning.com/Study/Exam/SubmitExam'
sumbExam = 'http://zjxy.hnhhlearning.com/Study/Exam?epaId='

# formalPassExam =


s = requests.session()

# # 构造header头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Referer': 'http://zjpy.hnhhlearning.com/',
    'Cookie': 'ASP.NET_SessionId=ryu3fx4wg31f3vu20lpccxtc;hbjyUsersCookieszjxy.hnhhlearning.com=615|615|2f047a1d01464cb3ac2facd6eb01f3aa; IsLoginUsersCookies_zjxy.hnhhlearning.comzjxy.hnhhlearning.com=IsLogin'
}
s.headers = headers

# 登陆到home
homeData = s.get(homeUrl)
homeContent = bs(homeData.content, 'lxml')


# 获取子课程
def getChildCources(sscId):
    courceData = s.get(learningUrl + 'sscId=' + sscId)
    courceContent = bs(courceData.content, 'lxml')

    child_cources_list = []
    for idx, tr in enumerate(courceContent.select(".xktable tbody tr")):
        tds = tr.select('td')
        percent = tds[2].contents[1]['src']
        percent = percent[percent.find('id=') + 3:]
        url = tds[3].contents[1]['href']
        medId = url[url.find('medId=') + 6:]

        child_cources_list.append({
            '子课程名称': tds[0].contents[0],
            '学习进度': percent,
            'url': url,
            'medId': medId
        })
    return child_cources_list


# 获取主课程
def getMainCources(homeContent):
    cources_list = []
    for idx, tr in enumerate(homeContent.select(".homelinetable-dashed-bom tr")):
        if idx != 0:
            tds = tr.select('td')
            percent = tds[2].contents[1]['src']
            percent = percent[percent.find('id=') + 3:]
            url = tds[3].contents[1]['href']
            sscId = url[url.find('sscId=') + 6:]

            cources_list.append({
                '课程名称': tds[0].contents[0],
                '学时': tds[1].contents[0],
                '学习进度': percent,
                'url': url,
                'sscId': sscId,
                '全部课程': getChildCources(sscId)
            })
    return cources_list


# 提交进度
def pushPercent(sscId, medId):
    courceData = s.get(learningMediaLiUrl + 'sscId=' + sscId + '&medId=' + medId)
    courceContent = bs(courceData.content, 'lxml')

    # 获取pushPercent参数
    m = re.search('var requestData =(.|\n)*?}', courceContent.text)
    data = m.group()
    data = data.replace("RequestType.Offen", "1")
    jsStr = 'function getObj(){' + data + ';return requestData;}'
    ctx = execjs.compile(jsStr)
    pushParams = ctx.call("getObj")
    pushParams['CurrentLength'] = 30

    learnMediaTime = re.search('var learnMediaTime.*', courceContent.text)[0]
    learnMediaTime = re.search('[0-9]+', learnMediaTime)[0]
    pushParams['CurrentTimespan'] = learnMediaTime

    # 获取pushPercent url
    m = re.search('var timingUrl = ".*?"', courceContent.text)
    data = m.group()
    pushUrl = re.search('"(\S*)"', data)[1]

    # 拼接参数
    # type == 2 代表开始
    pushParams['Type'] = 2
    courceData = s.get(pushUrl + 'sscId=' + sscId + '&medId=' + medId, params=pushParams)
    testStr = courceData.text
    result = json.loads(re.search('\((\S*)\)', testStr)[1]);
    if result['Value'] == None:
        print(threading.current_thread().getName() + '异常' + result['Error'] + '\n' + courceData.request.url)
    print(threading.current_thread().getName() + '完成' + str(result['Value']['Process']))

    # type == 1 代表持续,类似于心跳...网站这里必须是先开始,然后再发心跳,才能增加进度.所以先要设置成2请求一次,再设置成1持续请求
    pushParams['Type'] = 2
    while (result['Value']['Process'] < 100):
        pushParams['CurrentTimespan'] = str(int(pushParams['CurrentTimespan']) + 30)

        time.sleep(pushParams['CurrentLength'])
        courceData = s.get(pushUrl + 'sscId=' + sscId + '&medId=' + medId, params=pushParams)
        testStr = courceData.text
        result = json.loads(re.search('\((\S*)\)', testStr)[1]);
        if result['Value'] == None:
            print(threading.current_thread().getName() + '异常' + result['Error'] + '\n' + courceData.request.url)
            return;
        print(threading.current_thread().getName() + '完成' + str(result['Value']['Process']))
        # requestData =


# 提交学习进度
def learn():
    cources_list = getMainCources(homeContent)
    for cource in cources_list:
        for childCource in cource['全部课程']:
            if int(childCource['学习进度']) == 100:
                print(childCource['子课程名称'] + ':已经学习过,不需要学习')
                continue
            print(childCource['子课程名称'] + ':开始学习')
            threading.Thread(None, target=pushPercent, name=childCource['子课程名称'],
                             args=(cource['sscId'], childCource['medId'])).start()
            # pushPercent(cource['sscId'], childCource['medId'])


# 从练习记录中获取考试答案,保存到数据库中
def getsAnswers():
    answersHomeData = s.get(testHistory, headers=headers)
    # answersHomeData = s.get(testHistory)
    answersHomeContent = bs(answersHomeData.content, 'lxml')
    for idx, tr in enumerate(answersHomeContent.select("#tabs-1 .listtable tbody tr")):
        saveAnswers(tr.select("td a")[0]['href'])


# 从练习记录中获取考试答案,保存到数据库中
@db_session
def saveAnswers(examViewUrl):
    answersHomeData = s.get(domin + examViewUrl)
    answersHomeContent = bs(answersHomeData.content, 'lxml')
    examName = str(re.search(r'\b\w*', answersHomeContent.select('.exampaperbox h2')[0].text)[0])
    examName = examName.strip()
    exam = select(p for p in Exam if p.name == examName)
    if (not exam.exists()):
        exam = Exam(name=examName, testFinish=False)
    else:
        exam = exam.first()
    for idx, tr in enumerate(answersHomeContent.select(".examchoose")):
        queStr = str(re.search(r'、.*', tr.select('table span')[0].text)[0])[1:]
        queStr = queStr.strip()
        que = select(p for p in Question if p.name == queStr)
        if (not que.exists()):
            que = Question(name=queStr, outId=tr.attrs['id'][len('Question_'):], exam=exam)
            tempStr = re.sub('\s*', '', tr.select('div')[0].text)
            ans = str(re.search('参考答案：.*\w', tempStr)[0])[len('参考答案：'):]
            for an in ans.split(","):
                an = an.strip()
                Answer(value=re.sub('[A-Z]+', '', an.strip()), outId=que.outId, question=que)
        commit()


# 通过练习的考试
def passTestExam(epaId):
    examData = s.get(passExam + epaId)
    examContent = bs(examData.content, 'lxml')
    postHeader = {

    }
    for idx, tr in enumerate(examContent.select(".examchoose")):
        submitAnswer(epaId, tr.attrs['id'][len('Question_'):], int(tr.attrs['questiontype']), tr)


@db_session
def submitAnswer(epaId, questionId, questionType, tr):
    pushParams = {
        'pagerId': epaId,
        'qusetionId': questionId,
        'ver': int(time.time()),
        'passage': '',
        'isSubmit': 'false'}
    ansQu = select(p for p in Answer if p.outId == questionId)
    if (not ansQu.exists()):
        return
    if questionType == 1:
        if (str(ansQu.first().value).find('正确') > -1):
            pushParams['passage'] = 'true'
        else:
            pushParams['passage'] = 'false'
    elif questionType == 2:
        for idx, trr in enumerate(tr.select("tr")):
            if (trr.text.find(ansQu.first().value) > -1):
                pushParams['passage'] = idx
                break;
    elif questionType == 3:
        ans = []
        for idx, trr in enumerate(tr.select("tr")):
            tempStr = False
            for an in ansQu:
                if (trr.text.find(an.value) > -1):
                    tempStr = True

            ans.append('true' if tempStr else 'false')
        pushParams['passage'] = '$$'.join(ans)
    subQuesData = s.post(sumbQuestion, params=pushParams)
    print(pushParams)
    print(subQuesData.text)


# 考试
def subExam(formalExam=False):
    answersHomeData = s.get(formalIndex if formalExam else testIndex)
    answersHomeContent = bs(answersHomeData.content, 'lxml')
    for idx, tr in enumerate(answersHomeContent.select("#tabs-1 .listtable tbody tr")):
        createPaperData = s.post(domin + tr.select("td a")[0]['href'] + "&type=Create")
        createPaperData = s.get(domin + tr.select("td a")[0]['href'])
        createPaperContent = bs(createPaperData.content, 'lxml')
        hrefStr = createPaperContent.select('.enterxz a')[0].attrs['href']
        epaId = hrefStr[hrefStr.index('=') + 1:]
        passTestExam(epaId)


# todo 暂时用别人的服务代替,后续自己架识别服务.
def getCaptcha(url):
    # 'rb'要加,编码问题
    # 从本地上传
    #  files = {'file':('pic.jpg',open('/user/xxxx.jpg','rb'),'image/jpeg')}
    # 直接读取验证码
    imageFile = s.get(url, stream=True)
    return imageFile.cookies.get('ValidateSessionName')

    # 发现这网站直接把验证码给返回了...
    # files = {'file': ('pic.jpg', imageFile.content, 'image/jpeg')}
    # r = requests.post('http://chongdata.com/ocr/upload_file.php', files=files)
    # while (True):
    #     time.sleep(2)
    #     captcha = requests.get('http://chongdata.com/ocr/' + re.search('url=\S*', r.text)[0][4:])
    #     if (captcha.text.find('识别结果') > -1):
    #         captcha = re.search('识别结果.*', bs(captcha.text, 'lxml').select('body')[0].text)[0]
    #         return int(re.search('[0-9]+', captcha)[0])


# 登陆
def login(passId, password):
    loginUrl = 'http://zjpx.hnhhlearning.com/Home/Login/DoHnzjLogin'
    code = getCaptcha(
        'http://zjpx.hnhhlearning.com/Public/Control/GetValidateCode?time=' + str(int(time.time())))
    account = {'LoginAccount': passId,
               'LoginPassword': password,
               'LoginValCode': code,
               'LoginType': '0',
               'HnzjLoginTab': '0',
               'X-Requested-With': 'XMLHttpRequest'
               }
    response = s.post(loginUrl, params=account)
    response = s.get('http://zjpx.hnhhlearning.com/Public/ShareSso/ToStudy')

    # json.dumps(session.cookies.get_dict()))  # 保存
    # session.cookies.update(json.loads(f.read()))  # 读取

    print('登陆成功' + response.text)


if __name__ == '__main__':
    login('X', '000000')

    # learn()
    # #获取答案
    # getsAnswers()
    # #正式考试
    subExam(True)

    print()
