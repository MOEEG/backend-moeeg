#Request se encarga de recepcionar los datos 
#que el cliente lo podría estar enviando a la pagina
from flask import Flask, request, jsonify, session, redirect, url_for
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
from flask_bcrypt import Bcrypt
from secrets import token_hex
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt

app = Flask(_name_)

#app.config['MONGO_URI']='mongodb://18.117.180.53:27017/moeegdb'
app.config['MONGO_URI']='mongodb://18.117.240.49/moeegdb'
#app.config['MONGO_URI']='mongodb://localhost/moeegdb'
app.config['SECRET_KEY'] = token_hex(16)
#La conexión
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
revoked_tokens = set()

# Settings
CORS(app)

####################################
######### Registrar Doctor #########
####################################
db_user = mongo.db.users

@app.route('/register', methods=['POST'])
def register():
    existing_user = db_user.find_one({'username': request.json["dni"]})

    if existing_user is None:
        hashed_password = bcrypt.generate_password_hash(request.json["dni"]).decode('utf-8')
        db_user.insert_one({
            'username': request.json["dni"],
            'name':request.json["name"], 
            'dni':request.json["dni"],
            'email':request.json["email"],
            'password': hashed_password,
            'phone':request.json["phone"],
            'age':request.json["age"]
            })
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'message': 'Username already exists'}), 409


# Ruta para el login de usuarios
@app.route('/login', methods=['POST'])
def login():
    print(request.json['username'])
    print(request.json['password'])
    login_user = db_user.find_one({'username': request.json['username']})
    print(login_user)
    print(login_user['password'])
    print(request.json['password'])
    print(bcrypt.check_password_hash(login_user['password'], request.json['password']))
    if login_user and bcrypt.check_password_hash(login_user['password'], request.json['password']):
        print('###################')
        print(login_user['username'])
        access_token = create_access_token(identity=login_user['username'])
        print(access_token)
        #session['username'] = request.json['username']
        #return jsonify({'message': 'Login successful'}), 200
        return jsonify(access_token=access_token)
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# Ruta para el logout de usuarios
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    revoked_tokens.add(jti)
    return jsonify({'message': 'Logout successful'}), 200

# Ruta para verificar el estado del usuario actual
# @app.route('/user', methods=['GET'])
# def get_user():
#     if 'username' in session:
#         return jsonify({'username': session['username']}), 200
#     else:
#         return jsonify({'message': 'User not logged in'}), 401

@app.route('/get_user', methods=['GET'])
@jwt_required()
def get_user():
    print(get_jwt_identity())
    current_user = get_jwt_identity()
    user = db_user.find_one({'username': current_user}, {'password': 0})  # Excluir la contraseña en la respuesta
    if user:
        print(user)
        return jsonify(
            {
        "_id":str(ObjectId(user['_id'])),
        #str(ObjectId(pat['_id']))
        # "username":user['username'],
        # "name":user['name'],
        # "dni":user['dni'],
        # "email":user['email'],
        # "phone":user['phone'],
        # "age":user['age']
        }
        ), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/update-password', methods=['PUT'])
@jwt_required()
def update_password():
    current_user_ = get_jwt_identity()
    print(session['username'])
    if 'username' in session:
        current_user = db_user.find_one({'username': session['username']})
        print(session['username'])
        if current_user and bcrypt.check_password_hash(current_user['password'], request.json['current_password']):
            new_password = bcrypt.generate_password_hash(request.json['new_password']).decode('utf-8')
            db_user.update_one({'_id': current_user['_id']}, {'$set': {'password': new_password}})
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'message': 'Current password is incorrect'}), 401
    else:
        return jsonify({'message': 'User not logged in'}), 401

###################################
######## Registrar Doctor ########
###################################


#Definición de colección de usuarios
#db_user = mongo.db.users
#@app.route('/users', methods= ['POST'])
#def createUsers():
#    #imprime los datos que el cliente te está enviando
#    #print(request.json)
#    id = db_user.insert_one({
#        'name':request.json["name"],
#        'dni':request.json["dni"],
#        'email':request.json["email"],
#        'password':request.json["password"],
#        'phone':request.json["phone"],
#        'age':request.json["age"]
#    })
#    return jsonify(str(id.inserted_id))

