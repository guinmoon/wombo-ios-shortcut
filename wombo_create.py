
#!/usr/bin/python3

import requests
import json
import time
import argparse
import random
import os
import pickle
import asyncio
from typing import List, Optional, Union,NamedTuple,Any, Dict,Literal
from requests import Session
# from aiohttp import ClientSession

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





# class HTTPSession:
#     __slots__ = ("session",)

#     def __init__(self, session: Optional[ClientSession]) -> None:
#         self.session = session

#     async def get_response(
#         self,
#         *,
#         method: str,
#         endpoint: str,
#         json: Optional[Dict[str, Any]] = None,
#     ) -> Any:
#         if isinstance(self.session, ClientSession) and not self.session.closed:
#             return await self._fetch(
#                 method=method,
#                 endpoint=endpoint,
#                 json=json,
#                 session=self.session,
#             )
#         async with ClientSession() as session:
#             return await self._fetch(
#                 method=method, endpoint=endpoint, json=json, session=session
#             )

#     async def _fetch(
#         self,
#         *,
#         method: str,
#         endpoint: str,
#         json: Optional[Dict[str, Any]],
#         session: ClientSession,
#     ) -> Any:
#         async with session.request(
#             method,
#             f"https://yandex.ru/lab/api/yalm/{endpoint}",
#             json=json,
#             raise_for_status=True,
#         ) as response:
#             return await response.json()

class HTTPSession:
    __slots__ = ("session",)

    def __init__(self, session: Optional[Session]) -> None:
        self.session = session

    def get_response(
        self,
        *,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if isinstance(self.session, Session):
            return self._fetch(
                method=method,
                endpoint=endpoint,
                json=json,
                session=self.session,
            )
        with Session() as session:
            return self._fetch(
                method=method, endpoint=endpoint, json=json, session=session
            )

    def _fetch(
        self,
        *,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]],
        session: Session,
    ) -> Any:
        with session.request(
            method, f"https://yandex.ru/lab/api/yalm/{endpoint}", json=json
        ) as response:
            response.raise_for_status()
            return response.json()


class TextType(NamedTuple):
    number: int
    name: str
    description: str


# class Balaboba:
#     """Asynchronous wrapper for Yandex Balaboba."""

#     __slots__ = ("_session",)

#     def __init__(self, session: Optional[ClientSession] = None) -> None:
#         """Asynchronous wrapper for Yandex Balaboba."""
#         self._session = HTTPSession(session)

#     @property
#     def session(self) -> Optional[ClientSession]:
#         return self._session.session

#     @session.setter
#     def session(self, session: Optional[ClientSession]) -> None:
#         self._session.session = session

#     async def get_text_types(
#         self, language: Literal["en", "ru"] = "ru"
#     ) -> List[TextType]:
#         endpoint = "intros" if language == "ru" else "intros_eng"
#         response = await self._session.get_response(
#             method="GET", endpoint=endpoint
#         )
#         return [TextType(*intro) for intro in response["intros"]]

#     async def balaboba(
#         self, query: str, text_type: Union[TextType, int]
#     ) -> str:
#         intro = (
#             text_type.number if isinstance(text_type, TextType) else text_type
#         )
#         response = await self._session.get_response(
#             method="POST",
#             endpoint="text3",
#             json={"query": query, "intro": intro, "filter": 1},
#         )
#         return "{}{}".format(response["query"], response["text"])


class Balaboba:
    """Wrapper for Yandex Balaboba."""

    __slots__ = ("_session",)

    def __init__(self, session: Optional[Session] = None) -> None:
        """Wrapper for Yandex Balaboba."""
        self._session = HTTPSession(session)

    @property
    def session(self) -> Optional[Session]:
        return self._session.session

    @session.setter
    def session(self, session: Optional[Session]) -> None:
        self._session.session = session

    def get_text_types(
        self, language: Literal["en", "ru"] = "ru"
    ) -> List[TextType]:
        endpoint = "intros" if language == "ru" else "intros_eng"
        response = self._session.get_response(method="GET", endpoint=endpoint)
        return [TextType(*intro) for intro in response["intros"]]

    def balaboba(self, query: str, text_type: Union[TextType, int]) -> str:
        intro = (
            text_type.number if isinstance(text_type, TextType) else text_type
        )
        response = self._session.get_response(
            method="POST",
            endpoint="text3",
            json={"query": query, "intro": intro, "filter": 1},
        )
        return "{}{}".format(response["query"], response["text"])


async def get_balaboba(orig_text):
    # from aiobalaboba import Balaboba
    bb = Balaboba()
    # text_types = await bb.get_text_types(language="en")
    # response = await bb.balaboba(orig_text, text_type=text_types[4])
    text_types = bb.get_text_types(language="en")
    response =  bb.balaboba(orig_text, text_type=text_types[4])
    return response


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
    # from balaboba import Balaboba
    # bb = Balaboba()
    # text_types = bb.get_text_types(language="en")
    # response = bb.balaboba(prompt, text_type=text_types[4])
    prompt=asyncio.run(get_balaboba(prompt))

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

