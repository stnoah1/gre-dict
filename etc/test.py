import pandas as pd
from tabulate import tabulate

from client.db import CONN

day = 30
sql_query = f"""
    SELECT A.name, A.meaning, B.count, B.recent_search
    FROM hackers_dictionary AS A
    LEFT JOIN my_dictionary AS B
    ON A.name = B.name
    WHERE A.day = {day}
    """

voca_day = pd.read_sql_query(sql_query, CONN)
voca_day['count'] = voca_day['count'].fillna(0)

print(tabulate(voca_day, headers='keys', tablefmt='grid'))
print(voca_day)
