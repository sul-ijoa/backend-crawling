# sul-ijoa_be_crawling
### 개발환경
**IDE:** IntelliJ IDEA 2023.2.3 (Ultimate Edition)  
**language:** python==3.11.4  
**library:**  
pandas==2.1.1  
numpy==1.25.2  
pyproj==3.4.1  
selenium==4.16.0  

### 공공데이터 수집
https://www.data.go.kr/data/15071760/fileData.do  
'서울특별시_일반음식점 인허가 정보' 사용

### 데이터 가공
1. 지역을 서교동으로 축소
2. 공공데이터에서 사용한 컬럼
   1. address
   2. restaurantName
   3. category
   4. x_coordinate
   5. y_coordinate
3. 필요한 컬럼
   1. latitude (x_coordinate를 latitude로 변환)
   2. longitude (y_coordinate를 longitude로 변환)
4. 추가한 컬럼 **(임의로 기입한 데이터이므로 정확하지 않음)**
   1. sojuPrice
   2. beerPrice
   3. businessHours

### 위도, 경도 추출
TM 좌표계(x, y좌표)를 WGS 84 좌표계(위도, 경도)로 변환  
공공데이터에서 제공한 x_coordinate, y_coordinate를 위도, 경도로 변환함  
변환 이후 x_coordinate, y_coordinate는 사용하지 않으므로 해당 컬럼을 삭제함  
**카카오맵에서 위치 마커를 띄우기 위해서는 위도/경도가 필요하므로 <br>
공공데이터에서 제공된 x, y좌표를 위도, 경도로 변환함**

1. 패키지 설치: pip install pandas numpy pyproj
   1. pandas: csv 파일 읽고 쓰는 데이터 작업을 위함
   2. numpy: 위도, 경도 계산을 위함
   3. pyproj: TM 좌표를 WGS 84 좌표계로 변환하기 위함
```
def convert_tm_to_latlon(tm_x, tm_y):
    """
    TM 좌표를 위도 경도로 변환하는 함수
    - tm_x: x 좌표값 또는 배열
    - tm_y: y 좌표값 또는 배열
    """
    p1 = pyproj.Proj(init='epsg:2097')  # TM 좌표계
    p2 = pyproj.Proj(init='epsg:4326')  # WGS 84 좌표계

    # 만약 tm_x, tm_y가 스칼라 값이라면 배열 형태로 변환
    if not isinstance(tm_x, (list, np.ndarray)):
        tm_x = np.array(tm_x)
    if not isinstance(tm_y, (list, np.ndarray)):
        tm_y = np.array(tm_y)

    lon, lat = pyproj.transform(p1, p2, tm_x, tm_y)
    return lat, lon
```
‘pyproj’ 라이브러리를 사용하여 TM좌표계를 WGS84 좌표계로 변환합니다.
‘pyproj.transform’ 함수를 호출하여 좌표를 변환하고, 위도(lat), 경도(lon)을 반환합니다.


### 가게 사진 크롤링
가게 정보에 사진을 띄우기위해 사진이 필요했지만 공공데이터에서는 지원해주지 않으므로 직접 크롤링하여 사진url을 추출함
1. 패키지 설치:pip install pandas selenium
   1. pandas: csv 파일 읽고 쓰는 데이터 작업을 위함
   2. selenium: 웹 크롤링을 위한 라이브러리
2. csv파일의 restaurantName을 구글에 검색해 By.CSS_SELECTOR, ".sFlh5c.pT0Scc.iPVvYb"인 사진의 url을 가져온다
   1. css_selector가 다를 시 그 다음의 사진을 크롤링 함
      ```
      except StaleElementReferenceException:
         # StaleElementReferenceException이 발생하면 다음 사진으로 크롤링을 진행함
         print("css selector 다름")
         continue
      except Exception as e:
         # 그 외 예외가 발생한 경우에 대한 처리
         if "Message:" not in str(e):
            print(f"오류 발생: {e}")
         else:
            print("css selector 다름")
         continue
      ```
3. 해당 restaurantName에 일치하는 사진을 imageURLs 컬럼을 추가해 데이터를 넣음