#@app.route('/users', methods= ['GET'])
#def getUsers():
#    users = []
#    for doc in db_user.find():
#        users.append({
#            "_id": str(ObjectId(doc['_id'])),
#            'name':str(doc["name"]),
#            'dni':str(doc["dni"]),
#            'email':str(doc["email"]),
#            'password':str(doc["password"]),
#            'phone':str(doc["phone"]),
#            'age':str(doc["age"])        
#        })
#    return jsonify(users)

#@app.route('/users/<id>', methods= ['GET'])
#def getUser(id):
#    user=db_user.find_one({'_id':ObjectId(id)})
#    return jsonify({
#        "_id": str(ObjectId(user['_id'])),
#        'name':user["name"],
#        'dni':user["dni"],
#        'email':user["email"],
#        'password':user["password"],
#        'phone':user["phone"],
#        'age':user["age"]                
#    })

#@app.route('/users/<id>', methods= ['DELETE'])
#def deleteUser(id):
#    user = db_user.delete_one({"_id":ObjectId(id)})
#    return jsonify({
#        "msg": "User deleted",
#        "user": id
#        })

#@app.route('/users/<id>', methods= ['PUT'])
#def updateUser(id):
#    db_user.update_one({"_id":ObjectId(id)},{'$set':{
#        'name':request.json["name"],
#        'dni':request.json["dni"],
#        'email':request.json["email"],
#        'password':request.json["password"],
#        'phone':request.json["phone"],
#        'age':request.json["age"]
#    }})
#    return jsonify({
#        "msg": "User updated",
#        "user": id
#        })






####################################
######## Registrar Paciente ########
####################################

db_patient = mongo.db.patients

@app.route('/patients', methods= ['POST'])
@jwt_required()

def createPatients():
    current_user = get_jwt_identity()

    #imprime los datos que el cliente te está enviando
    #print(request.json)
    id = db_patient.insert_one({
        'name':request.json["name"],
        'dni':request.json["dni"],
        'email':request.json["email"],
        'phone':request.json["phone"],
        'age':request.json["age"],
        'contact_name':request.json["contact_name"],
        'contact_phone':request.json["contact_phone"]
    })
    return jsonify(str(id.inserted_id))


@app.route('/patients', methods= ['GET'])
@jwt_required()
def getPatients():
    current_user = get_jwt_identity()
    patients = []
    for pat in db_patient.find():
        patients.append({
            "_id": str(ObjectId(pat['_id'])),
            'name':str(pat["name"]),
            'dni':str(pat["dni"]),
            'email':str(pat["email"]),
            'phone':str(pat["phone"]),
            'age':str(pat["age"]),        
            'contact_name':str(pat["contact_name"]),        
            'contact_phone':str(pat["contact_phone"])        
        })
    return jsonify(patients)

@app.route('/patients/<id>', methods= ['GET'])
@jwt_required()
def getPatient(id):
    current_user = get_jwt_identity()
    patient=db_patient.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(patient['_id'])),
        'name':patient["name"],
        'dni':patient["dni"],
        'email':patient["email"],
        'phone':patient["phone"],
        'age':patient["age"],
        'contact_name':patient["contact_name"],
        'contact_phone':patient["contact_phone"],
    })

@app.route('/patients/<id>', methods= ['DELETE'])
@jwt_required()
def deletePatient(id):
    current_user = get_jwt_identity()
    patient = db_patient.delete_one({"_id":ObjectId(id)})
    return jsonify({
        "msg": "patient deleted",
        "patient": id
        })

