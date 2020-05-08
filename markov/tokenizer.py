from read_files import read_files
import pymongo


class Tokenizer:
    """
    Токенизатор текста
    """
    class Strategy:
        """
        Базовая стратегия токенизатора
        """
        def __init__(self):
            self.idx2word = list()
            self.word2idx = dict()

        def idx_to_word(self, idx):
            """
            Получение слова для заданного индекса

            :param idx: индекс
            :type idx: int
            :return: слово по заданному индексу
            :rtype: str
            """
            return self.idx2word[idx]

        def word_to_idx(self, word):
            """
            Получение индекса для заданного слова

            :param word: слово
            :type word: str
            :return: индекс по заданному слову
            :rtype: int
            """
            return self.word2idx[word]

        def update(self, word):
            """
            Добавление слова в токенизатор

            :param word: слово
            :type word: str
            """
            if word not in self.word2idx.keys():
                self.idx2word.append(word)
                self.word2idx[word] = len(self.idx2word) - 1

    class GenerateNewStrategy(Strategy):
        """
        Стратегия, предназначенная для первичного запуска токенизатора
        """
        def __init__(self, text_path):
            """
            Инициализация 'word2idx' и 'idx2word' по заданному датасету

            :param text_path: путь к датасету
            :type text_path: str
            """
            super().__init__()
            text = read_files(text_path)
            text = (text.lower()).split()
            data = sorted(set(text))
            self.word2idx = {item: idx for idx, item in enumerate(data)}
            self.idx2word = [item for item in data]

            del data
            del text

    class FullLoadStrategy(Strategy):
        """
        Стратегия, полностью загружающая токенизатор из базы данных
        """
        def __init__(self, collection):
            """
            Загрузка 'word2idx' и 'idx2word' из базы данных

            :param collection: коллекция токенизатора
            """
            super().__init__()
            self.idx2word = list()
            self.word2idx = dict()
            for pair in collection.find():
                self.idx2word.append(pair['word'])
                self.word2idx[pair['word']] = pair['idx']

    class LoadStrategy:
        """
        Стратегия для работы с токенизатором из базы данных
        """
        def __init__(self, collection):
            """

            :param collection: коллекция токенизатора
            """
            self.collection = collection

        def idx_to_word(self, idx):
            """
            Получение слова для заданного индекса из базы данных

            :param idx: индекс
            :type idx: int
            :return: слово по заданному индексу
            :rtype: str
            """

            if type(idx) == str:
                idx = int(idx)

            return self.collection.find_one({'idx': idx})['word']

        def word_to_idx(self, word):
            """
            Получение идекса по заданному слову из базы данных

            :param word: слово
            :type word: str
            :return: индекс по заданному слову
            :rtype: int
            """
            return self.collection.find_one({'word': word})['idx']

        def update(self, word, counter):
            """
            Добавление слова в токенизатор

            :param word: слово
            :type word: str
            :param counter: счетчик
            :type counter: class counter.Counter
            """
            found = self.collection.update_one({'word': word.lower()}, {'$setOnInsert': {'idx': counter.get('tokens') + 1}}, upsert=True).upserted_id
            if found is not None:
                counter.increment('tokens', 1)

        def update_many(self, words, counter):
            """
            Множественный вызов def update(word, counter)

            :param words: список слов
            :type words: list
            :param counter: счетчик
            :type counter: class counter.Counter
            """
            mx = len(words)
            for i, word in enumerate(words):
                print("updating tokenizer: {}/{}".format(i, mx))
                self.update(word, counter)

        def update_from_text(self, text_path, counter):
            """
            Обновление токенизатора по тексту

            :param text_path: путь к тексту
            :type text_path: str
            :param counter: счетчик
            :type counter: class counter.Counter
            """
            text = read_files(text_path)
            self.update_many(text.split(), counter)

    def __init__(self, strategy):
        """

        :param strategy: выбранная стратегия для токенизатора
        :type strategy:  class tokenizer.Tokenizer.Strategy
        """
        self.strategy = strategy
        self.end_symbol = self.word2idx('end')

    def word2idx(self, word):
        """
        Вызов метода 'word2idx' для заданной стратегии

        :param word: слово
        :type word: str
        :return: индекс по заданному слову
        :rtype: str
        """
        return self.strategy.word_to_idx(word)

    def idx2word(self, idx):
        """
        Вызов метода 'idx2word' для заданной стратегии

        :param idx: индекс
        :type idx: int
        :return: слово по заданному индексу
        :rtype: int
        """
        return self.strategy.idx_to_word(idx)

    def text_to_int(self, text):
        """
        Конвертация текста в цифры

        :param text: текст
        :type text: str, optional
        :return: токенизированный текст
        :rtype: list
        """
        if type(text) == list:
            text = ' '.join(text)
        res = list()
        inp = text.split()
        ln = len(inp)
        for i, word in enumerate(inp):
            res.append(self.word2idx(word.lower()))
            print('converting text to int: {}/{}'.format(i + 1, ln))
        return res  # [self.word2idx(i.lower()) for i in text.split()]

    def int_to_text(self, text_as_int):
        """
        Конвертация токенизированного текста в обычный

        :param text_as_int: токенизированный текст
        :type text_as_int: list, optional
        :return: текст
        :rtype: str
        """
        if type(text_as_int) == str:
            text_as_int = list(map(int, text_as_int.split()))
        text = ' '.join([self.strategy.idx_to_word(id) for id in text_as_int])
        return text

    def save(self, collection):
        """
        Сохранение токенизатора в базу данных

        :param collection: имя коллекции
        """
        collection.create_index([('idx', pymongo.ASCENDING)], name='idx2word', unique=True)
        collection.create_index([('word', pymongo.ASCENDING)], name='word2idx', unique=True)
        collection.insert_many([{'idx': idx, 'word': word} for idx, word in enumerate(self.strategy.idx2word)])

    def change_strategy(self, strategy):
        """
        Смена стратегии

        :param strategy: новая стратегия
        :type strategy: class tokenizer.Tokenizer.Strategy
        """
        del self.strategy
        self.strategy = strategy
