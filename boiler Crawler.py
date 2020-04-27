import requests
from openpyxl import load_workbook
from bs4 import BeautifulSoup
from boilerpipe.extract import Extractor

# requests.get 모듈의 headers 인자에 넣을 값
# 서버에게 외부 프로그램이 아닌 정상적인 형태로 접근하는 것으로 보일 수 있음
header = {'User-Agent': 'Mozilla/5.0', 'referer': 'http://naver.com'}
title_list = []  # 제목 리스트
url_list = []  # URL 리스트


def get_final_url(origin_url):
    '''
    본문 태그들이 포함된 원본 HTML을 사용하기 위한 URL 가공
    가공을 하지 않으면 본문 태그들이 보이지 않는다
    '''
    try:
        url_1 = origin_url
        html_result = requests.get(url_1)
        soup_temp = BeautifulSoup(html_result.text, 'html.parser')
        area_temp = soup_temp.find(id='screenFrame')
        url_2 = area_temp.get('src')

    # id='screenFrame 태그를 못 찾았을때, url_1이 이미 url_2단계
    except:
        try:
            area_temp = soup_temp.find(id='mainFrame')
            url_3 = area_temp.get('src')
            url_4 = "https://blog.naver.com" + url_3
            return url_4
        except:
            return origin_url

    # 예외가 아닌 경우 url_2를 가지고 계속 URL 가공
    try:
        html_result = requests.get(url_2)
        soup_temp = BeautifulSoup(html_result.text, 'html.parser')
        area_temp = soup_temp.find(id='mainFrame')
        url_3 = area_temp.get('src')
        url_4 = "https://blog.naver.com" + url_3
        return url_4

    except Exception as ex:
        print('오류 발생 :', ex)
        return origin_url


def food_excel():
    '''
    food.xlsx 리스트 저장
    '''
    try:
        load_wb = load_workbook('C:/Users/박범진/PycharmProjects/recipe/food.xlsx', data_only=True)
        load_ws = load_wb['food']
        get_cells = load_ws['A1':'A843']

        food = []
        for row in get_cells:
            for cell in row:
                food.append(cell.value)

        return food

    except Exception as ex:
        print('오류 발생 :', ex)


def search_obj_parsing(keyword, page):
    '''
    검색 결과 객체 파싱
    '''
    try:
        # 검색 URL = 네이버 검색
        url = 'http://search.naver.com/search.naver'

        # 검색 조건들
        param = {
            'where': 'post',  # 블로그 검색
            'query': keyword,  # 검색 단어
            'st': 'sim',  # 정렬, sim-관련도, date-최신
            'srchby': 'all',  # 검색영역, all-전체, title-제목
            'dup_remove': 1,  # 유사문서 포함 제거, 0-검색, 1-제외
            'start': 1 + (page * 10)  # 검색 페이지
        }

        # 응답
        response = requests.get(url, params=param, headers=header)

        # 객체로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup

    except Exception as ex:
        print('오류 발생 :', ex)


def blog_obj_parsing(url):
    '''
    블로그 포스트 객체 파싱
    '''
    try:
        # 응답
        response = requests.get(url, headers=header)

        # 객체로 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        return soup

    except Exception as ex:
        print('오류 발생 :', ex)


def blog_body_html(soup):
    '''
    블로그 포스트 Body 부분 파싱
    '''
    try:
        # 객체 형태 코드에서 body 부분 파싱
        area_body = soup.findAll('div', {'class': 'se-main-container'})

        # body 부분 파싱이 없을 경우
        if not area_body:
            # 객체 형태 코드에서 body 부분 파싱
            area_body = soup.findAll("div", {"id": {"postViewArea", "post-view"}})

            # body 부분 파싱이 없을 경우
            if not area_body:
                print("오류 발생 : No results matched with blog body")

            return str(area_body)

        return str(area_body)

    except Exception as ex:
        print('오류 발생 :', ex)


def title_list_add(soup):
    '''
    블로그 포스트 제목 리스트
    '''
    try:
        # 객체 형태 코드에서 title 부분 파싱
        area_title = soup.find('div', {'class': 'blog section _blogBase _prs_blg'}).find_all('a', {
            'class': 'sh_blog_title _sp_each_url _sp_each_title'})

        # title 부분 파싱이 없을 경우
        if not area_title:
            print("오류 발생 : No results matched")
            exit()

        # Title 저장
        for tag in area_title:
            title_temp = str(tag.get('title'))
            title_list.append(title_temp)

    except Exception as ex:
        print('오류 발생 :', ex)


def url_list_add(soup):
    '''
    가공된 URL 리스트
    '''
    try:
        # 객체 형태 코드에서 URL 부분 파싱
        area_url = soup.find('div', {'class': 'blog section _blogBase _prs_blg'}).find_all('a', {'class': 'url'})

        # URL 부분 파싱이 없을 경우
        if not area_url:
            print("오류 발생 : No results matched")
            exit()

        # 가공된 URL 저장
        for tag in area_url:
            url_temp = str(tag.get('href'))
            url_list.append(get_final_url(url_temp))

    except Exception as ex:
        print('오류 발생 :', ex)


def search_count(soup):
    '''
    검색된 개수
    '''
    try:
        # 객체 형태 코드에서 건수 부분 파싱
        area_count = soup.find_all('span', {'class': 'title_num'})

        # 건수 부분 파싱이 없을 경우
        if not area_count:
            print("오류 발생 : No results matched")
            exit()

        st = str(area_count).find(' / ') + 3
        ed = str(area_count).find('건')

        return str(area_count)[st:ed]

    except Exception as ex:
        print('오류 발생 :', ex)


def main():
    '''
    메인 실행 부분
    '''
    # 검색 실행
    try:
        food = food_excel()  # food.xlsx 리스트

        keyword = str(input("> 검색단어 : "))  # 검색 단어 입력
        soup = search_obj_parsing(keyword, 0)  # 검색결과 객체 파싱
        print("검색된 결과", search_count(soup), "건")  # 검색건수 출력

        choice = int(input("> 검색번호(1-1000) : "))  # 검색할 번호 입력

        # 첫페이지가 아닐경우 해당페이지 객체 파싱
        if choice > 10:
            page = int(choice / 10)
            soup = search_obj_parsing(keyword, page)

        title_list_add(soup)  # title_list 에 추가
        url_list_add(soup)  # url_list 에 추가

        list_num = (choice % 10) - 1  # 리스트 번호
        if list_num == -1:
            list_num = 9

        url_names = ['blog.me', 'blog.naver']  # 네이버 블로그인지 판별할 리스트
        for url_name in url_names:
            # URL이 네이버 블로그가 맞는지
            if url_name in url_list[list_num]:
                soup = blog_obj_parsing(url_list[list_num])  # 블로그 포스트 객체 파싱
                # 블로그 포스트 본문 파싱 후 추출
                extractor = Extractor(extractor='KeepEverythingExtractor', html=blog_body_html(soup))
                extracted_text = extractor.getText()  # 텍스트 뽑기(한덩어리)
                raw_texts = list(extracted_text.splitlines())  # 문장으로 나누기

                print("- 제목 :", title_list[list_num])  # 블로그 포스트 제목 출력
                print("- 내용")  # 이하 내용 출력
                for line in raw_texts:
                    for i in range(len(food)):
                        if food[i] in line:  # food.xlsx에 있는 단어가 있을 시
                            print(line)
                            break

                exit()

        # 네이버 블로그가 아닐 경우 종료
        print("오류 발생 : 네이버 블로그만 지원합니다.")
        exit()

    except Exception as ex:
        print('오류 발생 :', ex)


main()  # 메인 실행

