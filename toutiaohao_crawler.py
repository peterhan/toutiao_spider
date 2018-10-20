import requests
import json
import os
import math,hashlib
import datetime,time
import PyV8
import sqlitedict
from gevent.pool import Pool

UA_ST = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'''
UA_ST = '''Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'''
UA_js = '''var navigator = {};
navigator["userAgent"] = "%s";
'''%UA_ST
HEADERS = {"User-Agent":UA_ST}    
SIG_JS_OBJ = False
DATE_FORMAT='%Y-%m-%d %H:%M:%S'

def dump_json(jo,i=None,e=None):
    if e is None:
        e =  'gbk' if os.name=='nt' else'utf8'
    return json.dumps(jo,ensure_ascii=False,indent=i).encode(e,'ignore')  
    
def get_date(fmt=DATE_FORMAT,base= datetime.datetime.now(), isobj=False, **kwargs ):
    i_str2date=lambda str_date,fmt: datetime.datetime.fromtimestamp(time.mktime(time.strptime(str_date,fmt)))
    if type(base)==str:
        dateobj= i_str2date(base,fmt)+ datetime.timedelta( **kwargs)
    else:
        dateobj = base + datetime.timedelta( **kwargs)
    if isobj: 
        return dateobj
    else: 
        return dateobj.strftime(fmt)
        
        
def unix2ts(uxts,mask=DATE_FORMAT,base=10):
    return \
        datetime.datetime.fromtimestamp( 
         int(uxts,base) 
        ).strftime(mask)
        
def ts2unix(str_date,mask=DATE_FORMAT):
    return \
        int(time.mktime(
         time.strptime(str_date, mask)
        )) 

def getASCP():
    t = int(math.floor(time.time()))
    e = hex(t).upper()[2:]
    m = hashlib.md5()
    m.update(str(t).encode(encoding='utf-8'))
    i = m.hexdigest().upper()

    if len(e) != 8:
        AS = '479BB4B7254C150'
        CP = '7E0AC8874BB0985'
        return AS,CP
    n = i[0:5]
    a = i[-5:]
    s = ''
    r = ''
    for o in range(5):
        s += n[o] + e[o]
        r += e[o + 3] + a[o]

    AS = 'A1' + s + e[-3:]
    CP = e[0:3] + r + 'E1'
    return AS,CP
    
def get_signature(uid,maxhot='0'):
    global UA_js
    global SIG_JS_OBJ
    if not SIG_JS_OBJ:
        js = open('toutiao.sig.js','rb').read().decode('utf8')
        js = UA_js +'\n'+js
        ctxt = PyV8.JSContext()  
        ctxt.enter()
        SIG_JS_OBJ = ctxt.eval(js)
        #ctxt.leave()
    return SIG_JS_OBJ(uid+''+maxhot)
    
def test_encrypt():
    AS,CP=getASCP()
    print AS,CP
    sig =  get_signature('5824952602')
    print type(sig),sig
    url ='https://www.toutiao.com/c/user/article/?page_type=1&user_id=5824952602&max_behot_time=0&count=20&as=A1053B1C1833323&cp=5BC883239283EE1&_signature=-VnTmAAAoptwuOoCoL-Wb.lZ04'
    print url.replace('-VnTmAAAoptwuOoCoL-Wb.lZ04',sig)
    
def get_veri_data(uid,maxhot='0'):
    _as,cp = getASCP()
    sig =get_signature(uid,maxhot)
    return {'uid':uid,'_as':_as,'cp':cp,'sig':sig}


    
def get_index_page(cat='news_car',maxhot = '1539912409'):    
    data =  get_veri_data('', maxhot=maxhot) 
    data['cat'] = cat
    data['maxhot'] = maxhot
    cookies={'uuid':'w:c1554d99c34047cc8e89fd','tt_webid':'6612754979269297671'}   
    url='https://www.toutiao.com/api/pc/feed/?category={cat}&utm_source=toutiao&widen=1&max_behot_time={maxhot}&max_behot_time_tmp={maxhot}&tadrequire=true&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    print url
    rp = requests.get(url,headers=HEADERS,cookies=cookies)
    jo = rp.json()
    # open('dbg.js','w').write(dump_json(jo))
    return jo

def extract_index_user_list(jo):
    ilist = []
    for d in jo['data']:
        # print d.keys()_url')})
        print ( '[%s][%s][%s]'%(d.get('title',''),d.get('source'),d.get('chinese_tag') )).encode('gbk','ignore')
    return ilist # print dump_json()
    
def get_uid_page(uid):    
    # print uj.keys()
    data = get_veri_data(uid)        
    url='https://www.toutiao.com/c/user/article/?page_type=1&user_id={uid}&max_behot_time=0&count=200&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    res = requests.get(url,headers=HEADERS)
    print url
    jo = res.json()
    jo.update({'uid':uid,'sig_data':data})
    jst = dump_json(jo) 
    print jo['data'][0].keys()
    return jo
    # break

def user_page_crawl():
    res = []
    idxd = sqlitedict.SqliteDict('./idx_db.db')
    for k,idx_js in idxd.items():
        print k
        user_list = extract_index_user_list(idx_js)
        continue
    
        obj=json.loads(row)
        jo = get_uid_page(obj['url'].split('/')[-2])
        res.append(dump_json(jo,i=None,e='utf8'))    
    
    
def index_crawl():    
    pool = Pool(8)
    cols='news_finance,news_entertainment,news_tech,news_game,news_sports,news_travel,news_car,news_hot,news_military,news_fashion,news_history,news_world,news_discovery,news_regime,news_baby,news_essay'.split(',')
    car_cols='car_new_arrival,SUV,car_guide,car_usage'
    idxd = sqlitedict.SqliteDict('./idx_db.db', autocommit=True)
    def fetch_one_col(col,i,idxd):
        try:
            maxhot = str(ts2unix(get_date())-i*2000)            
            jo = get_index_page(col, maxhot)
            ilist = extract_index_user_list(jo)
            key = 'idx_%s_%s'%(col,maxhot)
            idxd[key] = jo
        except Exception as e:
            print e.message,col
        
    for col in cols[:]:
        for i in range(20):
            pool.spawn(fetch_one_col, col,i,idxd)
    pool.join()
    idxd.close()
        
if __name__=='__main__':
    # index_crawl()
    user_page_crawl()