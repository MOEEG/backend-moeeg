#Request se encarga de recepcionar los datos 
#que el cliente lo podría estar enviando a la pagina
from flask import Flask, request, jsonify, url_for
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS
from io import BytesIO
from keras.models import load_model
import pandas as pd
from joblib import dump, load
import dwt
import numpy as np
import channels 
import os
import mne
from tqdm import tqdm

app = Flask(__name__)
##app.config['MONGO_URI']='mongodb://18.218.20.150/moeegdb'
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
        'dni':request.json["dni"],
        'email':request.json["email"],
        'password':request.json["password"],
        'phone':request.json["phone"],
        'age':request.json["age"],
        'contact_name':request.json["contact_name"],
        'contact_phone':request.json["contact_phone"]
    })
    return jsonify(str(id.inserted_id))


@app.route('/patients', methods= ['GET'])
def getPatients():
    patients = []
    for pat in db_patient.find():
        patients.append({
            "_id": str(ObjectId(pat['_id'])),
            'name':str(pat["name"]),
            'dni':str(pat["dni"]),
            'email':str(pat["email"]),
            'password':str(pat["password"]),
            'phone':str(pat["phone"]),
            'age':str(pat["age"]),        
            'contact_name':str(pat["contact_name"]),        
            'contact_phone':str(pat["contact_phone"])        
        })
    return jsonify(patients)

@app.route('/patients/<id>', methods= ['GET'])
def getPatient(id):
    patient=db_patient.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(patient['_id'])),
        'name':patient["name"],
        'dni':patient["dni"],
        'email':patient["email"],
        'password':patient["password"],
        'phone':patient["phone"],
        'age':patient["age"],
        'contact_name':patient["contact_name"],
        'contact_phone':patient["contact_phone"],
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
        'dni':request.json["dni"],
        'email':request.json["email"],
        'password':request.json["password"],
        'phone':request.json["phone"],
        'age':request.json["age"],
        'contact_name':request.json["contact_name"],
        'contact_phone':request.json["contact_phone"]
    }})
    return jsonify({
        "msg": "Patient updated",
        "patient": id
        })



##################################
##### Registrar Observación ######
##################################
#Upload and Retrieve File AWS Mongo

#Definición de colección de media

db_observation = mongo.db.observations

@app.route('/Observations', methods=['POST'])
def createObservations():
    try:
        #aca quizás se necesite cambiar a string(patient_id) en la fila 205
        patient_id=request.json['_id']
        doctor_id=request.json['_id']
        media_id=request.json['_id']
        

        # Obtener el nombre del paciente,el doctor y el nombre del archivo por su ID
        patient = db_patient.find_one({'_id': ObjectId(patient_id)})
        doctor = db_user.find_one({'_id':  ObjectId(doctor_id)})
        media = db_media.find_one({'_id': ObjectId(media_id)})
        
        
        print(patient,doctor)
        id = db_observation.insert_one({
            'patient_name':patient['name'],
            'doctor_name':doctor['name'],
            'file_name':media['filename']
        })
        return jsonify(str(id.inserted_id))
    except Exception as e:
        print(e)

@app.route('/observations', methods= ['GET'])
def getObservatios():
    observations = []
    for med in db_observation.find():
        observations.append({
            "_id": str(ObjectId(med['_id'])),
            'patient_name':str(med['patient_name']),
            'doctor_name':str(med['doctor_name']),      
            'file_name':str(med['file_name'])      
        })
    return jsonify(observations)

@app.route('/observations/<id>', methods= ['GET'])
def getObservation(id):
    observation=db_observation.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(observation['_id'])),
        'patient_name':observation["patient_name"],
        'doctor_name':observation["doctor_name"],           
        'file_name':observation['file_name']     
    })

@app.route('/observations/<id>', methods= ['DELETE'])
def deleteObservation(id):
    observation = db_observation.delete_one({"_id":ObjectId(id)})
    return jsonify({
        "msg": "observation deleted",
        "observation": id
        })

@app.route('/observations/<id>', methods= ['PUT'])
def updateObservation(id):
    db_observation.update_one({"_id":ObjectId(id)},{'$set':{
        'patient_name':request.json["patient_name"],
        'doctor_name':request.json["doctor_name"],
        'file_name':request.json["file_name"],
    }})
    return jsonify({
        "msg": "Observation updated",
        "observation": id
        })



##################################
####### Registrar Archivo ########
##################################
#Upload and Retrieve File AWS Mongo

#Definición de colección de media

db_media = mongo.db.medias

