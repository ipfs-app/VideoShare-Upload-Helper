import json
import os
import sqlite3
from fastapi import FastAPI, UploadFile, File, Form
import random
import pika

app = FastAPI()



def loadjson(jsonfile):
    with open(jsonfile) as json_file:
        data = json.load(json_file)
        return data

conf = loadjson(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))
user_pwd = pika.PlainCredentials(conf['rabbitmq']['user'], conf['rabbitmq']['pass'])
s_conn = pika.BlockingConnection(pika.ConnectionParameters(conf['rabbitmq']['host'], credentials=user_pwd, heartbeat=0))
chan = s_conn.channel()
chan.queue_declare(queue=conf['rabbitmq']['queuename'], durable=True)

def init_db():
    conn = sqlite3.connect(conf['database'])  # 连接到数据库，如果数据库不存在则会创建
    c = conn.cursor()  # 创建一个游标对象
    # 创建一个表
    c.execute('''CREATE TABLE IF NOT EXISTS videos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  video_id TEXT NOT NULL,
                  secret_key TEXT NOT NULL,
                  state TEXT NULL,
                  title TEXT NULL,
                  describe TEXT NULL,
                  json_hash TEXT NULL,
                  start_time INTEGER NULL,
                  end_time INTEGER NULL
                  )''')
    conn.commit()  # 提交事务
    conn.close()  # 关闭连接

def random_id(length):
    return ''.join(random.choice(conf['video-key-range']) for _ in range(length))

# 访问路径/index 函数
@app.get("/latest")
def latest():
    conn = sqlite3.connect(conf['database'])
    c = conn.cursor()
    # 最近的100条视频，过滤id，hash，title，封面
    c.execute("SELECT date, title, json_hash FROM videos WHERE state = 'ready' ORDER BY id DESC LIMIT 100")
    result = c.fetchall()
    conn.close()
    result = [{"date": i[0], "title": i[1], "json_hash": i[2]} for i in result]
    return {"data": result, "player": conf['player']}


# 访问路径/create_video 函数
@app.get("/create_video")
def create_video():
    import datetime
    now = datetime.datetime.now()
    now = now.strftime("%Y%m%d")
    conn = sqlite3.connect(conf['database'])
    flag = True
    while flag:
        video_id = random_id(4)
        c = conn.cursor()
        c.execute("SELECT * FROM videos WHERE video_id=? AND date=?", (video_id, now))
        result = c.fetchone()
        if not result:
            flag = False
    # 生成随机字符串包含大小写符号
    secret_key = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))
    c.execute("INSERT INTO videos (video_id, date, secret_key,state) VALUES (?,?,?,?)", (video_id, now, secret_key,"notReady"))
    conn.commit()
    conn.close()

    return {"date": now, "id": video_id, "secret": secret_key}

# 访问路径/get_video 函数
@app.get("/get_video")
def get_video(date: str, id: str, secret: str):
    conn = sqlite3.connect(conf['database'])
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE video_id=? AND date=? AND secret_key=?", (id, date, secret))
    result = c.fetchone()
    conn.close()
    if not result:
        return {"error": "video not found"}
    state = result[4]
    if state == "notReady":
        return {"data": {"title": result[5], "describe": result[6], "state":"notReady"}}
    elif state == "progress":
        return {"data": {"startTime": result[8], "state":"progress"}}
    elif state == "ready":
        return {"data": {"json_hash": result[7],"player": conf['player'], "state":"ready"}}
    else:
        return {"error": "video not found"}

# 访问路径/save_video 
@app.post("/save_video")
def file_upload(video: UploadFile = File(...), cover: UploadFile = File(...), id: str = Form(...),date: str = Form(...),secret: str = Form(...),title: str = Form(...),describe: str = Form(...)):
    conn = sqlite3.connect(conf['database'])
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE video_id=? AND date=? AND secret_key=?", (id, date, secret))
    result = c.fetchone()
    conn.close()
    if not result:
        return {"error": "video not found"}

    if not os.path.exists(os.path.join(conf["local-storage"],date,id)):
        os.makedirs(os.path.join(conf["local-storage"],date,id))
    # 保存文件
    with open(os.path.join(conf["local-storage"],date,id,"video.mp4"), 'wb') as f:
        for i in iter(lambda: video.file.read(1024 * 1024 * 10), b''):
            f.write(i)
    f.close()
    with open(os.path.join(conf["local-storage"],date,id,"cover.jpg"), 'wb') as f:
        for i in iter(lambda: cover.file.read(1024 * 1024 * 10), b''):
            f.write(i)
    f.close()
    # 更新数据库中的其他字段

    conn = sqlite3.connect(conf['database'])
    c = conn.cursor()
    c.execute("UPDATE videos SET title=?, describe=? WHERE video_id=? AND date=? AND secret_key=?",
              (title, describe, id, date, secret))
    conn.commit()
    conn.close()
    
    # 向mq发送消息
    message = {"id": id, "date": date, "secret": secret}
    chan.basic_publish(exchange='', routing_key=conf['rabbitmq']['queuename'], body=json.dumps(message),
                       properties=pika.BasicProperties(delivery_mode=2))

    return {"message": "upload seccess"}

if __name__ == '__main__':
    import uvicorn

    # 如果本地数据库文件不存在则运行init_db
    if not os.path.exists(conf['database']):
        init_db()

    runConf = conf['service']
    uvicorn.run(app=app,
                host=runConf['host'],
                port=runConf['port'],
                workers=runConf['workers'])
