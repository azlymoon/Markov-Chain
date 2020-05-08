class Counter:
    """
    Счетчик индексов в базе данных
    """
    def __init__(self, db):
        """

        :param db: база данных
        """
        self.db = db

    def initialize(self, collection_name, last_id: int = 0):
        """

        :param collection_name: имя коллекции
        :type collection_name: str
        :param last_id: id последнего элемента
        :type last_id: int
        """
        self.db['counter'].insert_one({'name': collection_name, 'last_id': last_id})

    def update(self, collection_name):
        """
        Обновление поля 'last_id' для 'collection_name' в коллекции 'counter'

        :param collection_name: имя коллекции
        :type collection_name: str
        """
        last_id = {'last_id': self.db[collection_name].find_one(sort=[('idx', -1)])['idx']}
        self.db['counter'].update_one({'name': collection_name}, {'$set': last_id})

    def increment(self, collection_name, increment_amount: int = 1):
        """
        Увеличение поля 'last_id' для 'collection_name' на 'increment_amount'

        :param collection_name: имя коллекции
        :type collection_name: str
        :param increment_amount: значение приращения
        :type increment_amount: int
        """
        self.db['counter'].find_one_and_update({'name': collection_name}, {'$inc': {'last_id': increment_amount}})

    def get(self, collection_name):
        """
        Получение 'last_id'

        :param collection_name: имя коллекции
        :type collection_name: str
        :return: last_id
        :rtype: int
        """
        return self.db['counter'].find_one({'name': collection_name})['last_id']