import aiohttp
import asyncio
import json
import socket

from loguru import logger

from .db import database
from . import config


ipinfo = "https://ipinfo.io/{}/json"
ip_api = "http://ip-api.com/json/{}"

dns_servers = [
    "ns1.reg.ru",
    "ns2.reg.ru"
]
ident_v4 = [
    "https://v4.ident.me",
    "https://api.ipify.org"
]
ident_v6 = [
    "https://v6.ident.me",
    "https://api6.ipify.org"
]


async def get_ip(v6=False):
    async with aiohttp.ClientSession() as session:
        if v6:
            for ident in ident_v6:
                try:
                    async with session.get(ident, timeout=3) as response:
                        response = await response.text()
                        return response
                except Exception:
                    logger.error("Не получается найти IPv6")
        for ident in ident_v4:
            try:
                async with session.get(ident, timeout=3) as response:
                    response = await response.text()
                    return response
            except Exception:
                logger.error("Не получается найти IPv4")
    
    # Если ни один не сработал..
    if v6:
        return database("ipv6")
    return database("ipv4")


async def setup(forced=False):
    async def change_ip(ipv4, ipv6):
        message = ""
        "NOIP синхронизация"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"http://{config.tokens.noip.name}:{config.tokens.noip.password}"
                    "@dynupdate.no-ip.com/"
                    f'nic/update?hostname={database("noip_host")}&myip={ipv4},{ipv6}',
                    headers={
                        "User-Agent": "Trassert MinecraftServer' \
                            '/Windows 11-22000 s3pple@yandex.ru"
                    },
                ) as response:
                    logger.info(await response.text())
                    message += "Связь с NOIP выполнена.\n"
            except Exception:
                logger.error("Не удалось связаться с NOIP")
                message += "Не удалось связаться с NOIP\n"

            "REGru синхронизация"
            try:
                input_data = {
                    "username": config.tokens.reg.email,
                    "password": config.tokens.reg.password,
                    "output_content_type": "plain",
                    "domain_name": database("host"),
                }
                post = await session.post(
                    "https://api.reg.ru/api/regru2/zone/clear", data=input_data
                )
                logger.info(await post.json(content_type="text/plain"))
                message += "Связь с REGru выполнена. (1)\n"
            except Exception:
                logger.error("Не удалось связаться с REGru (1)")
                message += "Не удалось связаться с REGru (1)\n"

            try:
                input_data = {
                    "username": config.tokens.reg.email,
                    "password": config.tokens.reg.password,
                    "subdomain": "@",
                    "ipaddr": v4,
                    "output_content_type": "plain",
                    "domain_name": database("host"),
                }
                post = await session.post(
                    "https://api.reg.ru/api/regru2/zone/add_alias", data=input_data
                )
                logger.info(await post.json(content_type="text/plain"))
                message += "Связь с REGru выполнена. (2)\n"
            except Exception:
                logger.error("Не удалось связаться с REGru (2)")
                message += "Не удалось связаться с REGru (2)\n"

            try:
                input_data = {
                    "username": config.tokens.reg.email,
                    "password": config.tokens.reg.password,
                    "subdomain": "@",
                    "ipaddr": v6,
                    "output_content_type": "plain",
                    "domain_name": database("host"),
                }
                post = await session.post(
                    "https://api.reg.ru/api/regru2/zone/add_aaaa", data=input_data
                )
                logger.info(await post.json(content_type="text/plain"))
                message += "Связь с REGru выполнена. (3)\n"
            except Exception:
                logger.error("Не удалось связаться с REGru (3)")
                message += "Не удалось связаться с REGru (3)\n"

            try:
                input_data = {
                    "username": config.tokens.reg.email,
                    "password": config.tokens.reg.password,
                    "subdomain": database("ipv6_subdomain"),
                    "ipaddr": v6,
                    "output_content_type": "plain",
                    "domain_name": database("host"),
                }
                post = await session.post(
                    "https://api.reg.ru/api/regru2/zone/add_aaaa", data=input_data
                )
                logger.info(await post.json(content_type="text/plain"))
                message += "Связь с REGru выполнена. (4)\n"
            except Exception:
                logger.error("Не удалось связаться с REGru (4)")
                message += "Не удалось связаться с REGru (4)\n"
            message += f"IP: {ipv4}, V6: {ipv6}"
            return message

    v4 = await get_ip()
    v6 = await get_ip(v6=True)
    if (
        database("ipv4") != v4
    ) or (
        database("ipv6") != v6
    ) or forced:
        database("ipv4", v4)
        database("ipv6", v6)
        return await change_ip(v4, v6)


async def get_loc(ip_address: str):
    async with aiohttp.ClientSession() as session:

        async def get(ip):
            if "%" in ip:
                ip = ip.split("%")[0]
            try:
                await asyncio.sleep(1)
                async with session.get(ip_api.format(ip)) as response:
                    if response.status == 429:
                        await asyncio.sleep(2)
                        return await get(ip)
                    info = await response.json()
                    logger.info(info)
                    if info["status"] == "success":
                        return [float(info["lat"]), float(info["lon"])]
                    else:
                        raise ValueError
            except Exception:
                await asyncio.sleep(1)
                async with session.get(ipinfo.format(ip)) as response:
                    info = await response.json()
                    logger.info(info)
                    if "status" in info:
                        if info["status"] == 404:
                            raise ValueError
                    location = info.get("loc")
                    latitude, longitude = location.split(",")
                    return [float(latitude), float(longitude)]

        try:
            data = await get(ip_address)
        except (
            json.decoder.JSONDecodeError,
            ValueError,
            aiohttp.client_exceptions.ContentTypeError,
        ):
            data = await get(socket.gethostbyname(ip_address))
    return data


async def observe():
    while True:
        await setup()
        await asyncio.sleep(config.coofs.IPSleepTime)