@app.route('/patients/<id>', methods= ['PUT'])
@jwt_required()
def updatePatient(id):
    current_user = get_jwt_identity()
    db_patient.update_one({"_id":ObjectId(id)},{'$set':{
        'name':request.json["name"],
        'dni':request.json["dni"],
        'email':request.json["email"],
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
@app.route('/observations', methods=['POST'])
@jwt_required()
def createObservation():
    current_user = get_jwt_identity()
    try:
        #aca quizás se necesite cambiar a string(patient_id) en la fila 205
        
        ultima_observation = db_observation.find_one(sort=[("_id", -1)])
        ultimo_correlativo = ultima_observation['_id'] if ultima_observation else 0


        patient_id=request.json['patient_id']
        doctor_id=request.json['doctor_id']
        media_id=request.json['media_id']
        print('#############################')
        print('#############################')
        print('#############################')
        
        print(patient_id)
        print(doctor_id)
        print(media_id)
        print('#############################')
        print('#############################')
        print('#############################')

        # Obtener el nombre del paciente,el doctor y el nombre del archivo por su ID
        patient = db_patient.find_one({'_id': ObjectId(patient_id)})
        doctor = db_user.find_one({'_id':  ObjectId(doctor_id)})
        media = db_media.find_one({'_id': ObjectId(media_id)})
        
        print('#############################')
        print('#############################')
        print(patient)
        print(doctor)
        print(media)   
        print('#############################')
        print('#############################')

        id = db_observation.insert_one({
            '_id': ultimo_correlativo+1,
            #'nro_observation': str('Nro_'+ultimo_correlativo),
            'patient_name':patient['name'], 
            'doctor_name':doctor['name'],  
            'file_name':media['file_name']  
        })
        return jsonify(str(id.inserted_id))
    except Exception as e:
        return e

@app.route('/observations', methods= ['GET'])
@jwt_required()
def getObservations():
    current_user = get_jwt_identity()
    observations = []
    for med in db_observation.find():
        observations.append({
            "_id": int((med['_id'])),
            'patient_name':str(med['patient_name']),
            'doctor_name':str(med['doctor_name']),      
            'file_name':str(med['file_name'])      
        })
    return jsonify(observations)

@app.route('/observations/<id>', methods= ['GET'])
@jwt_required()
def getObservation(id):
    current_user = get_jwt_identity()
    observation=db_observation.find_one({'_id':int(id)})
    return jsonify({
        "_id": str(str(observation['_id'])),
        'patient_name':observation["patient_name"],
        'doctor_name':observation["doctor_name"],           
        'file_name':observation['file_name']     
    })

@app.route('/observations/<id>', methods= ['DELETE'])
@jwt_required()
def deleteObservation(id):
    current_user = get_jwt_identity()
    observation = db_observation.delete_one({"_id":int(id)})
    return jsonify({
        "msg": "observation deleted",
        "observation": id
        })

@app.route('/observations/<id>', methods= ['PUT'])
@jwt_required()
def updateObservation(id):
    current_user = get_jwt_identity()
    #aca quizás se necesite cambiar a string(patient_id) en la fila 205
    patient_id=request.json['patient_id']
    doctor_id=request.json['doctor_id']
    media_id=request.json['media_id']
    
    #Obtener el nombre del paciente,el doctor y el nombre del archivo por su ID
    patient = db_patient.find_one({'_id': ObjectId(patient_id)})
    doctor = db_user.find_one({'_id':  ObjectId(doctor_id)})
    media = db_media.find_one({'_id': ObjectId(media_id)})
    
    db_observation.update_one({"_id":int(id)},{'$set':{
        'patient_name':patient['name'],
        'doctor_name':doctor['name'],  
        'file_name':media['file_name']  
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
@jwt_required()
def createMedia():
    current_user = get_jwt_identity()
    #try:    
    eeg_file=request.files["file"]

    if "medias" in mongo.db.list_collection_names():
        if db_media.find_one({'file_name': eeg_file.filename}):
            return "Archivo ya existe"

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

              for t in tqdm(range(int(np.divide(raw.n_times,256))), desc="Procesando Predicción"):
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
@jwt_required()
def getMedias():
    current_user = get_jwt_identity()
    medias = []
    for med in db_media.find():
        medias.append({
            "_id": str(ObjectId(med['_id'])),
            'file_name':str(med["file_name"]),
            'time':str(med["time"])      
        })
    return jsonify(medias)

@app.route('/medias/<id>', methods= ['GET'])
@jwt_required()
def getMedia(id):
    media=db_media.find_one({'_id':ObjectId(id)})
    return jsonify({
        "_id": str(ObjectId(media['_id'])),
        'file_name':media["file_name"],
        'time':media["time"]           
    })

@app.route('/medias/<id>', methods= ['DELETE'])
@jwt_required()
def deleteMedia(id):
    current_user = get_jwt_identity()
    media = db_media.find_one({'_id':ObjectId(id)})
    file = mongo.db.fs.files.find_one({'filename': media['file_name']})
    _ = db_media.delete_one({"_id":ObjectId(id)})
    _ = mongo.db.fs.files.delete_one({"_id":ObjectId(file['_id'])})
    _ = mongo.db.fs.chunks.delete_many({"files_id":ObjectId(file['_id'])})
    # for chunk in chunks:
        # _ = mongo.db.fs.chunks.delete_one({"_id":ObjectId(chunk['_id'])})
    return jsonify({
        "msg": "media deleted",
        "media": id
        })

###################################
###### Registrar Resultados #######
###################################

#Definición de colección de results

db_result = mongo.db.results

@app.route('/results', methods=['POST'])
@jwt_required()
def createResult():
    try:
        ultima_result = db_result.find_one(sort=[("_id", -1)])
        ultimo_correlativo = ultima_result['_id'] if ultima_result else 0
        current_user = get_jwt_identity()

        #aca quizás se necesite cambiar a string(patient_id) en la fila 205
        observation_id=request.json['observation_id']
        print("########################")
        print("########################")
        print(observation_id)
        observation = db_observation.find_one({'_id':int(observation_id)})
        print(observation)
        media = db_media.find_one({'file_name':observation['file_name']})
        print("########################")
        print("########################")
        print(media)
        print("########################")
        print("########################")
        print(observation['patient_name'])
        print("########################")
        print("########################")
        print(observation['doctor_name'])
        print("########################")
        print("########################")
        print(media['time'])
        print("########################")
        print("########################")
        print(ultimo_correlativo)
        id = db_result.insert_one({
            '_id': int(ultimo_correlativo)+1,
            'patient_name':observation['patient_name'], 
            'doctor_name':observation['doctor_name'],  
            'ictal_time':media['time']  
        })
        return jsonify(str(id.inserted_id))
    except Exception as e:
        return e

@app.route('/results', methods= ['GET'])
@jwt_required()
def getResults():
    current_user = get_jwt_identity()
    results = []
    for res in db_result.find():
        results.append({
            "_id": int(res['_id']),
            'patient_name':str(res['patient_name']),
            'doctor_name':str(res['doctor_name']),      
            'ictal_time':str(res['ictal_time'])      
        })
    return jsonify(results)

@app.route('/results/<id>', methods= ['GET'])
@jwt_required()
def getResult(id):
    current_user = get_jwt_identity()
    result=db_result.find_one({'_id':int(id)})
    return jsonify({
        "_id": (int(result['_id'])),
        'patient_name':result["patient_name"],
        'doctor_name':result["doctor_name"],           
        'ictal_time':result['ictal_time']     
    })

@app.route('/results/<id>', methods= ['DELETE'])
@jwt_required()
def deleteResult(id):
    current_user = get_jwt_identity()
    result = db_result.delete_one({"_id":int(id)})
    return jsonify({
        "msg": "result deleted",
        "result": id
        })

@app.route('/results/<id>', methods= ['PUT'])
@jwt_required()
def updateResult(id):
    current_user = get_jwt_identity()
    #aca quizás se necesite cambiar a string(patient_id) en la fila 205
    observation_id=request.json['observation_id']
    print("########################")
    print(observation_id)
    observation = db_observation.find_one({'_id':int(observation_id)})
    print(observation)
    media = db_media.find_one({'file_name':observation['file_name']})
    
    
    db_result.update_one({"_id":int(id)},{'$set':{
        'ictal_time':media['time']  
    }})
    return jsonify({
        "msg": "Result updated",
        "result": id
        })



# Del archivo que hemos alamcenado obtenemos el array, 
# falta configurar para que devuelva en un json los 23 canales 
@app.route('/files/<id>', methods= ['GET'])
@jwt_required()
def getFile(id):
    current_user = get_jwt_identity()

    media=db_media.find_one({'_id':ObjectId(id)})

    # Obtén el eeg_file que contiene la imagen por su identificador
    eeg_file = mongo.db.fs.files.find_one({'filename': (media['file_name'])})

    #Cargar modelo

    if eeg_file:
        # Recupera los fragmentos de la imagen desde GridFS
        chunks = mongo.db.fs.chunks.find({'files_id': ObjectId(eeg_file['_id'])}).sort('n')
        
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
            
        data=raw.get_data()
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
            'data':data         
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

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000 ,debug=True)
