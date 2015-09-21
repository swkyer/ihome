#!/usr/bin/python
# -*- coding: utf8 -*-
#encoding=utf-8

import os, time
import wave
import urllib, urllib2, pycurl
import base64, uuid
import json
import jieba, jieba.analyse


## get access token by api key & secret key

PROCESSING = 0
EXIT = 0
EXTSTR = u'�˳���'

def get_token():
    apiKey = "lGn7jCPtUChUvvsj2iEcLsYq"
    secretKey = "e9fedf7c4f715ae8ebbddabd90127421"

    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;

    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    return json.loads(json_data)['access_token']

def dump_res(buf):
    global PROCESSING, EXIT, EXTSTR
    print buf
    err = json.loads(buf)['err_no']
    print 'err_no: %d' % err
    if err != 0:
        PROCESSING = 2
    else:
        result = json.loads(buf)['result']
        print 'result : %s' % (result[0])
        if result[0] == EXTSTR:
            EXIT = 1
        PROCESSING = 0
        seg_list = jieba.cut(result[0])
        print(",".join(seg_list))
        for x, w in jieba.analyse.extract_tags(result[0], withWeight=True):
            print('%s %s' % (x, w))

## post audio to server
def use_cloud(token, audio_p):
    with open(audio_p, 'rb') as f:
        speech_data = f.read();
    #audio_data = base64.b64encode(speech_data).decode('utf-8')
    audio_data = speech_data
    f_len = len(speech_data)
    print 'file lenght %s' % f_len

    cuid = uuid.UUID(int=uuid.getnode()).hex[-12:]
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    http_header = [
        'Content-Type: audio/wav; rate=8000',
        'Content-Length: %d' % f_len
    ]

    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(srv_url)) #curl doesn't support unicode
    #c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.HTTPHEADER, http_header)   #must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, audio_data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    c.perform() #pycurl.perform() has no return val

## acrecord audio
def record_audio(autio_path):
    cmd = 'arecord -D plughw:1,0 -d 2 -f S16_LE ' + autio_path;
    print cmd
    os.system(cmd)
    

IDX = 0
if __name__ == "__main__":
    global PROCESSING, EXIT,IDX
    token = get_token()
    print token
    audio_p = '/tmp/audio.wav'
    while IDX < 100:
        IDX = IDX + 1
        record_audio(audio_p)
        PROCESSING = 1
        use_cloud(token, audio_p)
        while PROCESSING==1:
            #delay for a while
            time.sleep(0.1)
        if EXIT == 1:
            print '@@@@@@@@@@'
            break

