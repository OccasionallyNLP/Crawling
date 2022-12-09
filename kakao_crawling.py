import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import os
import pandas as pd
import argparse
import string
import pandas as pd
import json
from utils.utils import get_logs
import time
from tqdm import tqdm
from typing import Dict, List
import re
import copy

def get_reviews(driver,action,c):
    # select review
    try:
        driver.find_element(value=f"#info\.search\.place\.list > li:nth-child({c}) > div.rating.clickArea > span.score > a",  by = 'css selector').click()
    except:
        return []
    # 아예 새 페이지가 열림.
    driver.implicitly_wait(args.wait_second)
    last_tab = driver.window_handles[1]
    driver.switch_to.window(window_name=last_tab)

    cnt = 1
    reviews = []
    check_cnt = 0
    while True:
        try:
            review=driver.find_element(value=f"#mArticle > div.cont_evaluation > div.evaluation_review > ul > li:nth-child({cnt})",  by = 'css selector').text
            reviews.append(review)
            check_cnt = 0
            cnt+=1
        except:
            try:
                tag = driver.find_element(value="#mArticle > div.cont_evaluation > div.evaluation_review > a",  by = 'css selector')
                action.move_to_element(tag).perform()
                driver.implicitly_wait(args.wait_second)   
                tag.click()
                check_cnt+=1
                driver.implicitly_wait(args.wait_second)   
                if check_cnt == 2:
                    break
            except:
                break    

    driver.close()
    first_tab = driver.window_handles[0]
    driver.switch_to.window(window_name=first_tab)
    return reviews

def get_data_from_page():
    c = 1
    while True:
        try:
            name = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.head_item.clickArea > strong > a.link_name"%c,by='css selector').text
            address = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.info_item > div.addr > p:nth-child(1)"%c,by='css selector').text
            score = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.rating.clickArea > span.score > em"%c,by='css selector').text
            reviews=get_reviews(driver, action, c)
            dic = dict(name=name, address = address, score = score, reviews = reviews)
            if dic in answer_list:
                return True
            answer_list.append(dic)
            c+=1
        except:
            return False
        
# query generate
def query_generation(query:str, location:Dict, city:str):
    #if i.split()[-1].endswith('점'):
    #   query = ' '.join(query.split()[:-1])
    query = city + ' ' + location['자치구'][:-1] + ' ' + query
    return query

MANGO_URL = 'https://www.mangoplate.com/'
KAKAO_URL = 'https://map.kakao.com/'
GOOGLE_URL = 'https://www.google.com/maps'
# OK - 기존과 바뀜 - 함수 통일화
ALPHABET = list(string.ascii_uppercase)
parser = argparse.ArgumentParser(description='parse')
# argument는 원하는 만큼 추가한다.
parser.add_argument('--output_dir', type=str, default = './output/seoul/kakao')
parser.add_argument('--data_dir', type=str, default = './data/seoul/%s.json')
parser.add_argument('--where', type=str, choices=['mango','google','kakao'], default='kakao')
parser.add_argument('--wait_second', type=int, default = 2)
parser.add_argument('--city', type=str, default = '서울')

if __name__ == '__main__':
    logger_1, logger_2 = get_logs()
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    if args.where == 'mango':
        default_url = MANGO_URL

    elif args.where == 'kakao':
        default_url = KAKAO_URL

    elif args.where == 'google':
        default_url = GOOGLE_URL
    options = webdriver.chrome.options.Options()
    options.add_argument('headless') #headless모드 브라우저가 뜨지 않고 실행됩니다.
    #options.add_argument('--window-size= x, y') #실행되는 브라우저 크기를 지정할 수 있습니다.
    options.add_argument('--start-maximized') #브라우저가 최대화된 상태로 실행됩니다.
    options.add_argument('--start-fullscreen') #브라우저가 풀스크린 모드(F11)로 실행됩니다.
    options.add_argument('--blink-settings=imagesEnabled=false') #브라우저에서 이미지 로딩을 하지 않습니다.
    options.add_argument('--mute-audio') #브라우저에 음소거 옵션을 적용합니다.
    #options.add_argument('incognito') #시크릿 모드의 브라우저가 실행됩니다.
    driver = webdriver.Chrome('../../Crawling/chromedriver', options=options)
    driver.get(default_url)
    action = ActionChains(driver)
    gus = [i.strip() for i in open('./data/서울시_자치구.txt','r',encoding='utf-8').readlines()]
    # data load
    #gus = [i.strip() for i in open('./data/서울시_자치구.txt','r',encoding='utf-8').readlines()]
    for gu in gus:
        data = json.load(open(args.data_dir%gu))
        unique_data = {}
        for i,j in data.items():
            j['name'] = i
            query = query_generation(i, j, args.city)
            unique_data[query]=j
        print(gu)
        now = time.time()
        ####################################################################################
        for _,(query, value) in enumerate(tqdm(unique_data.items())):
            # if _ == 1:
            #     break
            driver.get(default_url)
            driver.implicitly_wait(args.wait_second)
            answer_list = []
            value['%s_score'%args.where]=[]
            driver.find_element(value="#search\.keyword\.query",  by = 'css selector').send_keys(query)
            driver.find_element(value="#search\.keyword\.query",  by = 'css selector').send_keys(Keys.RETURN)
            check = False
            try:
                # 1 page 이상인 경우
                driver.find_element(value="#info\.search\.place\.more",by='css selector').click()
                time.sleep(args.wait_second)
                while True:
                    page_list = driver.find_element(value="#info\.search\.page > div",by='css selector').text.split()[1:-1]
                    for p in page_list:
                        change_p = int(p)%5 
                        if change_p == 0:
                            change_p = 5
                        driver.find_element(value="#info\.search\.page\.no%s"%change_p,by='css selector').click()
                        time.sleep(args.wait_second)
                        check = get_data_from_page()
                        if check:
                            break
                    if check:
                        break
                    driver.find_element(value="#info\.search\.page\.next",by='css selector').click()
                    driver.implicitly_wait(args.wait_second)

            except:
                get_data_from_page()
            value['%s_score'%args.where]=copy.deepcopy(answer_list)
            logger_1.info(query)
            logger_1.info(value)
            continue
        ####################################################################################
        print(time.time()-now)
        json.dump(unique_data,open(os.path.join(args.output_dir,'%s.json'%gu),'w'))
