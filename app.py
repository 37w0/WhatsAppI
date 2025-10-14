from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app=Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

#Modelo de la base de datos
class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    date_time=db.Column(db.DateTime, default=datetime.utcnow)
    text_message=db.Column(db.TEXT)

#Crear la bd si no existe
with app.app_context():
    db.create_all()


def order_rows_by_datetime(rows):
    return sorted(rows, key=lambda row: row.date_time, reverse=True)

@app.route('/')
def index():
    #Obtener todos los registros de la tabla Log
    rows=Log.query.all()
    ordered_rows=order_rows_by_datetime(rows)
    return render_template('index.html',rows=ordered_rows)

messages_log=[]

#Funcion para agregar mensajes al log y guardarlos en la base de datos
def add_message_log(text_message):
    new_log=Log(text_message=text_message)
    db.session.add(new_log)
    db.session.commit()
    messages_log.append(text_message)

#add_message_log(json.dumps("Prueba 1 de mensaje PY"))

#Token de verificacion para la configuracion del webhook de Meta WhatsApp
TOKENAPP='DONKEY!'
@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method=='GET':
        challenge=verifyToken(request)
        return challenge
    elif request.method=='POST':
        response=receiveMessage(request)

def verifyToken(request):
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token and challenge == TOKENAPP:
            return challenge
        else:
            return jsonify({'error': 'Token de verificación inválido'}), 401

def receiveMessage(request):
    req = request.get_json()
    add_message_log(json.dumps(request.json))
    return jsonify({'status': 'EVENT_RECEIVED'}), 200

    #    return 'Token de verificación inválido'
    # if request.method=='GET':
    #     if request.args.get('hub.verify_token')==TOKENAPP:
    #         return request.args.get('hub.challenge')
    #     return 'Token de verificación inválido'
    # if request.method=='POST':
    #     data=request.json
    #     print(json.dumps(data,indent=4))
    #     try:
    #         text_message=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #         add_message_log(text_message)
    #     except:
    #         pass
    #     return 'EVENT_RECEIVED'

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)