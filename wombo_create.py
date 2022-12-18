
#!/usr/bin/python3

import http.client
import requests
import json
import time
import argparse
import random
import os
import pickle



DEBUG=False

def identify(identify_key):    
    body = {"key": identify_key}
    r = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={identify_key}",
        data=body,
    )
    if r.status_code != requests.codes.ok:
        error = f"Error during identification. Status code error: {r.status_code}"
        print(error)
        exit(1)
    id_token = r.json()["idToken"]
    local_id = ""
    # body = {"idToken": id_token}
    # r = requests.post(
    #     f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={identify_key}",
    #     data=body,
    # )
    # if r.status_code != requests.codes.ok:
    #     assert False, f"Error during identification. Status code error: {r.status_code}"
    # local_id = r.json()["users"][0]["localId"]
    # if DEBUG:
    #     print("Identification done!")

    return {"id_token": id_token, "local_id": local_id}



def create(id_token: str, prompt: str, style: int, ID=None,one=False):
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": "bearer " + id_token,
            "Origin": "https://paint.api.wombo.ai/",
            "Referer": "https://paint.api.wombo.ai/",
            "User-Agent": "Mozilla/5.0",
        }
    )
    
    body = '{"input_spec":{"prompt":"' + prompt + '","style":' + str(style)+ ',"display_freq":10}}'        

    id=ID
    display_freq = 1
    if ID is None:
        id = session.post("https://paint.api.wombo.ai/api/tasks", data='{"premium": false}').json()["id"]
        r = session.put(f"https://paint.api.wombo.ai/api/tasks/{id}", data=body)
        if DEBUG:
            print(f"Status: {r.json()['state']}")
        display_freq = r.json()["input_spec"]["display_freq"] / 10
        with open('session.dump', 'wb') as f:
            pickle.dump(session, f)
        with open('id.dump', 'w') as f:
            f.write(id)
        print(prompt)
        exit(0)
    else:
        with open('session.dump', 'rb') as f:
            session = pickle.load(f)
        with open('id.dump', 'r') as f:
            id = f.readline()
   
    latest_task = session.get(f"https://paint.api.wombo.ai/api/tasks/{id}").json()
    if latest_task["state"] != "completed" and one:
            print("pending")
            exit(0)
    while latest_task["state"] != "completed":
        time.sleep(display_freq)
        latest_task = session.get(f"https://paint.api.wombo.ai/api/tasks/{id}").json()


    result = session.post(f"https://paint.api.wombo.ai/api/tradingcard/{id}")
    img_uri = result.json()
    return img_uri


def get_random_style(styles_fname):
    styles = open(styles_fname).read().splitlines()
    return styles[random.randint(0,len(styles)-1)]

def generate_prompt(prompttext1,prompttext2):
    prompt1 = open(prompttext1).read().splitlines()
    prompt2 = open(prompttext2).read().splitlines()
    return prompt1[random.randint(0,len(prompt1)-1)]+" "+prompt2[random.randint(0,len(prompt2)-1)]+" "+prompt1[random.randint(0,len(prompt1)-1)]


def update_styles(styles_fname):
    r = requests.get("https://paint.api.wombo.ai/api/styles")
    styles = json.loads(r.text)
    lines = []
    for style in styles:
        lines.append(str(style["id"]))
    with open(styles_fname, 'w') as f:
        f.write("\n".join(lines))
    return styles

def translate(to_translate, to_language="auto", from_language="auto"):
    import re
    import html
    from requests.utils import requote_uri
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
    base_link = "http://translate.google.com/m?tl=%s&sl=%s&q=%s"
    to_translate = requote_uri(to_translate)
    link = base_link % (to_language, from_language, to_translate)
    request = requests.get(link,headers=agent)
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    re_result = re.findall(expr, request.text)
    if (len(re_result) == 0):
        result = ""
    else:
        result = html.unescape(re_result[0])
    return (result)


