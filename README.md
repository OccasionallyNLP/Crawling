# Crawling
crawling - 맛집

## 일정
22.11.5 ~ 부터 진행 중  
22.11.27 : 리뷰 데이터도 긁어오도록.
22.12.01 : 카카오, 망고플레이트 리뷰 데이터 크롤링 완료.

## 크롤링 할 대상
1. 네이버 : 개발 진행 
    - 네이버 지도가 hash? 등으로 크롤링을 못하게 해두었기에, 네이버에서 검색을 해서 가져오는 방식으로 변경(22.11.20)  
    - 22.12.10 mobile web으로 접근해서 크롤링 할 예정
2. 카카오 : 개발 완료
    - 22.11.19
    - 서울시 25개 구 130시간 정도 소요
    - 리뷰 데이터도 긁어오는 것 추가시 너무 많은 시간이 소요됨. 강남구만 120시간 예상
        - 22.12.10 최적화가 필요함 - log 분석 진행 중.  
        - log 분석 (강남구 - 1271개) : 2개 이상의 주소인 경우가 17.6%에 달함
            - city, gu, dong까지 넣어서 검색을 진행하는 것이 합리적으로 보임.
            - dong은 소재지 주소(구 주소)로 진행(없으면 도로명 주소로)
        
3. 망고플레이트 : 개발 완료
    - 22.11.19

## Data
행안부에서 제공하는 음식점 데이터를 토대로, 네카망 데이터 수집 중.
1. 네이버 : 리뷰 긁어오는 것 막아둠 - 22.12.10 재확인 예정 - 모바일 버전은 가능할 것으로 생각됨.
2. 카카오
3. 망고플레이트

## HW
- 개발 PC - 윈도우
- 워크 스테이션 - 우분투 

## selenium 우분투 설치
chrome - linux 90.0.4430.72 version 설치

https://somjang.tistory.com/entry/Ubuntu-Ubuntu-%EC%84%9C%EB%B2%84%EC%97%90-Selenium-%EC%84%A4%EC%B9%98%ED%95%98%EA%B3%A0-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0  : ubuntu에 selenium 설치하기

https://mryeo.tistory.com/10  : chrome 삭제 후 재설치

https://miiingo.tistory.com/349  : 구버전의 chrome 설치
https://www.slimjet.com/chrome/google-chrome-old-version.php 
