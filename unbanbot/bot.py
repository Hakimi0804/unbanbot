# SPDX-License-Identifier: Apache-2.0

import re
import os
import sys
import logging

from pyrogram.client import Client
from pyrogram.types import Message
from pyrogram.enums.chat_members_filter import ChatMembersFilter
from pyrogram.handlers.message_handler import MessageHandler

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    level=logging.INFO)
log: logging.Logger = logging.getLogger(__name__)

# Fetch credentials from environ
if os.getenv("BOT_CREDENTIALS") is None:
    log.fatal("Environment variable BOT_CREDENTIALS is not set!")
    sys.exit(1)


CREDENTIALS_RAW: list = os.getenv("BOT_CREDENTIALS").split(",")  # pyright: ignore
if len(CREDENTIALS_RAW) != 3:
    log.fatal("BOT_CREDENTIALS variable was incorrectly set, please refer to the documentation.")
    sys.exit(1)

CREDENTIALS: dict = {
    "api_id": CREDENTIALS_RAW[0],
    "api_hash": CREDENTIALS_RAW[1],
    "bot_token": CREDENTIALS_RAW[2],
}


async def getbanned(bot: Client, message: Message) -> None:
    if not re.match(r"^/getbanned", message.text):
        return

    banned_users: list = [x.user.id async for x in bot.get_chat_members(message.chat.id, filter=ChatMembersFilter.BANNED)]
    if len(banned_users) == 0:
        await message.reply_text("No banned users.")
    else:
        await message.reply_text(banned_users)


async def unbanall(bot: Client, message: Message) -> None:
    if not re.match(r"^/unbanall", message.text):
        return

    banned_users: list = [x.user.id async for x in bot.get_chat_members(message.chat.id, filter=ChatMembersFilter.BANNED)]

    msg = await message.reply_text(f"Unbanning {len(banned_users)} users...")
    for user in banned_users:
        log.info(f"unban: {user}")
        await bot.unban_chat_member(message.chat.id, user)

    await msg.edit_text(f"Unbanned {len(banned_users)} users.")


bot: Client = Client("src_bot",
                     api_id=CREDENTIALS["api_id"],
                     api_hash=CREDENTIALS["api_hash"],
                     bot_token=CREDENTIALS["bot_token"])

bot.add_handler(MessageHandler(getbanned), 0)
bot.add_handler(MessageHandler(unbanall), 1)
bot.run()
