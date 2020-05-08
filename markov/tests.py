import unittest
import pymongo

from markov import MarkovGenerator


class TrainTests_lol(unittest.TestCase):
    def setUp(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client['test_db']

    def test_train(self):
        generator = MarkovGenerator(MarkovGenerator.TrainStrategy(database=self.db, text_path='test_texts/test.txt', window_size=2))

        manual_model = {
            'end бои': {'у': 1},
            'бои у': {'сопоцкина': 1},
            'у сопоцкина': {'и': 1},
            'сопоцкина и': {'друскеник': 1},
            'и друскеник': {'закончились': 1},
            'друскеник закончились': {'отступлением': 1},
            'закончились отступлением': {'германцев': 1},
            'отступлением германцев': {'.': 1},
            'германцев .': {'end': 1},
        }

        model = dict()
        tokenizer = generator.strategy.tokenizer
        for line in self.db['model'].find():
            line_key = ' '.join([tokenizer.idx2word(idx) for idx in line['key'].split()])
            line_value = {tokenizer.idx2word(key): value for key, value in line['value'].items()}
            model[line_key] = line_value

        self.assertEqual(manual_model, model)

    def test_retrain(self):
        dual_manual_model = {
            'end бои': {'у': 1},
            'бои у': {'сопоцкина': 1},
            'у сопоцкина': {'и': 1},
            'сопоцкина и': {'друскеник': 1},
            'и друскеник': {'закончились': 1},
            'друскеник закончились': {'отступлением': 1},
            'закончились отступлением': {'германцев': 1},
            'отступлением германцев': {'.': 1},
            'германцев .': {'end': 1},
            'end об': {'этом': 1},
            'об этом': {'сообщает': 1},
            'этом сообщает': {'afp': 1},
            'сообщает afp': {'.': 1},
            'afp .': {'end': 1}
         }
        train_generator = MarkovGenerator(MarkovGenerator.TrainStrategy(database=self.db,
                                                                        text_path='test_texts/test.txt',
                                                                        window_size=2))

        retrain_generator = MarkovGenerator(MarkovGenerator.RetrainStrategy(database=self.db,
                                                                            text_path='test_texts/retrain_test',
                                                                            window_size=2))

        model = dict()
        tokenizer = retrain_generator.strategy.tokenizer
        for line in self.db['model'].find():
            line_key = ' '.join([tokenizer.idx2word(idx) for idx in line['key'].split()])
            line_value = {tokenizer.idx2word(key): value for key, value in line['value'].items()}
            model[line_key] = line_value

        self.assertEqual(dual_manual_model, model)

    def tearDown(self):
        self.client.drop_database('test_db')


unittest.main()
