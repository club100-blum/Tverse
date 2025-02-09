import asyncio
from asyncio import sleep, Semaphore
from random import uniform
from typing import Union
import random
import aiohttp
from aiohttp_proxy import ProxyConnector

from .agents import generate_random_user_agent
from data import config
from utils.tverse import TverseBot
from utils.core import logger
from utils.helper import format_duration
from utils.telegram import AccountInterface
from utils.proxy import to_url

try:
    from aiocfscrape import CloudflareScraper
    Session = CloudflareScraper
except:
    logger.info("Error when importing aiocfscrape.CloudflareScraper, using aiohttp.ClientSession instead")
    Session = aiohttp.ClientSession


sem = Semaphore(config.ACCOUNT_PER_ONCE)
async def start(account: AccountInterface):
    sleep_dur = 0
    while True:
        await sleep(sleep_dur)
        async with sem:
            proxy = account.get_proxy()
            if proxy is None:
                connector = None
            else:
                connector = ProxyConnector.from_url(to_url(proxy))
            async with Session(headers={'User-Agent': generate_random_user_agent(device_type='android',
                                                                                        browser_type='chrome')},
                                        timeout=aiohttp.ClientTimeout(total=60), connector=connector) as session:
                try:
                    tverse = TverseBot(account=account, session=session)
                    await sleep(uniform(*config.DELAYS['ACCOUNT']))
                    await tverse.start()
                    a=await tverse.login()
                    session_a=a['session']
                    id_a=a['id'] or 'undefined'
                    galaxy_a = a['galaxy'] or 0
                    us=await tverse.user_data(session_a,id_a)
                    logger.success(f"{us['first_name']} | Login success! | Stars: {us['stars']} | Dust: {us['dust']}")
                    if galaxy_a == 0:
                        await tverse.begin_galaxy(session_a)
                        logger.success(f"{us['first_name']} | Created Galaxy")
                    get_galaxy = await tverse.get_galaxy(session_a)
                    logger.success(f"{us['first_name']} | Galaxy {get_galaxy['title']}")
                    await asyncio.sleep(random.randint(1, 3))
                    galaxy_id = get_galaxy['id']
                    boosts = await tverse.boosts(session_a)
                    await asyncio.sleep(random.randint(1, 3))
                    if boosts != None:
                        await tverse.boosts_start(session_a,boosts)
                        logger.success(f"{us['first_name']} | Boosts activated!")
                    await asyncio.sleep(random.randint(1, 3))
                    collect_dust=await tverse.collect_dust(session_a)
                    dust_collected = collect_dust.get('dust') or 0
                    logger.success(f"{us['first_name']} | Dust collected +{dust_collected}")
                    await asyncio.sleep(random.randint(1, 3))
                    buy_star=await tverse.buy_stars(session_a,galaxy_id)
                    if buy_star == True:
                        logger.success(f"{us['first_name']} | +100 stars purchased")


                except Exception as e:
                        logger.error(f"Error: {e}")
                except Exception as outer_e:
                    logger.error(f"Session error: {outer_e}")
        logger.info(f"Reconnecting in {format_duration(config.ITERATION_DURATION)}...")
        sleep_dur = config.ITERATION_DURATION


async def stats():
    logger.success("Analytics disabled")
