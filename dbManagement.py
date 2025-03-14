import json
from datetime import datetime, timedelta
from bcrypt import hashpw, checkpw, gensalt
import jwt
from flask import jsonify
import mysql.connector

# Configuración de la conexión a la base de datos
config = {
    'user': 'root',
    'password': 'Hefestion7',
    'host': 'localhost',
    'database': 'tennews'
}

def obtain_id_username(username):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return user_id

def obtain_id_business(business_name):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id FROM businesses WHERE name = %s"
    cursor.execute(query, (business_name,))
    user_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return user_id

# Método para obtener elementos de un usuario por su ID de usuario
def obtain_elements_from_user(user):
    user_id = obtain_id_username(user)
    if user_id is None:
        return []  # O maneja este caso de alguna otra manera

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT name, type FROM elements WHERE owner_id = %s"
    cursor.execute(query, (user_id['id'],))  # Pasa solo el valor del ID como parámetro
    results = cursor.fetchall()
    elements = [row[0] for row in results]
    types = [row[1] for row in results]
    print(types)
    cursor.close()
    connection.close()

    return elements, types

def obtain_username_password(username):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT password_hash FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user_password = cursor.fetchone()
    print(user_password)
    cursor.close()
    connection.close()
    print(user_password)
    return user_password

def register_normal(user, hashed_password):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    # Insertar el nuevo usuario y su contraseña hasheada en la base de datos
    query = "INSERT INTO users (username, password_hash, permission) VALUES (%s, %s, 'normal')"
    try:
        cursor.execute(query, (user, hashed_password))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Usuario registrado correctamente'}), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al registrar usuario: {err}'}), 500


