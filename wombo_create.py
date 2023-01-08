
#!/usr/bin/python3

import http.client
import json
import time
import argparse
import random
import os
import pickle
import ssl


DEBUG=False

_unverified_context = ssl._create_unverified_context()

def identify(identify_key):    
    conn = http.client.HTTPSConnection("identitytoolkit.googleapis.com",context = _unverified_context)    
    payload = json.dumps(
        {"key": identify_key}
    )
    headers = {}
    conn.request("POST", f"/v1/accounts:signUp?key={identify_key}", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data=json.loads(data)
    id_token = data["idToken"]
    local_id = ""
    return {"id_token": id_token, "local_id": local_id}



def create(id_token: str, prompt: str, style: int, ID=None,one=False):    
    conn = http.client.HTTPSConnection("paint.api.wombo.ai",context = _unverified_context)    
    headers={
            "Authorization": "bearer " + id_token,
            "Origin": "https://paint.api.wombo.ai/",
            "Referer": "https://paint.api.wombo.ai/",
            "User-Agent": "Mozilla/5.0",
        }
    
    body = '{"input_spec":{"prompt":"' + prompt + '","style":' + str(style)+ ',"display_freq":10}}'        

    id=ID
    display_freq = 1
    if ID is None:        
        conn.request("POST", f"/api/tasks", '{"premium": false}', headers)
        data=conn.getresponse().read()        
        id=json.loads(data)["id"]
        conn.request("PUT", f"/api/tasks/{id}", body, headers)
        data=conn.getresponse().read()        
        r=json.loads(data)             
        if DEBUG:
            print(f"Status: {r['state']}")
        display_freq = r["input_spec"]["display_freq"] / 10
        with open('headers.dump', 'wb') as f:
            pickle.dump(headers, f)
        with open('id.dump', 'w') as f:
            f.write(id)
        with open('prompt.dump', 'w') as f:
            f.write(prompt)
        print(prompt)
        exit(0)
    else:
        with open('headers.dump', 'rb') as f:
            headers = pickle.load(f)
        with open('id.dump', 'r') as f:
            id = f.readline()
   
    conn.request("GET", f"/api/tasks/{id}", body, headers)
    data=conn.getresponse().read()        
    latest_task=json.loads(data)     
    if latest_task["state"] != "completed" and one:
            print("pending")
            exit(0)
    while latest_task["state"] != "completed":
        time.sleep(display_freq)
        conn.request("GET", f"/api/tasks/{id}", body, headers)
        data=conn.getresponse().read()        
        latest_task=json.loads(data)         

    
    conn.request("POST", f"/api/tradingcard/{id}", body, headers)
    data=conn.getresponse().read()        
    img_uri=json.loads(data) 
    return img_uri


def get_random_style(styles_fname,styles_blist_fname=None):
    styles = open(styles_fname).read().splitlines()
    style = styles[random.randint(0,len(styles)-1)] 
    if styles_blist_fname is not None:
        styles_blist = open(styles_blist_fname).read().splitlines()        
        while style in styles_blist:
            style = styles[random.randint(0,len(styles)-1)] 
    return style

def generate_prompt(prompttext1,prompttext2):
    prompt1 = open(prompttext1).read().splitlines()
    prompt2 = open(prompttext2).read().splitlines()
    return prompt1[random.randint(0,len(prompt1)-1)]+" "+prompt2[random.randint(0,len(prompt2)-1)]+" "+prompt1[random.randint(0,len(prompt1)-1)]


def update_styles(styles_fname):
    conn = http.client.HTTPSConnection("paint.api.wombo.ai",context = _unverified_context)    
    conn.request("GET", f"/api/styles")
    data=conn.getresponse().read()        
    styles = json.loads(data)
    lines = []
    for style in styles:
        lines.append(str(style["id"]))
    with open(styles_fname, 'w') as f:
        f.write("\n".join(lines))
    return styles

def translate(to_translate, to_language="auto", from_language="auto"):
    import re
    import html    
    from urllib.parse import quote
    agent = {'User-Agent':
         "Mozilla/4.0 (\
        compatible;\
        MSIE 6.0;\
        Windows NT 5.1;\
        SV1;\
        .NET CLR 1.1.4322;\
        .NET CLR 2.0.50727;\
        .NET CLR 3.0.04506.30\
        )"}
    base_link = "/m?tl=%s&sl=%s&q=%s"        
    to_translate = quote(to_translate, safe="")
    link = base_link % (to_language, from_language, to_translate)    
    conn = http.client.HTTPSConnection("translate.google.com",context = _unverified_context)    
    conn.request("GET", link,headers=agent)
    data=conn.getresponse().read().decode("utf-8")    
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    re_result = re.findall(expr, data)
    if (len(re_result) == 0):
        result = ""
    else:
        result = html.unescape(re_result[0])
    return (result)


def sync_balaboba(orig_text,text_type=32):            
    conn = http.client.HTTPSConnection("yandex.ru",context = ssl._create_unverified_context())    
    payload = json.dumps({
        "query": orig_text,
        "intro": text_type,
        "filter": 1
    })
    headers = {
        'authority': 'yandex.ru',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,tr;q=0.6',
        'content-type': 'application/json',   
        'cookie': ' gdpr=0; font_loaded=YSv1; my=Yy4BAQA=; L=V3tnfnNCZAt0ZXlcUFpyXkEHdF5xfwNaJjQrJDhWPywRHBMHOg==.1650910133.14958.382310.5e65922eda40cb548cefbb656d408ba0; is_gdpr=0; is_gdpr_b=CN/1QxDceigC; maps_routes_travel_mode=pedestrian; mda=0; _ym_d=1661953552; i=sBpirENXXPTL70XxYGVxTj3E7hrPj8kvdPEJkUPAx0crSYUOrzouYcmkfaypPzX1BiDzafTI09JKx7WBJpDtkqHZkkQ=; skid=5072158841662295591; yabs-frequency=/5/0000000000000000/1LmOhY66wcEWI240/; uxs_uid=b86d71e0-52d7-11ed-b984-a716bc3a0a85; yp=1676851698.szm.1:2560x1080:1918x978#1966270133.udn.cDrQkNGA0YLRkdC8INCh0LDQstC60LjQvQ%3D%3D; _ga=GA1.2.665324730.1668340417; device_id=acf9a7620e7f6e426f0ef047093baa3fe482af221; active-browser-timestamp=1670159080952; yuidss=6661439881598172333; ymex=1986138190.yrts.1670778190#1977313667.yrtsi.1661953667; Session_id=3:1671124318.5.0.1598172763379:Z83oWw:45.1.2:1|476815516.52737370.2.2:52737370|3:10262653.814841.oE8KD1KWu101cDVoFOqf46tAEjk; sessionid2=3:1671124318.5.0.1598172763379:Z83oWw:45.1.2:1|476815516.52737370.2.2:52737370|3:10262653.814841.fakesign0000000000000000000; ys=udn.cDrQkNGA0YLRkdC8INCh0LDQstC60LjQvQ%3D%3D#c_chck.2237070386; _ym_visorc=w; _ym_isad=1; _yasc=PGoX/oCOAcEclGXNcRffVJTDEqh3ShcVajzRQbi+sCSryX32wCjWQxBJeSuDaq9iV34zzw==; _yasc=vV7XHnq3z+6EstLxDJikm2Rp1exoPAC+8bBPiqE982Y7Qhwa4urpn8LP4C5WFq+geDmopw==; i=P00wshG7ooxNGAQOB2CCaomtwM0hxgA/MaVPi4wlwI/aALwMrJ/AOC6cNzuzP+PnCLOCYg8TG10gDkKozP2CAg5fcQg=; ',     
        'origin': 'https://yandex.ru',        
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }    
    conn.request("POST", "/lab/api/yalm/text3", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data=json.loads(data)
    return "{} {}".format(data["query"],data["text"])

def escape_prompt(in_prompt):
    prompt = in_prompt.replace("'","")
    prompt = prompt.replace("\n","")
    prompt = prompt.replace(":","")
    prompt = prompt.replace("  "," ")
    prompt = prompt.replace("\\","")
    return prompt



identify_key = "AIzaSyDCvp5MTJLUdtBYEKYWXJrlLzu1zuKM6Xw"

style = "r"
prompt = "r"
task_id = None
res_f_name = __dir=os.path.dirname(os.path.realpath(__file__))+'/res.jpg'

parser = argparse.ArgumentParser(
                    prog = 'wombo create',
                    description = 'get image from wombo',
                    epilog = 'Enjoy.')
parser.add_argument('-k','--key')
parser.add_argument('-u','--update',action='store_true')          
parser.add_argument('-i','--iterations',action='store_true')
parser.add_argument('-o','--one',action='store_true')
parser.add_argument('-c','--crop',action='store_true')
parser.add_argument('-d','--download',action='store_true')          
parser.add_argument('-r','--rename',action='store_true')
parser.add_argument('-b','--blacklist',action='store_true')
parser.add_argument('-s', '--style')      
parser.add_argument('-t', '--translate',action='store_true')
parser.add_argument('-p', '--prompt')      
args = parser.parse_args()

if args.update:
    update_styles("styles")
    print("done")
    exit(0)

if args.key is not None:
    identify_key =   args.key                        
if args.style is not None:    
    style = args.style
if args.prompt is not None:  
    prompt = args.prompt
if args.iterations:  
    task_id = args.iterations

if args.crop:
    from PIL import Image
    im = Image.open(res_f_name)
    width, height = im.size
    left = 62
    top = 215
    right = width-62
    bottom = height-154
    
    im = im.crop((left, top, right, bottom))
    if args.rename:
        from datetime import datetime
        now = datetime.now()            
        dt_string = now.strftime("%Y-%m-%d_%H_%M_%S")
        res_f_name = __dir=os.path.dirname(os.path.realpath(__file__))+f'/out/{dt_string}.jpg'
        with open('prompt.dump', 'r') as f:
            info_prompt = f.readlines()
            with open(res_f_name+'.txt', 'w') as f:
                f.writelines(info_prompt)
    im.save(res_f_name)
    print("crop done")
    exit(0)

__dir=os.path.dirname(os.path.realpath(__file__)) 

if prompt=="r":       
    prompt = generate_prompt(__dir+"/words1",__dir+"/words2")
if prompt=="b":
    prompt = generate_prompt(__dir+"/words1",__dir+"/words2")
    prompt=sync_balaboba(prompt,27)

if args.translate:    
    prompt = prompt.replace('\n','')
    prompt = prompt.replace('+','')
    prompt=translate(prompt, 'en')

if style=="r":        
    if args.blacklist:
        style = get_random_style(__dir+"/styles",__dir+"/styles_blist")    
    else:
        style = get_random_style(__dir+"/styles")    


prompt = escape_prompt(prompt)

if  not args.download:
    res = identify(identify_key=identify_key)
    img_uri = create(res["id_token"], prompt, style,task_id,args.one)
    with open('url.dump', 'w') as f:
        f.write(img_uri)    
    print("get url done")   
else:
    with open('url.dump', 'r') as f:
        import urllib.request        
        img_uri=f.readline()
        ssl._create_default_https_context = ssl._create_unverified_context                
        urllib.request.urlretrieve(img_uri, res_f_name)
    print("download img done")   

# print(img_uri)

# python3 wombo_create.py -p b && python3 wombo_create.py -i && python3 wombo_create.py -d && python3 wombo_create.py -c