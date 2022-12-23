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
from utils.utils import *
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

def get_data_from_page(output, org_addr:str):
    c = 1
    while True:
        try:
            name = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.head_item.clickArea > strong > a.link_name"%c,by='css selector').text
            # 도로명 주소
            address = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.info_item > div.addr > p:nth-child(1)"%c,by='css selector').text
            score = driver.find_element(value="#info\.search\.place\.list > li:nth-child(%d) > div.rating.clickArea > span.score > em"%c,by='css selector').text
            # 원본의 address와 비교
            if org_addr:
                org_addr = ' '.join(org_addr.split()[:3]).strip()
                org_addr = re.sub('특별시','', org_addr)
                addr = ' '.join(address.split()[:3]).strip()
                if addr != org_addr:
                    c+=1
                    continue
            # 아니면 일단 다 검색.
            # 주소 정합성 O
            # 그러면 가져온다.
            # output과 비교
            if output.get(address):
                reviews = output[address]['reviews']                                
            else:
                reviews = get_reviews(driver, action, c)
            dic = dict(name=name, address = address, score = score, reviews = reviews)
            if dic in answer_list:
                return True
            answer_list.append(dic)
            c+=1
        except:
            return False
        
# query generate
def query_generation(df):
    # nan
    if type(df['소재지전체주소'])==float:
        if type(df['도로명전체주소'])==float:
            address = ''
        else:
            address = df['도로명전체주소']
    else:
        address = df['소재지전체주소']
    if address: 
        address = ' '.join(address.split()[:3]).strip()
    query = address+' '+df['사업장명']
    return query.strip()

# OK - 기존과 바뀜 - 함수 통일화
ALPHABET = list(string.ascii_uppercase)
parser = argparse.ArgumentParser(description='parse')
# argument는 원하는 만큼 추가한다.
parser.add_argument('--output_dir', type=str, default = './output/seoul/kakao')
parser.add_argument('--data_dir', type=str, default = './Seoul/%s_kakao_further.csv')
parser.add_argument('--web_driver', type=str, default='./chromedriver_win32/chromedriver')
parser.add_argument('--wait_second', type=int, default = 2)

if __name__ == '__main__':
    logger_1, logger_2 = get_logs()
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    default_url = KAKAO_URL
    options = webdriver.chrome.options.Options()
    #options.add_argument('headless') #headless모드 브라우저가 뜨지 않고 실행됩니다.
    #options.add_argument('--window-size= x, y') #실행되는 브라우저 크기를 지정할 수 있습니다.
    options.add_argument('--start-maximized') #브라우저가 최대화된 상태로 실행됩니다.
    options.add_argument('--start-fullscreen') #브라우저가 풀스크린 모드(F11)로 실행됩니다.
    options.add_argument('--blink-settings=imagesEnabled=false') #브라우저에서 이미지 로딩을 하지 않습니다.
    options.add_argument('--mute-audio') #브라우저에 음소거 옵션을 적용합니다.
    #options.add_argument('incognito') #시크릿 모드의 브라우저가 실행됩니다.
    driver = webdriver.Chrome(args.web_driver, options=options)
    driver.get(default_url)
    action = ActionChains(driver)
    #gus = [i.strip() for i in open('./서울시_자치구.txt','r',encoding='utf-8').readlines()]
    gus = ['강남구']
    for gu in gus:
        data = pd.read_csv(args.data_dir%gu)
        data['query']=data.apply(query_generation, axis=1)
        output = {} # key - address, # item - name, 
        output_kakao_score = {}
        # 최적화
        # address에 있다면, 진행하지 않고
        ## 있을 때, 원본 데이터와 시 구 동이 같아야만 진행. 아니면 진행 x
        print(gu)
        now = time.time()
        ####################################################################################
        for idx in tqdm(data.index):
            if idx==20:
                break
            driver.get(default_url)
            driver.implicitly_wait(args.wait_second)
            answer_list = []
            
            query = data['query'][idx]
            org_addr = data['도로명전체주소'][idx]
            if type(org_addr)==float:
                org_addr = ''
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
                        check = get_data_from_page(output, org_addr)
                        if check:
                            break
                    if check:
                        break
                    
                    # 다음 페이지로 넘어가기.
                    driver.find_element(value="#info\.search\.page\.next",by='css selector').click()
                    driver.implicitly_wait(args.wait_second)
                    next_page_list = driver.find_element(value="#info\.search\.page > div",by='css selector').text.split()[1:-1]
                    if next_page_list == page_list:
                        break

            except:
                get_data_from_page(output, org_addr)
            # output에 추가
            for a in answer_list:
                output[a['address']]=a
            #TOD
            kakao_score = copy.deepcopy(answer_list)
            output_kakao_score[idx]=kakao_score
            #data.loc[idx,'kakao_score'] = kakao_score
            logger_1.info(query)
            logger_1.info(kakao_score)
            continue
        ####################################################################################
        print(time.time()-now)
        data.to_csv(os.path.join(args.output_dir,'%s.csv'%gu))
        json.dump(output_kakao_score,open(os.path.join(args.output_dir,'%s_output_kakao_score.json'%gu),'w'))
        json.dump(output,open(os.path.join(args.output_dir,'%s_output.json'%gu),'w'))