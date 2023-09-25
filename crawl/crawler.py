from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import requests
import os
import re

total_num = 0
 
def image_down_multi(image_url_list):
    global total_num
    for i in range(len(image_url_list)):
        keword_image_get = requests.get(image_url_list[i])
        num = total_num + i
        
        with open(fr'image/{num}_image.jpg', 'wb') as fl_s:
            fl_s.write(keword_image_get.content)
        
        total_num += 1
 
 
def remove_all_file(file_path):
    if os.path.exists(file_path):
        for file in os.scandir(file_path):
            os.remove(file.path)
        return 'Remove All File'
    else:
        return 'Directory Not Found'


 
user_agents = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
              'Chrome/102.0.5005.63 Safari/537.36'
ver_1 = re.compile(r'(?<=Chrome/).+?(?= )').search(user_agents).group()
ver_2 = chromedriver_autoinstaller.get_chrome_version()
if not ver_1 == ver_2:
    user_agents = user_agents.replace(ver_1, ver_2)
headers = {'user-agent': user_agents}
 
print('무신사 이미지 다운로드 시작')
base_url = 'https://www.musinsa.com/app/goods/'

for goods_num in range(1, 1000000):
    image_list = []
    image_page = base_url + str(goods_num)
    if not image_page:
        continue
 
    get_req = requests.get(image_page, timeout=10, headers=headers)
    if not get_req.status_code == 200:
        print('페이지 접근 오류!')
        continue
 
    soup = BeautifulSoup(get_req.text, 'html.parser')
    
    # 이미지 클래스 체크
    if not soup.find(class_='product_img_basic'):
        # print('이미지 요소를 찾을 수 없음!')
        continue
    
    # remove_all_file('image')  # 폴더 초기화
    
    # print('goods_num: {goods_num} 발견, 다운로드를 시도합니다'.format(goods_num=goods_num))
 
    # img 태그에서 src(이미지 url)를 리스트에 넣기
    # 리스트에 넣을 때 이미지 사이즈 변환 (초기값 60px에서 500px로)
    prdt_image_tags = soup.find(class_='product_thumb').find_all('img')
    [image_list.append('http:' + str(src['src']).replace('60.jpg', '500.jpg')) for src in prdt_image_tags]
 
    # 이미지 다운로드
    image_down_multi(image_list)