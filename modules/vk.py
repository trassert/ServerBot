from loguru import logger

from vkbottle.dispatch.rules import ABCRule
from vkbottle.bot import Bot, Message

from . import config
from . import db
from . import phrase
from . import telegram


client = Bot(token=config.tokens.vk.token)


class CaseRule(ABCRule[Message]):
    def __init__(self, command: str):
        self.command = command.lower()

    async def check(self, message: Message) -> bool:
        return message.text.lower() == self.command


@client.on.message(text="/ip")
@client.on.message(text="/айпи")
@client.on.message(text="/хост")
@client.on.message(CaseRule("/host"))
async def host(message: Message):
    logger.info("Запрошен IP в ВК")
    await message.answer(phrase.server.host.format(db.database("host")))


@client.on.chat_message()
async def tg_chat(message: Message):
    try:
        user_info = await client.api.users.get(user_ids=message.from_id)
        name = "{} {}".format(user_info[0].first_name, user_info[0].last_name)
    except IndexError:
        return logger.info("Юзер не найден, пропускаем")
    logger.info(f"ВК>ТГ: {name} > {message.text}")
    return await telegram.telegram.send_message(
        config.chats.chat,
        reply_to=config.chats.topics.vk,
        message=f"**{name}**\n{message.text}",
    )
