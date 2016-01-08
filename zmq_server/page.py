#coding:utf-8
from bottle import route,run,debug,request,redirect,response,error,static_file
import bottle,os
from cmath import log as mathclog
import time,sys,datetime,random,acc
from base import *
from life import *
from svgcandle import *
from mongo_log_handlers import MongoHandler
from settings import mongo_server
from qqmail import *
from log import *
import thread

def mathlog(a):return mathclog(a).real

def now():return datetime.datetime.now()

cache = {}
cache['pass'] = time.time()+3600*24*7

def logten():
    ip = request['REMOTE_ADDR']
    day= datetime.datetime.now().strftime("_%Y_%m_%d_%H")
    url = request.environ['PATH_INFO']+day
    if 'url' not in cache:
        cache['url'] = {}
    if ip+url not in cache['url']:
        cache['url'][ip+url]=0
        if len(cache['url'])>200:
            cache['url']={}
            logit('clear cache url')
        if 'Mozilla/4.0' in request.environ.get('HTTP_USER_AGENT','no agent'):
            pass
        else:
            logit('''url @ %s [ <a href="http://www.baidu.com/s?wd=%s&_=%.0f" target="_blank">%s</a> ] %.1f
                <span style="color:gray">%s</span>'''%(url,ip,time.time()/10,ip,cache['pass']-time.time(),request.environ.get('HTTP_USER_AGENT','no agent')))
    return True

@error(500)
def error500(error):
    try:
        logger.error(error.traceback)
    finally:
        return ''

@error(404)
def error404(error):
    logten()
    return ''

@route('/logs/')
def show_logs():
    logten()
    _list = MongoHandler().show()
    _dt = datetime.timedelta(hours=8)
    if _list:
        out = ''.join([ '<pre>%s >>> %s</pre>'%((_dt+one['timestamp'].as_datetime()).strftime("%Y-%m-%d %H:%M:%S"),one['message']) for one in _list])
        return '''<html><head><title>%s</title><META HTTP-EQUIV="REFRESH" CONTENT="10"></head><body>
                %s</body></html>'''%((_dt+_list[0]['timestamp'].as_datetime()).strftime("%H:%M:%S"),out)
    else:
        return '''<html><head><META HTTP-EQUIV="REFRESH" CONTENT="100"></head><body>
                <br/></body></html>'''

@route('/')
def index():
    logten()
    global cache
    _all = conn.database_names()
    _list = filter(lambda x:'_' in x and x[0]=='k',_all)
    out = []
    len = request.query.l or cache.get('len','100')
    cache['len'] = len
    for one in [10,50,100,200]:
        out.append('<a href="/?l=%d">%d</a>'%(one,one))
    out.append("<br/>")
    out.append("<br/>")
    for one in _list:
        out.append('<a href="/list/%s/" target="_blank">%s</a>'%(one,one))
    all = '&nbsp;'.join(out)
    return '''<html><head></head><body><br/>%s</body></html>'''%all

@route('/delete/:symbol/')
def del_symbol(symbol):
    conn.drop_database(symbol)
    return 'ok'

@route('/list/:symbol/')
def get_symbol(symbol):
    logten()
    len = request.query.l or cache.get('len','100')
    cache['len'] = len
    _k,_exchange,_symbol,_plus = symbol.split('_')
    b=Base(_exchange,_symbol,conn,allstate,plus=_plus)
    s=SVG('',[],'')
    _all = s.get_lines()
    _tf = b.get_timeframe()
    out = []
    out.append(_exchange)
    out.append(_symbol)
    out.append(_plus)
    out.append("<br/>")
    for one in _all:
        for tf in _tf:
            out.append('<a href="/image/%s/%s/%s/" target="_blank">%s[%s]</a>'%(symbol,one,tf,one,tf))
        out.append("<br/>")
    out.append("<br/>")
    out.append("<br/>")
    out.append("<br/>")
    out.append("<br/>")
    out.append("<br/>")
    out.append("<br/>")
    out.append(u'<a href="/delete/%s/" target="_blank">删除 %s !!!</a>'%(symbol,symbol))
    all = '&nbsp;'.join(out)
    return '''<html><head></head><body><br/>%s</body></html>'''%all

@route('/image/:symbol/:group/:tf/')
def get_image(symbol,group,tf):
    logten()
    len = request.query.l or cache.get('len','100')
    o = request.query.p or '0'
    cache['len'] = len
    _k,_exchange,_symbol,_plus = symbol.split('_')
    if _plus:
        b=Base(_exchange,_symbol,conn,allstate,plus=_plus)
    else:
        b=Base(_exchange,_symbol,conn,allstate)
    out = []
    out.append(_exchange)
    out.append(_symbol)
    out.append(_plus)
    out.append(group)
    out.append("<br/>")
    _svg = b.get_image(tf,len,group,offset=int(o))
    _page = ''.join(['''<a href="/image/%s/%s/%s/?p=%d">-%d-</a>'''%(symbol,group,tf,i,i) for i in range(11)])
    out.append(_svg)
    out.append("<br/>")
    out.append(_page)
    all = '&nbsp;'.join(out)
    return '''<!DOCTYPE html><head><META HTTP-EQUIV="REFRESH" CONTENT="10"></head><body><br/>%s</body></html>'''%all
