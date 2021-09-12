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
import datetime
from datetime import date
import os
from csv import writer
import pandas as pd
import dateutil.parser as dparser

import random
app = Flask(__name__)
login_manager = LoginManager()
session_serializer = SecureCookieSessionInterface() \
                        .get_signing_serializer(app)
     
@app.route("/customer_details")
def reports():
    return render_template("/customer.html")

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
    df = pd.read_csv("custmast.csv")
    temp = df.to_dict('records')
    lst = []
    for i in temp:
        lst.append(i['contact no'])
    print(lst)
    return render_template('addOrder.html',sendlst=lst,leng = len(lst))

@app.route("/bill")
def bill():
    return render_template('bill.html')



@app.route('/secondOrder', methods=['POST'])
def secondORder():
    cname,doctor,name, quantity = int(flask.request.form['cname']),flask.request.form['Doctor'],flask.request.form['name'], flask.request.form['quantity']
    dfmed = pd.read_csv("medmast.csv")
    tempmed = dfmed.to_dict('records')
    dfreord = pd.read_csv("reorder.csv")
    tempreord = dfreord.to_dict('records')
    df = pd.read_csv("order.csv")
    temp1 = df.to_dict('records')
    df = pd.read_csv("sales_1.csv")
    temp = df.to_dict('records')
    if True:
      print("temp",tempmed)
      # -----------Checking Expired or adding in reorder table ----
      for i in tempmed:
          print("Here",i['med name'],name)
          if i['med name'] == name:
              med_date = dparser.parse(str(i['exp date']),fuzzy=True).date()

              today = dparser.parse(str(date.today()),fuzzy=True).date()
              #print(datetime.datetime.strptime(str(today), "%Y-%m-%d"),datetime.datetime.strptime(str(med_date), "%Y-%m-%d"))
              remaining = datetime.datetime.strptime(str(med_date), "%Y-%m-%d")-datetime.datetime.strptime(str(today), "%Y-%m-%d")
              #print(remaining.days)
              #print("dates",med_date,todays_date,str(date.today()))
              time = str(remaining).split(" ",1)[0]
              #print(remaining,int(time))
              if int(time) <= 0:
                  with open('reorder.csv', 'a') as f_object:
                      writer_object = writer(f_object)
                      print("in",list(i.values()))
                      writer_object.writerow(list(i.values()))
                      f_object.close()
                  
                  #print(dfmed,dfmed['med name'] != name)
                  delete = dfmed[dfmed['med name'] == name ].index
                  #print(delete)
                  dfmed = dfmed.drop(delete)
                  with open('medmast.csv', 'w') as f:
                      #print(dfmed.iloc[1:])
                      dfmed.to_csv(f, header=True)
                  #print(dfmed)
                  return render_template('sorry.html', data="Sorry medicine is going To expired in  some days We have Reorder it We will remind you" )
      # ---- Enter in order Table
      lst = [temp1[-1]['order id'] +1,temp1[-1]['order id'] +1,temp1[-1]['prod id'] +1,name,date.today(), quantity,20]  
      with open('order.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(lst)
        f_object.close()
      medname = []
      qty = 0
      for i in tempmed:
          medname.append(i['med name'])
      if name in medname:
          ind = int(medname.index(name))
          qty = tempmed[ind]['qty']
          company = tempmed[ind]['manufacturer']
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
                  custname.append(int(i['contact no']))
              print("checking ",cname,custname)
              if int(cname) not in custname:
                  return 'Sorry Wrong customer. Want to Add new Customer <a href="/addCust" class="btn btn-dark">click here</a>'
              newind = int(custname.index(cname))
              dfcust['loyalty'][newind] = tempcust[ind]['loyalty']+10
              dfcust.to_csv("custmast.csv",index=False)  
              print(dfcust)
              
          with open('sales_1.csv', 'a') as f_object:
              writer_object = writer(f_object)
              lst = [temp[-1]['sale code'] +1,name, quantity,20,date.today(),company]
              writer_object.writerow(lst)
              f_object.close()
          print(qty)
          if int(qty) < 10:
              return render_template('bill.html', sendlst=send,messages=True)
          return render_template('bill.html', sendlst=send)
      columnNames = df.columns.values
      salt = ''
      for i in tempreord:
          if name == i['med name']:
              salt= i['salt']
              print(salt)
      lst = []
      for i in tempmed:
          if i['salt'] == salt:
              lst.append(i['med name'])
      return render_template('sorry.html', data='Sorry medicine Not Avaiable We have Reordered', sendlst = lst )
 
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
  lst = [temp[-1]['cust id'] +1,name, address,gender,contact,0]
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
    
    df = pd.read_csv("medmast.csv")
    temp = df.to_dict('records')
    
    dford = pd.read_csv("order.csv")
    tempord = dford.to_dict('records')
    img = io.BytesIO()
    print( df.columns.values,temp)
    y = [1,2,3,4,5]
    x = [0,2,1,3,4]
    
    price=[]
    name=[]
    temp2=[]
    name2=[]
    for i in temp:
        for key,value in  i.items():
            if key == 'price':
                price.append(int(value))
            elif key=='med name':
                name.append(value)
    print(dford)
    for j in tempord:
        print(temp2,j['prescription'])
        
        if j['prescription'] not in temp2:
            temp2.append(j['prescription'])
            name2.append([j['prescription'],j['amount']])
        else:
            for i in range(len(name2)):
                if j['prescription'] == name2[i][0]:
                    name2[i][1] += j['amount']
    print("names",name2)
    ordername = []
    orderprice = []
    for i in range(len(name2)):
        ordername.append(name2[i][0])
        orderprice.append(name2[i][1])
        
    print("This",name,price)
    plt.bar(name,price)
    if os.path.exists('./static/images/new_plot.png'):
        os.remove('./static/images/new_plot.png')
    plt.savefig('./static/images/new_plot.png', format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    
    plt.bar(ordername,orderprice)
    if os.path.exists('./static/images/order.png'):
        os.remove('./static/images/order.png')
    plt.savefig('./static/images/order.png', format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template("graph.html",url="../static/images/new_plot.png",url2="../static/images/order.png")




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

@app.route("/GetPrescriptionData")
@login_required
def GetPrescriptionData():
    df = pd.read_csv("prescription.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    return render_template('record.html', records=temp, colnames=columnNames)

@app.route("/Special_customer")
@login_required
def GetSplcustomerData():
    df = pd.read_csv("splcustomer.csv")
    temp = df.to_dict('records')
    columnNames = df.columns.values
    for i in temp:
        med_date = dparser.parse(str(i['reminder date']),fuzzy=True).date()
        today = dparser.parse(str(date.today()),fuzzy=True).date()
        print(datetime.datetime.strptime(str(today), "%Y-%m-%d"),datetime.datetime.strptime(str(med_date), "%Y-%m-%d"))
        remaining = datetime.datetime.strptime(str(med_date), "%Y-%m-%d")-datetime.datetime.strptime(str(today), "%Y-%m-%d")
        print(remaining)   
        time = str(remaining).split(" ",1)[0]
        if int(time) <= 5:
            flash(f"Reminder less 5 days is are there : name {i['name']}  Contact {i['Custcontact']} Dispense Date {i['dispense date']}")
        
    return render_template('record.html', records=temp, colnames=columnNames)

@app.route("/reports")
@login_required
def GetReportsData():
    df = pd.read_csv("sales_1.csv")
    temp = df.to_dict('records')
    profit,qty = 0,0
    for i in temp:
        profit = profit + i['amount']
        qty = qty+i['qty']
    return render_template('reports.html',profit = profit,quantity=qty)



if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)