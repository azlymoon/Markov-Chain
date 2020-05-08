import pymongo
from counter import Counter
from dictogram import Dictogram
from tokenizer import Tokenizer
from read_files import read_files


class MarkovChain:
    """
    Цепь Маркова
    """
    def __init__(self, database, window_size):
        self.window_size = window_size

        print('CONNECTING TO A DB')
        if type(database) == str:
            client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.db = client[database]
        else:
            self.db = database

        self.model = self.db['model']
        self.tokens = self.db['tokens']

        self.counter = Counter(self.db)

    def set_tokenizer(self, tokenizer):
        """
        Инициализация токенизатора для цепи Маркова

        :param tokenizer: токенизатор
        :type tokenizer: class tokenizer.Tokenizer
        """
        self.tokenizer = tokenizer

    def generate_random_start_sequence(self):
        """
        Генерация начала предложения

        :return: случайное начало предложения
        :rtype: str
        """
        random_sequence = self.get_random_start_sequence()[0]
        key, value = random_sequence['key'], random_sequence['value']
        return ' '.join(key.split()[1:]) + ' ' + str(Dictogram(value).return_weighted_random_word())

    def generate_random_sentence(self, length, start_sequence):
        """
        Генерация предложения

        :param length: количестов слов в предложение
        :type length: int
        :param start_sequence: начало предложения
        :type start_sequence: str
        :return: предложение
        :rtype: str
        """
        current_word_sequence = tuple(map(int, start_sequence.split()))
        sentence = list(current_word_sequence)
        sentence_num = 0
        while sentence_num < length:
            current_dictogram = Dictogram(self.get_sequence(' '.join(map(str, current_word_sequence))))
            random_weighted_word = current_dictogram.return_weighted_random_word()
            current_word_sequence = current_word_sequence[1:] + tuple([random_weighted_word])
            sentence.append(current_word_sequence[-1])
            sentence_num += 1
        return sentence

    def create_model_from_text(self, text_path):
        """
        Создание цепи Маркова из текста

        :param text_path: путь к тексту
        :type text_path: str
        :return: модель цепи Маркова
        :rtype: dict
        """
        markov_model = dict()
        # Проверка наличия уже обученой модели
        print('-READING TEXT')
        data = self.tokenizer.text_to_int(read_files(text_path).split())
        self.tokenizer.change_strategy(Tokenizer.LoadStrategy(self.tokens))
        range_len = len(data) - self.window_size
        for current_word in range(0, len(data) - self.window_size):
            print("creating: {}/{}".format(current_word + 1, range_len))
            # Создаем окно
            window = tuple(data[current_word: current_word + self.window_size])
            # Добавляем в словарь
            if window in markov_model:
                # Присоединяем к уже существующему распределению
                markov_model[window].update([data[current_word + self.window_size]])
            else:
                markov_model[window] = Dictogram([data[current_word + self.window_size]])
        return markov_model

    def generate(self, length):
        """
        Генерация предложения

        :param length: количество слов в тексте
        :type length: int
        :return: сгенерированное предложение
        :rtype: str
        """

        start = self.generate_random_start_sequence()
        sentence = self.generate_random_sentence(length, start)

        return self.tokenizer.int_to_text([word for word in sentence if word != self.tokenizer.end_symbol])

    def save(self, data):
        """
        Сохранение цепи Маркова в базу данных

        :param data: модель цепи Маркова
        :type data: dict
        """
        # TODO: end_symbol is not enough add some start ones
        # Creating indexes
        self.model.create_index([('key', pymongo.ASCENDING)], name='keys', unique=True)

        res = list()
        items = data.items()
        ln = len(items)
        batch_size = 1e5
        for i, (key, value) in enumerate(data.items()):
            print('saving: {}/{}'.format(i + 1, ln))
            start = key[0] == self.tokenizer.end_symbol
            key = ' '.join(map(str, key))
            value = {str(value_key): value_value for value_key, value_value in value.items()}
            increments = {'value.{}'.format(k): val for k, val in value.items()}
            if start:
                res.append(pymongo.UpdateOne({'key': key}, {'$inc': increments, '$set': {'start': start}}, upsert=True))
            else:
                res.append(pymongo.UpdateOne({'key': key}, {'$inc': increments, '$setOnInsert': {'start': start}},
                                             upsert=True))
            if (i + 1) % batch_size == 0:
                self.model.bulk_write(res, ordered=False)
                res = list()
        if len(res) > 0:
            self.model.bulk_write(res, ordered=False)

    def get_random_start_sequence(self):
        """
        Получение случайного начала предложения из базы данных

        :return: начало предложения
        :rtype: list
        """
        return list(self.model.aggregate([{'$match': {'start': True}}, {'$sample': {'size': 1}}]))

    def get_sequence(self, key):
        """
        Получение значений из модели по ключу

        :param key: ключ
        :type key: str
        """
        res = self.model.find_one({'key': key})
        return {int(key): value for key, value in res['value'].items()}
