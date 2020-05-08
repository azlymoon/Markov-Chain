import random


class Dictogram(dict):
    def __init__(self, iterable=None):
        # Инициализируем наше распределение как новый объект класса,
        # добавляем имеющиеся элементы
        super(Dictogram, self).__init__()
        self.types = 0  # число уникальных ключей в распределении
        self.tokens = 0  # общее количество всех слов в распределении
        if iterable:
            self.update(iterable)

    def update(self, iterable):
        """
        Обновляем распределение элементами из имеющегося итерируемого набора данных

        :param iterable: optional
        """
        for item in iterable:
            if item in self:
                self[item] += 1
                self.tokens += 1
            else:
                self[item] = 1
                self.types += 1
                self.tokens += 1

    def count(self, item):
        """
        Возвращаем значение счетчика элемента, или 0

        :param item: значение
        :return: значение счетчика
        :rtype: int
        """
        if item in self:
            return self[item]
        return 0

    def return_random_word(self):
        """
        Вернуть случайное слово

        :return: случайное слово
        :rtype: str
        """
        random_key = random.sample(self, 1)
        # Другой способ:
        # random.choice(histogram.keys())
        return random_key[0]

    def return_weighted_random_word(self):
        """
        Сгенерировать псевдослучайное число между 0 и (n-1), где n - общее число слов

        :return: случайное число
        :rtype: str
        """
        random_int = random.randint(0, self.tokens-1)
        index = 0
        list_of_keys = list(self.keys())
        # вывести 'случайный индекс:', random_int
        for i in range(0, self.types):
            index += self[list_of_keys[i]]
            # вывести индекс
            if index > random_int:
                # вывести list_of_keys[i]
                return list_of_keys[i]