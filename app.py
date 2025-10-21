from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import http.client

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
        reponse=receiveMessage(request)
        return reponse

def verifyToken(req):
        token = req.args.get('hub.verify_token')
        challenge = req.args.get('hub.challenge')
        #print(f"Token recibido: {token}, Challenge recibido: {challenge}")

        if challenge and token == TOKENAPP:
            return challenge
        else:
            return jsonify({'error': 'Token invalido'}), 401

def receiveMessage(req):
    req = request.get_json()
    # add_message_log(json.dumps(request.json))

    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        obj_message = value['messages']

        if obj_message:
            messages = obj_message[0]

            if "type" in messages:
                message_type = messages["type"]

                if message_type == "interactive":
                    return 0
                
                if "text" in messages:
                    text_message = messages["text"]["body"]
                    from_number = messages["from"]

                    send_message_whatsapp(text_message, from_number)

                    add_message_log(json.dumps(messages))

        return jsonify({'message': 'EVENT_RECEIVED'}), 200
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'}), 200

def send_message_whatsapp(txt_message, to_number):
    txt_message=txt_message.lower()

    if "hola" in txt_message:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": "¡Hola! ¿En qué puedo ayudarte hoy?"
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "body": "Lo siento, no entiendo tu mensaje. ¿Podrías reformularlo?"
            }
        }

    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAkZAQZCGei9QBP4uwfv9rGgPk8mrkit7AxX1bBIZB4bQ3HInznU6tQGIPf565FVa7xHvnTerTr6CYiZCURiGZBwCY6byFSF4ADUxQxB9ZBqNB8Khu9ZC2AU1hwlJpyx5H3MzixVIO5faOHBBsl4C9zRIlvwkad7TN0xFnnc5O2tl7aYS3Wt6BkmFiLskmqDnnlOhZC0dUDcaUOJEuR9NCLZA1v3CAzvrGMB6LB1eayuEWcPB"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v24.0/827599870434160/messages", data, headers)
        response = connection.getresponse()
        print(response.status,response.reason)
    except Exception as e:
        add_message_log(json.dumps(e))
    finally:
        connection.close()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)