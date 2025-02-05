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

    bet_already = '❌ : Ставка уже есть!'
    no = '❌ : Игра уже запущена!'
    chat = '❌ : Эта игра работает только в чате сервера!'
    error = '❌ : Произошла ошибка! Попробуйте позже'
    hints_all = '❌ : Подсказки кончились!'
    already_down = '❌ : Игра и так не запущена!'
    down = '❌ : Игра остановлена!\nБыло загадано слово **"{}"**'


class ping:
    set = '🌐 : **Понг!**\nОтветил {}'
    min = 'быстрее скорости света! 🚑'


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
    not_enough = '❌ : Не хватает денег!\nНа вашем счету всего **{}**'
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
        'Свяжитесь с @trassert, чтобы перенести аккаунт.'

    success = '✅ : Ник успешно привязан!\nПодарок - {}!'


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


class word:
    add = '✅ : Слово добавлено!'
    request = 'Пользователь {user} предложил слово **"{word}"**'
    exists = '❌ : Слово уже есть!'
    success = '✅ : **Админ одобрил слово "{word}"!**\n' \
        '@{user} получает {money}.'
    set = '⏳ : Жду ответа админа, чтобы добавить слово **"{word}"**'
    no = '❌ : @{user}, слово **"{word}"** отклонено!'
    noadd = '❌ : Слово не будет добавлено.'
    no_user = '📝 : Команда работает только от имени юзера.'


stat_server = '📊 : Топ игроки {} сервера:\n'
dns = '🌐 : Ответ провайдера: {}'

hotmc_money = '🤑 : И получил за это {}\n'
hotmc = '**🗳 : {nick} проголосовал за сервер!**\n{money}' \
    '**[Проголосовать](hotmc.ru/vote-274472)**'

servers_money = '🤑 : И получил за это {}\n'
servers = '**🗳 : {nick} проголосовал за сервер!**\n{money}' \
    '**[Проголосовать](minecraft-servers.ru/server/trassert)**'

github = '**🎉 : Я получил обновление!**\n' \
    'Автор: **{author}**\n' \
    'Сообщение: {message}\n' \
    '\n' \
    '**[Что изменилось]({url})**'

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
        ], 'emo': '🗡'
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
        ], 'emo': '🏜'
    },
    'flower': {
        'quotes': [
            'От пчёл с любовью!'
        ], 'emo': '🌻'
    },
    'heads': {
        'quotes': [
            'Да ты хоть знаешь, каково их было убивать?',
            'Мрачные сувениры... из далекого прошлого.',
            'Не спрашивайте, откуда они...',
            'Коллекционное издание!'
        ], 'emo': '😵'
    },
    'mine': {
        'quotes': [
            'Вот они, блестяшки!',
            'Прямо из недр земли!',
            'Добыто тяжким трудом!',
            'Искрящиеся сокровища!'
        ], 'emo': '⛏️'
    },
    'music': {
        'quotes': [
            'Пластинки от гениев музыки',
            'Мелодии, которые запомнятся надолго.',
            'Настоящее музыкальное путешествие!'
        ], 'emo': '🎼'
    },
    'nether': {
        'quotes': [
            'в ад я больше не сунусь..',
            'Из самого сердца Нижнего мира!',
            'Не забудьте взять с собой зелье огнестойкости!',
            'Это единственное, что я смог оттуда вынести.'
        ], 'emo': '🔥'
    },
    'raiders': {
        'quotes': [
            'Пока я собирал это, меня пару раз ударила летающая тварь!',
            'Добыча с небольшим риском для жизни.',
            'Лучше не знать, откуда всё это...',
            'Они будут скучать по этому...'
        ], 'emo': '😡'
    },
    'remains': {
        'quotes': [
            'Обломки великой цивилизации!',
            'Остатки былого величия..',
            'Тайны прошлого ждут своего исследователя...',
            'Артефакты давно ушедшей эпохи.'
        ], 'emo': '🏚'
    },
    'sculk': {
        'quotes': [
            'Меня чуть не убил Хранитель',
            'Это не для слабонервных...',
            'Из глубин скрытой цивилизации.',
            'Будь осторожен с этим...'
        ], 'emo': '🥷🏻'
    },
    'water': {
        'quotes': [
            'Самая свежая рыбка!',
            'Улов дня!',
            'Морские деликатесы!'
        ], 'emo': '🐠'
    },
    'witch': {
        'quotes': [
            'в доме ведьмы ужасно пахло..',
            'Настоящее колдовское снадобье!'
        ], 'emo': '🧙🏻‍♀️'
    },
    'blacksmith': {
        'quotes': [
            'Ещё разок, молот, и железо станет послушным!',
            'Каждая вещь – плод честного труда и закаленной стали.',
            'Выбирайте товар, господин!',
            'Уверен, вам понравится.'
        ],
        'emo': '⚒️'
    }
}
