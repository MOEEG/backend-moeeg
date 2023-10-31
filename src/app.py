#Request se encarga de recepcionar los datos 
#que el cliente lo podría estar enviando a la pagina
from flask import Flask, request, jsonify, url_for
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS
from io import BytesIO
import os
import mne

app = Flask(__name__)
##app.config['MONGO_URI']='mongodb://18.219.115.121/moeegdb'
app.config['MONGO_URI']='mongodb://localhost/moeegdb'
#La conexión
mongo = PyMongo(app)

# Settings
CORS(app)

#Definición de colección de usuarios
db_user = mongo.db.users

@app.route('/users', methods= ['POST'])
def createUsers():
    #imprime los datos que el cliente te está enviando
    #print(request.json)
    id = db_user.insert_one({
        'name':request.json["name"],
        'dni':request.json["dni"],
        'email':request.json["email"],
        'password':request.json["password"],
        'phone':request.json["phone"],
        'age':request.json["age"]
    })
    return jsonify(str(id.inserted_id))

@app.route('/users', methods= ['GET'])
def getUsers():
    users = []
    for doc in db_user.find():
        users.append({
            "_id": str(ObjectId(doc['_id'])),
            'name':str(doc["name"]),
            'dni':str(doc["dni"]),
            'email':str(doc["email"]),
            'password':str(doc["password"]),
            'phone':str(doc["phone"]),
            'age':str(doc["age"])        
        })
    return jsonify(users)

@app.route('/users/<id>', methods= ['GET'])
def getUser(id):
    user=db_user.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(user['_id'])),
        'name':user["name"],
        'dni':user["dni"],
        'email':user["email"],
        'password':user["password"],
        'phone':user["phone"],
        'age':user["age"]                
    })

@app.route('/users/<id>', methods= ['DELETE'])
def deleteUser(id):
    user = db_user.delete_one({"_id":ObjectId(id)})
    return jsonify({
        "msg": "User deleted",
        "user": id
        })

@app.route('/users/<id>', methods= ['PUT'])
def updateUser(id):
    db_user.update_one({"_id":ObjectId(id)},{'$set':{
        'name':request.json["name"],
        'dni':request.json["dni"],
        'email':request.json["email"],
        'password':request.json["password"],
        'phone':request.json["phone"],
        'age':request.json["age"]
    }})
    return jsonify({
        "msg": "User updated",
        "user": id
        })

#Upload and Retrieve File AWS Mongo

#Definición de colección de media
db_medias = mongo.db.medias


@app.route('/medias', methods=['POST'])
def createMedia():
    try:
        eeg_file=request.files["file"]
        mongo.save_file(eeg_file.filename, eeg_file)
        id = db_medias.insert_one({
            'requester_name':request.form.get("requester_name"),
            'performer_name':request.form.get("performer_name"),
            'file_name':eeg_file.filename
        })
        return jsonify(str(id.inserted_id))
    except Exception as e:
        print(e)

# Del archivo que hemos alamcenado obtenemos el array, 
# falta configurar para que devuelva en un json los 23 canales 
@app.route('/files/<id>', methods= ['GET'])
def getFile(id):
    # Obtén el eeg_file que contiene la imagen por su identificador
    eeg_file = mongo.db.fs.files.find_one({'_id': ObjectId(id)})

    if eeg_file:
        # Recupera los fragmentos de la imagen desde GridFS
        chunks = mongo.db.fs.chunks.find({'files_id': ObjectId(id)}).sort('n')
        
        egg_file_bytes = b''
        
        for chunk in chunks:
            egg_file_bytes += chunk['data']

        egg_bytes=BytesIO(egg_file_bytes)

        ruta_archivo='archivo.edf'

        with open(ruta_archivo, 'wb') as file:
            file.write(egg_bytes.getbuffer())
        raw = mne.io.read_raw_edf('archivo.edf', preload=True)
        
        if os.path.exists(ruta_archivo):
            # Eliminar el archivo
            os.remove(ruta_archivo)
            print(f"Archivo {ruta_archivo} eliminado correctamente.")
        else:
            print(f"El archivo {ruta_archivo} no existe o ya ha sido eliminado.")
            
        # Obtener información de los canales
        info = raw.info

        # Seleccionar solo los canales EEG
        picks = mne.pick_types(info, eeg=True)

        # Leer los datos de los canales seleccionados
        data, times = raw[picks]

        print(len(data[0]))
        
        #print(egg_file_bytes)
        #print(raw.ch_names)
        return "done :D"
    else:
        return "Archivo no encontrado", 404


# Del archivo que hemos alamcenado obtenemos el array, 
# para luego desintegrarlo por segundos y cada segundo será leido 
# cuando termine de leer el primer segundo será colocado en el modelo Deep Learing
# Este identificará si es ictal o preictal
# registrará en una tupla el tiempo inicio y fin, además de registrar si es ictal o precital
# se identificará si es preictal o ictal, en este caso solo tomaremos los ictales
@app.route('/predict/<id>', methods= ['GET'])
def getPredict(id):
    # Obtén el eeg_file que contiene la imagen por su identificador
    eeg_file = mongo.db.fs.files.find_one({'_id': ObjectId(id)})

    if eeg_file:
        # Recupera los fragmentos de la imagen desde GridFS
        chunks = mongo.db.fs.chunks.find({'files_id': ObjectId(id)}).sort('n')
        
        egg_file_bytes = b''
        
        for chunk in chunks:
            egg_file_bytes += chunk['data']

        egg_bytes=BytesIO(egg_file_bytes)

        ruta_archivo='archivo.edf'

        with open(ruta_archivo, 'wb') as file:
            file.write(egg_bytes.getbuffer())
        raw = mne.io.read_raw_edf('archivo.edf', preload=True)
        
        if os.path.exists(ruta_archivo):
            # Eliminar el archivo
            os.remove(ruta_archivo)
            print(f"Archivo {ruta_archivo} eliminado correctamente.")
        else:
            print(f"El archivo {ruta_archivo} no existe o ya ha sido eliminado.")
            
        # Obtener información de los canales
        info = raw.info

        # Seleccionar solo los canales EEG
        picks = mne.pick_types(info, eeg=True)

        # Leer los datos de los canales seleccionados
        data, times = raw[picks]

        # Creamos un diccionario vacío para almacenar los registros EEG de los pacientes
        registros_3600_segundos = {}

        print(data)
        for t in range(3600):
            registro_paciente = {}
            for c in range(len(raw.ch_names)):
                fig=raw.get_data(picks=c,start=t*256, stop=(t+1)*256)
                if (sum(fig[0])!=0): 
                    registro_paciente[c] = fig[0]
            registros_3600_segundos[f"Segundo_{t}"] = registro_paciente
        
        lst_seg_ictal=[]
        for t in range(3600):
            aux=0
            for c in range(len(raw.ch_names)):
                if(model.predict(registros_3600_segundos[f"Segundo_{t}"][c])==0):
                    aux+=1
            if(aux>12):
                lst_seg_ictal+=[(t,t+1)]
        #print(egg_file_bytes)
        #print(raw.ch_names)
        return "done :D"
    else:
        return "Archivo no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)




