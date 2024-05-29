from flask import Flask,redirect,url_for,render_template,request,session
import os
import database as db
from flask import flash
from datetime import date
from datetime import datetime


app=Flask(__name__)
app.secret_key = '1234'

#iniciacion de aplicacion
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('index.html')
    return render_template('index.html')

#-----------------------------------------------------------------------------------------------------------------------
# LOGIN Y LOGOUT
#-----------------------------------------------------------------------------------------------------------------------

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
            return redirect(url_for("gestionCompras"))
        else:
            if user_type == 4:
                return redirect(url_for("developer"))
            else: 
                return redirect(url_for("home"))


#-----------------------------------------------------------------------------------------------------------------------
# DASHBOARDS PRINCIPALES
#-----------------------------------------------------------------------------------------------------------------------
#lanzar el dashboard para administrador
@app.route("/administrador")
def administrador():
    return render_template('administrador.html')

#lanzar el dashboard para compras
@app.route("/gestionCompras")
def gestionCompras():
    return render_template('compras.html')
        
#lanzar el dashboard para developer  
@app.route("/developer")
def developer():
    return render_template('developer.html') 

#-----------------------------------------------------------------------------------------------------------------------
# RUTAS DE COMPRAS
#-----------------------------------------------------------------------------------------------------------------------

#GENERAR ENTRADA
@app.route('/entrada/<int:id>')
def entrada(id):
    query = f"SELECT *, a.cantidad_desc_compra * a.valor_unit_desc_compra Total FROM desc_compra a INNER JOIN item b ON a.id_ttem = b.id_item INNER JOIN unidad_item c ON b.id_unidad_item = c.id_unidad_item WHERE a.id_compra = {id} AND a.entregado_desc_compra = 0"
    query1 = f"SELECT *, a.cantidad_desc_compra * a.valor_unit_desc_compra Total FROM desc_compra a INNER JOIN item b ON a.id_ttem = b.id_item INNER JOIN unidad_item c ON b.id_unidad_item = c.id_unidad_item WHERE a.id_compra = {id} AND a.entregado_desc_compra = 1"
    data0 = db.select(query)
    data1 = db.select(query1)
    return render_template("generarEntrada.html",noEntregados = data0, entregados = data1)

# ORDENES DE COMPRA ABIERTAS
@app.route('/ordenesAbiertas')
def ordenesAbiertas():
    sql = "SELECT a.id_compra Numero, a.fecha_compra Fecha, a.subtotal_compra Subtotal, a.iva_compra IVA, a.total_compra Total, b.name_user Usuario, c.name_proveedor Proveedor, a.status_compra FROM compra a INNER JOIN user b INNER JOIN proveedor c ON a.id_usuario = b.id_user and a.id_proveedor = c.id_proveedor WHERE a.status_compra = 1"
    execute = db.select(sql)
    return render_template('ordenesAbiertas.html', data = execute)

@app.route('/crearOrden')
def crearOrden():
    sql = "SELECT * FROM proveedor"
    data = db.select(sql)
    return render_template('crearOrden.html',data=data)

@app.route('/ordenNueva',methods = ["POST","GET"])
def ordenNueva():
    __idProveedor = request.form['id']
    fecha = datetime.today().strftime('%Y-%m-%d')  # Formatea la fecha como 'YYYY-MM-DD'
    SQLCreaCompra = f"INSERT INTO `compra`(`id_usuario`, `fecha_compra`, `id_proveedor`,`status_compra`) VALUES ({session['id']}, '{fecha}', {__idProveedor}, 0)"
    db.executeSQL(SQLCreaCompra)
    return redirect(url_for("itemOrder",id_proveedor = __idProveedor))

@app.route('/itemOrden')
def itemOrder():
    __idProveedor = request.args.get('id_proveedor')
    SQLItems = f"SELECT * FROM item WHERE id_proveedor = {__idProveedor} AND id_item NOT IN (SELECT id_ttem FROM desc_compra WHERE id_compra = (SELECT MAX(id_compra) FROM compra))"
    sqlCompra = "SELECT MAX(id_compra) FROM compra"
    data = db.select(SQLItems)
    id_compra = db.select(sqlCompra)
    return(render_template('seleccionaItem.html',data = data,id_compra=id_compra)) 

