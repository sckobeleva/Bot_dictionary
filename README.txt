﻿Бот-словарь

Использует АPI Яндекс.Словаря, знает 7 языков (en, fr, de, it, es, tr, pl).
При старте предлагает пользователю выбрать язык, в дальнейшем запоминает и использует его.
Если пользователь не выбрал язык, но начал ввод слова, бот просит сначала выбрать язык.
При вводе слова бот определяет, если это кириллица, то переводит с русского на иностранный, если нет - наоборот.
Изменить язык можно с помощью стандартных команд /start или /settings.
При перезапуске бота (проблемы с сетью, изменения в коде и т.д.) язык по умолчанию обнуляется, и бот просит выбрать язык заново.
При возникновении ошибок на стороне Яндекс.Словаря, бот их обрабатывает и отправляет пользователю в читаемом виде.