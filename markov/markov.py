from tokenizer import Tokenizer
from markov_chain import MarkovChain


class MarkovGenerator:
    """
    Обертка для 'class MarkovChain' и 'class Tokenizer'
    """
    class Strategy:
        """
        Базовая стратегия генератора
        """
        def __init__(self, database, text_path, window_size):
            """

            :param text_path: путь к датасету
            :type text_path: str
            :param window_size: размер окна
            :type window_size: int
            """
            self.model = MarkovChain(database, window_size)
            self.text_path = text_path

    class TrainStrategy(Strategy):
        """
        Стратегия для первичного запуска цепи Маркова
        """
        def __init__(self, database, text_path, window_size):
            """

            :param text_path: путь к датасету
            :type text_path: str
            :param window_size: размер окна
            :type window_size: int
            """
            super().__init__(database, text_path, window_size)
            self.tokenizer = Tokenizer(Tokenizer.GenerateNewStrategy(self.text_path))
            self.model.set_tokenizer(self.tokenizer)
            self.model.counter.initialize('tokens')
            self.train()
            self.model.counter.update('tokens')

        def train(self):
            """
            Запуск первичнго обучения цепи Маркова
            """
            print('SAVING A TOKENIZER')
            self.model.tokenizer.save(self.model.tokens)
            print('BUILDING A MODEL')
            model = self.model.create_model_from_text(self.text_path)
            print('SAVING A MODEL')
            self.model.save(model)

    class RetrainStrategy(Strategy):
        """
        Стратегия дообучения цепи Маркова
        """
        def __init__(self, database, text_path, window_size):
            """

            :param text_path: путь к датасету
            :type text_path: str
            :param window_size: размер окна
            :type window_size: int
            """
            super().__init__(database, text_path, window_size)
            self.tokenizer = Tokenizer(Tokenizer.LoadStrategy(self.model.tokens))
            self.model.set_tokenizer(self.tokenizer)
            self.model.counter.update('tokens')
            self.retrain()

        def retrain(self):
            """
            Запуск дообучения цепи Маркова
            """
            print('SAVING A TOKENIZER')
            self.model.tokenizer.strategy.update_from_text(self.text_path, self.model.counter)
            print('BUILDING A MODEL')
            model = self.model.create_model_from_text(self.text_path)
            print('SAVING A MODEL')
            self.model.save(model)

    class GenerateStrategy:
        """
        Стратегия генерации текста
        """
        def __init__(self, database, window_size):
            """

            :param window_size:
            :type window_size: int
            """
            self.model = MarkovChain(database, window_size)
            self.tokenizer = Tokenizer(Tokenizer.LoadStrategy(self.model.tokens))
            self.model.set_tokenizer(self.tokenizer)

    def __init__(self, strategy):
        """

        :param strategy:
        :type strategy: class tokenizer.Tokenizer.Strategy
        """
        self.strategy = strategy

    def generate_sentence(self, size_sent):
        """
        Генерация предложения

        :param size_sent: количество слов в пердложение
        :type size_sent: int
        :return: сгенеиррованное предложение
        :rtype: str
        """
        return self.strategy.model.generate(size_sent)

    def generate_sentences(self, count, size_sent):
        """
        Генерация нескольких предложений

        :param count: количесвто предложений
        :type count: int
        :param size_sent: количесвто слов в предложение
        :type size_sent: int
        :return: сгенерированные предложения
        :rtype: list
        """
        res = []
        for i in range(count):
            try:
                sentence = self.generate_sentence(size_sent) + '\n' * 3
                res.append(sentence)
            except KeyboardInterrupt:
                break
        return res


def main():
    text_path = 'texts/corpus_100.txt'

    generator = MarkovGenerator(MarkovGenerator.TrainStrategy(database='mydatabase', text_path=text_path, window_size=2))

    print('GENERATING TEXT')
    generator.generate_sentences(count=10, size_sent=100)


if __name__ == "__main__":
    main()
