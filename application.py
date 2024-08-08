from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from math import ceil

app = Flask(__name__)

# Conexão com o MongoDB
connection_string = "mongodb+srv://brennocauet:8TR1u8o751kib82b@teste.ioqwvws.mongodb.net/?retryWrites=true&w=majority&appName=Teste"
client = MongoClient(connection_string)
db_connection = client.get_database("MeuBanco")
collection = db_connection.get_collection("ApiTeste")

def calcular_idade(data_nascimento):
    today = datetime.today()
    born = datetime.strptime(data_nascimento, '%Y-%m-%d')
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

@app.route('/cliente', methods=['GET'])
def obter_clientes():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    total_clients = collection.count_documents({})
    total_pages = ceil(total_clients / per_page)
    
    clientes = list(collection.find().skip((page - 1) * per_page).limit(per_page))
    for cliente in clientes:
        cliente['_id'] = str(cliente['_id'])
    
    return jsonify({
        'clientes': clientes,
        'page': page,
        'per_page': per_page,
        'total_clients': total_clients,
        'total_pages': total_pages
    })

@app.route('/cliente/<string:id>', methods=['GET'])
def obter_cliente_por_id(id):
    cliente = collection.find_one({'_id': ObjectId(id)})
    if cliente:
        cliente['_id'] = str(cliente['_id'])
        return jsonify(cliente)
    return jsonify({'mensagem': 'Cliente não encontrado'}), 404

@app.route('/cliente/cpf/<string:cpf>', methods=['GET'])
def obter_cliente_por_cpf(cpf):
    cliente = collection.find_one({'cpf': cpf})
    if cliente:
        cliente['_id'] = str(cliente['_id'])
        return jsonify(cliente)
    return jsonify({'mensagem': 'Cliente não encontrado'}), 404

@app.route('/cliente', methods=['POST'])
def adicionar_cliente():
    novo_cliente = request.get_json()
    
    if not all(key in novo_cliente for key in ('nome', 'endereco', 'cpf', 'data_nascimento')):
        return jsonify({'mensagem': 'Campos obrigatórios: nome, endereco, cpf, data_nascimento'}), 400
    
    novo_cliente['idade'] = calcular_idade(novo_cliente['data_nascimento'])
    
    result = collection.insert_one(novo_cliente)
    novo_cliente['_id'] = str(result.inserted_id)
    return jsonify(novo_cliente), 201

@app.route('/cliente/<string:id>', methods=['PUT'])
def editar_cliente_id(id):
    cliente_alterado = request.get_json()
    
    if 'data_nascimento' in cliente_alterado:
        cliente_alterado['idade'] = calcular_idade(cliente_alterado['data_nascimento'])
    
    result = collection.update_one({'_id': ObjectId(id)}, {'$set': cliente_alterado})
    if result.matched_count:
        cliente_alterado['_id'] = id
        return jsonify(cliente_alterado)
    return jsonify({'mensagem': 'Cliente não encontrado'}), 404

@app.route('/cliente/<string:id>', methods=['DELETE'])
def deletar_cliente_id(id):
    result = collection.delete_one({'_id': ObjectId(id)})
    if result.deleted_count:
        return jsonify({'mensagem': 'Cliente deletado com sucesso'})
    return jsonify({'mensagem': 'Cliente não encontrado'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
