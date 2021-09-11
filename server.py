from conf import firebase
from flask import Flask, redirect, render_template,request

db = firebase.database()
auth = firebase.auth()

app = Flask(__name__)

#index con contador de casos resueltos
@app.route("/") 
def home():
    cr = 0
    try:
        casos_resueltos = db.child("Quejas y Sugerencias").get()
        for i in casos_resueltos.each():
            stat = db.child("Quejas y Sugerencias").child(i.key()).child('Status').get()
            if stat.val() == 'Resuelto':
                cr = cr + 1
                
    except:
        print('error')

    return render_template("index.html", cr=cr)

#inicio de sesion
@app.route("/login")
def login():
    return render_template("login.html")

#menu administrador
@app.route("/menuadmin")
def menuadmin():
    return render_template("menuadmin.html")

#registo de usuario nuevo
@app.route('/registro')
def registro():

    return render_template("registrouser.html")

#vista p/resetear el password
@app.route('/resetpass')
def resetpass():
    return render_template("resetpass.html")

#muestra la lista de todas las quejas y sugerencias
@app.route('/displaydata')
def displaydata():
    folios=[]
    data ={}
    dato = db.child("Quejas y Sugerencias").get()
    for i in dato.each():
        folios.append(i.key())
        val = db.child("Quejas y Sugerencias").child(i.key()).child("Status").get()
        data[i.key()] = val.val()
        

    return render_template("displaydata.html",data=data)

#muestra los datos de la queja/sugerencia seleccionada
@app.route("/selectedqs/<folio>")
def selectedqs(folio):
    if db.child("Quejas y Sugerencias").child(folio).get():

        obs = db.child("Quejas y Sugerencias").child(folio).child("Observacion").get()
        stat = db.child("Quejas y Sugerencias").child(folio).child("Status").get()

        if stat.val() == "Pendiente, sin leer": #si el comentario esta pendiente y sin leer, al ser abierto saldrá que fue leido
            db.child("Quejas y Sugerencias").child(folio).update({"Status": "Pendiente, leído"})
        
        if obs.val():
            observacion = obs.val()
            print(observacion)
        else:
            observacion = " "
        data = {
            "Categoria":(db.child("Quejas y Sugerencias").child(folio).child("Categoria").get()).val(),
            "Asunto":(db.child("Quejas y Sugerencias").child(folio).child("Asunto").get()).val(),
            "Comentario":(db.child("Quejas y Sugerencias").child(folio).child("Comentario").get()).val(),
            "Status":(db.child("Quejas y Sugerencias").child(folio).child("Status").get()).val(),
            "Observacion" : observacion
        }
        return render_template("selectedqs.html", data = data, folio=folio)
    else:
        return "<h1>No existe el folio!</h1>"

    

#actualiza el status y agrega las observaciones del admin 
#--------------PENDIENTE!------------------
@app.route('/update/<folio>', methods = ['POST'])
def update(folio):

    if request.method == 'POST':
        try:
            observacion = request.form['observacion']
            status = request.form['status']
            db.child("Quejas y Sugerencias").child(folio).update({"Status": status})
            db.child("Quejas y Sugerencias").child(folio).update({"Observacion": observacion})
                

        except:
            print('error')

    return render_template("updated.html")

#validacion inicio de sesion 
@app.route("/loguser", methods = ['POST'])
def loginuser():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']

        
    try:
        user = auth.sign_in_with_email_and_password(correo, contrasena)
        
        if user:
            return redirect('/menuadmin')
    except:
        return "<h1>Correo o constraseña incorrecta</h1><p><a href='login'>Intentalo de nuevo</p>"

@app.route("/resetpasswor", methods = ['POST'])
def ressetpas():
    if request.method == 'POST':
        correo = request.form['correo']
        auth.send_password_reset_email(correo)
    return "<h1>Listo, Revisa tu correo </h1><p><a href='/'>Volver al inicio</p>"

if __name__ == "__main__":
    print("running....")
    #app.run()
    app.run(debug = True)