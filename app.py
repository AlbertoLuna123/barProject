from flask import Flask,redirect,url_for,render_template,request,session
import os
import database as db

app=Flask(__name__)
app.secret_key = '1234'

#iniciacion de aplicacion
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('index.html')
    return render_template('index.html')

#Inicio de sesion
@app.route('/signin',methods = ["POST","GET"])
def singin():
    if request.method == "POST" and 'email' in request.form and 'pass1':
        _email = request.form['email']
        _pass1 = request.form['pass1']
        
        cursor = db.database.cursor()
        sql = "SELECT * FROM user WHERE email_user = %s AND password_user = %s"
        data = (_email,_pass1)
        cursor.execute(sql,data)
        account = cursor.fetchone()
        if account:
            session['logueado'] = True
            id = account[0]
            session['id'] = id
            session['type'] = account[15]
            return redirect(url_for("starting"))
        else:
            return render_template('index.html')
    else:
        print("Request method GET")
        return render_template('index.html')
    
#Cierre de sesion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
    
#califica el tipo de usuario y dezpliega el homepage
@app.route('/starting')
def starting():
    user_type = session['type']
    if user_type == 1:
        return redirect(url_for("administrador"))
    else:
        if user_type == 2:
            return redirect(url_for("compras"))
        else:
            if user_type == 4:
                return redirect(url_for("developer"))
            else: 
                return redirect(url_for("home"))
            
#lanzar el dashboard para administrador
@app.route("/administrador")
def administrador():
    return render_template('administrador.html')

#lanzar el dashboard para compras
@app.route("/compras")
def compras():
    return render_template('compras.html')
        
#lanzar el dashboard para developer  
@app.route("/developer")
def developer():
    return render_template('developer.html') 

@app.route("/personal")
def personal():
    cursor = db.database.cursor()
    sql = f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType"
    cursor.execute(sql)
    user = cursor.fetchall()
    return render_template("personal.html",user = user)

@app.route("/usuario/<int:id>")
def usuario(id):
    id=id
    cursor = db.database.cursor()
    sql = f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType WHERE a.id_user = {id}"
    cursor.execute(sql)
    user = cursor.fetchone()
    return render_template("user.html",user=user)

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)