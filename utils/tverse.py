import asyncio
import random

from aiohttp import ClientSession
import aiohttp
import re
from data import config
from utils.core import logger
from utils.telegram import AccountInterface
import urllib.parse
from bs4 import BeautifulSoup

def gen_xapi(lid=None, mid=None, appid=None):
    return f"{lid}:{mid}:{appid}:{str(random.random())}"

headers = {
    "Host": "api.tonverse.app",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": "\"Windows\"",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\", \"Microsoft Edge WebView2\";v=\"130\"",
    "sec-ch-ua-mobile": "?0",
    "Accept": "*/*",
    "Origin": "https://app.tonverse.app",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://app.tonverse.app/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}
def convert_to_url_encoded(data: str) -> str:

    parts = data.split('&')
    parsed_data = {}

    for part in parts:
        key, value = part.split('=', 1)
        if key == "user":
            parsed_data[key] = urllib.parse.quote(value)
        else:
            parsed_data[key] = value

    encoded_data = "&".join([f"{key}={value}" for key, value in parsed_data.items()])
    return encoded_data

class RefCodeError(Exception):
    pass

class AccountUsedError(Exception):
    pass

class TverseBot:
    def __init__(
            self,
            account: AccountInterface,
            session: ClientSession
            ):
        self.account = account
        self.session = session

    async def logout(self):

        await self.session.close()
    async def start(self):
        link='https://app.tonverse.app/'
        headers={
            'Host':	'app.tonverse.app',
            'User-Agent':	'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
            'Accept-Language':	'ru'
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(link,ssl=False) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Ищем все script-теги и фильтруем вручную
                for script in soup.find_all('script', {'type': 'text/javascript'}):
                    if (src := script.get('src')) and '/assets/js/app.js?' in src:
                        version = src.split('?')[-1]
                        self.session.headers['X-Application-Version'] = version
                        return

    async def login(self):

        try:
            data=await self.account.get_tg_web_data()
            encoded_data = convert_to_url_encoded(data)

            data={
                'bot_id': '7631205793',
                'data':f'{encoded_data}'
            }

            resp = await self.session.post("https://api.tonverse.app/auth/telegram",
                                           data=data,headers=headers,ssl=False)
            resp_json = await resp.json()
            return resp_json['response']
        except Exception as err:
            logger.info(f"{err}")

            return False

    async def user_data(self, session_token, id="undefined"):
        urlencoded_data = {
            "session": session_token,
            "id": id
        }

        response = await self.session.post('https://api.tonverse.app/user/info',data=urlencoded_data,headers=headers,ssl=False)
        rer=await response.json()
        return rer['response']

    async def begin_galaxy(self,session_token):
        urlencoded_data = {
            "session": session_token,
            "stars": 100,
            "referral": config.REF
        }

        response = await self.session.post("https://api.tonverse.app/galaxy/begin",headers=headers, data=urlencoded_data,ssl=False)
        await response.json()
        return

    async def boosts(self,session_token):
        urlencoded_data={
            'session':session_token
        }
        response = await self.session.post("https://api.tonverse.app/user/boosts",headers=headers, data=urlencoded_data,ssl=False)
        try:
            data = await response.json()
            ids = [item['id'] for item in data['response']['items']]
            return ids
        except:
            return None
    async def boosts_start(self,session_token,boosts):
        try:
            for boost in boosts:
                await asyncio.sleep(random.randint(1, 3))
                urlencoded_data = {
                    'session': session_token,
                    'boost_id': boost
                }
                response = await self.session.post("https://api.tonverse.app/boost/activate", headers=headers,
                                                   data=urlencoded_data, ssl=False)
                await response.json()
            return
        except:
            return





    async def buy_stars(self,session_token, galaxy_id):
        urlencoded_data = {
            "session": session_token,
            "galaxy_id": galaxy_id,
            "stars": 100
        }
        response = await self.session.post('https://api.tonverse.app/stars/create',  data=urlencoded_data, headers=headers, ssl=False)
        rer = await response.json()
        try:
            if rer['response']['success'] == 1:
                return True
            else:
                return False
        except:
            return False

    async def collect_dust(self, session_token):
        urlencoded_data = {
            "session": session_token
        }

        response = await self.session.post("https://api.tonverse.app/galaxy/collect",  data=urlencoded_data,headers=headers,ssl=False)
        rer = await response.json()
        return rer['response']

    async def get_galaxy(self,  session_token, id="null", member_id="null"):
        urlencoded_data = {
            "session": session_token,
            "id": id,
            "member_id": member_id
        }

        response = await self.session.post("https://api.tonverse.app/galaxy/get",data=urlencoded_data,headers=headers,ssl=False)
        rer=await response.json()
        return rer['response']
