import asyncio

from loguru import logger

from app.prometheus import start_prometheus
from app.worker import (
    get_address_balance,
    get_masterchain_info,
    get_shards,
    get_shards_last,
    get_transactions_by_mc_block,
    get_transactions_by_mc_block_last,
)

logger.add(
    "logs/tc-stat.log",
    rotation="1 day",
    retention="7 days",
    level="INFO",
)


async def main():
    start_prometheus()

    logger.info("Starting workers for TON Center APIs...")

    try:
        await asyncio.gather(
            get_masterchain_info(),
            get_address_balance(),
            get_transactions_by_mc_block(),
            get_transactions_by_mc_block_last(),
            get_shards(),
            get_shards_last(),
        )
    except KeyboardInterrupt:
        logger.info("Exiting with keyboard interrupt")


if __name__ == "__main__":
    asyncio.run(main())
