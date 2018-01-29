from flask import Flask, jsonify
from flaskext.mysql import MySQL
import requests
import re

# regex = r"\d{8}-\d{6}"
regex = regex = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'flask_user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Paralaxx'
app.config['MYSQL_DATABASE_DB'] = 'asteriskcdrdb'
app.config['MYSQL_DATABASE_HOST'] = '192.168.1.63'

mysql.init_app(app)

def parse_data_start(data):
    data_start = data[0:4]+'-'+data[4:6]+'-'+data[6:8]+' '+data[9:11]+':'+data[11:13]+':'+data[13:15]
    print('!!!!!'+data_start)
    return data_start

def split_data(datas):
    stt = datas.split(',')
    rpm = dict(zip([0,1,2,3,4,5,6,7,8],stt))
    return rpm

@app.route('/api/v1/list/asterisk/start=<date_start>')
def aget(date_start):
    try:
        if (re.match(regex, date_start)):
            cur = mysql.connect().cursor()
            # sql = '''select DATE_FORMAT(calldate,"%Y%m%d-%H%i%s") as daclldate , dcontext, dst, src, duration, path, translation from asteriskcdrdb.cdr where  DATE_FORMAT(calldate, "%Y%m%d-%H%i%s")  >{}'''.format(date_start)
            sql = 'select calldate, dcontext, dst, src, duration, path, translation from asteriskcdrdb.cdr where  calldate >{}'.format(parse_data_start(date_start))
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
        if (re.match(regex, date_start)):
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