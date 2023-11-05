#Request se encarga de recepcionar los datos 
#que el cliente lo podría estar enviando a la pagina
from flask import Flask, request, jsonify, url_for
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS
from io import BytesIO
import os
import mne

app = Flask(__name__)
##app.config['MONGO_URI']='mongodb://18.117.105.88/moeegdb'
app.config['MONGO_URI']='mongodb://localhost/moeegdb'
#La conexión
mongo = PyMongo(app)

# Settings
CORS(app)

#Definición de colección de usuarios
db_user = mongo.db.users

###################################
######## Registrar Doctor ########
###################################
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






####################################
######## Registrar Paciente ########
####################################

db_patient = mongo.db.patients

@app.route('/patients', methods= ['POST'])
def createPatients():
    #imprime los datos que el cliente te está enviando
    #print(request.json)
    id = db_patient.insert_one({
        'name':request.json["name"],
        'lastname':request.json["lastname"],
        'phone':request.json["phone"]
    })
    return jsonify(str(id.inserted_id))

@app.route('/patients', methods= ['GET'])
def getPatients():
    patients = []
    for pat in db_patient.find():
        patients.append({
            "_id": str(ObjectId(pat['_id'])),
            'name':str(pat["name"]),
            'lastname':str(pat["lastname"]),
            'phone':str(pat["phone"])   
        })
    return jsonify(patients)

@app.route('/patients/<id>', methods= ['GET'])
def getPatient(id):
    patient=db_patient.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(patient['_id'])),
        'name':patient["name"],
        'lastname':patient["lastname"],
        'phone':patient["phone"]           
    })

@app.route('/patients/<id>', methods= ['DELETE'])
def deletePatient(id):
    patient = db_patient.delete_one({"_id":ObjectId(id)})
    return jsonify({
        "msg": "patient deleted",
        "patient": id
        })

@app.route('/patients/<id>', methods= ['PUT'])
def updatePatient(id):
    db_patient.update_one({"_id":ObjectId(id)},{'$set':{
        'name':request.json["name"],
        'lastname':request.json["lastname"],
        'phone':request.json["phone"]
    }})
    return jsonify({
        "msg": "Patient updated",
        "patient": id
        })

# db_patient = mongo.db.patients

# @app.route('/patients', methods= ['POST'])
# def createPatients():
#     #imprime los datos que el cliente te está enviando
#     #print(request.json)
#     id = db_patient.insert_one({
#         'name':request.json["name"],
#         'dni':request.json["dni"],
#         'email':request.json["email"],
#         'password':request.json["password"],
#         'phone':request.json["phone"],
#         'age':request.json["age"]
#     })
#     return jsonify(str(id.inserted_id))

# @app.route('/patients', methods= ['GET'])
# def getPatients():
#     patients = []
#     for pat in db_patient.find():
#         patients.append({
#             "_id": str(ObjectId(pat['_id'])),
#             'name':str(pat["name"]),
#             'dni':str(pat["dni"]),
#             'email':str(pat["email"]),
#             'password':str(pat["password"]),
#             'phone':str(pat["phone"]),
#             'age':str(pat["age"])        
#         })
#     return jsonify(patients)

# @app.route('/patients/<id>', methods= ['GET'])
# def getPatient(id):
#     patient=db_patient.find_one({'_id':ObjectId(id)})
#     return jsonify({
#         "_id": str(ObjectId(patient['_id'])),
#         'name':patient["name"],
#         'dni':patient["dni"],
#         'email':patient["email"],
#         'password':patient["password"],
#         'phone':patient["phone"],
#         'age':patient["age"]                
#     })

# @app.route('/patients/<id>', methods= ['DELETE'])
# def deletePatient(id):
#     patient = db_patient.delete_one({"_id":ObjectId(id)})
#     return jsonify({
#         "msg": "patient deleted",
#         "patient": id
#         })

# @app.route('/patients/<id>', methods= ['PUT'])
# def updatePatient(id):
#     db_patient.update_one({"_id":ObjectId(id)},{'$set':{
#         'name':request.json["name"],
#         'dni':request.json["dni"],
#         'email':request.json["email"],
#         'password':request.json["password"],
#         'phone':request.json["phone"],
#         'age':request.json["age"]
#     }})
#     return jsonify({
#         "msg": "Patient updated",
#         "patient": id
#         })






##################################
####### Registrar Archivo ########
##################################
#Upload and Retrieve File AWS Mongo

#Definición de colección de media
db_medias = mongo.db.medias

@app.route('/medias', methods=['POST'])
def createMedia():
    try:
        eeg_file=request.files["file"]
        patient_id=request.form.get("patient_id")
        doctor_id=request.form.get("doctor_id")

        # Obtener el nombre del paciente y del doctor por su ID
        patient = db_patient.find_one({'_id': patient_id})
        doctor = db_user.find_one({'_id': doctor_id})

        mongo.save_file(eeg_file.filename, eeg_file)
        id = db_medias.insert_one({
            'patient_name':patient['name'],
            'doctor_name':doctor['name'],
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

        data=data.tolist()
        print(len(data))
        #print(data.tolist())
        #print(egg_file_bytes)
        #print(raw.ch_names)
        return jsonify({
            'data 1':data[0],         
            'data 2':data[1],        
            'data 3':data[2],         
            'data 4':data[3],         
            'data 5':data[4],         
            'data 6':data[5],         
            'data 7':data[6],         
            'data 8':data[7],         
            'data 9':data[8],         
            'data 10':data[9],         
            'data 11':data[10],         
            'data 12':data[11],         
            'data 13':data[12],         
            'data 14':data[13],         
            'data 15':data[14],         
            'data 16':data[15],         
            'data 17':data[16],         
            'data 18':data[17],         
            'data 19':data[18],         
            'data 20':data[19],         
            'data 21':data[20],         
            'data 22':data[21],         
            'data 23':data[22]         
        })
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
                lst_seg_ictal+=[[t,t+1]]
        #print(egg_file_bytes)
        #print(raw.ch_names)
        return "done :D"
    else:
        return "Archivo no encontrado", 404

if __name__ == "__main__":
    app.run(debug=True)




