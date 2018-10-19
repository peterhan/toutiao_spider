import requests
import json
import math,time,hashlib
import PyV8

UA_ST = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'''
UA_ST = '''Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'''
UA_js = '''var navigator = {};
navigator["userAgent"] = "%s";
'''%UA_ST

headers = {"User-Agent":UA_ST}    

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

def dump_json(jo):
    return json.dumps(jo,ensure_ascii=False,indent=2).encode('gbk','ignore')  
    
def get_index(cat='news_car'):
    maxhot = '1539912409'
    data =  get_veri_data('', maxhot=maxhot) 
    data['cat'] = cat
    data['maxhot'] = maxhot
    url='https://www.toutiao.com/api/pc/feed/?category={cat}&utm_source=toutiao&widen=50&max_behot_time={maxhot}&max_behot_time_tmp={maxhot}&tadrequire=true&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    print url
    rp = requests.get(url,headers=headers)
    print dump_json(rp.json())

    
def get_uid_page(uid):    
    # print uj.keys()
    data = get_veri_data(uid)        
    url='https://www.toutiao.com/c/user/article/?page_type=1&user_id={uid}&max_behot_time=0&count=20&as={_as}&cp={cp}&_signature={sig}'.format(**data)
    res = requests.get(url,headers=headers)
    print url
    jst = dump_json(res.json())     
    print >>fo,'\t'.join([str(uid),url,jst])
    # break


if __name__=='__main__':
    for col in 'news_car,car_new_arrival,SUV,car_guide,car_usage,news_hot'.split(','):
        get_index(col)
