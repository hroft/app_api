from flask import Flask, jsonify
from flaskext.mysql import MySQL
import requests
import re
import configparser

regex = r"\d{8}-\d{6}"
regex2 = r"\d{8}T\d{6}Z"
#собираем данные для работы из script.conf файла
conf = configparser.RawConfigParser()
conf.read('script.conf')
host = conf.get('db_autch', 'host')
user = conf.get('db_autch', 'user')
password = conf.get('db_autch', 'password')
db_name = conf.get('db_autch', 'db_name')

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = conf.get('db_autch', 'user')
app.config['MYSQL_DATABASE_PASSWORD'] = conf.get('db_autch', 'password')
app.config['MYSQL_DATABASE_DB'] = conf.get('db_autch', 'db_name')
app.config['MYSQL_DATABASE_HOST'] = conf.get('db_autch', 'host')

mysql.init_app(app)

def parse_data_start(data):
    data_start = data[0:4]+'-'+data[4:6]+'-'+data[6:8]+' '+data[9:11]+':'+data[11:13]+':'+data[13:15]
    # print('!!!!!'+data_start)
    return data_start

def calldate_replace(data):
    #2018-01-20T10:58:30+03:00
    dt = re.sub('T', ' ', data[0:-6])
    return dt

def split_data(datas):
    stt = datas.split(',')
    stt[5] = calldate_replace(stt[5])
    rpm = dict(zip([0,1,2,3,4,5,6,7,8],stt))
    return rpm

@app.route('/api/v1/list/asterisk/start=<date_start>')
def aget(date_start):
    try:
        if (re.match(regex, date_start)):
            ds = parse_data_start(date_start)
            cur = mysql.connect().cursor()
           #sql = '''select DATE_FORMAT(calldate,"%Y-%m-%d %H:%i:%s") as dacalldate , dcontext, dst, src, duration, path, translation from asteriskcdrdb.cdr where  DATE_FORMAT(calldate, "%Y%m%d-%H%i%s")  >{}'''.format(date_start)
            sql = 'select DATE_FORMAT(calldate,"%Y-%m-%d %H:%i:%s") as dacalldate, dcontext, dst, src, duration, path, translation from asteriskcdrdb.cdr where  calldate > "{}"'.format(ds)
            cur.execute(sql)
            r = [dict((cur.description[i][0], value)
                    for i, value in enumerate(row)) for row in cur.fetchall()]
            return jsonify({'list' : r})
        else:
            return 'не верный формат даты'
        
    except Exception as e:
        raise e
    

@app.route('/api/v1/list/megafon/start=<date_start>')
def mget(date_start):
    try:
        if (re.match(regex2, date_start)):
            url = ('https://stroy.megapbx.ru/sys/crm_api.wcgp?token=683444d0-285-4205-a7c2-3e74b7bf4213&cmd=history&start={}').format(date_start)
            r = requests.get(url)
            data = r.text.split('\r\n')
            m = []
            for datas in data:
                if not (datas == ''):
                    m.append(split_data(datas))
            jll = jsonify({'list':m})
            return jll
        else:
            return 'не верный формат даты'
    except Exception as e:
        raise e
    

@app.route('/')
def iget():
    index = '''

    <div>
    <hr />
     <h2>NOTE:</h2> 
     <p>получать данные с asterisk с даты data_start</p>
     <p>/api/v1/list/asterisk/start=date_start</p>
          <p>получать данные с megafon с даты data_start</p>
     <p>/api/v1/list/megafon/start=date_start</p>
     <p>формат даты 20180117-000000 год месяц число - часы минуты секунды</p>
    <hr />
    </div>
    '''
    return index

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)