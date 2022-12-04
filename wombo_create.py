
import requests
import json
import time
import argparse
import random
import os
import pickle

DEBUG=False

def sign_up(key):
    body = {"key": key}

    r = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={key}",
        data=body,
    )

    if r.status_code != requests.codes.ok:
        error = f"Error during identification. Status code error: {r.status_code}"
        print(error)
        assert False, error

    if DEBUG:
        print("Google identification sign up.")
    id_token = r.json()["idToken"]
    if DEBUG:
        print("  => idToken got.")
    return id_token


def look_up(identify_key, id_token):
    body = {"idToken": id_token}

    r = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={identify_key}",
        data=body,
    )

    if r.status_code != requests.codes.ok:
        assert False, f"Error during identification. Status code error: {r.status_code}"

    if DEBUG:
        print("Google identification look up.")
    local_id = r.json()["users"][0]["localId"]
    if DEBUG:
        print("  => localId got.")
    return local_id

def identify(identify_key):
    id_token = sign_up(identify_key)
    local_id = look_up(identify_key, id_token)
    if DEBUG:
        print("Identification done!")

    return {"id_token": id_token, "local_id": local_id}


def task(session, id):
    r = session.get(f"https://paint.api.wombo.ai/api/tasks/{id}")

    rep = r.json()
    if DEBUG:
        print(f"Status: {rep['state']}")
    return rep

def create(id_token: str, prompt: str, style: int, ID=None):
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": "bearer " + id_token,
            "Origin": "https://paint.api.wombo.ai/",
            "Referer": "https://paint.api.wombo.ai/",
            "User-Agent": "Mozilla/5.0",
        }
    )

    # def init_task():
    #     # from io import StringIO
    #     # body = StringIO()
    #     # json.dump({"premium": False}, body)
    #     # body=body.getvalue()
    #     body = '{"premium": false}'
    #     r = s.post("https://paint.api.wombo.ai/api/tasks", data=body)

    #     return r.json()["id"]

    
    body = (
        '{"input_spec":{"prompt":"'
        + prompt
        + '","style":'
        + str(style)
        + ',"display_freq":10}}'
    )

    id=ID
    display_freq = 10
    if ID is None:
        id = s.post("https://paint.api.wombo.ai/api/tasks", data='{"premium": false}').json()["id"]
        r = s.put(f"https://paint.api.wombo.ai/api/tasks/{id}", data=body)

        # wombolog.info(f"Status: {r.json()['state']}")
        if DEBUG:
            print(f"Status: {r.json()['state']}")
        display_freq = r.json()["input_spec"]["display_freq"] / 10
        with open('session.dump', 'wb') as f:
            pickle.dump(s, f)
        with open('id.dump', 'w') as f:
            f.write(id)
        print(prompt)
        exit(0)
    else:
        with open('session.dump', 'rb') as f:
            s = pickle.load(f)
        with open('id.dump', 'r') as f:
            id = f.readline()

    latest_task = task(s, id)    
    while latest_task["state"] != "completed":
        time.sleep(display_freq)
        latest_task = task(s, id)

    result = s.post(f"https://paint.api.wombo.ai/api/tradingcard/{id}")
    img_uri = result.json()

    if img_uri:
        if DEBUG:
            print(f"Url result: {img_uri}")
        return img_uri
    else:
        print("Invalid image uri, can't download result!")

def generate_prompt2(prompttext_f,prompt_len):
    prompt = open(prompttext_f).read().splitlines()
    vocab = len(prompt)
    generated = []
    num_word = prompt_len
    while len(sorted(set(generated), key=lambda d: generated.index(d))) < num_word:
        rand = random.randint(0, vocab)
        generated.append(prompt[rand-1])
    return (' '.join(sorted(set(generated), key=lambda d: generated.index(d))))


def get_random_style(styles_fname):
    styles = open(styles_fname).read().splitlines()
    return styles[random.randint(0,len(styles)-1)]

# def generate_prompt_old(prompttext_f,prompt_len):
#     prompt = open(prompttext_f).read().splitlines()
#     vocab = len(prompt)
#     generated = []
#     num_word = prompt_len
#     while len(sorted(set(generated), key=lambda d: generated.index(d))) < num_word:
#         rand = random.randint(0, vocab)
#         generated.append(prompt[rand-1])
#     return (' '.join(sorted(set(generated), key=lambda d: generated.index(d))))

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

#https://paint.api.wombo.ai/api/styles

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
    # EXIF = im.getexif()
    # EXIF[0x9286] = f"({style}) {prompt}"
    width, height = im.size
    left = 62
    top = 215
    right = width-62
    bottom = height-154
    
    im = im.crop((left, top, right, bottom))
    im.save(res_f_name)
    # im.save(res_f_name,exif=EXIF)
    print("done")
    exit(0)

__dir=os.path.dirname(os.path.realpath(__file__)) 

if prompt=="r":   
    # prompt = generate_prompt(__dir+"/words1",__dir+"/words2")
    prompt = generate_prompt(__dir+"/words1.txt",__dir+"/words2.txt")

if style=="r":    
    # style = get_random_style(__dir+"/styles")
    style = get_random_style(__dir+"/styles.txt")


if  not args.download:
    res = identify(identify_key=identify_key)
    img_uri = create(res["id_token"], prompt, style,task_id)
    with open('url.dump', 'w') as f:
        f.write(img_uri)    
else:
    with open('url.dump', 'r') as f:
        img_uri=f.readline()
        r = requests.get(img_uri, allow_redirects=True)
        open(res_f_name, 'wb').write(r.content)
print("done")   
# print(img_uri)

