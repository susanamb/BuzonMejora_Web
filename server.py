from conf import firebase
from flask import Flask, redirect, render_template, request, session
import os

db = firebase.database()
auth = firebase.auth()


app = Flask(__name__)
app.secret_key = os.urandom(24)


# index con contador de casos resueltos
@app.route("/")
def home():
    try:
        if session['usr']:
            return render_template("menuadmin.html")
    except:
        cr = 0
        cr = contadorCasos(cr)
        return render_template("index.html", cr=cr)
        
    return render_template("index.html", cr=0)


# inicio de sesion


    cr = 0
    cr = contadorCasos(cr)
    return render_template("index.html", cr=cr)
    
#inicio de sesion
@app.route("/login")
def login():
    try:
        if session['usr']:
            return render_template("menuadmin.html")
    except:        
        return render_template("login.html", user = ' ')

    return render_template("login.html")

    return render_template("login.html")
# menu administrador


@app.route("/menuadmin")
def menuadmin():
    try:
        if session['usr']:
            return render_template("menuadmin.html")
        else:
            return render_template("login.html")
    except:
        return render_template("login.html", user='f')

# registo de usuario nuevo


@app.route('/registro')
def registro():
    try:
        if session['usr']:
            return render_template("registrouser.html")
    except:
        return render_template("login.html", user='f')

# guardar usuario nuevo


@app.route('/saveuser', methods=['POST'])
def saveuser():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        concontrasena = request.form['confirmacontrasena']
        cor = correo.endswith("@uabc.edu.mx")

        if contrasena != concontrasena:  # si las contrasenas no coinciden
            return render_template("registrouser.html", warnin="claves")
        elif not cor:  # si el correo no es uabc
            return render_template("registrouser.html", warnin="correo")
        elif contrasena == concontrasena and cor:  # si los datos son correctos
            try:
                user = auth.create_user_with_email_and_password(
                    correo, contrasena)
                auth.send_email_verification(user['idToken'])

                return render_template("registrouser.html", warnin="success")
            except:
                return render_template("registrouser.html", warnin="Contraseña muy debil")


# vista p/resetear el password
@app.route('/resetpass')
def resetpass():
    return render_template("resetpass.html")

# muestra la lista de todas las quejas y sugerencias


@app.route('/displaydata')
def displaydata():
    try:
        if session['usr']:
            folios = []
            data = {}
            dato = db.child("Quejas y Sugerencias").get()
            for i in dato.each():
                folios.append(i.key())
                val = db.child("Quejas y Sugerencias").child(i.key()).child("Status").get()
                data[i.key()] = val.val()

            return render_template("displaydata.html", data=data)
        else:
            return render_template("login.html", user = 'f')
    except:
        return render_template("login.html", user='f')

#filtros 
@app.route("/filterdata/<asunto>")
def filtros(asunto):
    try:
        #a = db.child("Quejas y Sugerencias").order_by_child("Categoria").get()
        
        all_data  = db.child("Quejas y Sugerencias").get() #trae la informacion de la base de datos
        data = {}
        child = ""
        if asunto == 'Queja' or asunto == 'Sugerencia': #si se se selecciono queja o sugerencia,          
            child = "Categoria"                             #entonces se busca en categorias
        elif asunto == 'Resuelto' or asunto == "Pendientes":#si se selecciono resuelto o pendiente,
            child = "Status"                                #entonces se busca en status

        for i in all_data.each(): #recorre todos los registros de la bd
            stat = db.child("Quejas y Sugerencias").child(i.key()).child(child).get()
            if stat.val() == asunto:
                dos = db.child("Quejas y Sugerencias").child(i.key()).child("Status").get()
                data[i.key()] = dos.val()
            elif stat.val().startswith("Pendiente") and asunto == "Pendientes":
                dos = db.child("Quejas y Sugerencias").child(i.key()).child("Status").get()
                data[i.key()] = dos.val()

        return render_template("displaydata.html", data=data)
    except:     
        return render_template("menuadmin.html")


# muestra los datos de la queja/sugerencia seleccionada
@app.route("/selectedqs/<folio>")
def selectedqs(folio):
    try:
        if session['usr']:
            if db.child("Quejas y Sugerencias").child(folio).get():

                obs = db.child("Quejas y Sugerencias").child(
                    folio).child("Observacion").get()
                stat = db.child("Quejas y Sugerencias").child(
                    folio).child("Status").get()

                # si el comentario esta pendiente y sin leer, al ser abierto saldrá que fue leido
                if stat.val() == "Pendiente, sin leer":
                    db.child("Quejas y Sugerencias").child(
                        folio).update({"Status": "Pendiente, leído"})

                if obs.val():
                    observacion = obs.val()
                else:
                    observacion = " "
                data = {
                    "Categoria": (db.child("Quejas y Sugerencias").child(folio).child("Categoria").get()).val(),
                    "Asunto": (db.child("Quejas y Sugerencias").child(folio).child("Asunto").get()).val(),
                    "Comentario": (db.child("Quejas y Sugerencias").child(folio).child("Comentario").get()).val(),
                    "Status": (db.child("Quejas y Sugerencias").child(folio).child("Status").get()).val(),
                    "Observacion": observacion
                }
                return render_template("selectedqs.html", data=data, folio=folio)
            else:
                return "<h1>No existe el folio!</h1>"
    except:
        return render_template("login.html", user='f')

#actualiza el status y agrega las observaciones del admin 
@app.route('/update/<folio>', methods = ['POST'])
def update(folio):

    if request.method == 'POST':
        try:
            observacion = request.form['observacion']
            status = request.form['status']
            db.child("Quejas y Sugerencias").child(
                folio).update({"Status": status})
            db.child("Quejas y Sugerencias").child(
                folio).update({"Observacion": observacion})

        except:
            print('error')

    return render_template("updated.html")


# validacion inicio de sesion

@app.route("/loguser", methods=['POST'])
def loginuser():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

    try:

        user = auth.sign_in_with_email_and_password(correo, contrasena)

        if user:
            user_info = auth.get_account_info(user['idToken'])
            verified = user_info['users'][0]['emailVerified']

            #
            if not verified:
                return render_template("login.html", user="false")

            else:

                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']
                session['usr'] = user_id
                return redirect('/menuadmin')
    except:
        return render_template("login.html", user="no")

# para resetear el password


@app.route("/resetpasswor", methods=['POST'])
def ressetpas():
    if request.method == 'POST':
        if request.form['correo']:
            correo = request.form['correo']

            cor = correo.endswith("@uabc.edu.mx")
            if cor:
                try:

                    auth.send_password_reset_email(correo)
                    return render_template("resetpass.html", user="si")
                except:
                    return render_template("resetpass.html", user="no")

@app.route("/manual")
def manual():
   return render_template('manual.html')


# el usuario cierra sesion

@app.route("/logout")
def logout():
    try:
        session['usr'] = 0
        cr = 0
        cr = contadorCasos(cr)
        return render_template("index.html", cr=cr)
    except:
        return redirect("/")


#cuenta los casos resueltos de la base de datos
def contadorCasos(cr):
    try:
            casos_resueltos = db.child("Quejas y Sugerencias").get()
            for i in casos_resueltos.each():
                stat = db.child("Quejas y Sugerencias").child(i.key()).child('Status').get()
                if stat.val() == 'Resuelto':
                    cr = cr + 1                      
    except:
            print('error')
            cr = 0
    return cr

if __name__ == "__main__":
    print("running....")
    # app.run()
    app.run(debug=True)
