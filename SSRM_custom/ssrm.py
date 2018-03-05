"""
Next steps:
http://songhuiming.github.io/pages/2016/08/18/highcharts-in-python-flask/
Implemented in:
/Users/admin/Documents/Projects/Flask_hc_test

And:
/Users/admin/random_code_bits/postgres_data
Generating the costs data sproc in this location
learningflask=# select * from costs;

"""

import json
import psycopg2
from flask import Flask, render_template, request, session, redirect, url_for
from models import db, User
from forms import SignupForm, LoginForm

'''
*flask*
Flask - main webapp lib
render_template - allows us to render html to the browser
request - allows us to handle POST and GET requests
session, redirect, url_for - all to do with the user session/ cookies (see slide 28 for descriptions)

*models*
connects us to the users table in postgres

*forms*
defines signup form
'''

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/learningflask'
db.init_app(app)
app.secret_key = "development-key"

def return_users_dict():
	conn = psycopg2.connect("dbname=learningflask")
	cur = conn.cursor()

	# create or replace function users_data() returns table(firstname varchar, lastname varchar, email varchar, uid int) as $$ begin return query select _u.firstname, _u.lastname, _u.email, _u.uid from users as _u; end; $$ language plpgsql;
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
	return l_dicts

def return_costs_dict():
	conn = psycopg2.connect("dbname=learningflask")
	cur = conn.cursor()

	# create or replace function costs_data() returns table(job_cost_id int, job_id int, cost_type varchar, job_cost_resource varchar, job_cost_supplier varchar, unit_cost float, unit_sales float) as $$ begin return query select c.job_cost_id, c.job_id, c.cost_type, c.job_cost_resource, c.job_cost_supplier, c.unit_cost, c.unit_sales from costs as c; end; $$ language plpgsql;
	cur.callproc('costs_data')
	l_dicts = []
	for result in cur.fetchall():
		d = {
			'job_cost_id': None,
			'job_id': None,
			'cost_type': None,
			'job_cost_resource': None,
			'job_cost_supplier': None,
			'unit_cost': None,
			'unit_sales': None
			}
		d['job_cost_id'] = result[0]
		d['job_id'] = result[1]
		d['cost_type'] = result[2]
		d['job_cost_resource'] = result[3]
		d['job_cost_supplier'] = result[4]
		d['unit_cost'] = result[5]
		d['unit_sales'] = result[-1]
		l_dicts.append(d)
	return l_dicts

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/about")
def about():
	return render_template("about.html")

