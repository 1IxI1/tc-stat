import asyncio
import os
import random
import time

from aiohttp import client as aiohttp_client
from dotenv import load_dotenv
from loguru import logger
from prometheus_client import Counter, Histogram

TOGGLE_PERIOD = 20

# this is used to randomize parameters we're passing in different methods
# we may replace those values with random data from any method at any moment.
# the only point is keeping it valid.
# like user may request any account and any block and so do we
common_data = {
    "last_mc_block": 42093840,
    "random_account": "EQA-X_yo3fzzbDbJ_0bzFWKqtRuZFIRa1sJsveZJ1YpViO3r",
}


load_dotenv()
headers = {"X-Api-Key": f"{os.getenv('TONCENTER_API_KEY')}"}


def worker(
    method: str, v: str = "v2", params: dict | None = None, metric_name: str = ""
):
    global common_data
    REQUEST_TIME = Histogram(f"{metric_name or method}_time", "Request processing time")
    REQUEST_SUCCESS = Counter(
        f"{metric_name or method}_success", "Count of successful requests"
    )
    REQUEST_FAILURE = Counter(
        f"{metric_name or method}_failure", "Count of failed requests"
    )

    def decorator(process_response):
        async def wrapper():
            while True:
                try:
                    # fill in fresh random data
                    if params:
                        for key in params:
                            if params[key] == "random_account":
                                params[key] = common_data["random_account"]
                            if params[key] == "random_block":
                                params[key] = random.randint(
                                    33000000, common_data["last_mc_block"]
                                )
                            if params[key] == "last_mc_block":
                                params[key] = common_data["last_mc_block"]

                    # make request
                    async with aiohttp_client.ClientSession() as session:
                        t = time.time()
                        with REQUEST_TIME.time():
                            async with session.get(
                                f"https://toncenter.com/api/{v}/{method}",
                                params=params,
                                headers=headers,
                            ) as response:
                                # handle response
                                response.raise_for_status()
                                response_json = await response.json()
                                # custom processing
                                await process_response(response_json)
                                t2 = time.time()
                                logger.debug(f"ok on {metric_name or method} - {t2-t}s")
                                REQUEST_SUCCESS.inc()
                except Exception as e:
                    REQUEST_FAILURE.inc()
                    logger.error(f"failed {metric_name or method}: {e}")

                await asyncio.sleep(TOGGLE_PERIOD)

        return wrapper

    return decorator


@worker("getMasterchainInfo")
async def get_masterchain_info(response_json):
    common_data["last_mc_block"] = int(
        response_json.get("result").get("last").get("seqno")
    )


@worker("getAddressBalance", params={"address": "random_account"})
async def get_address_balance(response_json):
    int(response_json.get("result"))


@worker(
    "transactionsByMasterchainBlock",
    v="v3",
    params={"seqno": "random_block", "limit": 1000},
)
async def get_transactions_by_mc_block(response_json):
    if not response_json.get("transactions"):
        logger.error(response_json)
        raise Exception("no transactions")


@worker(
    "transactionsByMasterchainBlock",
    v="v3",
    params={"seqno": "last_mc_block", "limit": 1000},
    metric_name="transactionsByMasterchainBlockLast",
)
async def get_transactions_by_mc_block_last(response_json):
    random_tx = random.choice(response_json.get("transactions"))
    common_data["random_account"] = random_tx["account"]
    logger.debug(common_data)


@worker("shards", params={"seqno": "random_block"})
async def get_shards(response_json):
    if not response_json.get("result").get("shards"):
        logger.error(response_json)
        raise Exception("no shards")


@worker("shards", params={"seqno": "last_mc_block"}, metric_name="shardsLast")
async def get_shards_last(response_json):
    if not response_json.get("result").get("shards"):
        logger.error(response_json)
        raise Exception("no shards")