@app.route('/anadirItems',methods = ['GET','POST'])
def anadirItems():
    __id_compra = request.form['id_compra']
    __ids = request.form.getlist('id')
    __cantidades = request.form.getlist('cantidad[]')
    __preciosUnit = request.form.getlist('precioUnitario[]')
    print(__id_compra)
    print(__ids)
    print(__cantidades)
    print(__preciosUnit)
    for i in range(len(__ids)):
        query = f"INSERT INTO `desc_compra`(`id_compra`, `id_ttem`, `cantidad_desc_compra`, `valor_unit_desc_compra`) VALUES ('{__id_compra}','{__ids[i]}','{__cantidades[i]}','{__preciosUnit[i]}')"
        db.executeSQL(query)
        query = f"UPDATE `compra` SET `status_compra`= 1 WHERE id_compra = {__id_compra}"
        db.executeSQL(query)
    
    subtotalList = [float(item) for item in __preciosUnit]
    cantList = [float(item) for item in __cantidades]
    subtotalIndiv = [a * b for a, b in zip(subtotalList, cantList)]
    subtotal = sum(subtotalIndiv)
    iva = subtotal * 0.16
    total = subtotal + iva
    update = f"UPDATE `compra` SET `subtotal_compra`='{subtotal}',`iva_compra`='{iva}',`total_compra`='{total}' WHERE id_compra = {__id_compra}"
    db.executeSQL(update)
    
    return redirect(url_for("ordenesAbiertas"))

#VIZUALIZAR ORDEN DE COMPRA COMPLETA
@app.route('/detalleCompra/<int:id>')
def compra(id):
    sqlCompra = f"SELECT * FROM compra a INNER JOIN user b INNER JOIN proveedor c ON a.id_usuario = b.id_user and a.id_proveedor = c.id_proveedor WHERE a.id_compra = {id}"
    sqlCompraDetalle = f"SELECT *, a.cantidad_desc_compra * a.valor_unit_desc_compra Total FROM desc_compra a INNER JOIN item b ON a.id_ttem = b.id_item INNER JOIN unidad_item c ON b.id_unidad_item = c.id_unidad_item WHERE a.id_compra = {id}"
    sqlBar =    f"select a.*, b.name_user, b.last_name_user, b.phone_user, b.email_user  from bar_information a INNER JOIN user b on a.id_user = b.id_user;"
    
    dataBar = db.select(sqlBar)
    dataCompra = db.select(sqlCompra)
    dataDetalleCompra = db.select(sqlCompraDetalle)
    return render_template('detalleCompra.html', dataCompra = dataCompra, dataDetalleCompra = dataDetalleCompra, dataBar = dataBar)

@app.route('/entrada/inventarioUpdate/<int:id>/<int:cant>/<int:idC>')
def inventarioUpdate(id,cant,idC):
    sql = f"UPDATE item SET existencia_item = existencia_item + {cant} WHERE id_item = {id}"
    db.executeSQL(sql)
    entregado = True
    query = f"UPDATE desc_compra SET entregado_desc_compra = {entregado} WHERE id_compra = {idC} AND id_ttem = {id}"
    db.executeSQL(query)
    return redirect(url_for('gestionInventario'))
#-----------------------------------------------------------------------------------------------------------------------
# MODULOS ESPECIFICOS
#-----------------------------------------------------------------------------------------------------------------------

#lanza el panel de gestion de inventario
@app.route('/gestionInventario')
def gestionInventario():
    cursor = db.database.cursor()
    sql_item = f"SELECT * FROM item a INNER JOIN unidad_item b ON a.id_unidad_item = b.id_unidad_item INNER JOIN categoria_item c ON a.id_categoria_item = c.id_categoria_item INNER JOIN proveedor d ON a.id_proveedor = d.id_proveedor"
    cursor.execute(sql_item)
    user_sorted = sorted(cursor.fetchall(), key=lambda x: x[0], reverse=True)
    
    sql_category = f"SELECT * FROM categoria_item ORDER BY nombre_categoria_item ASC"
    cursor.execute(sql_category)
    category = cursor.fetchall()
    
    sql_unidad = f"SELECT * FROM unidad_item ORDER BY nombre_unidades_item ASC"
    cursor.execute(sql_unidad)
    unidad = cursor.fetchall()
    
    sql_proveedor = f"SELECT id_proveedor, name_proveedor FROM proveedor ORDER BY name_proveedor ASC"
    cursor.execute(sql_proveedor)
    proveedor = cursor.fetchall()
    
    return render_template("gestionInventario.html",user = user_sorted, categoria = category, unidad = unidad, proveedor = proveedor)

#ruta para crear un nuevo item
@app.route('/newItem', methods = ["POST","GET"])
def newItem():
    __nombre = request.form['nombreitem']
    __existencia = request.form['existencia']
    __unidad = request.form['unidad']
    __categoria = request.form['categoria']
    __precio = request.form['precio']
    __min = request.form['min']
    __preoveedor = request.form['proveedor']
    __nota = request.form['nota']
    __desc = request.form['desc']
    today = datetime.today()
    
    sql = f"INSERT INTO `item`(`nombre_item`, `desc_item`, `existencia_item`, `id_unidad_item`, `precio_unitario_item`, `ultimo_update_item`, `id_proveedor`, `id_categoria_item`, `nivel_minimo_item`, `notas_item`) VALUES ('{__nombre}','{__desc}','{__existencia}','{__unidad}','{__precio}','{today}','{__preoveedor}','{__categoria}','{__min}','{__nota}')"
    execute = db.executeSQL(sql)
    if execute == "Completo":
        flash("Item registrado de manera correcta", "success")
    else:
        flash(f"Error: {execute}", "danger")
        
    return redirect(url_for("gestionInventario"))

