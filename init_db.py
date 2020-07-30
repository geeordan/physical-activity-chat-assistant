import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, user_id VARCHAR, found_body_part VARCHAR, exercise_inquiry VARCHAR, exercise0 VARCHAR, exercise1 VARCHAR, exercise2 VARCHAR, exercise_num INTEGER, amount_of_seconds INTEGER, initial_timer_ts VARCHAR, initial_timer_channel VARCHAR);")
conn.commit()
cur.close()
conn.close()