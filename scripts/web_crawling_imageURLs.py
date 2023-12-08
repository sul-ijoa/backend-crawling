import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# HTTP 요청에 사용할 헤더 설정
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

# Chrome 브라우저에서 헤더 설정을 위한 ChromeOptions 설정
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={headers['User-Agent']}")

# ChromeOptions를 사용하여 Chrome 브라우저 초기화
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.google.com/imghp?hl=ko&tab=ri&ogbl")

# 스크립트가 위치한 디렉토리 경로
script_dir = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 경로
input_csv_path = os.path.join(script_dir, '..', 'data', 'output_latlon_csv', '서교동_latlon.csv')
output_csv_path = os.path.join(script_dir, '..', 'data', 'output_latlon_imageURLs_csv', '서교동_latlon_imageUrl.csv')

# CSV 파일 읽기
df = pd.read_csv(input_csv_path)
restaurant_names = df['restaurantName']

# 이미지 URL을 담을 리스트 초기화
all_image_urls = []

# 각 음식점에 대해 검색 및 이미지 수집
for restaurantName in restaurant_names:
    # 이미지가 로드될 때까지 대기하는 WebDriverWait 생성
    wait = WebDriverWait(driver, 2)

    # 검색어 입력
    elem = driver.find_element(By.NAME, "q")  # 페이지 리로드 후 요소를 다시 찾음
    elem.clear()
    elem.send_keys(restaurantName)
    elem.send_keys(Keys.RETURN)

    # 이미지 엘리먼트들이 로드될 때까지 대기
    images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".rg_i.Q4LuWd")))

    # 4개의 이미지 URL
    image_urls = []
    for i, image in enumerate(images):
        if len(image_urls) >= 4:
            break  # 이미지 4개를 수집했으면 루프 종료

        try:
            # 각각의 작은 이미지 클릭
            image.click()

            # 대기 후 큰 이미지 선택
            big_image = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sFlh5c.pT0Scc.iPVvYb")))
            image_url = big_image.get_attribute("src")
            print(f"'{restaurantName}'의 이미지{i + 1} URL:", image_url)

            # 개별 이미지 URL을 리스트에 추가
            image_urls.append(image_url)

        except StaleElementReferenceException:
            print("css selector 다름")
            continue
        except Exception as e:
            if "Message:" not in str(e):
                print(f"오류 발생: {e}")
            else:
                print("css selector 다름")
            continue

    # 이미지 URL을 문자열로 변환하여 리스트에 추가
    all_image_urls.append(', '.join(map(str, image_urls)))

# 이미지 URL 리스트를 데이터프레임에 추가
df['imageURLs'] = all_image_urls

# 결과를 CSV 파일로 저장
df.to_csv(output_csv_path, index=False)