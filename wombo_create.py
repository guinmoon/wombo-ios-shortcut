
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


def get_random_style(styles_fname):
    styles = open(styles_fname).read().splitlines()
    return styles[random.randint(0,len(styles)-1)]

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
        'origin': 'https://yandex.ru',        
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
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
        import urllib.request        
        img_uri=f.readline()
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve(img_uri, res_f_name)
    print("download img done")   

# print(img_uri)

# python3 wombo_create.py -p b && python3 wombo_create.py -i && python3 wombo_create.py -d && python3 wombo_create.py -c