@app.route('/medias', methods=['POST'])
def createMedia():
    #try:    
    
    eeg_file=request.files["file"]

    mongo.save_file(eeg_file.filename, eeg_file)
    
    eeg_file = mongo.db.fs.files.find_one({'filename': eeg_file.filename})

    #Cargar modelo
    #print(next(iter(eeg_file.values())))
    if eeg_file:
        # Recupera los fragmentos de la imagen desde GridFS
        chunks = mongo.db.fs.chunks.find({'files_id': ObjectId(next(iter(eeg_file.values())))}).sort('n')
        
        egg_file_bytes = b''
        
        for chunk in chunks:
            egg_file_bytes += chunk['data']

        egg_bytes=BytesIO(egg_file_bytes)

        ruta_archivo='archivo.edf'

        with open(ruta_archivo, 'wb') as file:
            file.write(egg_bytes.getbuffer())
    
        #Cargar modelo
    
        if ruta_archivo:
            b=channels.b()
            raw = mne.io.read_raw_edf(ruta_archivo, preload=True)

            if os.path.exists(ruta_archivo):
                # Eliminar el archivo
                os.remove(ruta_archivo)
                print(f"Archivo {ruta_archivo} eliminado correctamente.")
            else:
                print(f"El archivo {ruta_archivo} no existe o ya ha sido eliminado.")

            count=0

            for i in raw.ch_names:
              if i in b:
                count+=1

            if count==23:
              lst_seg_ictal=[]

              df = pd.DataFrame(columns= ['Coeficiente_' + str(i) for i in range(256+1)])

              ss=load('std_scaler.bin')

              model = load_model('DWT_prime_model.h5')

              for t in tqdm(range(3600), desc="Procesando Parte 1"):
                  df_copy=df
                  #registro_paciente = {}
                  for c in (raw.ch_names):
                    if (c in b):
                      fig=raw.get_data(picks=raw.ch_names.index(c),start=t*256, stop=(t+1)*256)
                      if (sum(fig[0])!=0): 
                          #registro_paciente[c] = fig[0]
                          array = dwt.wavelet_denoising(fig[0], wavelet="db18", level=1)
                          array = np.insert(array, 0,b.index(c))
                          #print(b.index(c))
                          new_row = pd.Series(array.flatten(), index=df_copy.columns)
                          df_copy = pd.concat([df_copy, new_row.to_frame().T], ignore_index=True)

                  X=np.array(df_copy)
                  #print(X.shape)

                  data_reshaped = X.reshape((X.shape[0]*X.shape[1]))

                  data_scaled=ss.transform(data_reshaped.reshape(1, -1))

                  X_norm = data_scaled.reshape(X.shape)

                  y_predic = np.round(model.predict(X_norm.reshape(1, X.shape[0], X.shape[1]),verbose=0))

                  if(y_predic==0):
                    lst_seg_ictal+=[[t,t+1]]
    

            #eeg_file=request.files["file"]

            #mongo.save_file(eeg_file.filename, eeg_file)

            #data=raw.get_data(start=0, stop=921600)
            #data=data.tolist()
            

            #print(eeg_file['filename'])
            #print("##############################################")
            #print("##############################################")
            #print("##############################################")
            #print("##############################################")
            ##print(data)
            #print("##############################################")
            #print("##############################################")
            #print("##############################################")
            #print("##############################################")
            #print(lst_seg_ictal)

            id = db_media.insert_one({
                'file_name':eeg_file['filename'],
                'time':lst_seg_ictal 
                #'1':raw.get_data(   picks=raw.ch_names.index('FP1-F7')).tolist(),  
                #'2':raw.get_data(   picks=raw.ch_names.index('F7-T7')).tolist(), 
                #'3':raw.get_data(   picks=raw.ch_names.index('T7-P7')).tolist(),
                #'4':raw.get_data(   picks=raw.ch_names.index('P7-O1')).tolist(),
                #'5':raw.get_data(   picks=raw.ch_names.index('FP1-F3')).tolist(), 
                #'6':raw.get_data(   picks=raw.ch_names.index('F3-C3')).tolist(),
                #'7':raw.get_data(   picks=raw.ch_names.index('C3-P3')).tolist(),
                #'8':raw.get_data(   picks=raw.ch_names.index('P3-O1')).tolist(),
                #'9':raw.get_data(   picks=raw.ch_names.index('FZ-CZ')).tolist(),
                #'10':raw.get_data(  picks=raw.ch_names.index('CZ-PZ')).tolist(),
                #'11':raw.get_data(  picks=raw.ch_names.index('FP2-F4')).tolist(), 
                #'12':raw.get_data(  picks=raw.ch_names.index('F4-C4')).tolist(),
                #'13':raw.get_data(  picks=raw.ch_names.index('C4-P4')).tolist(),
                #'14':raw.get_data(  picks=raw.ch_names.index('P4-O2')).tolist(),
                #'15':raw.get_data(  picks=raw.ch_names.index('FP2-F8')).tolist(), 
                #'16':raw.get_data(  picks=raw.ch_names.index('F8-T8')).tolist(),
                #'17':raw.get_data(  picks=raw.ch_names.index('T8-P8-0')).tolist(),  
                #'18':raw.get_data(  picks=raw.ch_names.index('P8-O2')).tolist(),
                #'19':raw.get_data(  picks=raw.ch_names.index('P7-T7')).tolist(),
                #'20':raw.get_data(  picks=raw.ch_names.index('T7-FT9')).tolist(), 
                #'21':raw.get_data(  picks=raw.ch_names.index('FT9-FT10')).tolist(),   
                #'22':raw.get_data(  picks=raw.ch_names.index('FT10-T8')).tolist(),  
                #'23':raw.get_data(  picks=raw.ch_names.index('T8-P8-1')).tolist(),   
            })
            return jsonify(str(id.inserted_id))
        else:
            return "Archivo no encontrado", 404
    #except Exception as e:
    #    return jsonify({"error": str(e)})

