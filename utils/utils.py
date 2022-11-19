import logging
def get_logs():
    logger_1 = logging.getLogger('')
    logger_1.setLevel(logging.INFO)
    
    logger_2 = logging.getLogger('log')
    logger_2.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s- %(message)s')
    file_handler = logging.FileHandler(r'log.txt',encoding='utf-8')
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger_1.addHandler(file_handler)
    logger_2.addHandler(stream_handler)
    return logger_1, logger_2