def add_element_db(element, type, user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    print(element)
    print(type)
    print(user_id)
    ids = user_id.__getitem__("id")
    print(ids)
    query = "INSERT INTO elements (name, type, owner_id) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (element, type, ids))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(element, type), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting element: {err}'}), 500

def obtain_chats_from_user(user):
    user_id = obtain_id_username(user)
    if user_id is None:
        return []  # O maneja este caso de alguna otra manera

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT id, namestr FROM chats WHERE owner_id = %s"
    cursor.execute(query, (user_id['id'],))  # Pasa solo el valor del ID como parámetro
    results = cursor.fetchall()
    names = [row[1] for row in results]
    #created_at = [row[1] for row in results]
    print(f"names: {names}")
    id= [row[0] for row in results]
    print(f"ids: {id}")
    #print(f"created_at: {created_at}")
    cursor.close()
    connection.close()

    return jsonify(id, names), 201

def obtain_businesses_from_user(user):
    user_id = obtain_id_username(user)
    if user_id is None:
        return []  # O maneja este caso de alguna otra manera

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT id, name FROM businesses WHERE owner_id = %s"
    cursor.execute(query, (user_id['id'],))  # Pasa solo el valor del ID como parámetro
    results = cursor.fetchall()
    names = [row[1] for row in results]
    #created_at = [row[1] for row in results]
    print(f"names: {names}")
    id= [row[0] for row in results]
    print(f"ids: {id}")
    #print(f"created_at: {created_at}")
    cursor.close()
    connection.close()

    return jsonify(id, names), 201

def obtain_memories_from_business(business_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT id, name FROM memories WHERE business_id = %s"
    cursor.execute(query, (business_id,))  # Pasa solo el valor del ID como parámetro
    results = cursor.fetchall()
    names = [row[1] for row in results]
    #created_at = [row[1] for row in results]
    print(f"names: {names}")
    id= [row[0] for row in results]
    print(f"ids: {id}")
    #print(f"created_at: {created_at}")
    cursor.close()
    connection.close()

    return jsonify(id, names), 201


def add_chat_db(chat_name, user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    print(chat_name)
    print(user_id)
    ids = user_id.__getitem__("id")
    print(ids)
    created_at = datetime.now()
    print(created_at)
    query = "INSERT INTO chats (namestr, created_at, owner_id) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (chat_name, created_at, ids))
        chat_id = cursor.lastrowid
        print(f"New chat ID: {chat_id}")
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(chat_name, created_at, chat_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting chat: {err}'}), 500

def add_new_message(message, chat_id, user_id):
    print("add_new_message")

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("created at:", created_at)
    print("message:", message)
    print("chat_id:", chat_id)
    print("user_id:", user_id)
    ids = user_id.__getitem__("id")
    query = """
        INSERT INTO messages (chat_id, content, user_id) 
        VALUES (%s, %s, %s)
    """
    try:
        print("Ejecutando consulta SQL...")
        cursor.execute(query, (chat_id, message, ids))
        connection.commit()
        print(f"Mensaje insertado con ID: {cursor.lastrowid}")  # ✅ Verificar si se insertó

        cursor.close()
        connection.close()
        return jsonify("hola"), 201
    except mysql.connector.Error as err:
        print("Error:", err)
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al insertar el mensaje: {err}'}), 500

def add_new_aimessage(message, chat_id):
    print("add_new_aimessage")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    userid = 42

    created_at = datetime.now()
    print(created_at)
    query = "INSERT INTO messages (chat_id, content, user_id) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (chat_id, message, userid))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting new message: {err}'}), 500

def delete_chat(chat_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    ids = chat_id.__getitem__("chat_id")
    print("id:")
    print(ids)
    print("noid")
    query = """
        UPDATE chats 
        SET prev_uid = (SELECT owner_id FROM (SELECT * FROM chats) AS temp WHERE id = %s), 
            owner_id = 89 
        WHERE id = %s
    """
    try:
        cursor.execute(query, (int(ids),int(ids)))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify("Chat Eliminado"), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error at retrieving messages from chat: {err}'}), 500

def delete_business(business_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    ids = business_id.__getitem__("business_id")
    print("id:")
    print(ids)
    print("noid")
    query = """
        UPDATE businesses 
        SET prev_uid = (SELECT owner_id FROM (SELECT * FROM businesses) AS temp WHERE id = %s), 
            owner_id = 89 
        WHERE id = %s
    """
    try:
        cursor.execute(query, (int(ids),int(ids)))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify("Chat Eliminado"), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error at retrieving messages from chat: {err}'}), 500

def delete_memory(memory_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    ids = memory_id.__getitem__("memory_id")
    print("id:")
    print(ids)
    print("noid")
    query = """
        UPDATE memories
        SET prev_uid = (SELECT business_id FROM (SELECT * FROM memories) AS temp WHERE id = %s), 
            business_id = 89 
        WHERE id = %s
    """
    try:
        cursor.execute(query, (int(ids),int(ids)))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify("Chat Eliminado"), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error at retrieving messages from chat: {err}'}), 500


def rm_element_db(element, type, user_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    print(element)
    print(type)
    print(user_id)
    ids = user_id.__getitem__("id")
    print(ids)
    query = "DELETE FROM elements WHERE name = %s AND type = %s AND owner_id = %s"
    try:
        cursor.execute(query, (element, type, ids))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(element, type), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting element: {err}'}), 500


def get_chat_messages(chat_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    ids = chat_id.__getitem__("chat_id")
    print(ids)
    query = "SELECT content, user_id FROM messages WHERE chat_id = %s ORDER BY time_set ASC"
    try:
        print("entrando al cursor")
        cursor.execute(query, (int(ids),))
        print("saliendo del cursor")
        results = cursor.fetchall()
        print(results)
        content = [row["content"] for row in results]
        user_id = [row["user_id"] for row in results]
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(content, user_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error at retrieving messages from chat: {err}'}), 500


def add_new_business(name, user_id):
    print("add_new_business")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    ids = user_id.__getitem__("id")

    created_at = datetime.now()
    print(created_at)
    query = "INSERT INTO businesses (name, owner_id) VALUES (%s, %s)"
    try:
        cursor.execute(query, (name, ids))
        business_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(business_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting new message: {err}'}), 500

def add_new_memory(name, user_id, business_id):
    print("add_new_report")
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    ids = user_id.__getitem__("id")

    created_at = datetime.now()
    print(created_at)
    query = "INSERT INTO memories (name, owner_id, business_id) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (name, ids, business_id))
        memory_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(memory_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting new memory: {err}'}), 500

def add_new_url(url, memory_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO url (urlstr, memory_id) VALUES (%s, %s)"
    try:
        cursor.execute(query, (url, memory_id))
        url_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(url_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting new url: {err}'}), 500

def add_new_pdf(pdf_name, text,memory_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO pdf (filename, content ,memory_id) VALUES (%s, %s, %s)"
    try:
        cursor.execute(query, (pdf_name, text, memory_id))
        pdf_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify(pdf_id), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error at inserting new pdf: {err}'}), 500

def retrieve_from_memory(memory_id):
    reports = obtain_reports_from_memory(memory_id)
    #tools = obtain_tools_from_report()
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT urlstr FROM url WHERE memory_id = %s", (memory_id,))
        urls = [row["urlstr"] for row in cursor.fetchall()]

        cursor.execute("SELECT filename FROM pdf WHERE memory_id = %s", (memory_id,))
        filenames = [row["filename"] for row in cursor.fetchall()]

        cursor.close()
        connection.close()

        # 🔹 Retornar ambas listas en un JSON
        print({"urls": urls, "filenames": filenames, "reports": reports})
        return jsonify({"urls": urls, "filenames": filenames, "reports": reports}), 200

    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error retrieving data: {err}'}), 500


def obtain_reports_from_memory(memory_id):
    """
    Obtiene los reportes asociados a una memoria específica.
    """
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, TEXT1, TEXT2, RESULT, report_name FROM REPORT WHERE memories_id = %s"
    try:
        print("executing reports cursor")
        cursor.execute(query, (memory_id,))
        results = cursor.fetchall()
        print("get reports as dict")
        reports = [{
            'id': row['id'],
            'name': row['report_name'],
            'TEXT1': row['TEXT1'],
            'TEXT2': row['TEXT2'],
            'RESULT': row['RESULT']
        } for row in results]
        cursor.close()
        connection.close()
        return reports
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al obtener los reportes: {err}'}), 500

def obtain_report_by_id(report_id):
    """
    Obtiene un reporte específico por su ID.
    """
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT id, TEXT1, TEXT2, RESULT, queries FROM REPORT WHERE id = %s"
    try:
        cursor.execute(query, (report_id,))
        result = cursor.fetchone()
        if result:
            report = {
                'id': result['id'],
                'TEXT1': result['TEXT1'],
                'TEXT2': result['TEXT2'],
                'RESULT': result['RESULT'],
                'queries': result['queries']
            }
            cursor.close()
            connection.close()
            return report
        else:
            cursor.close()
            connection.close()
            return jsonify({'message': 'Reporte no encontrado'}), 404
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al obtener el reporte: {err}'}), 500

def update_report_text(report_id, text1, text2):
    """
    Actualiza un reporte específico por su ID.
    """
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = """
        UPDATE REPORT
        SET TEXT1 = %s, TEXT2 = %s
        WHERE id = %s
    """
    try:
        cursor.execute(query, (
            text1,
            text2,
            report_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Reporte actualizado correctamente'}), 200
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al actualizar el reporte: {err}'}), 500


def update_report_result(report_id,result):
    """
    Actualiza un reporte específico por su ID.
    """
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = """
        UPDATE REPORT
        SET RESULT = %s
        WHERE id = %s
    """
    try:
        cursor.execute(query, (
            result,
            report_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Reporte actualizado correctamente'}), 200
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al actualizar el reporte: {err}'}), 500




def update_report(report_id, text1, text2, result):
    """
    Actualiza un reporte específico por su ID.
    """
    print("update_report" + text1 + text2 + result)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = """
        UPDATE REPORT
        SET TEXT1 = %s, TEXT2 = %s, RESULT = %s
        WHERE id = %s
    """
    try:
        cursor.execute(query, (
            text1,
            text2,
            result,
            report_id
        ))
        connection.commit()
        cursor.close()
        connection.close()
        print("reporte actualizado correctamente")
        return jsonify({'message': 'Reporte actualizado correctamente'}), 200
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(f"Error de MySQL: {err}")
        return jsonify({'error': f'Error al actualizar el reporte: {err}'}), 500


def delete_report(report_id):
    """
    Elimina un reporte específico por su ID.
    """
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = "DELETE FROM REPORT WHERE id = %s"
    try:
        cursor.execute(query, (report_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({'message': 'Reporte eliminado correctamente'}), 200
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error al eliminar el reporte: {err}'}), 500


def add_tool_to_report(tool_name, report_id, result, query_data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)

    query = "INSERT INTO tool_result (tool, result, query_data, report_id) VALUES (%s, %s, %s, %s)"

    try:
        cursor.execute(query, (tool_name, result, json.dumps(query_data), report_id))
        tool_result_id = cursor.lastrowid
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify({"tool_result_id": tool_result_id}), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        print(err)
        return jsonify({'error': f'Error inserting tool result: {err}'}), 500


def delete_tool_from_report(tool_result_id):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "DELETE FROM tool_result WHERE id = %s"

    try:
        cursor.execute(query, (tool_result_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify("Tool result deleted"), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error deleting tool result: {err}'}), 500

def update_tool_result(tool_result_id, new_tool_name, new_result, new_query_data):
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor(dictionary=True)
    query = "UPDATE tool_result SET tool = %s, result = %s, query_data = %s WHERE id = %s"

    try:
        cursor.execute(query, (new_tool_name, new_result, json.dumps(new_query_data), tool_result_id))
        connection.commit()
        cursor.close()
        connection.close()
        return jsonify("Tool result updated"), 201
    except mysql.connector.Error as err:
        cursor.close()
        connection.close()
        return jsonify({'error': f'Error updating tool result: {err}'}), 500


def obtain_tools_from_report(report_id):
    report = obtain_report_by_id(report_id)
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    query = "SELECT id, tool, query_data, result FROM tool_result WHERE report_id = %s"
    cursor.execute(query, (report_id,))
    results = cursor.fetchall()
    result_list = []
    for row in results:
        result_list.append({
            "tool": row[1],
            "query": row[2],
            "result": row[3]
        })
    names = [row[1] for row in results]
    ids = [row[0] for row in results]
    querys_data = [row[2] for row in results]
    results = [row[3] for row in results]
    cursor.close()
    connection.close()

    return report, result_list


def add_tools_batch_to_report(tools, report_id):
    # Validar que tools sea una lista
    print("report_id: " + report_id)
    if not isinstance(tools, list):
        return jsonify({"error": "Se esperaba una lista de herramientas"}), 400
    
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()
    
    query = "INSERT INTO tool_result (tool, result, query_data, report_id) VALUES (%s, %s, %s, %s)"
    
    # Preparar los datos para executemany
    values = []
    for tool in tools:
        # Asegurarse de que tool es un diccionario
        if not isinstance(tool, dict):
            continue
            
        # Obtener valores con manejo de errores
        tool_name = tool.get('tool', '')
        tool_result = tool.get('result', '')
        
        # Manejar la consulta (query) que puede ser un string o un diccionario
        query_data = tool.get('query', {})
        if isinstance(query_data, dict):
            query_data = json.dumps(query_data)
        
        values.append((tool_name, tool_result, query_data, report_id))
    
    try:
        if values:  # Solo ejecutar si hay valores para insertar
            cursor.executemany(query, values)
            connection.commit()
            inserted_rows = cursor.rowcount
            return jsonify({"message": f"Se insertaron {inserted_rows} herramientas"}), 201
        else:
            return jsonify({"message": "No se insertaron herramientas, lista vacía o inválida"}), 200
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()
