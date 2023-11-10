from flask import*
from flask import Flask, request, jsonify, render_template, redirect, flash, send_file
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import pickle
from flask import Flask, render_template, request, send_from_directory
import utils
import train_models as tm
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template, redirect, flash, send_file
from sklearn.preprocessing import MinMaxScaler
from werkzeug.utils import secure_filename
import pickle
from flask import Flask, render_template, request, send_from_directory
import utils
import train_models as tm
import os
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re




app=Flask(__name__)
app.secret_key='your secret key'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='root'
app.config['MYSQL_DB']='stock'
mysql=MySQL(app)


pol = pickle.load(open('poly.pkl','rb'))
regresso = pickle.load(open('regressor.pkl','rb'))
scaler = MinMaxScaler()

def perform_training(stock_name, df, models_list):
    all_colors = {'SVR_linear': '#FF9EDD',
                  'SVR_poly': '#FFFD7F',
                  'SVR_rbf': '#FFA646',
                  'linear_regression': '#CC2A1E',
                  'random_forests': '#8F0099',
                  'KNN': '#CCAB43',
                  'elastic_net': '#CFAC43',
                  'DT': '#85CC43',
                  'LSTM_model': '#CC7674'}

    print(df.head())
    dates, prices, ml_models_outputs, prediction_date, test_price = tm.train_predict_plot(stock_name, df, models_list)
    origdates = dates
    if len(dates) > 20:
        dates = dates[-20:]
        prices = prices[-20:]

    all_data = []
    all_data.append((prices, 'false', 'Data', '#000000'))
    for model_output in ml_models_outputs:
        if len(origdates) > 20:
            all_data.append(
                (((ml_models_outputs[model_output])[0])[-20:], "true", model_output, all_colors[model_output]))
        else:
            all_data.append(
                (((ml_models_outputs[model_output])[0]), "true", model_output, all_colors[model_output]))

    all_prediction_data = []
    all_test_evaluations = []
    all_prediction_data.append(("Original", test_price))
    for model_output in ml_models_outputs:
        all_prediction_data.append((model_output, (ml_models_outputs[model_output])[1]))
        all_test_evaluations.append((model_output, (ml_models_outputs[model_output])[2]))

    return all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data, all_test_evaluations

all_files = utils.read_all_stock_files('individual_stocks_5yr')
            


            




@app.route('/')
def nav():
    return render_template('home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    #output message if something goes wrong...
    msg=''
    #check if "username", "password", "email" POST request exist(user submitted from)
    if request.method=='POST':
        #create variable for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phno = request.form['phno']


        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #check if account exists using mysql
        cursor.execute('SELECT * FROM  register WHERE username = %s',(username,))
        account = cursor.fetchone()
        #if account exists show error and validation checks
        if account:
            msg = 'Account already exists..!' 
        elif  not re.match (r'[^@]+@[^@]+\.[^@]+',email):
            msg='Invalid email address..!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg = 'Username must contain only characters and numbers...!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one upper case character, one special symbol and must be between 6 to 10 characters long...!'
        elif not username or not password or not email:
            msg = 'Please fill out the form..!'
        else:
            #account doesn't exist and the form data is valid, now insert new account into register table
            cursor.execute('INSERT INTO register VALUES (NULL,%s,%s,%s,%s)',(username,password,email,phno))
            mysql.connection.commit()
            flash('You have successfully registered...! Please proceed for login...!')
            return redirect(url_for('login'))
    elif request.method =='POST':
        #form is empty....(no post fill)
        msg = 'Please fill out the form..!'
        return msg
    #show registration form with message (if any)
    return render_template('register.html',msg=msg)






@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/loginaction',methods=['POST'])
def loginaction():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * from register WHERE username=%s AND password=%s',(username,password,))
        account=cursor.fetchone()
        if account:
            return render_template('upload.html')
        else:
            return 'Invalid Login'
        # if username=='admin' and password=='admin':
        #     # return 'login Success'
        #     return render_template('upload.html')
        # else:
        #     return 'login failed'

@app.route('/abstract')
def abstract():
 	return render_template("abstract.html")

@app.route('/preview',methods=["POST"])
def preview():
    if request.method=='POST':
        dataset=request.files['datasetfile']
        df=pd.read_csv(dataset,encoding='unicode_escape')
        df.set_index('Id',inplace=True)
        return render_template("preview.html",df_view=df)
 
@app.route('/landing_function')
def landing_function():
    all_files= utils.read_all_stock_files('individual_stocks_5')
    df=all_files['A']
    df=pd.read_csv('GOOG_30_days.csv')
    all_prediction_data,all_prediction_data, prediction_date,dates,all_data,all_data=perform_training('A',df,['SVR_linear'])
    stock_files=list(all_files.keys())
    return render_template('home.html',show_results="false",stocklen=len(stock_files),stock_files=stock_files,len2=len([]),all_prediction_data=[],prediction_date="",dates=[],all_data=[],len=len([]))


@app.route('/prediction')
def prediction():
 	return render_template("prediction.html")
    
@app.route('/predict',methods=['POST'])
def predict():
	int_feature = [x for x in request.form.values()]
	 
	final_features = [np.array(int_feature)]
	Total_infections  = pol.transform(final_features)
	prediction=regresso.predict(Total_infections )
	pred=format(int(prediction[0]))
	
	return render_template('prediction.html', prediction_text= pred) 

@app.route('/process', methods=['POST'])
def process():

    stock_file_name = request.form['stockfile']
    ml_algoritms = request.form.getlist('mlalgos')

    # all_files = utils.read_all_stock_files('individual_stocks_5yr')
    df = all_files[str(stock_file_name)]
    # df = pd.read_csv('GOOG_30_days.csv')
    all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data, all_test_evaluations = perform_training(str(stock_file_name), df, ml_algoritms)
    stock_files = list(all_files.keys())

    return render_template('index.html',all_test_evaluations=all_test_evaluations, show_results="true", stocklen=len(stock_files), stock_files=stock_files,
                           len2=len(all_prediction_data),
                           all_prediction_data=all_prediction_data,
                           prediction_date=prediction_date, dates=dates, all_data=all_data, len=len(all_data))


@app.route('/chart')
def chart():
 	return render_template("chart.html")

@app.route('/future')
def future():
 	return render_template("future.html")

if __name__=='__main__':
    app.run(debug=True)

    