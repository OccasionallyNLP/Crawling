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

# basic
MANGO_URL = 'https://www.mangoplate.com/'
KAKAO_URL = 'https://map.kakao.com/'
GOOGLE_URL = 'https://www.google.com/maps'
# OK - 기존과 바뀜 - 함수 통일화
ALPHABET = list(string.ascii_uppercase)

logger_1, logger_2 = get_logs()
parser = argparse.ArgumentParser(description='parse')
# argument는 원하는 만큼 추가한다.
parser.add_argument('--output_dir', type=str, default = './output/seoul/mango')
parser.add_argument('--data_dir', type=str, default = './data/seoul/%s.json')
parser.add_argument('--where', type=str, choices=['mango','google','kakao'], default='mango')
parser.add_argument('--city', type=str, default = '서울')
parser.add_argument('--wait_second', type=int, default = 2)



# query generate
def query_generation(query:str, location:Dict, city:str):
    if i.split()[-1].endswith('점'):
        query = ' '.join(query.split()[:-1])
    query = city + ' ' + location['자치구'][:-1] + ' ' + query
    return query

# review
def parse_review_info(review_info):
    review_info = review_info.split('\n')
    output = {}
    for i in review_info:
        if i.strip().startswith('전체'):
            try:
                output['total'] = int(i.strip().split()[-1])
            except:
                output['total'] = 0
                output['good'] = 0
                output['fine'] = 0
                output['not_good'] = 0
                return output
        elif i.strip().startswith('맛있다'):
            output['good'] = int(i.strip().split()[-1])
        elif i.strip().startswith('괜찮다'):
            output['fine'] = int(i.strip().split()[-1])
        elif i.strip().startswith('별로'):
            output['not_good'] = int(i.strip().split()[-1])
    return output

def get_review_data(driver,action):
    cnt = 1
    prev_cnt = None
    reviews = []
    check_cnt = 0
    while True:
        try:
            review = driver.find_element(value=f"body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > ul > li:nth-child({cnt}) > a",  by = 'css selector').text
            reviews.append(review)
            cnt+=1
            check_cnt = 0
        except:
            try:
                tag = driver.find_element(value="body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > div.RestaurantReviewList__MoreReviewButton",  by = 'css selector')
                action.move_to_element(tag).perform()
                driver.implicitly_wait(args.wait_second)   
                driver.find_element(value="body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > div.RestaurantReviewList__MoreReviewButton",  by = 'css selector').click()
                driver.implicitly_wait(args.wait_second)   
                check_cnt+=1
                if check_cnt>1:
                    break
            except:
                break
    return reviews

# page 내에서 information 가져오기
def get_information_from_page(driver, value, page=1):
    # 음식점이 존재하는 경우
    try:
        score = driver.find_element(value=f"body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li.list-restaurant.server_render_search_result_item > div.list-restaurant-item > figure > figcaption > div",  by = 'css selector')
    except:
        # 유일하지 않은 경우
        value['mango_score'].append(None)
        # 아예 존재하지 않는 경우
        return page
    # 한 페이지 내
    for i in range(1,12):
        for j in range(1,3):
            try:
                # 만약 20개가 넘게 있다면 error가 안남.
                score = driver.find_element(value=f'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child({i}) > div:nth-child({j}) > figure > figcaption > div',  by = 'css selector').text
                if score:
                    # 상세 페이지 클릭
                    driver.find_element(value=f'body > main > article > div.column-wrapper > div > div > section > div.search-list-restaurants-inner-wrap > ul > li:nth-child({i}) > div:nth-child({j}) > figure > figcaption > div > a',  by = 'css selector').click()
                    driver.implicitly_wait(args.wait_second)
                    detailed_info=driver.find_element(value="body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table",  by = 'css selector').text
                    # review_info
                    review_info=driver.find_element(value=f"body > main > article > div.column-wrapper > div.column-contents > div > section.RestaurantReviewList > header",  by = 'css selector').text
                    review_info=parse_review_info(review_info)
                    reviews = get_review_data(driver,action)
                    driver.back()
                    driver.implicitly_wait(args.wait_second)
                    value['mango_score'].append(dict(score=score, detailed_info=detailed_info, review_info=review_info, review=reviews))
                else:
                    try:
                        driver.find_element(value=f"body > main > article > div.column-wrapper > div > div > section > div.paging-container > p > a:nth-child({page+1})",  by = 'css selector').click()
                        driver.implicitly_wait(args.wait_second)
                        page+=1
                        return page
                    # 다음 페이지가 없다면 검색 다시
                    except:
                        return page
            except:
                # 다음 페이지
                try:
                    driver.find_element(value=f"body > main > article > div.column-wrapper > div > div > section > div.paging-container > p > a:nth-child({page+1})",  by = 'css selector').click()
                    driver.implicitly_wait(args.wait_second)
                    page+=1
                    return page
                # 다음 페이지가 없다면 기존 페이지 반환
                except:
                    return page
    

if __name__=='__main__':
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
    for gu in gus:
        data = json.load(open(args.data_dir%gu))
        unique_data = {}
        for i,j in data.items():
            j['name'] = i
            query = query_generation(i, j, args.city)
            unique_data[query]=j
        print(gu)
        now = time.time()
        for _,(query, value) in enumerate(tqdm(unique_data.items())):
            page = 1
            current_page = -1
            value['%s_score'%args.where]=[]
            # query 입력
            # 서울로 검색하기 위함임.
            driver.find_element(value="#main-search",  by = 'css selector').send_keys(query)
            driver.find_element(value="#main-search",  by = 'css selector').send_keys(Keys.RETURN)
            driver.implicitly_wait(args.wait_second)
            while current_page!=page:
                current_page = page
                page = get_information_from_page(driver, value, page)
            # 재검색
            driver.get(MANGO_URL)
            driver.implicitly_wait(args.wait_second)
            logger_1.info(query)
            logger_1.info(value)
            #logger_2.info(query)
            #logger_2.info(value)
            continue    
        print(time.time()-now)
        json.dump(unique_data,open('./output/seoul/%s_mango_add.json'%gu,'w'))