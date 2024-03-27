from flask import Flask,redirect,url_for,render_template,request,session
import os
import database as db
from flask import flash


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
        msg_error = "Las credenciales ingresadas no son válidas. Por favor, revisa tu nombre de usuario y contraseña e intenta nuevamente."
        return render_template('index.html',msg = msg_error)
    
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

@app.route('/gestionInventario')
def gestionInventario():
    return render_template('gestionInventario.html')


#lanza el panel del personal para ver la tabla de ususarios y crear nuevos
@app.route("/personal")
def personal():
    cursor = db.database.cursor()
    sql = f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType"
    cursor.execute(sql)
    user = cursor.fetchall()
    user_sorted = sorted(user, key=lambda x: x[0], reverse=True)
    return render_template("personal.html",user = user_sorted)

#muestra toda la informacion del usuario seleccionado en un formulario para realizar su edicion
@app.route("/usuario/<int:id>")
def usuario(id):
    id=id
    cursor = db.database.cursor()
    sql = f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType WHERE a.id_user = {id}"
    cursor.execute(sql)
    user = cursor.fetchone()
    return render_template("user.html",user=user)

#realiza la funcion update y retorna la ruta de personal
@app.route('/edit_user/<int:id>',methods = ["POST","GET"])
def method_name(id):
    id = id
    _nombre = request.form['nombre']
    _apellidos = request.form['apellidos']
    _email = request.form['email']
    _status = request.form['status']
    _telefono = request.form['telefono']
    _refper1nom = request.form['refper1nom']
    _refper1tel = request.form['refper1tel']
    _refper2nom = request.form['refper2nom']
    _refper2tel = request.form['refper2tel']
    _domicilio = request.form['domicilio']
    _rfc = request.form['rfc']
    _curp = request.form['curp']
    _nss = request.form['nss']
    _tipo = request.form['tipo']
    
    cursor = db.database.cursor()
    sql = f"""
        UPDATE `user` 
        SET 
        `name_user`='{_nombre}',
        `last_name_user`='{_apellidos}',
        `email_user`='{_email}',
        `phone_user`='{_telefono}',
        `personal_ref_1_user`='{_refper1nom}',
        `phone_personal_ref_1_user`='{_refper1tel}',
        `personal_ref_2_user`='{_refper2nom}',
        `phone_personal_ref_2_user`='{_refper2tel}',
        `address_user`='{_domicilio}',
        `status_user`='{_status}',
        `rfc_user`='{_rfc}',
        `curp_user`='{_curp}',
        `nss_user`='{_nss}',
        `id_userType`='{_tipo}' 
        WHERE id_user = {id}
    """
    try:
        cursor.execute(sql)
        db.database.commit()
        return redirect(url_for("personal"))
    except db.database.MySQLError as error:
        return redirect(url_for("Personal"))
        
#registra usuarios nuevos en la base de datos, obtiene los datos del formulario de "PERSONAL"
@app.route("/register",methods = ["POST","GET"])
def register():
    _nombre = request.form['nombre']
    _apellidos = request.form['apellidos']
    _email = request.form['email']
    _contrasena = request.form['contrasena']
    _telefono = request.form['telefono']
    _refper1nom = request.form['refper1nom']
    _refper1tel = request.form['refper1tel']
    _refper2nom = request.form['refper2nom']
    _refper2tel = request.form['refper2tel']
    _domicilio = request.form['domicilio']
    _rfc = request.form['rfc']
    _curp = request.form['curp']
    _nss = request.form['nss']
    _tipo = request.form['tipo']
    
    cursor = db.database.cursor()
    sql = f"""
        INSERT INTO `user`(
    `name_user`, 
    `last_name_user`, 
    `email_user`, 
    `password_user`, 
    `phone_user`, 
    `personal_ref_1_user`, 
    `phone_personal_ref_1_user`, 
    `personal_ref_2_user`, 
    `phone_personal_ref_2_user`, 
    `address_user`,
    `status_user`,  
    `rfc_user`, 
    `curp_user`, 
    `nss_user`, 
    `id_userType`) 
    VALUES (
        '{_nombre}',
        '{_apellidos}',
        '{_email}',
        '{_contrasena}',
        '{_telefono}',
        '{_refper1nom}',
        '{_refper1tel}',
        '{_refper2nom}',
        '{_refper2tel}',
        '{_domicilio}',
        'Activo',
        '{_rfc}',
        '{_curp}',
        '{_nss}',
        '{_tipo}')
    """
    try:
        cursor.execute(sql)
        db.database.commit()
        return redirect(url_for("personal"))
    
    except db.database.errors.Error as error:
        return redirect(url_for("personal"))
    
@app.route("/delete/<int:id>")
def delete(id):
    id = id
    delete = db.delete(id) 
    print(delete)
    if delete == "Registro eliminado":
        flash("Registro eliminado con exito", "success")
    else:
        flash(f"Error> {delete}", "danger")
        
    return redirect(url_for("personal"))

if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)
    
