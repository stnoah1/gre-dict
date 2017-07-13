import pandas as pd
import sqlite3

conn = sqlite3.connect("voca.db")
df = pd.read_sql_query("select * from airlines limit 5;", conn)