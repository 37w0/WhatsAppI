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

                #Guardar el tipo de mensaje en el log
                add_message_log(json.dumps(messages))

                if message_type == "interactive":
                    interactive_type = messages["interactive"]["type"]
                    if interactive_type == "button_reply":
                        text_message = messages["interactive"]["button_reply"]["id"]
                        from_number = messages["from"]
                        from_number = from_number.replace("521", "+52")

                        sand_message_whatsapp(text_message, from_number)


                
                if "text" in messages:
                    text_message = messages["text"]["body"]
                    from_number = messages["from"]
                    from_number = from_number.replace("521", "+52")

                    sand_message_whatsapp(text_message, from_number)

                    #Guardar el mensaje recibido en el log
                    add_message_log(json.dumps(messages))

        return jsonify({'message': 'EVENT_RECEIVED'}), 200
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'}), 200

def sand_message_whatsapp(txt_message, to_number):
    txt_message=txt_message.lower()

    if "hola" in txt_message:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": "Respuesta automatica: Hola, ¿en qué puedo ayudarte?"
                }
        }
    elif "ayuda" in txt_message:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "Elige una de las siguientes opciones:"
                },
                "footer": {
                    "text": "¿De que empresa necesitas soporte?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnCoAdictt",
                                "title": "Adictt"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnCoDomarts",
                                "title": "Domarts"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "btnCoConverse",
                                "title": "Corporativo"
                            }
                        }
                    ]
                }
            }
        }
    elif "btnCoAdictt" in txt_message:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": "Elige una de las siguientes opciones:"
                },
                "footer": {
                    "text": "¿De que boutique nos estás contactando?"
                },
                "action": {
                    "section": [
                        {
                            "title": "Boutiques Adictt",
                            "rows": [
                                {
                                    "id": "btnAdicttOUGC",
                                    "title": "MULTIBRAND OUTLET GUADALAJARA CENTRO"
                                },
                                {
                                    "id": "btnAdicttARAG",
                                    "title": "MULTIBRAND ARAGON"
                                },
                                {
                                    "id": "btnAdicttMBCY",
                                    "title": "MULTIBRAND COYOACAN"
                                },
                                {
                                    "id": "btnAdicttBUEN",
                                    "title": "MULTIBRAND BUENAVISTA"
                                },
                                {
                                    "id": "btnAdicttOUCH",
                                    "title": "MULTIBRAN OUTLET CHALCO CENTRO"
                                },
                                {
                                    "id": "btnAdicttCHAL",
                                    "title": "MULTIBRAN OUTLET CHALCO"
                                },
                                {
                                    "id": "btnAdicttOURG",
                                    "title": "MULTIBRAN OUTLET ARAGON"
                                },
                                {
                                    "id": "btnAdicttOTEP",
                                    "title": "MULTIBRAN OUTLET TEPOZAN"
                                },
                                {
                                    "id": "btnAdicttTEXC",
                                    "title": "MULTIBRAN OUTLET TEXOCOCO"
                                },
                                {
                                    "id": "btnAdicttOGPT",
                                    "title": "MULTIBRAN OUTLET GRAN PATIO TEXCOCO"
                                },
                                {
                                    "id": "btnAdicttCOAC",
                                    "title": "MULTIBRAN OUTLET COACALCO"
                                },
                                {
                                    "id": "btnAdicttTECA",
                                    "title": "MULTIBRAN OUTLET TECAMAC"
                                },
                                {
                                    "id": "btnAdicttGSUR",
                                    "title": "MULTIBRAND GRAN SUR"
                                },
                                {
                                    "id": "btnAdicttOURO",
                                    "title": "MULTIBRAND OUTLET ROSARIO"
                                },
                                {
                                    "id": "btnAdicttERMI",
                                    "title": "MULTIBRAND ERMITA"
                                },
                                {
                                    "id": "btnAdicttCUER",
                                    "title": "MULTIBRAND OUTLET CUERNAVACA"
                                },
                                {
                                    "id": "btnAdicttOUJY",
                                    "title": "MULTIBRAND OUTLET LA JOYA"
                                },
                                {
                                    "id": "btnAdicttVIGA",
                                    "title": "MULTIBRAND LA VIGA"
                                },
                                {
                                    "id": "btnAdicttOTEX",
                                    "title": "MULTIBRAND OUTLET TEXCOCO CENTRO"
                                },
                                {
                                    "id": "btnAdicttMBME",
                                    "title": "MULTIBRAND OUTLET MARIANO ESCOBEDO"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {
                "preview_url": True,
                "body": "Respuesta automatica: Gracias por tu mensaje. Te responderemos pronto."
                }
        }

    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAkZAQZCGei9QBPxMIelnghky2ZB9IzFTw6SWAkOrRcEmgZCE4NX7LPR8Bq7XZBTT6WEIKQg08U9WK8GCXaZAmGZAVoZA7fnBCqzm1RyV4KePPfGEAfbcqg02Op0JPyylxELp89UOR0dP0lgy7DlkZCCCbLjM88HkZA42Lfz9ktIOPCzO8PcpEE0Dy402k8g6Pa0OhaAhlnZBZBhyecz2KyhfmJtVUZCz4vT1mAahIRsdXgZAnpZAyQ"
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