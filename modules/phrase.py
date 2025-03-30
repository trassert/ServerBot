
class crocodile:
    game = '✅ : Это игра **Крокодил**.\n' \
        '\n' \
        '🤔 : В ней нужно угадывать слова, ' \
        'используя команду **"/подсказка"**\n' \
        '🎊 : Кто первым назовёт слово полностью, тот и победил'
    new = '✅ : Ты отгадал часть слова!\nСлово: **"{}"**'
    bet = '✅ : Поставлена ставка **{}** на следующую игру в крокодила'
    up = '✅ : Загадал слово, попробуйте его отгадать!'
    win = '✅ : Ты победил! Загаданное слово было **"{}"**'

    super_game = '🔥 : Начата **СУПЕР-ИГРА**!\n\n' \
        '@trassert загадал слово, попробуйте его отгадать!'
    super_game_wait = '**🔥 : СУПЕР-ИГРА начнётся через 1 минуту!**'
    super_game_here = '🔥 : Нельзя - скоро начнётся супер-игра!'

    stat = '🔝 : Топ игроков крокодила:\n\n{}'
    bet_win = '\n**Ты выиграл {}**'

    not_enough = '❌ : Не хватает изумрудов чтобы погасить ставки!\n'\
        'На вашем счету всего **{}**'
    bet_already = '❌ : Ставка уже есть!'
    no = '❌ : Игра уже запущена!'
    chat = '❌ : Эта игра работает только в чате сервера!'
    error = '❌ : Произошла ошибка! Попробуйте позже'
    hints_all = '❌ : Подсказки кончились!'
    already_down = '❌ : Игра и так не запущена!'
    down = '❌ : Игра остановлена!\nБыло загадано слово **"{}"**'
    down_payed = '❌ : **{user}** остановил игру, потратив **{money}**\n' \
        'Было загадано слово **"{word}"**'


class ping:
    set = '**Понг!**\n🤖 : Бот ответил {}'
    min = 'быстрее скорости света! 🚑'


class ticket:
    in_chat = '🎟 : Можно создать только в лс бота!'
    no_value = '💰 : Укажите количество изумрудов'
    not_int = '❌ : Сумма не является числом!'
    bigger_than_zero = '❌ : Сумма чека меньше 1!'
    added = '**💎 : Чек для получения изумрудов**\n\n' \
        'Сумма: **{value}**\n' \
        'Автор: **{author}**\n\n' \
        'ID чека: **{id}**\n'
    no_arg = '🎟 : Введите ID чека для активации'
    no_such = '🎟 : Не найден чек с таким ID'
    got = '❤️ : Активирован чек от **{author}**\n' \
        'Сумма: **{value}**'


class money:
    wallet = '💰 : Ваш баланс: **{}**'
    add_money = '✅ : Счёт {name} изменён:\n{old} -> {new}'
    swap_money = '✅ : Переслал {}!'
    all_money = '🏦 : Всего в обороте {}'

    change_balance_use = '\nИспользование: `/изменить баланс 10 @durov`'
    swap_balance_use = '\nИспользование: `/скинуть 10 @durov`'

    negative_count = '❌ : Число должно быть больше нуля!'
    no_people = '❌ : Нет тега!'
    no_such_people = '❌ : Нет такого человека!'
    no_count = '❌ : Нет количества изумрудов!'
    nan_count = '❌ : Неверное количество изумрудов!'
    not_enough = '❌ : Не хватает изумрудов!\nНа вашем счету всего {}'
    max_count = '❌ : Максимальная ставка на крокодил - **{}**'
    min_count = '❌ : Минимальная ставка на крокодил - **{}**'


class help:
    comm = '🤖 : [Помощь по командам](https://teletype.in/@trassert/commandsv2)'


class server:
    stopped = '❌ : Сервер выключен!'
    overload = '❌ : Сервер перегружен, попробуйте позже'
    host = '🌐 : Айпи сервера: {}'


class nick:
    not_append = '❌ : Привяжите ник чтобы пользоваться магазином!'
    too_short = '❌ : Ник должен быть не меньше 4 символов!'
    too_big = '❌ : Ник должен быть не больше 16 символов!'
    taken = '❌ : Ник занят!'
    invalid = '❌ : Ник должен содержать только англ. буквы, цифры и "_".'
    already_have = '❌ : У вас уже есть ник!\n' \
        '**Сменить ник за {price}?**'
    who = '❌  : Не найден пользователь!\n' \
        'Использование: `/ник @durov`'
    no_nick = '📝 : Игрок ещё не привязал ник'
    usernick = '📝 : Ник игрока: **{}**'
    already_you = '📝 : Этот ник совпадает с вашим'


    success = '✅ : Ник успешно привязан!\n' \
        'Подарок - {}!\n'
    buy_nick = '✅ : Успешно!\n{user} изменил ник, потратив {price}'


