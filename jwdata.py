import requests
import re

userno = 2022211500
pwd = "Ww12345678"
login_url = "http://jwglweixin.bupt.edu.cn/bjyddx/login"
query_url = "http://jwglweixin.bupt.edu.cn/bjyddx/todayClassrooms?campusId=01"


def login():
    payload = {
        'userNo': userno,
        'pwd': pwd,

    }

    response = requests.post(login_url, data=payload)

    # 检查HTTP响应状态码
    if response.status_code == 200:
        try:
            # 尝试解析响应JSON数据
            response_data = response.json()

            global token
            token = response_data['data']['token']
            return token
        except requests.exceptions.JSONDecodeError:
            # 处理JSON解析错误
            print("Failed to decode JSON from response. Response content:", response.text)
    else:
        # 输出非200状态码的响应内容
        print("Login failed, HTTP status code:", response.status_code)
        print("Response content:", response.text)
        return None


def extract(classrooms, prefix):
    full_prefix = prefix + '-'
    parts = classrooms.split(',')

    match = []
    for part in parts:
        part = part.strip()
        if part.startswith(full_prefix):
            match.append(part)
    return match


def query(data):
    payload = {
        'userNo': userno,
        'pwd': pwd,
        'token': token,

    }
    response = requests.post(query_url, data=payload)

    # 检查HTTP响应状态码
    if response.status_code == 200:
        try:
            # 尝试解析响应JSON数据
            response_data = response.json()

            classtable = []
            for item in response_data['data']:
                classtable.append(item)

            queryFirst = []

            for item in classtable:
                if item.get('NODENAME') == data['NODENAME']:
                    queryFirst.append(item)
            print(queryFirst)
            matchString = queryFirst[0]['CLASSROOMS']
            print(matchString)

            result = extract(matchString, data['CLASSROOMS'])
            print(result)





        except requests.exceptions.JSONDecodeError:
            # 处理JSON解析错误
            print("Failed to decode JSON from response. Response content:", response.text)
    else:
        # 输出非200状态码的响应内容
        print("Login failed, HTTP status code:", response.status_code)
        print("Response content:", response.text)
        return None


def init():
    data = {
        # 时间段第几节课， 1 = 8-8.45
        'NODENAME': '1',
        # 哪个教学楼，1=教1，2=教2
        'CLASSROOMS': '2',
    }
    return data


if __name__ == '__main__':
    data = init()
    login()
    query(data)
