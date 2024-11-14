import json
import os
import re
import time
import sqlite3
import pika



def loadjson(jsonfile):
    with open(jsonfile) as json_file:
        data = json.load(json_file)
        return data


conf = loadjson(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json"))

user_pwd = pika.PlainCredentials(conf['rabbitmq']['user'], conf['rabbitmq']['pass'])
s_conn = pika.BlockingConnection(pika.ConnectionParameters(conf['rabbitmq']['host'], credentials=user_pwd, heartbeat=0))
chan = s_conn.channel()
chan.queue_declare(queue=conf['rabbitmq']['queuename'], durable=True)


def callback(ch, method, properties, body):
    data = json.loads(body.decode('UTF-8'))
    # 更新数据库的start_time字段
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("UPDATE videos SET start_time=?,state=? WHERE video_id=? AND date=? AND secret_key=?",
              (int(time.time()),"progress", data['id'], data['date'], data['secret']))
    conn.commit()
    conn.close()
    
    # 将视频文件添加到ipfs
    video_path = os.path.join(conf["local-storage"], data['date'],data['id'],  "video.mp4")
    result = os.popen(f"ipfs add -s size-1048576 --nocopy --cid-version 1 {video_path}").read()
    video_hash = re.search(r'added\s+(\w+)', result).group(1)
    result = os.popen(f"ipfs files cp -p  /ipfs/{video_hash} /{data['date']}/{data['id']}/video.mp4").read()

    # 将视封面件添加到ipfs
    cover_path = os.path.join(conf["local-storage"], data['date'],data['id'],  "cover.jpg")
    result = os.popen(f"ipfs add -s size-1048576 --nocopy --cid-version 1 {cover_path}").read()
    cover_hash = re.search(r'added\s+(\w+)', result).group(1)
    result = os.popen(f"ipfs files cp -p  /ipfs/{cover_hash} /{data['date']}/{data['id']}/cover.jpg").read()

    # 获取ffmpeg信息
    v_info = json.loads(os.popen(f"cd /{conf["local-storage"]}/{data['date']}/{data['id']};ffprobe -v quiet -print_format json -show_format -show_streams video.mp4").read())
    # 查询数据
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT * FROM videos WHERE video_id=? AND date=? AND secret_key=?", (data['id'], data['date'], data['secret']))
    result = c.fetchone()
    conn.close()

    json_data = {
        'title': result[5],
        'describe': result[6],
        'cover': "/ipfs/%s" % cover_hash,
        'files': [{
            'title': result[5],
            'size': int(v_info['format']['size']),
            'duration': int(float(v_info['format']['duration'])),
            'url': "/ipfs/%s" % video_hash,
            'type': "mp4",
            'mediainfo': v_info
        }]
    }
    # 保存json文件
    json_file = os.path.join(conf["local-storage"], data['date'],data['id'], 'files.json')
    file = open(json_file, 'w')
    json.dump(json_data, file, ensure_ascii=False)
    file.close()
    
    result = os.popen(f"ipfs add -s size-1048576 --nocopy --cid-version 1 {json_file}").read()
    json_hash = re.search(r'added\s+(\w+)', result).group(1)



    # 更新数据库的json_hash字段
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("UPDATE videos SET json_hash=?,end_time=?,state=? WHERE video_id=? AND date=? AND secret_key=?",
              ("/ipfs/%s" % json_hash, int(time.time()), "ready", data['id'], data['date'], data['secret']))
    conn.commit()
    conn.close()
    # 发送确认消息
    ch.basic_ack(delivery_tag=method.delivery_tag)


chan.basic_qos(prefetch_count=1)
chan.basic_consume(queue=conf['rabbitmq']['queuename'], on_message_callback=callback, auto_ack=False)
chan.start_consuming()