class shop:
    shop = '<blockquote>{quote}</blockquote>\n\n' \
        '<b>{emo} : Вот мои товары:</b>\n\n' \
        '1. {trade_1}{value_1} - {price_1}\n' \
        '2. {trade_2}{value_2} - {price_2}\n' \
        '3. {trade_3}{value_3} - {price_3}\n' \
        '4. {trade_4}{value_4} - {price_4}\n' \
        '5. {trade_5}{value_5} - {price_5}\n\n' \
        '<i>для покупки нажмите на соответствующую кнопку</i>'
    buy = '✅ : Товар {} успешно куплен!'
    update = '**✅ : Странствующий торговец пришёл с новыми товарами!**\n' \
        'Тема: {theme}'

    old = '❌ : Странствующий торговец уже обновил свои товары!'
    timeout = '❌ : Странствующий торговец чем то занят..'


class perms:
    no = '❌ : Вы не админ!'
    admin_add = '✅ : **Новый администратор!**\nНик - {nick}\nID - {id}'
    admin_del = '❌ : **Администратор удалён!**'


class no:
    server = '❌ : Нет такого сервера!'
    days = '❌ : Неверно введено количество дней!'
    response = '❌ : Введите свой запрос!'
    arg = '❌ : Не указан аргумент'


class word:
    add = '✅ : Слово добавлено!'
    request = 'Пользователь {user} предложил слово **"{word}"**\n\n' \
        'Подсказка: **{hint}**'
    exists = '❌ : Слово уже есть!'
    success = '✅ : **Админ одобрил слово "{word}"!**\n' \
        '{user} получает {money}.'
    set = '⏳ : Жду ответа админа, чтобы добавить слово **"{word}"**'
    no = '❌ : {user}, слово **"{word}"** отклонено!'
    noadd = '❌ : Слово не будет добавлено.'
    no_user = '📝 : Команда работает только от имени юзера.'
    long = '📝 : Слишком длинное слово'


class enchant:
    no_arg = '🤔 : Укажи название зачарования'
    no_diff = '😓 : Не знаю такого зачарования'
    main = '**🤔 : Я думаю, ты о нём:**\n\n{}'


class stat:
    chat = '📊 : Топ общительных на сервере за {}:\n\n'
    server = '📊 : Топ игроки {} сервера:\n'
    empty = '😓 : Никто ещё не писал сегодня'
    gift = '💪 : **{user}** cегодня самый активный\n' \
        'Он получает **{gift}** как подарок!'


class casino:
    start = '**🎰 : Сыграем в рулетку?**\n' \
        '\n' \
        '\nВнеси {} изумрудов, чтобы сыграть!'
    do = '✅ : Крути рулетку! (Отправь в чат 🎰)'
    win = '**🎊 : Ты выиграл!**\n+{} изумрудов'
    partially = '🤔 : Выпало 2/3\nТы ничего не выиграл, но и не проиграл.'
    lose = '😢 : Ничего не выпало'
    timeout = '🫤 : {}, ты слишком долго думал!'


class state:
    all = '**🏰 : Государства:**\n\n'
    empty_list = '🏰 : Государств пока ещё нет!'
    no_name = '📝 : Укажите название государства'
    not_valid = '📝 : Название не совпадает с критериями'
    already_here = '🏰 : Государство с таким названием уже есть'
    not_connected = '📝 : Сначала привяжите свой ник в майнкрафте'
    make = '🏰 : Образовано новое государство - **"{}"**!'
    already_author = '❌ : У вас уже есть государство'
    already_player = '❌ : Вы уже состоите в государстве'
    not_find = '📝 : Не найдено такое государство'
    error = '📝 : Произошла какая-то ошибка, попробуйте позже'
    admit = '🏰 : Вы теперь в государстве **"{}"**'
    new_player = '🆕 : В государстве **"{state}"** новый участник — **{player}**!'
    get = '🏰 : {type} "{name}" \n'
    up = '🆙 : **{name}** теперь обладает статусом **{type}**!'


not_for_you = '👎 : Кнопка не для вас'
leave_message = '😓 : {} покинул нас'
vote_money = '🤑 : И получил за это {}\n'

hotmc = '**🗳 : {nick} проголосовал за сервер!**\n{money}' \
    '**[Проголосовать](hotmc.ru/vote-274472)**'
servers = '**🗳 : {nick} проголосовал за сервер!**\n{money}' \
    '**[Проголосовать](minecraft-servers.ru/server/trassert)**'
github = '**🎉 : Я получил обновление!**\n' \
    'Автор: **{author}**\n' \
    'Сообщение: {message}\n' \
    '\n' \
    '**[Что изменилось]({url})**'
dns = '🌐 : Ответ:\n{}'

