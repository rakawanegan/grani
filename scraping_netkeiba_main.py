import os
import pandas as pd
import datetime
import json
from src.scraping_netkeiba import Results, HorseResults, Peds, Return, update_data, get_race_id_list


def update_race_data(START_YEAR, END_YEAR, DATA_RACE_RESULTS, DATA_RETURN_RESULTS) -> list:
    # レースIDのリストを取得
    race_ids = get_race_id_list(START_YEAR, END_YEAR)
    # まずはレース結果のデータを取得
    Results.info()
    pre_race_results = pd.read_csv(DATA_RACE_RESULTS) if os.path.exists(DATA_RACE_RESULTS) else pd.DataFrame()
    race_results = Results.scrape(race_ids)
    # 払い戻し表のデータを取得
    Return.info()
    pre_return_data = pd.read_csv(DATA_RETURN_RESULTS) if os.path.exists(DATA_RETURN_RESULTS) else pd.DataFrame()
    return_data = Return.scrape(race_ids)
    # 取得したデータを更新
    updated_race_results = update_data(pre_race_results, race_results)
    updated_return_data = update_data(pre_return_data, return_data)
    # それぞれのデータをCSVファイルに保存
    updated_race_results.to_csv(DATA_RACE_RESULTS)
    updated_return_data.to_csv(DATA_RETURN_RESULTS)
    return race_ids


def update_horse_data(DATA_RACE_RESULTS, DATA_HORSE_RESULTS, DATA_PEDS_RESULTS, race_ids) -> list:
    # 前回取得した馬IDのリストを取得
    pre_horse_results_index = set(pd.read_csv(DATA_RACE_RESULTS, index_col=0).loc[race_ids, "horse_id"].unique()) if os.path.exists(DATA_RACE_RESULTS) else set()
    # 馬IDのリストを取得
    horse_ids = list(set(pd.read_csv(DATA_RACE_RESULTS)["horse_id"].unique()) - pre_horse_results_index)
    horse_ids = [str(horse_id) for horse_id in horse_ids]
    # 馬の過去成績のデータを取得
    HorseResults.info()
    pre_horse_results = pd.read_csv(DATA_HORSE_RESULTS) if os.path.exists(DATA_HORSE_RESULTS) else pd.DataFrame()
    horse_results = HorseResults.scrape(horse_ids)
    # 血統データを取得
    Peds.info()
    pre_peds_data = pd.read_csv(DATA_PEDS_RESULTS) if os.path.exists(DATA_PEDS_RESULTS) else pd.DataFrame()
    peds_data = Peds.scrape(horse_ids)
    # 取得したデータを更新
    updated_horse_results = update_data(pre_horse_results, horse_results)
    updated_peds_data = update_data(pre_peds_data, peds_data)
    # それぞれのデータをCSVファイルに保存
    updated_horse_results.to_csv(DATA_HORSE_RESULTS)
    updated_peds_data.to_csv(DATA_PEDS_RESULTS)
    return horse_ids


def main():
    START_YEAR = 2020 # スクレイピングする年の開始年
    END_YEAR = 2023 # スクレイピングする年の終了年
    DATA_BASE_DIR = 'data/scraped_data'
    DATA_RACE_RESULTS = f'{DATA_BASE_DIR}/race_results.csv'
    DATA_RETURN_RESULTS = f'{DATA_BASE_DIR}/return_data.csv'
    DATA_HORSE_RESULTS = f'{DATA_BASE_DIR}/horse_results.csv'
    DATA_PEDS_RESULTS = f'{DATA_BASE_DIR}/peds_data.csv'
    ONLY_HORSE_RESULTS = False # Trueにするとレース結果のデータを取得せず、馬の過去成績のデータだけを取得する(なんらかの理由でレース結果のみデータを持っている場合に使用)

    os.makedirs(DATA_BASE_DIR, exist_ok=True)

    # 前回実行時のメタデータを取得
    metadata = {}
    pre_metadata = json.load(open(f'{DATA_BASE_DIR}/metadata.json')) if os.path.exists(f'{DATA_BASE_DIR}/metadata.json') else {}
    if len(pre_metadata):
        print('previous execute date info: ', pre_metadata['date'])
    metadata["pre_metadata"] = pre_metadata

    # レースデータを取得
    race_ids = update_race_data(START_YEAR, END_YEAR, DATA_RACE_RESULTS, DATA_RETURN_RESULTS) if not ONLY_HORSE_RESULTS else []
    horse_ids = update_horse_data(DATA_RACE_RESULTS, DATA_HORSE_RESULTS, DATA_PEDS_RESULTS, race_ids)

    # メタデータを更新
    metadata["date"] =  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    metadata["append_race_id"] = race_ids
    metadata["append_horse_id"] = horse_ids
    with open(f'{DATA_BASE_DIR}/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)

if __name__ == "__main__":
    main()
