import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")
WEATHER_API_HOST = os.environ.get("API_HOST")


def get_weather(city_name):
    # GeoAPI请求头及URL
    headers = {"X-QW-Api-Key": WEATHER_API_KEY}
    URL_GeoAPI = f"https://{WEATHER_API_HOST}/geo/v2/city/lookup?location={city_name}"
    try:
        GET_Geo_API_JSON = httpx.get(URL_GeoAPI, headers=headers, timeout=10)
        GET_Geo_API_JSON.raise_for_status()
        if GET_Geo_API_JSON.status_code != 200:
            print(f"无法识别城市：{city_name}")
            return None
        # 解析json文件
        GEO_JSON = GET_Geo_API_JSON.json()
        # 从JSON获取城市名
        LOCATION_NAME = GEO_JSON["location"][0]

        # 从JSON获取经纬度 location是列表，取第0个元素再拿lat/lon
        LOCATION_LAT = LOCATION_NAME["lat"]
        LOCATION_LON = LOCATION_NAME["lon"]

        # 实时天气情况的URL
        GET_WEATHER_URL = f"https://{WEATHER_API_HOST}/weather/v1/current/{LOCATION_LAT}/{LOCATION_LON}"
        try:

            GET_WEATHER_STATEMENT_JSON = httpx.get(GET_WEATHER_URL, headers=headers, timeout=10)
            GET_WEATHER_STATEMENT_JSON.raise_for_status()
            if GET_WEATHER_STATEMENT_JSON.status_code != 200:
                print(f"已找到城市 但无法获取该天气信息：{city_name}")
                return None

            GET_WEATHER_JSON = GET_WEATHER_STATEMENT_JSON.json()
            weather_condition = GET_WEATHER_JSON["condition"]["text"]
            weather_temperature = GET_WEATHER_JSON["temperature"]["value"]
            weather_feelsLike = GET_WEATHER_JSON["feelsLike"]["value"]
            weather_result = f"城市：{city_name}\n天气情况：{weather_condition}\n温度：{weather_temperature}\n体感温度：{weather_feelsLike}"
            return weather_result
        except httpx.HTTPStatusError as e:
            print(f"error: 状态码:{e.response.status_code}，获取WEATHER_STATEMENT_JOSN失败")
            return f"查询天气接口失败，状态码：{e.response.status_code}"
        except httpx.RequestError as e:
            print(f"error! 天气接口网络失败：{e}")
            return "天气接口网络请求失败"
        # json.JSONDecodeError 捕获天气接口那一步的 .json()报错
        except json.JSONDecodeError:
            print("error！天气接口返回数据不是合法JSON")
            return "天气接口返回数据解析失败"

    except httpx.HTTPStatusError as e:
        print(f"error: 状态码:{e.response.status_code}，获取GEO_JSON失败")
        return f"城市解析接口失败，状态码：{e.response.status_code}"
    except httpx.RequestError as e:
        print(f"error! Geo接口网络失败：{e}")
        return "城市解析接口网络请求失败"
    # json.JSONDecodeError 捕获 Geo 那一步的 .json()报错
    except json.JSONDecodeError:
        print("error！Geo地理接口返回数据不是合法JSON")
        return "城市地理接口返回数据解析失败"
