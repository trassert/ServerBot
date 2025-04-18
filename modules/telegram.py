import asyncio
import re

from os import path
from loguru import logger
from random import choice, random, randint
from datetime import datetime

from telethon.tl.types import (
    ReplyInlineMarkup,
    KeyboardButtonRow,
    KeyboardButtonCallback,
)
from telethon import events
from telethon.sync import TelegramClient
from telethon import errors as TGErrors
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.custom import Message

from . import config
from . import db
from . import phrase
from . import dice
from . import ip
from . import vk
from . import chart
from . import crosssocial
from . import ai

from .system_info import get_system_info
from .mcrcon import MinecraftClient
from .formatter import decline_number, remove_section_marks


client = TelegramClient(
    session=path.join('db', 'bot'),
    api_id=config.tokens.bot.id,
    api_hash=config.tokens.bot.hash,
    device_model="Bot",
    system_version="4.16.30-vxCUSTOM",
    use_ipv6=True
)


crocodile_path = path.join("db", "crocodile", "all.txt")
crocodile_blacklist_path = path.join("db", "crocodile", "blacklist.txt")


'Вспомогательные функции'


async def get_name(id, push=True, minecraft=False):
    "Выдает @пуш, если нет - имя + фамилия"
    try:
        if minecraft is True:
            nick = db.nicks(id=int(id)).get()
            if nick is not None:
                return (
                    f"[{nick}]"
                    f"(tg://user?id={id})"
                )
        user_name = await client.get_entity(int(id))
        if user_name.username is None or push is False:
            if user_name.last_name is None:
                return (
                    f"[{user_name.first_name}]"
                    f"(tg://user?id={id})"
                )
            else:
                return (
                    f"[{user_name.first_name} {user_name.last_name}]"
                    f"(tg://user?id={id})"
                )
        else:
            return "@" + user_name.username
    except Exception as e:
        return 'Неопознанный персонаж'


'Кнопки бота'


@client.on(events.CallbackQuery())
async def callback_action(event: events.CallbackQuery.Event):
    data = event.data.decode('utf-8').split('.')
    logger.info(f'{event.sender_id} отправил КБ - {data}')
    if data[0] == 'crocodile':
        if data[1] == 'start':
            if db.database('crocodile_super_game') == 1:
                return await event.answer(
                    phrase.crocodile.super_game_here, alert=True
                )
            if db.database("current_game") != 0:
                return await event.answer(phrase.crocodile.no, alert=True)
            with open(
                crocodile_path, 'r', encoding='utf8'
            ) as f:
                word = choice(f.read().split('\n'))
            unsec = ""
            for x in list(word):
                if x.isalpha():
                    unsec += "_"
                elif x == " ":
                    unsec += x
            db.database(
                "current_game",
                {"hints": [], "word": word, "unsec": unsec}
            )
            client.add_event_handler(
                crocodile_hint,
                events.NewMessage(pattern=r'(?i)^/подсказка')
            )
            client.add_event_handler(
                crocodile_handler,
                events.NewMessage(chats=event.chat_id)
            )
            return await event.reply(phrase.crocodile.up)
        elif data[1] == 'stop':
            entity = await client.get_entity(event.sender_id)
            user = f'@{entity.username}' if entity.username \
                else entity.first_name + " " + entity.last_name
            if db.database("current_game") == 0:
                return await event.answer(
                    phrase.crocodile.already_down, alert=True
                )
            if db.database('crocodile_super_game') == 1:
                return await event.answer(
                    phrase.crocodile.super_game_here, alert=True
                )
            bets_json = db.database('crocodile_bets')
            if bets_json != {}:
                bets = round(sum(list(bets_json.values())) / 2)
                bets = 1 if bets < 1 else bets
                sender_balance = db.get_money(event.sender_id)
                if sender_balance < bets:
                    return await event.answer(
                        phrase.crocodile.not_enough.format(
                            decline_number(sender_balance, 'изумруд')
                        ),
                        alert=True
                    )
                db.add_money(event.sender_id, -bets)
            word = db.database("current_game")["word"]
            db.database("current_game", 0)
            db.database('crocodile_last_hint', 0)
            client.remove_event_handler(crocodile_hint)
            client.remove_event_handler(crocodile_handler)
            if bets_json != {}:
                return await event.reply(
                    phrase.crocodile.down_payed.format(
                        user=user,
                        money=decline_number(
                            bets,
                            'изумруд'
                        ),
                        word=word
                    )
                )
            return await event.reply(phrase.crocodile.down.format(word))
    elif data[0] == 'shop':
        if int(data[-1]) != db.database("shop_version"):
            return await event.answer(phrase.shop.old, alert=True)
        nick = db.nicks(id=event.sender_id).get()
        if nick is None:
            return await event.answer(phrase.nick.not_append, alert=True)
        shop = db.get_shop()
        del shop['theme']
        balance = db.get_money(event.sender_id)
        items = list(shop.keys())
        item = shop[items[int(data[1])]]
        if balance < item['price']:
            return await event.answer(
                phrase.money.not_enough.format(
                    decline_number(balance, 'изумруд')
                ),
                alert=True
            )
        try:
            async with MinecraftClient(
                host=db.database('ipv4'),
                port=config.tokens.rcon.port,
                password=config.tokens.rcon.password
            ) as rcon:
                command = f'invgive {nick} {item["name"]} {item["value"]}'
                logger.info(f'Выполняется команда: {command}')
                await rcon.send(command)
        except TimeoutError:
            return await event.answer(phrase.shop.timeout, alert=True)
        db.add_money(event.sender_id, -item['price'])
        return await event.answer(
            phrase.shop.buy.format(
                items[int(data[1])]
            ),
            alert=True
        )
    elif data[0] == 'word':
        user_name = await get_name(data[3])
        if data[1] == 'yes':
            with open(
                crocodile_path,
                'a',
                encoding='utf-8'
            ) as f:
                f.write(f'\n{data[2]}')
            db.add_money(data[3], config.coofs.WordRequest)
            await client.send_message(
                config.chats.chat,
                phrase.word.success.format(
                    word=data[2],
                    user=user_name,
                    money=decline_number(
                        config.coofs.WordRequest, 'изумруд'
                    )
                )
            )
            return await client.edit_message(
                event.sender_id,
                event.message_id,
                phrase.word.add
            )
        if data[1] == 'no':
            with open(
                crocodile_blacklist_path,
                'a',
                encoding='utf-8'
            ) as f:
                f.write(f'\n{data[2]}')
            await client.send_message(
                config.chats.chat,
                phrase.word.no.format(
                    word=data[2],
                    user=user_name
                )
            )
            return await client.edit_message(
                event.sender_id,
                event.message_id,
                phrase.word.noadd
            )
    elif data[0] == 'nick':
        if event.sender_id != int(data[2]):
            return await event.answer(phrase.not_for_you)
        if db.nicks(id=event.sender_id).get() == data[1]:
            return await event.answer(phrase.nick.already_you, alert=True)
        balance = db.get_money(event.sender_id)
        if balance - config.coofs.PriceForChangeNick < 0:
            return await event.answer(
                phrase.money.not_enough.format(
                    decline_number(balance, 'изумруд')
                )
            )
        db.add_money(event.sender_id, -config.coofs.PriceForChangeNick)
        db.nicks(data[1], event.sender_id).link()
        user_name = await get_name(data[2])
        return await event.reply(
            phrase.nick.buy_nick.format(
                user=user_name,
                price=decline_number(
                    config.coofs.PriceForChangeNick, 'изумруд'
                )
            )
        )
    elif data[0] == 'casino':
        if data[1] == 'start':
            balance = db.get_money(event.sender_id)
            if balance < config.coofs.PriceForCasino:
                return await event.answer(
                    phrase.money.not_enough.format(
                        decline_number(balance, 'изумруд')
                    ), alert=True
                )
            db.add_money(event.sender_id, -config.coofs.PriceForCasino)
            await event.answer(phrase.casino.do)
            response = []

            async def check(message):
                if event.sender_id != message.sender_id:
                    return
                if getattr(message, 'media', None) is None:
                    return
                if getattr(message.media, 'emoticon', None) is None:
                    return
                if message.media.emoticon != '🎰':
                    return
                pos = dice.get(message.media.value)
                if (
                    pos[0] == pos[1]
                ) and (
                    pos[1] == pos[2]
                ):
                    logger.info(
                        f'{message.sender_id} - победил в казино'
                    )
                    db.add_money(
                        message.sender_id,
                        config.coofs.PriceForCasino*config.coofs.CasinoWinRatio
                    )
                    await asyncio.sleep(2)
                    await message.reply(
                        phrase.casino.win.format(
                            config.coofs.PriceForCasino*config.coofs.CasinoWinRatio
                        )
                    )
                elif (
                    pos[0] == pos[1]
                ) or (
                    pos[1] == pos[2]
                ):
                    db.add_money(
                        message.sender_id,
                        config.coofs.PriceForCasino
                    )
                    await asyncio.sleep(2)
                    await message.reply(phrase.casino.partially)
                else:
                    logger.info(f'{message.sender_id} проиграл в казино')
                    await asyncio.sleep(2)
                    await message.reply(phrase.casino.lose)
                client.remove_event_handler(check)
                logger.info('Снят обработчик казино')
                response.append(1)

            client.add_event_handler(
                check,
                events.NewMessage(config.chats.chat)
            )
            await asyncio.sleep(config.coofs.CasinoSleepTime)
            if 1 not in response:
                return await event.answer(
                    phrase.casino.timeout.format(
                        await get_name(event.sender_id)
                    )
                )
    elif data[0] == 'state':
        if data[1] == 'pay':
            nick = db.nicks(id=event.sender_id).get()
            if nick is None:
                return await event.answer(
                    phrase.state.not_connected,
                    alert=True
                )
            balance = db.get_money(event.sender_id)
            state = db.state(data[2])
            if state.price > balance:
                return await event.answer(
                    phrase.money.not_enough.format(
                        decline_number(balance, 'изумруд')
                    ),
                    alert=True
                )
            db.add_money(event.sender_id, -state.price)
            state.change('money', state.money+state.price)
            players = state.players
            players.append(event.sender_id)
            state.change("players", players)
            await client.send_message(
                entity=config.chats.chat,
                message=phrase.state.new_player.format(
                    state=state.name,
                    player=nick
                ),
                reply_to=config.chats.topics.rp
            )
            if (
                state.type == 0
            ) and (
                len(players) >= config.coofs.Type1Players
            ):
                await client.send_message(
                    entity=config.chats.chat,
                    message=phrase.state.up.format(
                        name=state.name,
                        type='Государство'
                    ),
                    reply_to=config.chats.topics.rp
                )
                state.change('type', 1)
            if (
                state.type == 1
            ) and (
                len(players) >= config.coofs.Type2Players
            ):
                await client.send_message(
                    entity=config.chats.chat,
                    message=phrase.state.up.format(
                        name=state.name,
                        type='Империя'
                    ),
                    reply_to=config.chats.topics.rp
                )
                state.change('type', 2)
            return await event.answer(
                phrase.state.admit.format(state.name),
                alert=True
            )
    else:
        pass


