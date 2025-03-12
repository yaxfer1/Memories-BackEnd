from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from bcrypt import hashpw, checkpw, gensalt
import embeder
import json
import multiscraping
import jwt
import os
import dbManagement
import generateParagraph
app = Flask(__name__)
CORS(app)
JWT_SECRET = 'secret'
from introduccion import research_graph

@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    print("ai_chat")
    try:
        # Obtener datos del JSON enviado en la solicitud
        data = request.get_json()

        # Extraer "id" y "message" asegurándonos de que existen
        chat_id = data.get("id")

        message = data.get("message")
        jwt_token = data.get('jwt')
        print(chat_id, message, jwt_token)
        try:
            payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
            username = payload['iss']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        user_id = dbManagement.obtain_id_username(username)
        print(dbManagement.add_new_message(message, chat_id, user_id))
        # Validar que ambos datos sean correctos
        if chat_id is None or message is None:
            return jsonify({"error": "Missing 'id' or 'message'"}), 400
        print("response")
        # Llamar a la función que procesa el chat
        response = research_graph(str(message))
        print(response)
        dbManagement.add_new_aimessage(response, chat_id)
        return jsonify(response)

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@app.route('/api/scrap_url', methods=['POST'])
def scrap_url():
    data = request.get_json()
    url = data.get("url")
    memory_id = data.get("memory_id")
    # Decodificar los bytes
    # Remover comillas adicionales
    normalized_text = url.strip('"')

    text = multiscraping.scrape_url(normalized_text)
    processor = embeder.URLProcessor()
    embeder.URLProcessor.process_text(processor, text, url)
    url_id = dbManagement.add_new_url(url, memory_id)
    return jsonify({
        "message": "URL Procesada",
        "url" : normalized_text,
        "texto" : text,
    }), 200