@app.route('/medias', methods= ['GET'])
def getMedias():
    medias = []
    for med in db_media.find():
        medias.append({
            "_id": str(ObjectId(med['_id'])),
            'file_name':str(med["file_name"]),
            'time':str(med["time"])      
        })
    return jsonify(medias)

@app.route('/medias/<id>', methods= ['GET'])
def getMedia(id):
    media=db_media.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(media['_id'])),
        'name':media["file_name"],
        'dni':media["time"]           
    })
#AQUI FALTA BORRO DE fs.CHUNK Y fs.FILES
@app.route('/medias/<id>', methods= ['DELETE'])
def deleteMedia(id):
    media = db_media.delete_one({"_id":ObjectId(id)})
    return jsonify({
        "msg": "media deleted",
        "media": id
        })





# Del archivo que hemos alamcenado obtenemos el array, 
# falta configurar para que devuelva en un json los 23 canales 
@app.route('/files/<id>', methods= ['GET'])
def getFile(id):
    # Obtén el eeg_file que contiene la imagen por su identificador
    eeg_file = mongo.db.fs.files.find_one({'_id': ObjectId(id)})

    #Cargar modelo

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
        for t in tqdm(range(3600), desc="Procesando Parte 1"):
            registro_paciente = {}
            for c in range(len(raw.ch_names)):
                fig=raw.get_data(picks=c,start=t*256, stop=(t+1)*256)
                if (sum(fig[0])!=0): 
                    registro_paciente[c] = fig[0]
            registros_3600_segundos[f"Segundo_{t}"] = registro_paciente
        
        model = load_model('DWT_model_the_best.h5')
        #ss=load('std_scaler.bin')
        
        lst_seg_ictal=[]
        for t in tqdm(range(3600), desc="Procesando Parte 2"):
            aux=0
            for c in range(len(raw.ch_names)):
                #print(registros_3600_segundos[f"Segundo_{t}"][c])
                #print(registros_3600_segundos[f"Segundo_{t}"][c].shape)
                #print('###############################')
                a=ss.transform(np.array(registros_3600_segundos[f"Segundo_{t}"][c]).reshape(1, 256))
                #print(a)
                #print(a.shape)
                #print('###############################')
                a=np.array(a).reshape(1, 256, 1)
                #print(a)
                #print(a.shape)
                #print('###############################')
                if(np.round(np.array(model.predict(a,verbose=0)))==0):
                    aux+=1
            if(aux>12):
                lst_seg_ictal+=[[t,t+1]]
        #print(egg_file_bytes)
        #print(raw.ch_names)

        data=data.tolist()
        #print(len(data))
        #print(data.tolist())
        #print(egg_file_bytes)
        #print(raw.ch_names)
        return jsonify({
            #'data 1':data[0],         
            #'data 2':data[1],        
            #'data 3':data[2],         
            #'data 4':data[3],         
            #'data 5':data[4],         
            #'data 6':data[5],         
            #'data 7':data[6],         
            #'data 8':data[7],         
            #'data 9':data[8],         
            #'data 10':data[9],         
            #'data 11':data[10],         
            #'data 12':data[11],         
            #'data 13':data[12],         
            #'data 14':data[13],         
            #'data 15':data[14],         
            #'data 16':data[15],         
            #'data 17':data[16],         
            #'data 18':data[17],         
            #'data 19':data[18],         
            #'data 20':data[19],         
            #'data 21':data[20],         
            #'data 22':data[21],         
            #'data 23':data[22],
            'time':lst_seg_ictal         
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
    
    #Cargar modelo
    model = load_model('src\DWT_model_best.h5')

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
                if(np.round(model.predict(registros_3600_segundos[f"Segundo_{t}"][c]))==0):
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




