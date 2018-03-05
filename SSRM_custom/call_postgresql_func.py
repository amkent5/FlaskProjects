# example calling a postgresql function
import json
import psycopg2

conn = psycopg2.connect("dbname=learningflask")
cur = conn.cursor()

cur.callproc('users_data')
l_dicts = []
for result in cur.fetchall():
	d = {
		'firstname': None,
		'lastname': None,
		'email': None,
		'uid': None
		}
	d['firstname'] = result[0]
	d['lastname'] = result[1]
	d['email'] = result[2]
	d['uid'] = result[3]
	l_dicts.append(d)

print l_dicts