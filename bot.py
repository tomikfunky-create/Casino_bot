#!/usr/bin/env python3
"""
🎰 Casino Bot - Main entry point
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from database import Database
from handlers import register_all_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting Casino Bot...")
    
    config = Config()
    db = Database(config.DB_PATH)
    await db.init()
    
    bot = Bot(token=config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Pass db and config to handlers via middleware
    dp["db"] = db
    dp["config"] = config
    
    register_all_handlers(dp)
    
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
