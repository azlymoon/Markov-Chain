def read_files(filenames):
    """
    Чтение текстовых файлов

    :param filenames: список путей к файлам
    :type filenames: str, optional
    :return: text
    :rtype: str
    """

    text = str()
    if type(filenames) == str:
        with open(filenames, 'r', encoding='utf-8') as file:
            text = file.read()
    else:
        raise TypeError
    return text
