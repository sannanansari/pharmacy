from flask import Response,Flask,render_template,redirect,session,flash
import flask_login
from flask_login import LoginManager,logout_user
import functools
from flask import request
from flask.sessions import SecureCookieSessionInterface
import make_response
import matplotlib.pyplot as plt
import flask
import io
import base64
from datetime import timedelta
from datetime import date
import os
from csv import writer
import pandas as pd
import random
app = Flask(__name__)
login_manager = LoginManager()
session_serializer = SecureCookieSessionInterface() \
                        .get_signing_serializer(app)
def login_required(func):
    @functools.wraps(func)
    def secure():
        if "session" not in request.cookies:
            return render_template("/404.html")
        return func()
    return secure
@app.route('/c')
def hello_world():
    return render_template("index.html")

@app.route('/')
def home():
  return render_template("login.html")

@app.route('/second', methods=['POST'])
def second():
  username, password = flask.request.form['username'], flask.request.form['password']
  if username=='admin' and password=='password':
      flask.session['username'] = 'admin'
      flask.session['password'] = 'password'
      flask.session['completed'] = True
      return flask.redirect('/GetCustData')
  else:
      return render_template("404.html")
  
@app.route("/addOrder")
@login_required
def AddOrderData():
    return render_template('addOrder.html')

@app.route("/bill")
def bill():
    return render_template('bill.html')


@app.route('/secondOrder', methods=['POST'])
def secondORder():
  cname,doctor,name, quantity = flask.request.form['cname'],flask.request.form['Doctor'],flask.request.form['name'], flask.request.form['quantity']
  df = pd.read_csv("sales_1.csv")
  temp = df.to_dict('records')
  columnNames = df.columns.values
  lst = [temp[-1]['sale code'] +1,name, quantity,20,date.today(),'company']
  with open('sales_1.csv', 'a') as f_object:
    writer_object = writer(f_object)
    writer_object.writerow(lst)
    f_object.close()
  df = pd.read_csv("order.csv")
  temp1 = df.to_dict('records')
  lst = [temp1[-1]['order id'] +1,temp1[-1]['order id'] +1,temp1[-1]['prod id'] +1,name,date.today(), quantity,20]  
  with open('order.csv', 'a') as f_object:
    writer_object = writer(f_object)
    writer_object.writerow(lst)
    f_object.close()
  dfmed = pd.read_csv("medmast.csv")
  tempmed = dfmed.to_dict('records')
  medname = []
  for i in tempmed:
      medname.append(i['med name'])
  if name in medname:
      ind = int(medname.index(name))
      lst = [tempmed[ind]['med name'] ,tempmed[ind]['qty'] ,tempmed[ind]['price']]  
      print("prev " ,dfmed['qty'][ind])
      dfmed['qty'][ind] = tempmed[ind]['qty']-int(quantity)
      print(dfmed['qty'][ind])
      dfmed.to_csv("medmast.csv",index=False)  
      send = [name,doctor,tempmed[ind]['price']*int(quantity),quantity]
      # Yahi pe customer table upldate ho raha hai
      if tempmed[ind]['price'] > 300:
          dfcust = pd.read_csv("custmast.csv")
          tempcust = dfcust.to_dict('records')
          custname = []
          for i in tempcust:
              custname.append(i['cust name'])
          newind = int(custname.index(cname))
          dfcust['loyalty'][newind] = tempcust[ind]['loyalty']+10
          dfcust.to_csv("custmast.csv",index=False)  
          print(dfcust)
      return render_template('bill.html', sendlst=send)
  return 'No medicine'
  
@app.route("/addCust")
@login_required
def AddCustData():
    return render_template('addcust.html')

@app.route('/secondCust', methods=['POST'])
def secondCust():
  name, address,gender,contact = flask.request.form['name'], flask.request.form['address'], flask.request.form['gender'], flask.request.form['contact']
  df = pd.read_csv("custmast.csv")
  temp = df.to_dict('records')
  columnNames = df.columns.values
  lst = [temp[-1]['cust id'] +1,name, address,gender,contact]
  with open('custmast.csv', 'a') as f_object:
    writer_object = writer(f_object)
    writer_object.writerow(lst)
    f_object.close()
  df1 = pd.read_csv("custmast.csv")
  temp1 = df1.to_dict('records')
  columnNames1 = df1.columns.values
  return render_template('record.html', records=temp1, colnames=columnNames1)

@app.route('/plot')
def build_plot():

    img = io.BytesIO()
    df = pd.read_csv("graph.csv")
    temp = df.to_dict('records')
    print( df.columns.values,temp)
    y = [1,2,3,4,5]
    x = [0,2,1,3,4]
    
    price=[]
    name=[]
    for i in temp:
        for key,value in  i.items():
            if key == 'price':
                price.append(int(value))
            elif key=='med name':
                name.append(value)
    print("This",name,price)
    plt.bar(name,price)
    if os.path.exists('./static/images/new_plot.png'):
        os.remove('./static/images/new_plot.png')
    plt.savefig('./static/images/new_plot.png', format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template("graph.html",url="../static/images/new_plot.png")




@app.route("/GetCustData")
@login_required
def GetCustData():
    df = pd.read_csv("custmast.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    return render_template('record.html', records=temp, colnames=columnNames)

@app.route('/logout')
@login_required
def logout():
    print(request.cookies)
    if request.cookies['session']:
        # prevent flashing automatically logged out message
        resp = app.make_response(render_template('login.html'))
        resp.set_cookie("session", expires=0,path="temp.com")
    flash('You have successfully logged yourself out.')
    return redirect('/')


@app.route("/GetMedData")
@login_required
def GetMedData():
    df = pd.read_csv("medmast.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    return render_template('record.html', records=temp, colnames=columnNames)

@app.route("/GetOrderData")
@login_required
def GetOrderData():
    df = pd.read_csv("order.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    return render_template('record.html', records=temp, colnames=columnNames)


@app.route("/GetSalesData")
@login_required
def GetSalesData():
    df = pd.read_csv("sales_1.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    return render_template('record.html', records=temp, colnames=columnNames)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)