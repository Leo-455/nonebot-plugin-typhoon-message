import asyncio
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from nonebot import logger

from .cma import handle_tcpq40, handle_wtpq20
from .model import TyphoonMessage, MessageMetadata
from .constants import UA, WEBPAGE_URL, MSG_BASE_URL


async def main() -> None:
    cache_msg_id = []
    async with httpx.AsyncClient() as client:
        if cache_msg_id == []:
            try:
                r = await client.get(url=WEBPAGE_URL, headers=UA, timeout=60)
                r.raise_for_status()
                # cache_msg_id = get_cma_ty_msgid(r)
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(e)

        while True:
            await asyncio.sleep(10)
            try:
                r = await client.get(url=WEBPAGE_URL, headers=UA, timeout=60)
                r.raise_for_status()
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                logger.warning(e)
                continue
            msg_ids = get_cma_ty_msgid(r)
            logger.debug(f"Get Msg Id List Success{msg_ids}")
            for msg_id in msg_ids:
                if msg_id not in cache_msg_id:
                    try:
                        r = await client.get(url=f"{MSG_BASE_URL}{msg_id}",
                                             headers=UA, timeout=60)
                        r.raise_for_status()
                        logger.success(f"Get Message {msg_id} success")
                    except (httpx.RequestError, httpx.HTTPStatusError) as e:
                        logger.warning(e)
                        continue
                    raw_ty_msg = get_cma_ty_raw_msg(r)
                    msg_type = raw_ty_msg[1].split()[0]
                    try:
                        match msg_type:
                            case "WTPQ20":
                                ty_data = handle_wtpq20(raw_ty_msg)
                            case "TCPQ40":
                                ty_data = handle_tcpq40(raw_ty_msg)
                            # case "WHCI40":
                            #     ty_data = handle_whci40(raw_ty_msg)
                            # case "WSCI40":
                            #     ty_data = handle_wsci40(raw_ty_msg)
                            case _:
                                continue
                        logger.success(f"Type {msg_type} Message {msg_id} paese success")
                    except Exception as e:
                        logger.error(f"台风报文解析异常{e}")# 这里要不要把错误捕获放到函数里面？
                        continue
                    logger.debug(ty_data)
                    msg_meta_data = MessageMetadata(
                        msg_id=msg_id, source="CMA", msg_type=msg_type
                        )
                    message = TyphoonMessage(
                        metadata=msg_meta_data,
                        ty_data=ty_data,
                        raw_msg=raw_ty_msg
                    )
                    json_text = message.model_dump_json(
                        indent=4,
                        by_alias=True,
                    )
                    Path("typhoon_message.json").write_text(
                        json_text,
                        encoding="utf-8",
                    )
                    cache_msg_id.append(msg_id)


def get_cma_ty_msgid(response) -> list:
    soup = BeautifulSoup(response.text, "html.parser")
    ids = [element.get("data-id")
           for element in soup.select("p.time")
           if element.get("data-id")]
    return ids

def get_cma_ty_raw_msg(response) -> list:
    soup = BeautifulSoup(response.text, "html.parser")
    p = soup.find("p")

    lines = [
        line.strip()
        for line in p.get_text(separator="\n").splitlines()
        if line.strip()
    ]
    return lines
