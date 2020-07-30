import psycopg2
import os
import urllib.parse as urlparse

# DATABASE_URL = os.environ['DATABASE_URL']
url = urlparse.urlparse(os.environ['DATABASE_URL'])
dbname = url.path[1:]
user = url.username
password = url.password
host = url.hostname
port = url.port

conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, user_id VARCHAR, found_body_part VARCHAR, exercise_inquiry VARCHAR, exercise0 VARCHAR, exercise1 VARCHAR, exercise2 VARCHAR, exercise_num INTEGER, amount_of_seconds INTEGER, initial_timer_ts VARCHAR, initial_timer_channel VARCHAR);")
conn.commit()
cur.execute("SELECT * FROM users")
print(cur.fetchall())
cur.close()
conn.close()

# import psycopg2
# import urllib.parse as urlparse
# import os


