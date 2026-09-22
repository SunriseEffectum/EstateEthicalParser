from natsort import natsorted
import pandas as pd
import json 

STATES_WEIGHTS = {
    "New Building": 0,
    "Very Good": 1,
    "Good": 2,
    "Bad": 3
}

def clean_data(csv_file_path):
    df = pd.read_csv(csv_file_path, sep=',', encoding='utf-8')
    df.info()

    print(df[['Price', 'Area']].describe())

    Q1_price = df['Price'].quantile(0.25)
    Q3_price = df['Price'].quantile(0.75)
    IQR_price = Q3_price - Q1_price

    Q1_area = df['Area'].quantile(0.25)
    Q3_area = df['Area'].quantile(0.75) 
    IQR_area = Q3_area - Q1_area

    p_max, p_min = Q3_price + 1.5 * IQR_price, Q1_price - 1.5 * IQR_price
    a_max, a_min = Q3_area + 1.5 * IQR_area, Q1_area - 1.5 * IQR_area

    df_clean = df[(df['Price'] >= p_min) & 
                  (df['Price'] <= p_max) &
                  (df['Area'] >= a_min) &
                  (df['Area'] <= a_max)].copy()

    valid_estate_types = [k for k, v in df['Estate Type'].value_counts().items() if v >= 10]

    df_clean = df_clean[df_clean['Estate Type'].isin(valid_estate_types)]

    text_columns = df_clean.select_dtypes(include=['object']).columns
    df_clean[text_columns] = df_clean[text_columns].fillna('Unknown')

    df_clean['Price'] = df_clean['Price'].astype('int32')

    specific_column_name = 'Furnished' if 'Furnished' in df_clean.columns else 'Material'

    df_clean = df_clean[df_clean['District'] != 'Hlavní město Praha']

    metadata = {
        "price_range": {"min": int(df_clean['Price'].min()), "max": int(df_clean['Price'].max())},
        "area_range": {"min": int(df_clean['Area'].min()), "max": int(df_clean['Area'].max())},
        "categories": {
            "estate_types": sorted(df_clean['Estate Type'].unique().tolist()),
            "districts": natsorted(df_clean['District'].unique().tolist()),
            "states": sort_states(df_clean['State'].unique().tolist()),
            specific_column_name.lower(): sorted(df_clean[specific_column_name].unique().tolist())
        },
        "stats": {
            "original_rows_num": len(df),
            "cleaned_rows": len(df_clean)
        }
    }

    output_csv = csv_file_path.replace('.csv', '_clean.csv')
    output_json = csv_file_path.replace('.csv', '_metadata.json')

    df_clean.to_csv(output_csv, index=False, encoding='utf-8')

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

def sort_states(states_list):
    return sorted(states_list, key=lambda x: STATES_WEIGHTS.get(x, 99))