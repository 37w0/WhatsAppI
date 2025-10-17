from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app=Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///Support.db'
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
    messages_log.append(text_message)
    
    new_log=Log(text_message=text_message)
    db.session.add(new_log)
    db.session.commit()
    
#Token de verificacion para la configuracion del webhook de Meta WhatsApp
TOKENAPP='MyTokenApp'

@app.route('/webhook',methods=['GET','POST'])
def webhook():
    if request.method=='GET':
        challenge=verifyToken(request)
        return challenge
    elif request.method=='POST':
        response=receiveMessage(request)
        return response

def verifyToken(req):
        token = req.args.get('hub.verify_token')
        challenge = req.args.get('hub.challenge')
        if token and challenge == TOKENAPP:
            return challenge
        else:
            return jsonify({'error': 'Token invalido'}), 404

def receiveMessage(req):
    req = request.get_json()
    add_message_log(json.dumps(request.json))
    return jsonify({'message': 'EVENT_RECEIVED'}), 200


if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)