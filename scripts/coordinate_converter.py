import pandas as pd
import numpy as np
import pyproj
import os

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

# 스크립트가 위치한 디렉토리 경로
script_dir = os.path.dirname(os.path.abspath(__file__))

# CSV 파일 경로
input_csv_path = os.path.join(script_dir, '..', 'data', 'input_csv', '서교동.csv')
output_csv_path = os.path.join(script_dir, '..', 'data', 'output_latlon_csv', '서교동_latlon.csv')

# CSV 파일 읽기
df = pd.read_csv(input_csv_path)

# 'x_coordinate'와 'y_coordinate' 열의 값이 숫자로 변환 가능한 행만 선택
df = df[pd.to_numeric(df['x_coordinate'], errors='coerce').notna()]
df = df[pd.to_numeric(df['y_coordinate'], errors='coerce').notna()]

# 'x_coordinate'와 'y_coordinate' 열의 값을 위도경도로 변환하여 새로운 열에 추가
df[['lat', 'lon']] = df.apply(
    lambda row: pd.Series(convert_tm_to_latlon(row['x_coordinate'], row['y_coordinate'])), axis=1)

# 변환된 결과를 새로운 CSV 파일로 저장
df.to_csv(output_csv_path, index=False)
