import pandas as pd
gre_db = pd.read_csv('data/gre_db.csv')
gre_db.columns = ["eng", "kor", "??"]
voca_set = {}
for index, row in gre_db.iterrows():
    voca_set[row['eng']] = row['kor']

voca_by_date = pd.read_csv('data/gre_voca_by_day.csv')

for index, row in voca_by_date.iterrows():
    try:
        voca_by_date.loc[index, 'Meaning'] = voca_set[row['Word.1']]
    except:
        print(row['Word.1'], 'not exist in db')
