
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



def create(id_token: str, prompt: str, style: int, ID=None):
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
    display_freq = 10
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
parser.add_argument('-i','--id',action='store_true')
parser.add_argument('-c','--crop',action='store_true')
parser.add_argument('-d','--download',action='store_true')          
parser.add_argument('-s', '--style')      
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
if args.id:  
    task_id = args.id

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

if style=="r":        
    style = get_random_style(__dir+"/styles")


if  not args.download:
    res = identify(identify_key=identify_key)
    img_uri = create(res["id_token"], prompt, style,task_id)
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

