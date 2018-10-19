import requests
import json
import math,hashlib
import datetime,time
import PyV8

UA_ST = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'''
UA_ST = '''Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'''
UA_js = '''var navigator = {};
navigator["userAgent"] = "%s";
'''%UA_ST
headers = {"User-Agent":UA_ST}    

DATE_FORMAT='%Y-%m-%d %H:%M:%S'

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
    js=open('toutiao.sig.js','rb').read().decode('utf8')
    js = UA_js +'\n'+js.replace(u'{need_replace}',uid  + "" +maxhot)    
    ctxt = PyV8.JSContext()
    ctxt.enter()
    vl5x = ctxt.eval(js)
    return vl5x
    
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

def dump_json(jo,i=None,e='gbk'):
    return json.dumps(jo,ensure_ascii=False,indent=i).encode(e,'ignore')  
    
def get_index(cat='news_car',maxhot = '1539912409'):    
    data =  get_veri_data('', maxhot=maxhot) 
    data['cat'] = cat
    data['maxhot'] = maxhot
    cookies={'uuid':'w:c1554d99c34047cc8e89fd','tt_webid':'6612754979269297671'}   
    url='https://www.toutiao.com/api/pc/feed/?category={cat}&utm_source=toutiao&widen=1&max_behot_time={maxhot}&max_behot_time_tmp={maxhot}&tadrequire=true&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    print url
    rp = requests.get(url,headers=headers,cookies=cookies)
    jo = rp.json()
    open('dbg.js','w').write(dump_json(jo))
    sl = []
    for d in jo['data']:
        # print d.keys()
        # print d
        sl.append(dump_json({'src':d.get('source'),'url':d.get('media_url')} ,i=None,e='utf8'))
        print d.get('title','').encode('gbk','ignore')
        # print dump_json()
    open('source_list.txt','w').write('\n'.join(sl))

    
def get_uid_page(uid):    
    # print uj.keys()
    data = get_veri_data(uid)        
    url='https://www.toutiao.com/c/user/article/?page_type=1&user_id={uid}&max_behot_time=0&count=200&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    res = requests.get(url,headers=headers)
    print url
    jo = res.json()
    jo.update({'uid':uid,'sig_data':data})
    jst = dump_json(jo) 
    print jo['data'][0].keys()
    return jo
    # break

def user_crawl():
    res = []
    for row in open('source_list.txt'):
        obj=json.loads(row)
        jo = get_uid_page(obj['url'].split('/')[-2])
        res.append(dump_json(jo,i=None,e='utf8'))
    open('upage.txt','a').write('\n'.join(res))
        
    
def index_crawl():
    cols='news_finance,news_entertainment,news_travel,news_car,car_new_arrival,SUV,car_guide,car_usage,news_hot'.split(',')
    for col in cols[1:2]:
        for i in range(10):
            mh = str(ts2unix(get_date())-i*2000)
            print mh
            get_index(col, mh)
        
if __name__=='__main__':
    # index_crawl()
    user_crawl()