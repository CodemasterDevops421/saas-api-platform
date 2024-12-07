import random
import string
from datetime import datetime, timedelta
import psycopg2
import json

def generate_test_users(count: int):
    users = []
    for i in range(count):
        users.append({
            'email': f'user{i}@test.com',
            'password': 'test123',
            'full_name': f'Test User {i}'
        })
    return users

def generate_api_requests(user_ids: list, days: int):
    requests = []
    endpoints = ['/analytics', '/users', '/billing']
    methods = ['GET', 'POST']
    
    for user_id in user_ids:
        for day in range(days):
            date = datetime.now() - timedelta(days=day)
            requests_count = random.randint(50, 200)
            
            for _ in range(requests_count):
                requests.append({
                    'user_id': user_id,
                    'endpoint': random.choice(endpoints),
                    'method': random.choice(methods),
                    'status_code': random.choices([200, 400, 500], weights=[0.95, 0.04, 0.01])[0],
                    'created_at': date + timedelta(seconds=random.randint(0, 86400))
                })
    return requests

def main():
    conn = psycopg2.connect(
        dbname="saas_platform",
        user="postgres",
        password="postgres",
        host="localhost"
    )
    cur = conn.cursor()
    
    # Generate and insert test data
    users = generate_test_users(1000)
    user_ids = []
    
    for user in users:
        cur.execute(
            "INSERT INTO users (email, hashed_password, full_name) VALUES (%s, %s, %s) RETURNING id",
            (user['email'], user['password'], user['full_name'])
        )
        user_ids.append(cur.fetchone()[0])
    
    requests = generate_api_requests(user_ids, 30)
    
    for req in requests:
        cur.execute(
            "INSERT INTO api_requests (user_id, endpoint, method, status_code, created_at) VALUES (%s, %s, %s, %s, %s)",
            (req['user_id'], req['endpoint'], req['method'], req['status_code'], req['created_at'])
        )
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()