#Nueva Categoria
@app.route('/newCategory',methods =['POST','GET'])
def newCategory():
    __categoria = request.form['categoria']
    
    query = f"INSERT INTO categoria_item (`nombre_categoria_item`) VALUES ('{__categoria}')"
    db.executeSQL(query)
    return redirect(url_for('gestionInventario'))

#Nuevo proveedor
@app.route('/nuevoProveedor',methods =['POST','GET'])
def nuevoProveedor():
    __nombreProveedor = request.form['nomProveedor']
    __nomContacto1 = request.form['nomContacto1']
    __telContacto1 = request.form['telContacto1']
    __emContacto1 = request.form['emContacto1']
    __nomContacto2 = request.form['nomContacto2']
    __telContacto2 = request.form['telContacto2']
    __emContacto2 = request.form['emContacto2']
    __telVentas = request.form['telVentas']
    __emVentas = request.form['emVentas']
    __dir = request.form['dir']
    
    sql = f"""INSERT INTO `proveedor`(`name_proveedor`, `name_contacto1_proveedor`, `tel_contacto1_proveedor`, `email_contacto1_proveedor`, `name_contacto2_proveedor`, `tel_contacto2_proveedor`, `email_contacto2_proveedor`, `tel_ventas_proveedor`, `email_ventas_proveedor`, `direccion_proveedor`) 
    VALUES ('{__nombreProveedor}','{__nomContacto1}','{__telContacto1}','{__emContacto1}','{__nomContacto2}','{__telContacto2}','{__emContacto2}','{__telVentas}','{__emVentas}','{__dir}')"""
    
    db.executeSQL(sql)
    
    
    return redirect(url_for('gestionInventario'))

#lanza el panel del personal para ver la tabla de ususarios y crear nuevos
@app.route("/personal")
def personal():
    cursor = db.database.cursor()
    sql= f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType"
    user = db.select(sql)
    user_sorted = sorted(user, key=lambda x: x[0], reverse=True)
    return render_template("personal.html",user = user_sorted)

#muestra toda la informacion del usuario seleccionado en un formulario para realizar su edicion
@app.route("/usuario/<int:id>")
def usuario(id):
    cursor = db.database.cursor()
    sql = f"SELECT * FROM user a INNER JOIN userType b ON a.id_userType = b.id_userType WHERE a.id_user = {id}"
    cursor.execute(sql)
    user = cursor.fetchone()
    return render_template("user.html",user=user)

#realiza la funcion update y retorna la ruta de personal
@app.route('/edit_user/<int:id>',methods = ["POST","GET"])
def edit_user(id):
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
    execute = db.executeSQL(sql)
    if execute == "Completo":
        flash("Usuario actualizado de manera correcta", "success")
    else:
        flash(f"Error: {execute}", "danger")
    return redirect(url_for("personal"))
        
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
    execute = db.executeSQL(sql)
    if execute == "Completo":
        flash("Usuario creado de manera correcta", "success")
    else:
        flash(f"Error: {execute}", "danger")
    return redirect(url_for("personal"))

#-----------------------------------------------------------------------------------------------------------------------
#RUTAS PARA ELIMINAR REGISTROS DE LAS TABLAS
#-----------------------------------------------------------------------------------------------------------------------

@app.route('/deleteItem/<int:id>')
def deleteItem(id):
    delete = db.delete(id,"item","id_item") 
    print(delete)
    if delete == "Registro eliminado":
        flash("Registro eliminado con exito", "success")
    else:
        flash(f"Error> {delete}", "danger")
        
    return redirect(url_for("gestionInventario"))


@app.route("/delete/<int:id>")
def delete(id):
    id = id
    delete = db.delete(id,"user","id_user") 
    print(delete)
    if delete == "Registro eliminado":
        flash("Registro eliminado con exito", "success")
    else:
        flash(f"Error> {delete}", "danger")
        
    return redirect(url_for("personal"))

#INICIALIZA LA APLICACION | DEBUG = TRUE PARA TEST, CAMBIAR PARA PRODUCCION
if __name__ == '__main__':
    #DEBUG is SET to TRUE. CHANGE FOR PROD
    app.run(port=5000,debug=True)
    