all_arg = ['весь', 'вся', 'общий', 'всего']
shop_quotes = {
    'armorer': {
        'quotes': [
            'Оружейник делает прекрасные товары!',
            'С этим можно торговаться!',
            'Блестящие шлема и мечи!',
            'Я думаю, с этим ты победишь всех',
            'Бери, или сам станешь кожанной бронёй.',
            'Цена выкована самим кузнецом!',
            'Я думаю, тебе бы подошло это.',
            'Ты хиленький, броня должна тебе помочь.',
            'Как насчёт такого?',
            'Не вздумай торговаться!',
            'Заточенное до остроты бритвы!',
            'С этим оружием ты будешь непобедим... почти.',
            'Не забудьте взять запасные клинки!',
            'Гарантия на прочность - моя жизнь!'
        ],
        'emo': '🗡',
        'translate': 'Оружейник'
    },
    'desert': {
        'quotes': [
            'В пустыне жарко...',
            '...слезятся в глазах миражи...',
            'Жители пустынь не были этому рады..',
            'Они до сих пор тёплые!',
            'Песок - он везде...',
            'Нашёл это в заброшенном оазисе.',
            'Чувствуешь запах песка?',
            'Это настоящее сокровище пустыни!'
        ],
        'emo': '🏜',
        'translate': 'Пустыня'
    },
    'flower': {
        'quotes': [
            'От пчёл с любовью!',
            'Красит что надо!'
        ],
        'translate': 'Красители',
        'emo': '🌻'
    },
    'heads': {
        'quotes': [
            'Да ты хоть знаешь, каково их было убивать?',
            'Мрачные сувениры... из далекого прошлого.',
            'Не спрашивайте, откуда они...',
            'Коллекционное издание!'
        ],
        'translate': 'Головы',
        'emo': '😵'
    },
    'mine': {
        'quotes': [
            'Вот они, блестяшки!',
            'Прямо из недр земли!',
            'Добыто тяжким трудом!',
            'Искрящиеся сокровища!'
        ],
        'translate': 'Шахтёрское ремесло',
        'emo': '⛏️'
    },
    'music': {
        'quotes': [
            'Пластинки от гениев музыки',
            'Мелодии, которые запомнятся надолго.',
            'Настоящее музыкальное путешествие!'
        ],
        'translate': 'Музыка',
        'emo': '🎼'
    },
    'nether': {
        'quotes': [
            'в ад я больше не сунусь..',
            'Из самого сердца Нижнего мира!',
            'Не забудьте взять с собой зелье огнестойкости!',
            'Это единственное, что я смог оттуда вынести.'
        ],
        'translate': 'Нижний мир',
        'emo': '🔥'
    },
    'raiders': {
        'quotes': [
            'Пока я собирал это, меня пару раз ударила летающая тварь!',
            'Добыча с небольшим риском для жизни.',
            'Лучше не знать, откуда всё это...',
            'Они будут скучать по этому...'
        ],
        'translate': 'Аванпост разбойников',
        'emo': '😡'
    },
    'remains': {
        'quotes': [
            'Обломки великой цивилизации!',
            'Остатки былого величия..',
            'Тайны прошлого ждут своего исследователя...',
            'Артефакты давно ушедшей эпохи.'
        ],
        'translate': 'Археология',
        'emo': '🏚'
    },
    'sculk': {
        'quotes': [
            'Меня чуть не убил Хранитель',
            'Это не для слабонервных...',
            'Из глубин скрытой цивилизации.',
            'Будь осторожен с этим...'
        ],
        'translate': 'Тёмный город',
        'emo': '🥷🏻'
    },
    'water': {
        'quotes': [
            'Самая свежая рыбка!',
            'Улов дня!',
            'Морские деликатесы!'
        ],
        'translate': 'Океан',
        'emo': '🐠'
    },
    'witch': {
        'quotes': [
            'в доме ведьмы ужасно пахло..',
            'Настоящее колдовское снадобье!'
        ],
        'translate': 'Домик ведьмы',
        'emo': '🧙🏻‍♀️'
    },
    'blacksmith': {
        'quotes': [
            'Ещё разок, молот, и железо станет послушным!',
            'Каждая вещь – плод честного труда и закаленной стали.',
            'Выбирайте товар, господин!',
            'Уверен, вам понравится.'
        ],
        'translate': 'Кузнец',
        'emo': '⚒️'
    },
    'end': {
        'quotes': [
            'Я уж думал, эндермены всё раскупили!',
            'Сокровище, добытое из глубин Энда!',
            'Почему эндермены так разговаривают?.. А, ладно, неважно. Покупай!',
            'Ха-ха, кристалл Энда делает бум!',
            'Ты видел этого дракона?',
            'С элитрами ты всегда будешь на высоте!',
            'хмурф-хмурф',
            '(звуки телепортации позади)'
        ],
        'translate': 'Энд',
        'emo': '🟣'
    },
    'redstone': {
        "quotes": [
            'Редстоун — это не просто пыль, это искусство!',
            'Собери свою схему!',
            'Товары для инженера!',
            'Всё, чего я хочу, это чтобы переключатель сделал... Что?!',
            'Собери схему, нажми кнопку, и мир изменится!',
            'Редстоун — это не просто проводка, это философия!',
            'О, ты знаешь, что нужно этому дому? Больше мигающих огней ;)',
            'Редстоун — это как музыка, только для инженеров!',
            'С редстоуном даже ты можешь стать изобретателем!',
            'Ты знаешь, что редстоун — это кровь Minecraft?',
            'С редстоуном даже губка может стать частью схемы!',
            'О, дай угадаю. Не купил достаточно редстоуна. Идиот'
        ],
        'translate': 'Редстоун',
        'emo': '🔴'
    }
}