@app.route('/api/upload_files', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({"error": "No files part in the request"}), 400

    uploaded_files = request.files.getlist("files")
    file_names = []
    files = []
    discarded_files = []
    processor = embeder.PDFProcessor(batch_size=10)

    memory_id = request.form.get("memory_id")
    print(memory_id)
    for file in uploaded_files:
        if file.filename == '':
            return jsonify({"error": "One of the files has no name"}), 400

        file_path = f"uploads/{file.filename}"

        if os.path.exists(file_path):
            # Si el archivo ya existe, se descarta
            discarded_files.append(file.filename)
            print(f"El archivo {file_path}, ya existe en la BD")

        else:
            print(f"Guardando el archivo: {file_path} ")
            file.save(file_path)
            file_names.append(file.filename)
            files.append(file)

        print("sigue el for ------------------ debug")

    if files:
        text = embeder.PDFProcessor.process_pdfs_and_insert(processor, files, memory_id)
        print(f"Texto extraído de los archivos:\n{text}")

    return jsonify({
        "message": "Archivos procesados",
        "files_uploaded": file_names,
        "files_discarded": discarded_files
    }), 200



# Función para generar el token JWT
def generate_jwt(username):
    payload = {
        'iss': username,
        'exp': datetime.utcnow() + timedelta(hours=1)  # Token expira en 1 hora
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Obtain hash from database
    user_data = dbManagement.obtain_username_password(username)
    stored_hash_with_salt = user_data.get("password_hash")

    # Verify password
    if stored_hash_with_salt and checkpw(password.encode('utf-8'), stored_hash_with_salt.encode('utf-8')):
        token = generate_jwt(username)
        return jsonify({'jwt': token}), 201
    else:
        return jsonify({'error': 'Invalid Credentials'}), 403

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Credenciales incompletas'}), 400

    # Hashear la contraseña antes de almacenarla en la base de datos
    hashed_password = hashpw(password.encode('utf-8'), gensalt())

    return dbManagement.register_normal(username, hashed_password)

@app.route('/api/add_chat', methods=['POST'])
def add_chat():
    data = request.json
    print(data)
    jwt_token = data.get('jwt')
    chat_name = data.get('chat_name')

    # Verificar y parsear el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    user_id = dbManagement.obtain_id_username(username)
    if user_id:

        return dbManagement.add_chat_db(chat_name, user_id)
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/get_chats', methods=['POST'])
def get_chats():
    data = request.json
    print("data: ")
    print(data)
    jwt_token = data.get('jwt')

    # Verificar y parsear el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    #user_id = dbManagement.obtain_id_username(username)
    if username:
        dbreturn = dbManagement.obtain_chats_from_user(username)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/get_businesses', methods=['POST'])
def get_businesses():
    data = request.json
    print("data: ")
    print(data)
    jwt_token = data.get('jwt')

    # Verificar y parsear el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    #user_id = dbManagement.obtain_id_username(username)
    if username:
        dbreturn = dbManagement.obtain_businesses_from_user(username)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/api/get_memories_from_business', methods=['POST'])
def get_memories_from_business():
    data = request.json
    print("data: ")
    print(data)
    jwt_token = data.get('jwt')
    business_id = data.get('business_id_string')
    # Verificar y parsear el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    if username:
        dbreturn = dbManagement.obtain_memories_from_business(business_id)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Business not found'}), 404

@app.route('/api/get_chat_messages', methods=['POST'])
def get_chat_messages():
    data = request.json
    #user_id = dbManagement.obtain_id_username(username)
    if data:
        dbreturn = dbManagement.get_chat_messages(data)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Mala peticion'}), 404

@app.route('/api/rm_chat', methods=['POST'])
def rm_chat():
    data = request.json
    print(data)
    #user_id = dbManagement.obtain_id_username(username)
    if data:
        dbreturn = dbManagement.delete_chat(data)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Mala peticion'}), 404

@app.route('/api/rm_business', methods=['POST'])
def rm_business():
    data = request.json
    print(data)
    #user_id = dbManagement.obtain_id_username(username)
    if data:
        dbreturn = dbManagement.delete_business(data)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Mala peticion'}), 404

@app.route('/api/rm_memory', methods=['POST'])
def rm_memory():
    data = request.json
    print(data)
    #user_id = dbManagement.obtain_id_username(username)
    if data:
        dbreturn = dbManagement.delete_memory(data)
        print(dbreturn)
        return dbreturn
    else:
        return jsonify({'error': 'Mala peticion'}), 404

@app.route('/api/add_business', methods=['POST'])
def add_business():
    data = request.json
    print(data)
    jwt_token = data.get('jwt')
    business_name = data.get('business_name')

    # Verificar y parsear el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    user_id = dbManagement.obtain_id_username(username)
    if user_id:

        return dbManagement.add_new_business(business_name, user_id)
    else:
        return jsonify({'error': 'Empresa no introducida correctamente'}), 404

@app.route('/api/add_memory', methods=['POST'])
def add_memory():
    data = request.json
    print(data)
    jwt_token = data.get('jwt')
    memory_name = data.get('memory_name')
    business_id = data.get('id_string')

    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Toke_ inválido'}), 401

    user_id = dbManagement.obtain_id_username(username)
    if user_id and business_id:
        return dbManagement.add_new_memory(memory_name, user_id, business_id)
    else:
        return jsonify({'error': 'Memoria no introducida correctamente'}), 404

@app.route('/api/retrieve_from_memory', methods=['POST'])
def retrieve_from_memory():
    data = request.json
    print(data)
    memory_id = data.get('memostr')

    # Verificar que se ha proporcionado un memory_id
    if not memory_id:
        return jsonify({'error': 'memory_id es requerido'}), 400

    # Llamar al método get_reports_from_db para obtener los reportes
    try:
        if memory_id:
            return dbManagement.retrieve_from_memory(memory_id)
        else:
            return jsonify({'error': 'Memoria no introducida correctamente'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_fromreport', methods=['POST'])
def get_fromreport():
    data = request.json
    print(data)
    report_id = data.get('reportstr')

    # Verificar que se ha proporcionado un memory_id
    if not report_id:
        return jsonify({'error': 'report_id es requerido'}), 400

    # Llamar al método get_reports_from_db para obtener los reportes
    try:
        if report_id:
            return dbManagement.retrieve_from_memory(report_id)
        else:
            return jsonify({'error': 'Memoria no introducida correctamente'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500



import tool_context

@app.route('/api/agent_actions', methods=['POST'])
def agent_actions():
    data = request.json
    print("agent_actions")
    print(data)
    if not data:
        return jsonify({'error': 'Mala petición'}), 404

    # Se espera que el front envíe el jwt y la query
    jwt_token = data.get('jwt')
    query = data.get('query')
    reportId = data.get('repIdstr')

    if not jwt_token or not query:
        return jsonify({'error': 'Falta jwt o query'}), 400

    # Validar el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        # Puedes extraer el usuario si lo necesitas, por ejemplo: username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    try:
        # Llamamos al método que ejecuta el grafo y devuelve el JSON con el historial de tools
        result_json = tool_context.research_graph(query)
        
        # Guardamos los resultados en la base de datos
        db_response, status_code = dbManagement.add_tools_batch_to_report(result_json, reportId)
        
        if status_code != 201:
            # Si hubo un error al guardar en la base de datos, devolvemos el error
            return db_response, status_code
            
        # Si todo está bien, devolvemos los resultados originales
        return json.dumps(result_json, indent=2), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_paragraph', methods=['POST'])
def generate_paragraph():
    data = request.json
    print("generate_paragraph")
    print(data)
    if not data:
        return jsonify({'error': 'Mala petición'}), 404

    # Se espera que el front envíe el jwt y la query
    jwt_token = data.get('jwt')
    query = data.get('query')

    if not jwt_token or not query:
        return jsonify({'error': 'Falta jwt o query'}), 400

    # Validar el token JWT
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        # Puedes extraer el usuario si lo necesitas, por ejemplo: username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    try:
        result_json = jsonify(generateParagraph.generateParagraph(input=query))
        print(result_json)
        return result_json, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add_report_to_memory', methods=['POST'])
def add_report_to_memory():
    data = request.json
    print(data)

    # Obtener el token JWT para verificar el usuario
    jwt_token = data.get('jwt')
    memory_id = data.get('memory_ids')
    report_name = data.get('report_name')

    # Verificar que el JWT es válido
    try:
        payload = jwt.decode(jwt_token, JWT_SECRET, algorithms=['HS256'])
        username = payload['iss']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    user_id = dbManagement.obtain_id_username(username)

    if user_id and memory_id:
        try:
            # Llamada al método add_report para agregar el reporte a la base de datos
            result = dbManagement.add_report_to_memory(report_name, memory_id)
            print(result)
            return jsonify(result), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({'error': 'Usuario o memoria no encontrados'}), 404

@app.route('/api/delete_report', methods=['DELETE'])
def delete_report():
    data = request.json
    report_id = data.get('report_id')  # Obtener el report_id desde el cuerpo de la solicitud

    # Verificar que se ha proporcionado un report_id
    if not report_id:
        return jsonify({'error': 'report_id es requerido'}), 400

    # Llamar al método delete_report_from_db para eliminar el reporte
    try:
        result = dbManagement.delete_report(report_id)
        if result:
            return jsonify({'message': 'Reporte eliminado correctamente'}), 200
        else:
            return jsonify({'message': 'No se encontró el reporte para eliminar'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_tool_to_report', methods=['POST'])
def add_tool_to_report_route():
    data = request.json
    tool_name = data.get('tool_name')
    report_id = data.get('report_id')
    result = data.get('result')
    query_data = data.get('query_data')

    if not all([tool_name, report_id, result, query_data]):
        return jsonify({'error': 'Faltan parámetros necesarios'}), 400

    try:
        response = dbManagement.add_tool_to_report(tool_name, report_id, result, query_data)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_tool_from_report', methods=['DELETE'])
def delete_tool_from_report_route():
    data = request.json
    tool_result_id = data.get('tool_result_id')

    if not tool_result_id:
        return jsonify({'error': 'tool_result_id es requerido'}), 400

    try:
        response = dbManagement.delete_tool_from_report(tool_result_id)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_tool_result', methods=['PUT'])
def update_tool_result_route():
    data = request.json
    tool_result_id = data.get('tool_result_id')
    new_tool_name = data.get('new_tool_name')
    new_result = data.get('new_result')
    new_query_data = data.get('new_query_data')

    if not all([tool_result_id, new_tool_name, new_result, new_query_data]):
        return jsonify({'error': 'Faltan parámetros necesarios'}), 400

    try:
        response = dbManagement.update_tool_result(tool_result_id, new_tool_name, new_result, new_query_data)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/obtain_tools_from_report', methods=['GET'])
def obtain_tools_from_report_route():
    report_id = request.args.get('report_id')  # Obtener el report_id desde los parámetros de la URL

    if not report_id:
        return jsonify({'error': 'report_id es requerido'}), 400

    try:
        response = dbManagement.obtain_tools_from_report(report_id)
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)