# viewing the signup page is a GET
# submitting the signup page is a POST
@app.route("/signup", methods=["GET", "POST"])
def signup():
	# if the user is signed in, they shouldn't be able to see the sign in page again
	if 'email' in session:
		return redirect(url_for('home'))

	form = SignupForm()

	if request.method == "POST":
		if form.validate() == False:
			return render_template('signup.html', form=form)
		else:
			# create new user object and fill it with records from the form
			newuser = User(form.first_name.data, form.last_name.data, form.email.data, form.password.data)
			db.session.add(newuser)
			db.session.commit()

			# when a new user signs up, create a new session
			session['email'] = newuser.email

			# then redirect the user to the apps home page using Flasks redirect and url_for functions
			return redirect(url_for('home'))
	
	elif request.method == "GET":
		return render_template('signup.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():

	if 'email' in session:
		return redirect(url_for('home'))
	
	form = LoginForm()
	
	if request.method == 'POST':
		if form.validate() == False:
			return render_template('login.html', form=form)
		else:
			# extract data from form
			email = form.email.data
			password = form.password.data
			
			# check that the user exists in the db
			user = User.query.filter_by(email=email).first()
			if user is not None and user.check_password(password):
				# then form the session
				session['email'] = email
				return redirect(url_for('home'))
			else:
				return redirect(url_for('login'))
	elif request.method == 'GET':
		return render_template('login.html', form=form)

@app.route('/logout')
def logout():
	# remove the users session
	session.pop('email', None)
	return redirect(url_for('index'))

@app.route("/home", methods=["GET", "POST"])
def home():

	# need to check that the user has signed in before they can access the home page
	if 'email' not in session:
		return redirect(url_for('login'))

	# use the result of the form to dynamically show different parts of home.html
	if request.method == 'POST':


		# http://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/demo/bar-basic/


		# Tests ####################
		form_val = request.form.getlist('btn_select_data')
		print form_val

		form_val2 = request.form.getlist('btn_select_chart_type')
		form_val3 = request.form.getlist('btn_select_xaxis')
		form_val4 = request.form.getlist('btn_select_yaxis')
		print form_val2
		print form_val3
		print form_val4
		##############################

		# selecting data
		if request.form['btn_select_data'] == 'show_users':			
			dict_users = return_users_dict()
			return render_template('home.html', val='show_users', dict_data=dict_users)

		elif request.form['btn_select_data'] == 'show_jobs':
			return render_template('home.html')	# just so it runs for now

		elif request.form['btn_select_data'] == 'show_costs':
			dict_costs = return_costs_dict()
			return render_template('home.html', val='show_costs', dict_data=dict_costs)
		

		# visualising data
		# this needs to be more dynamic...
		elif request.form['btn_select_chart_type'] == 'bar':
			return render_template('home.html', show_charting='True')

			"""
			chart = {"renderTo": 'div_chart', "type": 'bar', "height": 350}
			dict_costs = return_costs_dict()
			if request.form['btn_select_xaxis'] == 'cost_type':
				# get a distinct list of the cost types in the dictionary and add them to the following:
				x_axis = {"categories": ['costtype1', 'costtype2', 'costtype3']}
			if request.form['btn_select_xaxis'] == 'job_cost_resource':
				x_axis = {"categories": ['job_cost_resource1', 'job_cost_resource2', 'job_cost_resource3']}
			if request.form['btn_select_yaxis'] == 'unit_costs':
				# get the data for costs in a list
				#series = [data_from_dict]
				series = [{"data": [107, 31, 63]}]
				y_axis = {"title": {"text": 'Unit Costs'}}
			if request.form['btn_select_yaxis'] == 'unit_costs':
				#series = [data_from_dict]
				series = [{"data": [7, 43, 22]}]
				y_axis = {"title": {"text": 'Unit Sales'}}
			return render_template('home.html', val='show_costs', dict_data=dict_costs, chart=chart,\
					series=series, xAxis=x_axis, yAxis=y_axis, show_charting='True')
			"""

		elif request.form['btn_select_chart_type'] == 'line':
			return render_template('home.html', show_charting='True')

			"""
			chart = {"renderTo": div_chart, "type": 'line', "height": 350}
			dict_costs = return_costs_dict()
			if request.form['btn_select_xaxis'] == 'cost_type':
				# get a distinct list of the cost types in the dictionary and add them to the following:
				x_axis = {"categories": ['costtype1', 'costtype2', 'costtype3']}
			if request.form['btn_select_xaxis'] == 'job_cost_resource':
				x_axis = {"categories": ['job_cost_resource1', 'job_cost_resource2', 'job_cost_resource3']}
			if request.form['btn_select_yaxis'] == 'unit_costs':
				# get the data for costs in a list
				#series = [data_from_dict]
				series = [{"data": [107, 31, 63]}]
				y_axis = {"title": {"text": 'Unit Costs'}}
			if request.form['btn_select_yaxis'] == 'unit_costs':
				#series = [data_from_dict]
				series = [{"data": [7, 43, 22]}]
				y_axis = {"title": {"text": 'Unit Sales'}}
			return render_template('home.html', val='show_costs', dict_data=dict_costs, chart=chart,\
					series=series, xAxis=x_axis, yAxis=y_axis, show_charting='True')
			"""

		else:
			return render_template('home.html', val='hide')
	else:
		return render_template('home.html')

if __name__ == "__main__":
	app.run(debug=True)