'Обработчики событий'


@client.on(events.ChatAction(chats=config.chats.chat))
async def chat_action(event):
    # Если пользователь ушёл из чата
    if event.user_left:
        user_name = await get_name(event.user_id)
        return await client.send_message(
            config.chats.chat,
            phrase.leave_message.format(
                user_name
            )
        )


'Обработчик вк-топика'


@client.on(events.NewMessage(config.chats.chat))
async def vk_chat(event):

    async def send():
        if event.text == '':
            return logger.info('Пустое сообщение')
        user_name = await client.get_entity(event.sender_id)
        if user_name.last_name is None:
            user_name = user_name.first_name
        else:
            user_name = user_name.first_name + " " + user_name.last_name
        logger.info(f"ТГ>ВК: {user_name} > {event.text}")
        await vk.client.api.messages.send(
            chat_id=config.tokens.vk.chat_id,
            message=f'{user_name}: {event.text}',
            random_id=0
        )

    if event.reply_to_msg_id == config.chats.topics.vk:
        return await send()
    if event.reply_to is not None:
        if event.reply_to.reply_to_top_id == config.chats.topics.vk:
            return await send()


'Обработчики команд'


@client.on(events.NewMessage(config.chats.chat, pattern=r'(?i)^/казино$'))
async def casino(event: Message):
    keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="💎 Внести изумруды", data=b"casino.start"
                    )
                ]
            )
        ]
    )
    return await event.reply(
        phrase.casino.start.format(config.coofs.PriceForCasino),
        buttons=keyboard
    )