def sync_balaboba(orig_text,text_type=29):        
    import ssl
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
        'cookie': 'yandexuid=6661439881598172333; gdpr=0; _ym_uid=1598172741236237445; yandex_login=svetlakov.art; font_loaded=YSv1; my=Yy4BAQA=; L=V3tnfnNCZAt0ZXlcUFpyXkEHdF5xfwNaJjQrJDhWPywRHBMHOg==.1650910133.14958.382310.5e65922eda40cb548cefbb656d408ba0; is_gdpr=0; is_gdpr_b=CN/1QxDceigC; maps_routes_travel_mode=pedestrian; mda=0; _ym_d=1661953552; i=sBpirENXXPTL70XxYGVxTj3E7hrPj8kvdPEJkUPAx0crSYUOrzouYcmkfaypPzX1BiDzafTI09JKx7WBJpDtkqHZkkQ=; skid=5072158841662295591; yabs-frequency=/5/0000000000000000/1LmOhY66wcEWI240/; uxs_uid=b86d71e0-52d7-11ed-b984-a716bc3a0a85; yp=1676851698.szm.1:2560x1080:1918x978#1966270133.udn.cDrQkNGA0YLRkdC8INCh0LDQstC60LjQvQ%3D%3D; _ga=GA1.2.665324730.1668340417; device_id=acf9a7620e7f6e426f0ef047093baa3fe482af221; active-browser-timestamp=1670159080952; yuidss=6661439881598172333; ymex=1986138190.yrts.1670778190#1977313667.yrtsi.1661953667; Session_id=3:1671124318.5.0.1598172763379:Z83oWw:45.1.2:1|476815516.52737370.2.2:52737370|3:10262653.814841.oE8KD1KWu101cDVoFOqf46tAEjk; sessionid2=3:1671124318.5.0.1598172763379:Z83oWw:45.1.2:1|476815516.52737370.2.2:52737370|3:10262653.814841.fakesign0000000000000000000; ys=udn.cDrQkNGA0YLRkdC8INCh0LDQstC60LjQvQ%3D%3D#c_chck.2237070386; _ym_visorc=w; _ym_isad=1; _yasc=PGoX/oCOAcEclGXNcRffVJTDEqh3ShcVajzRQbi+sCSryX32wCjWQxBJeSuDaq9iV34zzw==; _yasc=MVFvW0JLow+Qd+xBygorYtbjt/QJ8Prrrv0j8caPjYpBWw28OCKXz6UjImHEUSzMJmGMIA==; i=tEpG3D7w+kLceBDH3esnB/oTbGTmWoob810CoP6kL1FVcunFG7M2IdMFjXyeBepTcPmahvEccPTh5R70LkJdBUAGzVc=; is_gdpr=0; is_gdpr_b=CLWnaxC1mwE=',
        'device-memory': '8',
        'downlink': '8.1',
        'dpr': '1',
        'ect': '4g',
        'origin': 'https://yandex.ru',
        'referer': 'https://yandex.ru/lab/yalm?style=11',
        'rtt': '50',
        'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'viewport-width': '2008'
    }    
    conn.request("POST", "/lab/api/yalm/text3", payload, headers)
    res = conn.getresponse()
    data = res.read()
    data=json.loads(data)
    return "{} {}".format(data["query"],data["text"])



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
parser.add_argument('-s', '--style')      
parser.add_argument('-t', '--translate',action='store_true')
parser.add_argument('-p', '--prompt')      
args = parser.parse_args()

if args.update:
    update_styles("styles.txt")
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
    im.save(res_f_name)
    print("crop done")
    exit(0)

__dir=os.path.dirname(os.path.realpath(__file__)) 

if prompt=="r":       
    prompt = generate_prompt(__dir+"/words1",__dir+"/words2")
if prompt=="b":
    prompt = generate_prompt(__dir+"/words1",__dir+"/words2")
    prompt=sync_balaboba(prompt,29)

if args.translate:    
    prompt=translate(prompt, 'en')

if style=="r":        
    style = get_random_style(__dir+"/styles")


if  not args.download:
    res = identify(identify_key=identify_key)
    img_uri = create(res["id_token"], prompt, style,task_id,args.one)
    with open('url.dump', 'w') as f:
        f.write(img_uri)    
    print("get url done")   
else:
    with open('url.dump', 'r') as f:
        img_uri=f.readline()
        r = requests.get(img_uri, allow_redirects=True)
        open(res_f_name, 'wb').write(r.content)
    print("download img done")   

# print(img_uri)

