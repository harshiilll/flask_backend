from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


import os


from datetime import datetime, date
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///final2.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
global login_ornot
login_ornot=False


port=os.getenv("PORT", default=5000)


current_date=date.today()
hour_and_minute = datetime.now().strftime("%H:%M")

class final2(db.Model):
     Sno= db.Column(db.Integer, primary_key=True)
     VehicleNumber=db.Column(db.String(20))
     DateofTable=db.Column(db.Date, nullable=True)
     Entry=db.Column(db.String(10), nullable=True)
     Exit=db.Column(db.String(10), nullable=True)
     Authorised=db.Column(db.String(5), default="Yes")

     def __repr__(self) -> str:
         return f"{self.Sno} - {self.VehicleNumber} - {self.Entry} - {self.Exit} - {self.Authorised}"

class master1(db.Model):
     userid= db.Column(db.Integer, primary_key=True)
     UserName=db.Column(db.String(30), unique=False)
     IdNumber=db.Column(db.Integer)
     VehicleNumber=db.Column(db.String(25), unique=True)
     PhoneNumber=db.Column(db.Integer)
     Email=db.Column(db.String(30))
     

     def __repr__(self) -> str:
         return f"{self.userid} - {self.UserName} - {self.IdNumber} - {self.VehicleNumber} - {self.PhoneNumber} - {self.Email}"


@app.route('/home')
def showit():
    if login_ornot is False:
        return render_template('login.html')
    dis_vehicle= db.session.query(final2.VehicleNumber).distinct().count()
    dis_dates= db.session.query(final2.DateofTable).distinct().count()  
    ratioAuth= final2.query.filter_by(Authorised="No").distinct().count()/final2.query.filter_by(Authorised="Yes").distinct().count()
    peak_hour= final2.query.filter(db.and_(final2.Entry <="11:00", final2.Entry >"08:30")).distinct().count()
    peak_hour+= final2.query.filter(db.and_(final2.Entry <="18:30", final2.Entry >="16:30")).distinct().count()
    return render_template('admin.html',ratio=round(ratioAuth,2), count=round(dis_vehicle,2), avgv_p_d=round(dis_vehicle/dis_dates,2),peak_hr=round(peak_hour/dis_dates,2))

@app.route('/search')
def search():
    if login_ornot is False:
        return render_template('login.html')
    return render_template('search.html')


@app.route('/view')
def view_default():
    if login_ornot is False:
        return render_template('login.html')
    return render_template('view.html')


@app.route('/insert')
def showinsert():
    if login_ornot is False:
        return render_template('login.html')
    return render_template('insert.html')

@app.route('/home', methods=['GET', 'POST'])
def showdetails():
    if login_ornot is False:
        return render_template('login.html')
    if request.method == 'POST':
        idsearch= request.form.get('show_results')
        search = final2.query.all()
    dis_vehicle= db.session.query(final2.VehicleNumber).distinct().count()
    dis_dates= db.session.query(final2.DateofTable).distinct().count()  
    ratioAuth= final2.query.filter_by(Authorised="No").distinct().count()/final2.query.filter_by(Authorised="Yes").distinct().count()
    peak_hour= final2.query.filter(db.and_(final2.Entry <="11:00", final2.Entry >"08:30")).distinct().count()
    peak_hour+= final2.query.filter(db.and_(final2.Entry <="18:30", final2.Entry >="16:30")).distinct().count()
    return render_template('admin.html', showSearch=search, ratio=round(ratioAuth,2), count=round(dis_vehicle,2), avgv_p_d=round(dis_vehicle/dis_dates,2),peak_hr=round(peak_hour/dis_dates,2))


@app.route('/insert', methods=['GET', 'POST'])    
def MasterEntry():
    if login_ornot is False:
        return render_template('login.html')
    if request.method=='POST':
        Name= request.form['UserName']
        Id= request.form['IdNum']
        Number= request.form['vehicle']
        phone= request.form['phone']
        email= request.form['Email']
        new_record=master1(UserName=Name, IdNumber=Id, VehicleNumber=Number,PhoneNumber=phone, Email=email)       #entry detail to db
        db.session.add(new_record)
        db.session.commit()
    allRecords= master1.query.all()
    return render_template('insert.html', masterrec=allRecords)


@app.route('/home/', methods=['GET'])
def automated_Entry():
    data1 = request.args.get("data", None)
    # data = request.get_json()
    # Number= request.form['vehicle']
    datenow=current_date
    entry= hour_and_minute
    data1=data1.upper()
    SnoOfexit = exit_or_not(data1)
    auth= findIt(data1)                                                                               #authorised or not
    if SnoOfexit is not None:
        changeit= final2.query.filter_by(Sno= SnoOfexit).first()
        changeit.Exit=hour_and_minute
        db.session.commit()
    else:  
        new_record=final2(VehicleNumber=data1, DateofTable=datenow, Entry=entry, Authorised= auth)       #entry detail to db
        db.session.add(new_record)
        db.session.commit()
        
    temprecords= final2.query.all()
    return render_template('admin.html', allRecords=temprecords)

def exit_or_not(num):
    first_row= final2.query.filter_by(VehicleNumber=num, Exit=None).first()
    if first_row is None:
        return None
    elif first_row.Exit is None and first_row.Entry is not None:
        return first_row.Sno
    return None

def findIt(num):
    exist = master1.query.filter_by(VehicleNumber=num).all()
    if  len(exist):
        return "Yes"   
    return "No"

@app.route('/view', methods=['GET', 'POST'])
def view_all():
    if login_ornot is False:
        return render_template('login.html')
    if request.method == 'POST':
        idsearch= request.form['vehicle']
        idsearch=idsearch.upper()
        search = master1.query.filter_by(VehicleNumber=idsearch).all()
    return render_template('view.html',showSearch=search)

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'Jashandeep01' or request.form['password'] != 'openocula':
            error = 'Invalid Credentials. Please try again.'
        else:
            global login_ornot
            login_ornot= True
            return render_template('admin.html')
    return render_template('login.html', error=error)



@app.route('/home', methods=['GET', 'POST'])
def deleteit():
    if request.method=='POST':
        whom= request.form['deleted']
    whom=master1.query.filter_by(VehicleNumber=whom).first()
    db.session.delete(whom)
    db.session.commit()
    return redirect(url_for('/home'))

@app.route('/search', methods=['GET', 'POST'])
def search_sep():
    if login_ornot is False:
        return render_template('login.html')
    if request.method == 'POST':
        idsearch= request.form['getdetail']
        idsearch=idsearch.upper()
        search = final2.query.filter_by(VehicleNumber=idsearch).all()
    tot_days= db.session.query(final2.DateofTable).filter_by(VehicleNumber=idsearch).distinct().count() 
    # parking_time= park(idsearch)
    return render_template('search.html',showSearch=search, totaldays=tot_days)

# def park(id):
#     entry=db.session.query(final2.Entry).filter_by(VehicleNumber=id).all()
#     exit=db.session.query(final2.Exit).filter_by(VehicleNumber=id).all()
#     enter=0
#     exit=0
#     for i in entry:
#         str=i[0]
#         str=str[:2]
#         enter+= int(str)
#     for i in exit:
#         if i[0] is not None:
#             str=i[0]
#             str=str[:2]
#             exiter+= int(str)
#     return abs(enter-exit)
if __name__ == "__main__":
    app.run(debug=True,port=os.getenv("PORT", default=5000))