@client.on(events.NewMessage(pattern=r'(?i)^\+чек(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^\+ticket(.*)'))
async def do_ticket(event: Message):
    if not event.is_private:
        return await event.reply(phrase.ticket.in_chat)
    arg = event.pattern_match.group(1).strip()
    if arg == '':
        return await event.reply(phrase.ticket.no_value)
    try:
        arg = int(arg)
        if arg < 1:
            return await event.reply(phrase.ticket.bigger_than_zero)
    except ValueError:
        return await event.reply(phrase.ticket.not_int)
    balance = db.get_money(event.sender_id)
    if balance < arg:
        return await event.reply(
            phrase.money.not_enough.format(
                decline_number(
                    balance, 'изумруд'
                )
            )
        )
    db.add_money(event.sender_id, -arg)
    ticket_id = db.ticket.add(event.sender_id, arg)
    return await event.reply(
        phrase.ticket.added.format(
            value=arg,
            author=await get_name(event.sender_id),
            id=ticket_id
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/чек(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/ticket(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/активировать(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^активировать(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/activate(.*)'))
async def get_ticket(event: Message):
    arg = event.pattern_match.group(1).strip()
    if arg == '':
        return await event.reply(phrase.ticket.no_value)
    ticket_info = db.ticket.get(arg)
    if ticket_info is None:
        return await event.reply(phrase.ticket.no_such)
    db.add_money(event.sender_id, ticket_info['value'])
    db.ticket.delete(arg)
    return await event.reply(
        phrase.ticket.got.format(
            author=await get_name(ticket_info['author']),
            value=decline_number(ticket_info['value'], 'изумруд')
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/топ соо(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/топ сообщений(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/топ в чате(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/актив сервера(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/мчат(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/мстат(.*)'))
async def active_check(event: Message):
    arg = event.pattern_match.group(1).strip()
    if arg in phrase.all_arg:
        text = phrase.stat.chat.format('всё время')
        all_data = db.statistic().get_all(all_days=True)
        chart.create_plot(db.statistic().get_raw())
        n = 1
        for data in all_data:
            if n > config.coofs.MaxStatPlayers:
                break
            text += f'{n}. {data[0]} - {data[1]}\n'
            n += 1
        return await client.send_file(
            event.chat_id,
            chart.chart_path,
            caption=text
        )
    try:
        days = int(arg)
        text = phrase.stat.chat.format(decline_number(days, 'день'))
        all_data = db.statistic(days=days).get_all()
        if days >= 7:
            chart.create_plot(db.statistic(days=days).get_raw())
            n = 1
            for data in all_data:
                if n > config.coofs.MaxStatPlayers:
                    break
                text += f'{n}. {data[0]} - {data[1]}\n'
                n += 1
            return await client.send_file(
                event.chat_id,
                chart.chart_path,
                caption=text
            )
    except ValueError:
        text = phrase.stat.chat.format('день')
        all_data = db.statistic().get_all()
    if all_data == []:
        return await event.reply(phrase.stat.empty)
    n = 1
    for data in all_data:
        if n > config.coofs.MaxStatPlayers:
            break
        text += f'{n}. {data[0]} - {data[1]}\n'
        n += 1
    return await event.reply(text)


@client.on(events.NewMessage(pattern=r'(?i)^/linknick(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/привязать(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^привязать(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/новый ник(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/линкник(.*)'))
async def link_nick(event: Message):
    nick = event.pattern_match.group(1).strip()
    if len(nick) < 4:
        return await event.reply(phrase.nick.too_short)
    if len(nick) > 16:
        return await event.reply(phrase.nick.too_big)
    if not re.match("^[A-Za-z0-9_]*$", nick):
        return await event.reply(phrase.nick.invalid)

    if db.nicks(nick=nick).get() is not None:
        if db.nicks(id=event.sender_id).get() == nick:
            return await event.reply(phrase.nick.already_you)
        return await event.reply(phrase.nick.taken)
    elif db.nicks(id=event.sender_id).get() is not None:
        if db.nicks(id=event.sender_id).get() == nick:
            return await event.reply(phrase.nick.already_you)
        keyboard = ReplyInlineMarkup(
            [
                KeyboardButtonRow(
                    [
                        KeyboardButtonCallback(
                            text="✅ Сменить",
                            data=f'nick.{nick}.{event.sender_id}'.encode()
                        )
                    ]
                )
            ]
        )
        return await event.reply(
            phrase.nick.already_have.format(
                price=decline_number(
                    config.coofs.PriceForChangeNick, 'изумруд'
                )
            ),
            buttons=keyboard
        )

    db.add_money(event.sender_id, config.coofs.LinkGift)
    db.nicks(nick, event.sender_id).link()
    return await event.reply(
        phrase.nick.success.format(
            decline_number(config.coofs.LinkGift, 'изумруд')
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/shop'))
@client.on(events.NewMessage(pattern=r'(?i)^/шоп$'))
@client.on(events.NewMessage(pattern=r'(?i)^/магазин$'))
@client.on(events.NewMessage(pattern=r'(?i)^магазин$'))
@client.on(events.NewMessage(pattern=r'(?i)^shop$'))
@client.on(events.NewMessage(pattern=r'(?i)^шоп$'))
async def shop(event: Message):
    version = db.database('shop_version')
    keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="1️⃣", data=f"shop.0.{version}".encode()
                    ),
                    KeyboardButtonCallback(
                        text="2️⃣", data=f"shop.1.{version}".encode()
                    ),
                    KeyboardButtonCallback(
                        text="3️⃣", data=f"shop.2.{version}".encode()
                    ),
                    KeyboardButtonCallback(
                        text="4️⃣", data=f"shop.3.{version}".encode()
                    ),
                    KeyboardButtonCallback(
                        text="5️⃣", data=f"shop.4.{version}".encode()
                    ),
                ]
            )
        ]
    )
    shop = db.get_shop()
    theme = shop['theme']
    del shop['theme']
    items = list(shop.keys())
    return await event.reply(
        phrase.shop.shop.format(
            trade_1=items[0],
            value_1=f' ({shop[items[0]]['value']})' if
            shop[items[0]]['value'] != 1 else '',
            price_1=decline_number(shop[items[0]]['price'], 'изумруд'),

            trade_2=items[1],
            value_2=f' ({shop[items[1]]['value']})' if
            shop[items[1]]['value'] != 1 else '',
            price_2=decline_number(shop[items[1]]['price'], 'изумруд'),

            trade_3=items[2],
            value_3=f' ({shop[items[2]]['value']})' if
            shop[items[2]]['value'] != 1 else '',
            price_3=decline_number(shop[items[2]]['price'], 'изумруд'),

            trade_4=items[3],
            value_4=f' ({shop[items[3]]['value']})' if
            shop[items[3]]['value'] != 1 else '',
            price_4=decline_number(shop[items[3]]['price'], 'изумруд'),

            trade_5=items[4],
            value_5=f' ({shop[items[4]]['value']})' if
            shop[items[4]]['value'] != 1 else '',
            price_5=decline_number(shop[items[4]]['price'], 'изумруд'),

            quote=choice(phrase.shop_quotes[theme]['quotes']),
            emo=phrase.shop_quotes[theme]['emo']
        ),
        buttons=keyboard,
        parse_mode="html"
    )


@client.on(events.NewMessage(pattern=r'(?i)^/хост$'))
@client.on(events.NewMessage(pattern=r'(?i)^/host$'))
@client.on(events.NewMessage(pattern=r'(?i)^/айпи$'))
@client.on(events.NewMessage(pattern=r'(?i)^/ip$'))
async def host(event: Message):
    await event.reply(phrase.server.host.format(db.database("host")))


@client.on(events.NewMessage(pattern=r'(?i)^/серв$'))
@client.on(events.NewMessage(pattern=r'(?i)^/сервер'))
@client.on(events.NewMessage(pattern=r'(?i)^/server'))
async def sysinfo(event: Message):
    await event.reply(get_system_info())


@client.on(events.NewMessage(pattern=r'(?i)^/помощь$'))
@client.on(events.NewMessage(pattern=r'(?i)^/help'))
@client.on(events.NewMessage(pattern=r'(?i)^/команды$'))
@client.on(events.NewMessage(pattern=r'(?i)^/commands$'))
@client.on(events.NewMessage(pattern=r'(?i)^команды$'))
@client.on(events.NewMessage(pattern=r'(?i)^бот помощь$'))
async def help(event: Message):
    return await event.reply(phrase.help.comm, link_preview=True)


@client.on(events.NewMessage(pattern=r'(?i)^/start$'))
@client.on(events.NewMessage(pattern=r'(?i)^/старт$'))
async def start(event: Message):
    return await event.reply(
        phrase.start.format(
            await get_name(event.sender_id, push=False)
        ),
        silent=True
    )


@client.on(events.NewMessage(pattern=r'(?i)^/пинг(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/ping(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^пинг(.*)'))
async def ping(event: Message):
    text = await crosssocial.ping(
        event.pattern_match.group(1).strip(),
        event.date.timestamp()
    )
    if text is None: return
    return await event.reply(text)


@client.on(events.NewMessage(pattern=r'(?i)^/крокодил$'))
@client.on(events.NewMessage(pattern=r'(?i)^/crocodile$'))
@client.on(events.NewMessage(pattern=r'(?i)^старт крокодил$'))
async def crocodile(event: Message):
    if not event.chat_id == config.chats.chat:
        return await event.reply(phrase.crocodile.chat)
    else:
        pass
    if db.database("current_game") == 0:
        keyboard = ReplyInlineMarkup(
            [
                KeyboardButtonRow(
                    [
                        KeyboardButtonCallback(
                            text="✅ Играть", data=b"crocodile.start"
                        ),
                        KeyboardButtonCallback(
                            text="❌ Остановить игру",
                            data=b"crocodile.stop"
                        )
                    ]
                )
            ]
        )
        return await event.reply(phrase.crocodile.game, buttons=keyboard)
    else:
        keyboard = ReplyInlineMarkup(
            [
                KeyboardButtonRow(
                    [
                        KeyboardButtonCallback(
                            text="❌ Остановить игру",
                            data=b"crocodile.stop"
                        )
                    ]
                )
            ]
        )
        return await event.reply(phrase.crocodile.no, buttons=keyboard)


@client.on(events.NewMessage(pattern=r'(?i)^/ставка(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/крокоставка(.*)'))
async def crocodile_bet(event: Message):
    try:
        bet = int(
            event.pattern_match.group(1).strip()
        )
        if bet < db.database('min_bet'):
            return await event.reply(
                phrase.money.min_count.format(
                    decline_number(db.database('min_bet'), 'изумруд')
                )
            )
        elif bet > db.database('max_bet'):
            return await event.reply(
                phrase.money.max_count.format(
                    decline_number(db.database('max_bet'), 'изумруд')
                )
            )
    except IndexError:
        bet = db.database('min_bet')
    except ValueError:
        return await event.reply(
            phrase.money.nan_count
        )
    sender_balance = db.get_money(event.sender_id)
    if sender_balance < bet:
        return await event.reply(
            phrase.money.not_enough.format(
                decline_number(sender_balance, 'изумруд')
            )
        )
    if db.database("current_game") != 0:
        return await event.reply(
            phrase.crocodile.no
        )
    all_bets = db.database('crocodile_bets')
    if str(event.sender_id) in all_bets:
        return await event.reply(
            phrase.crocodile.bet_already
        )
    db.add_money(event.sender_id, -bet)
    all_bets[str(event.sender_id)] = bet
    db.database('crocodile_bets', all_bets)
    return await event.reply(
        phrase.crocodile.bet.format(
            decline_number(bet, 'изумруд')
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/суперигра(.*)'))
async def super_game(event: Message):
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    arg = event.pattern_match.group(1).strip()
    bets = db.database('crocodile_bets')
    bets[str(config.tokens.bot.creator)] = 50
    db.database('crocodile_bets', bets)
    db.database('crocodile_super_game', 1)
    db.database('max_bet', 100)
    db.database('min_bet', 50)
    await client.send_message(
        config.chats.chat, phrase.crocodile.super_game_wait
    )
    await asyncio.sleep(60)
    db.database(
        'current_game',
        {
            'hints': [],
            'unsec': '_'*len(arg),
            'word': arg
        }
    )
    client.add_event_handler(
        crocodile_hint,
        events.NewMessage(pattern=r'(?i)^/подсказка')
    )
    client.add_event_handler(
        crocodile_handler,
        events.NewMessage(chats=config.chats.chat)
    )
    return await client.send_message(
        config.chats.chat, phrase.crocodile.super_game
    )


@client.on(events.NewMessage(pattern=r'(?i)^/ии(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/ai(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^ии(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/бот(.*)'))
async def gemini(event: Message):
    arg = event.pattern_match.group(1).strip()
    if len(arg) < 1:
        return await event.reply(phrase.no.response)
    response = await ai.response(arg)
    if response is None:
        return await event.reply(phrase.server.overload)
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            await event.reply(response[x:x+4096])
    else:
        return await event.reply(response)


@client.on(events.NewMessage(pattern=r'//(.+)'))
async def mcrcon(event: Message):
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    command = event.pattern_match.group(1).strip()
    logger.info(f'Выполняется команда: {command}')
    try:
        async with MinecraftClient(
            host=db.database('ipv4'),
            port=config.tokens.rcon.port,
            password=config.tokens.rcon.password
        ) as rcon:
            resp = remove_section_marks(await rcon.send(command))
            logger.info(f'Ответ команды:\n{resp}')
            if len(resp) > 4096:
                for x in range(0, len(resp), 4096):
                    await event.reply(f'```{resp[x:x+4096]}```')
            else:
                return await event.reply(f'```{resp}```')
    except TimeoutError:
        return await event.reply(phrase.server.stopped)


@client.on(events.NewMessage(pattern=r'(?i)^\+вт\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^\-вт\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^\+wl\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^\-wl\s(.+)'))
async def whitelist(event: Message):
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    if event.text[0] == '-':
        command = f'swl remove {event.pattern_match.group(1).strip()}'
    else:
        command = f'swl add {event.pattern_match.group(1).strip()}'
    logger.info(f'Выполняется команда: {command}')
    try:
        async with MinecraftClient(
            host=db.database('ipv4'),
            port=config.tokens.rcon.port,
            password=config.tokens.rcon.password
        ) as rcon:
            resp = remove_section_marks(await rcon.send(command))
            logger.info(f'Ответ команды:\n{resp}')
            return await event.reply(f'✍🏻 : {resp}')
    except TimeoutError:
        return await event.reply(phrase.server.stopped)


@client.on(events.NewMessage(pattern=r"\+cтафф(.*)"))
@client.on(events.NewMessage(pattern=r"\+staff(.*)"))
async def add_staff(event: Message):
    if event.sender_id != config.tokens.bot.creator:
        return await event.reply(phrase.perms.no)
    try:
        tag = event.pattern_match.group(1).strip()
        user = await client(
            GetFullUserRequest(tag)
        )
        user = user.full_user.id
    except IndexError:
        reply_to_msg = event.reply_to_msg_id
        if reply_to_msg:
            reply_message = await event.get_reply_message()
            user = reply_message.sender_id
            entity = await client.get_entity(user)
            if entity.username is None:
                if entity.last_name is None:
                    tag = entity.first_name
                else:
                    tag = entity.first_name + " " + entity.last_name
            else:
                tag = f'@{entity.username}'
        else:
            return await event.reply(
                phrase.money.no_people
            )
    admins = db.database('admins_id')
    admins.append(user)
    db.database('admins_id', admins)
    return await event.reply(
        phrase.perms.admin_add.format(nick=tag, id=user)
    )


@client.on(events.NewMessage(pattern=r"\-cтафф(.*)"))
@client.on(events.NewMessage(pattern=r"\-staff(.*)"))
async def del_staff(event: Message):
    if event.sender_id != config.tokens.bot.creator:
        return await event.reply(phrase.perms.no)
    try:
        tag = event.pattern_match.group(1).strip()
        user = await client(
            GetFullUserRequest(tag)
        )
        user = user.full_user.id
    except IndexError:
        reply_to_msg = event.reply_to_msg_id
        if reply_to_msg:
            reply_message = await event.get_reply_message()
            user = reply_message.sender_id
            entity = await client.get_entity(user)
            if entity.username is None:
                if entity.last_name is None:
                    tag = entity.first_name
                else:
                    tag = entity.first_name + " " + entity.last_name
            else:
                tag = f'@{entity.username}'
        else:
            return await event.reply(
                phrase.money.no_people
            )
    admins = db.database('admins_id')
    while user in admins:
        admins.remove(user)
    db.database('admins_id', admins)
    return await event.reply(phrase.perms.admin_del)


@client.on(events.NewMessage(pattern=r'(?i)^/топ игроков$'))
@client.on(events.NewMessage(pattern=r'(?i)^/topplayers$'))
@client.on(events.NewMessage(pattern=r'(?i)^/bestplayers$'))
@client.on(events.NewMessage(pattern=r'(?i)^/toppt$'))
async def server_top_list(event: Message):
    try:
        async with MinecraftClient(
            host=db.database('ipv4'),
            port=config.tokens.rcon.port,
            password=config.tokens.rcon.password
        ) as rcon:
            await event.reply(
                remove_section_marks(
                    await rcon.send('playtime top')
                ).replace(
                    '[i] Лидеры по времени на сервере',
                    phrase.stat.server
                ).replace(
                    '***',
                    ''
                )
            )
    except TimeoutError:
        return await event.reply(phrase.server.stopped)


@client.on(events.NewMessage(pattern=r'(?i)^/баланс$'))
@client.on(events.NewMessage(pattern=r'(?i)^баланс$'))
@client.on(events.NewMessage(pattern=r'(?i)^/wallet'))
@client.on(events.NewMessage(pattern=r'(?i)^wallet$'))
@client.on(events.NewMessage(pattern=r'(?i)^/мой баланс$'))
@client.on(events.NewMessage(pattern=r'(?i)^мой баланс$'))
async def get_balance(event: Message):
    return await event.reply(
        phrase.money.wallet.format(
            decline_number(
                db.get_money(event.sender_id), 'изумруд'
            )
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/изменить баланс(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/change balance(.*)'))
async def add_balance(event: Message):
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    args = event.pattern_match.group(1).strip().split()
    try:
        tag = args[1]
        user = await client(
            GetFullUserRequest(tag)
        )
    except IndexError:
        return await event.reply(
            phrase.money.no_people+phrase.money.change_balance_use
        )
    except ValueError:
        return await event.reply(
            phrase.money.no_such_people+phrase.money.change_balance_use
        )
    try:
        new = int(args[0])
    except IndexError:
        return await event.reply(
            phrase.money.no_count+phrase.money.change_balance_use
        )
    except ValueError:
        return await event.reply(
            phrase.money.nan_count+phrase.money.change_balance_use
        )
    old = db.get_money(user.full_user.id)
    db.add_money(user.full_user.id, new)
    await event.reply(
        phrase.money.add_money.format(
            name=tag,
            old=old,
            new=old+new
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/скинуть(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/кинуть(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/дать(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/перевести(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^перевести(.*)'))
async def swap_money(event: Message):
    args = event.pattern_match.group(1).strip()
    if len(args) < 1:
        return await event.reply(phrase.money.no_count+phrase.money.swap_balance_use)
    args = args.split()

    try:
        count = int(args[0])
        if count <= 0:
            return await event.reply(phrase.money.negative_count)
    except ValueError:
        return await event.reply(
            phrase.money.nan_count+phrase.money.swap_balance_use
        )

    try:
        tag = args[2]
        user = await client(
            GetFullUserRequest(tag)
        )
        user = user.full_user.id
    except (TypeError, ValueError, IndexError):
        reply_to_msg = event.reply_to_msg_id
        if reply_to_msg:
            reply_message = await event.get_reply_message()
            user = reply_message.sender_id
        else:
            return await event.reply(
                phrase.money.no_people+phrase.money.swap_balance_use
            )

    sender_balance = db.get_money(event.sender_id)
    if sender_balance < count:
        return await event.reply(
            phrase.money.not_enough.format(
                decline_number(sender_balance, 'изумруд')
            )
        )
    db.add_money(event.sender_id, -count)
    db.add_money(user, count)
    return await event.reply(
        phrase.money.swap_money.format(
            decline_number(count, 'изумруд')
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/dns$'))
@client.on(events.NewMessage(pattern=r'(?i)^/днс$'))
async def tg_dns(event: Message):
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    return await event.reply(
        phrase.dns.format(await ip.setup(True)),
        parse_mode="html"
    )


@client.on(events.NewMessage(pattern=r'(?i)^/банк$'))
async def all_money(event: Message):
    return await event.reply(
        phrase.money.all_money.format(
            decline_number(db.get_all_money(), 'изумруд')
        )
    )


@client.on(events.NewMessage(pattern=r'(?i)^/топ крокодил$'))
@client.on(events.NewMessage(pattern=r'(?i)^/топ слова$'))
@client.on(events.NewMessage(pattern=r'(?i)^/стат крокодил$'))
@client.on(events.NewMessage(pattern=r'(?i)^/стат слова$'))
@client.on(events.NewMessage(pattern=r'(?i)^топ крокодила$'))
async def crocodile_wins(event: Message):
    all = db.crocodile_stat.get_all()
    text = ''
    n = 1
    for id in all.keys():
        if n > 10:
            break
        text += f'{n}. {await get_name(id, minecraft=True)}: {all[id]}\n'
        n += 1
    return await event.reply(
        phrase.crocodile.stat.format(text),
        silent=True
    )


@client.on(events.NewMessage(pattern=r'(?i)^/слово(.*)'))
async def word_request(event: Message):
    word = event.pattern_match.group(1).strip().lower()
    with open(
        crocodile_path, 'r', encoding='utf-8'
    ) as f:
        if word in f.read().split('\n'):
            return await event.reply(
                phrase.word.exists
            )
    with open(
        crocodile_blacklist_path, 'r', encoding='utf-8'
    ) as f:
        if word in f.read().split('\n'):
            return await event.reply(
                phrase.word.in_blacklist
            )
    try:
        entity = await client.get_entity(event.sender_id)
    except TypeError:
        return await event.reply(
            phrase.word.no_user
        )
    entity = entity.username
    logger.info(f'Пользователь {entity} хочет добавить слово "{word}"')
    keyboard = ReplyInlineMarkup(
        [
            KeyboardButtonRow(
                [
                    KeyboardButtonCallback(
                        text="✅ Добавить",
                        data=f"word.yes.{word}.{event.sender_id}".encode()
                    ),
                    KeyboardButtonCallback(
                        text="❌ Отклонить",
                        data=f"word.no.{word}.{event.sender_id}".encode()
                    )
                ]
            )
        ]
    )
    try:
        hint = None
        while hint is None:
            hint = await ai.response(
                f'Сделай подсказку для слова "{word}". '
                'Ни в коем случае не добавляй никаких "подсказка для слова.." '
                'и т.п, ответ должен содержать только подсказку. '
                'Не забудь, что подсказка не должна '
                'содержать слово в любом случае. '
            )
        await client.send_message(
            config.tokens.bot.creator,
            phrase.word.request.format(
                user=f'@{entity}',
                word=word,
                hint=hint
            ),
            buttons=keyboard
        )
    except TGErrors.ButtonDataInvalidError:
        return await event.reply(
            phrase.word.long
        )
    return await event.reply(
        phrase.word.set.format(word=word)
    )


@client.on(events.NewMessage(pattern=r'(?i)^/nick(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/ник(.*)'))
async def check_nick(event: Message):
    try:
        user = await client(
            GetFullUserRequest(event.pattern_match.group(1).strip())
        )
        user = user.full_user.id
    except (TypeError, ValueError, IndexError):
        reply_to_msg = event.reply_to_msg_id
        if reply_to_msg:
            reply_message = await event.get_reply_message()
            user = reply_message.sender_id
        else:
            return await event.reply(phrase.nick.who)
    nick = db.nicks(id=user).get()
    if nick is None:
        return await event.reply(phrase.nick.no_nick)
    return await event.reply(phrase.nick.usernick.format(nick))


@client.on(events.NewMessage(pattern=r'(?i)^/госва$'))
@client.on(events.NewMessage(pattern=r'(?i)^/государства$'))
@client.on(events.NewMessage(pattern=r'(?i)^государства$'))
@client.on(events.NewMessage(pattern=r'(?i)^список госв$'))
async def states_all(event: Message):
    data = db.states.get_all()
    if data == {}:
        return await event.reply(phrase.state.empty_list)
    text = phrase.state.all
    n = 1
    for state in data:
        text += f'{n}. **{state}** - {len(data[state]["players"])} чел.\n'
        n += 1
    return await event.reply(text)


@client.on(events.NewMessage(pattern=r'(?i)^\+госво(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^\+государство(.*)'))
async def states_make(event: Message):
    arg = event.pattern_match.group(1).strip()
    if arg == '':
        return await event.reply(phrase.state.no_name)
    if len(arg) > 28:
        return await event.reply(phrase.state.too_long)
    if (
        not re.fullmatch(r'^[а-яА-ЯёЁa-zA-Z\- ]+$', arg)
    ) or (
        re.fullmatch(r'^[\- ]+$', arg)
    ):
        return await event.reply(phrase.state.not_valid)
    if db.nicks(id=event.sender_id).get() is None:
        return await event.reply(phrase.state.not_connected)
    if db.states.if_author(event.sender_id) is not False:
        return await event.reply(phrase.state.already_author)
    if db.states.if_player(event.sender_id) is not False:
        return await event.reply(phrase.state.already_player)
    arg = arg.capitalize()
    if db.states.add(arg, event.sender_id) is not True:
        return await event.reply(phrase.state.already_here)
    await client.send_message(
        entity=config.chats.chat,
        message=phrase.state.make.format(arg),
        reply_to=config.chats.topics.rp
    )
    return await event.reply(phrase.state.make.format(arg))


@client.on(events.NewMessage(pattern=r'(?i)^/вступить(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^вступить(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/г вступить(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/г войти(.*)'))
async def states_enter(event: Message):
    arg = event.pattern_match.group(1).strip()
    if arg == '':
        return await event.reply(phrase.state.no_name)
    if db.states.find(arg) is False:
        return await event.reply(phrase.state.not_find)
    nick = db.nicks(id=event.sender_id).get()
    if nick is None:
        return await event.reply(phrase.state.not_connected)
    if db.states.if_player(event.sender_id) is not False:
        return await event.reply(phrase.state.already_player)
    state = db.state(arg)
    if state.enter != True:
        return await event.reply(phrase.state.enter_exit)
    if state.price != 0:
        return await event.reply(
            phrase.state.pay_to_enter,
            buttons=ReplyInlineMarkup(
                [
                    KeyboardButtonRow(
                        [
                            KeyboardButtonCallback(
                                text=f"✅ Оплатить вход ({state.price})",
                                data=f'state.pay.{state.name}'.encode()
                            )
                        ]
                    )
                ]
            )
        )
    players = state.players
    players.append(event.sender_id)
    state.change("players", players)
    await client.send_message(
        entity=config.chats.chat,
        message=phrase.state.new_player.format(
            state=state.name,
            player=nick
        ),
        reply_to=config.chats.topics.rp
    )
    if (
        state.type == 0
    ) and (
        len(players) >= config.coofs.Type1Players
    ):
        await client.send_message(
            entity=config.chats.chat,
            message=phrase.state.up.format(
                name=state.name,
                type='Государство'
            ),
            reply_to=config.chats.topics.rp
        )
        state.change('type', 1)
    if (
        state.type == 1
    ) and (
        len(players) >= config.coofs.Type2Players
    ):
        await client.send_message(
            entity=config.chats.chat,
            message=phrase.state.up.format(
                name=state.name,
                type='Империя'
            ),
            reply_to=config.chats.topics.rp
        )
        state.change('type', 2)
    return await event.reply(phrase.state.admit.format(state.name))


@client.on(events.NewMessage(pattern=r'(?i)^/госво(.*)'))
@client.on(events.NewMessage(pattern=r'(?i)^/государство(.*)'))
async def states_get(event: Message):
    arg = event.pattern_match.group(1).strip()
    if arg == '':
        player_in = db.states.if_player(event.sender_id)
        if player_in is not False:
            arg = player_in
        author_in = db.states.if_author(event.sender_id)
        if author_in is not False:
            arg = author_in
        else:
            return await event.reply(phrase.state.no_name)
    if db.states.find(arg) is False:
        return await event.reply(phrase.state.not_find)
    state = db.state(arg)
    enter = "Свободный" if state.enter else "Закрыт"
    if state.price > 0:
        enter = decline_number(state.price, 'изумруд')
    tasks = [get_name(player, minecraft=True) for player in state.players]
    idented_players = await asyncio.gather(*tasks)
    return await event.reply(
        phrase.state.get.format(
            type=phrase.state_types[state.type],
            name=state.name,
            money=state.money,
            author=db.nicks(id=state.author).get(),
            enter=enter,
            desc=state.desc,
            date=state.date,
            players=len(state.players),
            list_players=', '.join(idented_players),
            xyz=state.coordinates
        ),
        silent=True
    )


@client.on(events.NewMessage(pattern=r'(?i)^/ливнуть'))
@client.on(events.NewMessage(pattern=r'(?i)^/покинуть госво'))
@client.on(events.NewMessage(pattern=r'(?i)^/покинуть государство'))
@client.on(events.NewMessage(pattern=r'(?i)^выйти из государства'))
@client.on(events.NewMessage(pattern=r'(?i)^выйти из госва'))
@client.on(events.NewMessage(pattern=r'(?i)^/г покинуть'))
@client.on(events.NewMessage(pattern=r'(?i)^/г выйти'))
async def states_leave(event: Message):
    state_name = db.states.if_player(event.sender_id)
    if state_name is False:
        return await event.reply(phrase.state.not_a_member)
    state = db.state(state_name)
    state.players.remove(event.sender_id)
    state.change('players', state.players)
    await client.send_message(
        entity=config.chats.chat,
        message=phrase.state.leave_player.format(
            state=state.name,
            player=db.nicks(id=event.sender_id).get()
        ),
        reply_to=config.chats.topics.rp
    )
    if (
        state.type == 2
    ) and (
        len(state.players) < config.coofs.Type2Players
    ):
        await client.send_message(
            entity=config.chats.chat,
            message=phrase.state.down.format(
                name=state.name,
                type='Государство'
            ),
            reply_to=config.chats.topics.rp
        )
        state.change('type', 1)
    if (
        state.type == 1
    ) and (
        len(state.players) < config.coofs.Type1Players
    ):
        await client.send_message(
            entity=config.chats.chat,
            message=phrase.state.down.format(
                name=state.name,
                type='Княжество'
            ),
            reply_to=config.chats.topics.rp
        )
        state.change('type', 0)
    return await event.reply(phrase.state.leave)


@client.on(events.NewMessage(pattern=r'(?i)^/г описание$'))
@client.on(events.NewMessage(pattern=r'(?i)^/о госве$'))
@client.on(events.NewMessage(pattern=r'(?i)^/г о госве$'))
async def states_desc_empty(event: Message):
    return await event.reply(phrase.state.no_desc)


@client.on(events.NewMessage(pattern=r'(?i)^/г описание\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^/о госве\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^/г о госве\s(.+)'))
async def states_desc(event: Message):
    state_name = db.states.if_author(event.sender_id)
    if state_name is False:
        return await event.reply(phrase.state.not_a_author)
    new_desc = event.pattern_match.group(1).strip()
    db.state(state_name).change('desc', new_desc)
    return await event.reply(phrase.state.change_desc)


@client.on(events.NewMessage(pattern=r'(?i)^/г корды$'))
@client.on(events.NewMessage(pattern=r'(?i)^/г координаты$'))
async def states_coords_empty(event: Message):
    return await event.reply(phrase.state.howto_change_coords)


@client.on(events.NewMessage(pattern=r'(?i)^/г корды\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^/г координаты\s(.+)'))
async def states_coords(event: Message):
    state_name = db.states.if_author(event.sender_id)
    if state_name is False:
        return await event.reply(phrase.state.not_a_author)
    arg = event.pattern_match.group(1).strip()
    try:
        arg = list(map(int, arg.split()))
    except ValueError:
        return await event.reply(phrase.state.howto_change_coords)
    if len(arg) != 3:
        return await event.reply(phrase.state.howto_change_coords)
    db.state(state_name).change('coordinates', ", ".join(list(map(str, arg))))
    return await event.reply(phrase.state.change_coords)


@client.on(events.NewMessage(pattern=r'(?i)^/г входы\s(.+)'))
@client.on(events.NewMessage(pattern=r'(?i)^/г вступления\s(.+)'))
async def states_enter(event: Message):
    state_name = db.states.if_author(event.sender_id)
    if state_name is False:
        return await event.reply(phrase.state.not_a_author)
    arg = event.pattern_match.group(1).strip()
    state = db.state(state_name)
    if arg in [
        'да',
        '+',
        'разрешить',
        'открыть',
        'true',
        'ok',
        'ок',
        'можно'
    ]:
        if state.enter is True:
            return await event.reply(
                phrase.state.already_open
            )
        state.change("enter", True)
        return await event.reply(
            phrase.state.enter_open
        )
    elif arg in [
        'нет',
        '-',
        'запретить',
        'закрыть',
        'false',
        'no',
        'нельзя',
        'закрыто'
    ]:
        if state.enter is False:
            return await event.reply(
                phrase.state.already_close
            )
        state.change("enter", False)
        return await event.reply(
            phrase.state.enter_close
        )
    elif arg.isdigit():
        arg = int(arg)
        state.change("price", arg)
        state.change("enter", True)
        return await event.reply(
            phrase.state.enter_price.format(
                decline_number(arg, "изумруд")
            )
        )
    else:
        return await event.reply(
            phrase.state.howto_enter
        )


@client.on(events.NewMessage(pattern=r'(?i)^/г входы$'))
@client.on(events.NewMessage(pattern=r'(?i)^/г вступления$'))
async def states_enter(event: Message):
    state_name = db.states.if_author(event.sender_id)
    if state_name is False:
        return await event.reply(phrase.state.not_a_author)
    state = db.state(state_name)
    if state.enter is True:
        if state.price != 0:
            state.change("price", 0)
        state.change("enter", False)
        return await event.reply(phrase.state.enter_close)
    elif state.enter is False:
        state.change("enter", True)
        return await event.reply(phrase.state.enter_open)


@client.on(events.NewMessage(pattern=r'(?i)^/time'))
@client.on(events.NewMessage(pattern=r'(?i)^/время$'))
@client.on(events.NewMessage(pattern=r'(?i)^/мск$'))
@client.on(events.NewMessage(pattern=r'(?i)^/msk$'))
async def msktime(event: Message):
    return await event.reply(phrase.time.format(datetime.now().strftime("%H:%M:%S")))


@client.on(events.NewMessage(pattern=r'(?i)^/тест\s(.+)'))
async def test(event: Message):
    arg = event.pattern_match.group(1).strip()
    if event.sender_id not in db.database('admins_id'):
        return await event.reply(phrase.perms.no)
    return event.reply(event.stringify())


'Эвенты для крокодила'


async def crocodile_hint(event: Message):
    game = db.database("current_game")
    hint = game["hints"]
    if event.sender_id in hint:
        return await event.reply(phrase.crocodile.hints_all)
    hint.append(event.sender_id)
    game["hints"] = hint
    db.database("current_game", game)
    word = game["word"]
    last_hint = db.database("crocodile_last_hint")
    if random() < config.coofs.PercentForRandomLetter and last_hint != 0:
        n = 1
        for letter in list(db['unsec']):
            if letter == '_':
                response = f'{n} буква в слове - **{db["word"][n-1]}**'
                break
            n += 1
    else:
        if last_hint != 0:
            check_last = 'Так же учитывай, ' \
                f'что подсказка {last_hint} уже была.'
        else:
            check_last = ''
        response = await ai.response(
            f'Сделай подсказку для слова "{word}". '
            'Ни в коем случае не добавляй никаких "подсказка для слова.." '
            'и т.п, ответ должен содержать только подсказку. '
            'Не забудь, что подсказка не должна '
            'содержать слово в любом случае. ' + check_last
        )
        if response is None:
            game = db.database("current_game")
            hint = game["hints"]
            hint.remove(event.sender_id)
            game["hints"] = hint
            db.database("current_game", game)
            return await event.reply(phrase.crocodile.error)
        db.database("crocodile_last_hint", response)
    return await event.reply(response)


async def crocodile_handler(event: Message):
    text = event.text.strip().lower()
    if len(text) > 0:
        current_word = db.database("current_game")["word"]
        current_mask = list(db.database("current_game")["unsec"])
        if text == current_word:
            bets = db.database('crocodile_bets')
            all = 0
            bets_str = ''
            topers = []
            n = 1
            for toper in db.crocodile_stat.get_all().keys():
                if n > config.coofs.TopLowerBets:
                    break
                topers.append(toper)
                n += 1
            if bets != {}:
                for key in list(bets.keys()):
                    if str(event.sender_id) == key:
                        if str(event.sender_id) in topers:
                            all += round(bets[key]*config.coofs.TopBets)
                        else:
                            all += round(
                                bets[key]*config.coofs.CrocodileBetCoo
                            )
                    else:
                        all += bets[key]
                db.add_money(event.sender_id, all)
                bets_str = phrase.crocodile.bet_win.format(
                    decline_number(all, 'изумруд'),
                )
            db.database("current_game", 0)
            db.database("crocodile_bets", {})
            db.database("crocodile_last_hint", 0)
            if db.database('crocodile_super_game') == 1:
                db.database('crocodile_super_game', 0)
                db.database('max_bet', config.coofs.CrocodileDefaultMaxBet)
                db.database('min_bet', config.coofs.CrocodileDefaultMinBet)
            client.remove_event_handler(crocodile_hint)
            client.remove_event_handler(crocodile_handler)
            db.crocodile_stat(event.sender_id).add()
            return await event.reply(
                phrase.crocodile.win.format(current_word)+bets_str
            )
        else:
            pass
        if text[0] != '/':
            if len(text) > len(current_word):
                n = 0
                for x in current_word:
                    if x == text[n] and current_mask[n] == "_":
                        current_mask[n] = x
                    n = n + 1
            else:
                n = 0
                for x in text:
                    if x == current_word[n] and current_mask[n] == "_":
                        current_mask[n] = x
                    n = n + 1
            if "".join(current_mask) == current_word:
                current_mask[randint(0, len(current_mask)-1)] = '_'
                cgame = db.database("current_game")
                cgame["unsec"] = "".join(current_mask)
                db.database("current_game", cgame)
                return await event.reply(
                    phrase.crocodile.new.format(
                        "".join(current_mask).replace("_", "..")
                    )
                )
            if list(db.database("current_game")["unsec"]) != current_mask:
                cgame = db.database("current_game")
                cgame["unsec"] = "".join(current_mask)
                db.database("current_game", cgame)
                return await event.reply(
                    phrase.crocodile.new.format(
                        "".join(current_mask).replace("_", "..")
                    )
                )


if db.database("current_game", log=False) != 0:
    client.add_event_handler(
        crocodile_handler, events.NewMessage(chats=config.chats.chat)
    )
    client.add_event_handler(
        crocodile_hint, events.NewMessage(pattern=r"(?i)^/подсказка$")
    )
