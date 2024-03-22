from flask import Flask, request, jsonify
from uuid import uuid4
from flask_cors import CORS
import os
import shutil
import schedule
import datetime
import json
import threading

app = Flask(__name__)
CORS(app)

# 定义存储数据的文件路径
DATA_FILE = 'materials.json'
# 这里存放历史数据
HISTORY_FOLDER = 'backup'
# 这里存放token
TOKENS_FILE = 'tokens.json'

try:
    with open(TOKENS_FILE, 'r') as file:
        tokens_data = json.load(file)
        valid_tokens = tokens_data['tokens']
except FileNotFoundError:
    valid_tokens = []

FRONT_ROOT = '../web_front/'
UPLOAD_FOLDER = 'uploads'  # 设置上传文件存储目录

if not os.path.exists(FRONT_ROOT + UPLOAD_FOLDER):
    os.makedirs(FRONT_ROOT + UPLOAD_FOLDER)
if not os.path.exists(HISTORY_FOLDER):
    os.makedirs(HISTORY_FOLDER)

materials = []

# 如果数据文件不存在，则创建一个空列表
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# 读取数据文件中的数据到内存中
with open(DATA_FILE, 'r') as f:
    materials = json.load(f)

# 备份数据文件
def backup_data():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    backup_filename = os.path.join(HISTORY_FOLDER, f'materials-{current_date}.json')
    shutil.copyfile(DATA_FILE, backup_filename)
    print("=========== Backuped Data ===========")

def print_time():
    current_date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    print(current_date)

# 每天固定时间执行备份操作
schedule.every().day.at("22:00").do(backup_data)
# schedule.every(10).seconds.do(print_time)

def schedule_loop():
    while True:
        schedule.run_pending()

# 获取所有物资
@app.route('/materials', methods=['GET'])
def get_materials():
    result = []
    for material in materials:
        latest_version = material['history'][-1] if material['history'] else {}
        result.append({
            'id': material['id'],
            'photo': material['photo'],
            'name': latest_version.get('name', ''),
            'location': latest_version.get('location', ''),
            'description': latest_version.get('description', '')
        })
    return jsonify(result)

# 添加物资
@app.route('/materials', methods=['POST'])
def add_material():
    data = request.form
    id = str(uuid4())  # 自动生成唯一ID

    history_entry = {'name': data.get('name', ''), 'description': data.get('description', ''), 
                             'location': data.get('location', ''), 'timestamp': datetime.datetime.now().isoformat()}
    # 保存上传的图片
    if 'photo' in request.files:
        photo = request.files['photo']
        filename = os.path.join(FRONT_ROOT, UPLOAD_FOLDER, photo.filename)
        photo.save(filename)
        filename = os.path.join(UPLOAD_FOLDER, photo.filename)
    else:
        filename = ''

    new_material = {'id': id, 'photo': filename, 'history': []}
    new_material['history'].append(history_entry)

    return_material = {
                    'id': id, 
                    'photo': new_material['photo'],
                    'name': history_entry['name'], 
                    'location': history_entry['location'], 
                    'description': history_entry['description'],
                }

    materials.append(new_material)
    
    # 更新数据文件
    with open(DATA_FILE, 'w') as f:
        json.dump(materials, f)
    
    return jsonify(return_material), 201

# 删除物资
@app.route('/materials/<string:id>', methods=['DELETE'])
def delete_material(id):
    global materials
    materials = [material for material in materials if material['id'] != id]
    # 更新数据文件
    with open(DATA_FILE, 'w') as f:
        json.dump(materials, f)
    return '', 204

# 更新物资信息
@app.route('/materials/<string:id>', methods=['PUT'])
def update_material(id):
    data = request.form

    for material in materials:
        if material['id'] == id:
        
            if 'photo' in request.files:
                photo = request.files['photo']
                filename = os.path.join(FRONT_ROOT, UPLOAD_FOLDER, photo.filename)
                photo.save(filename)
                filename = os.path.join(UPLOAD_FOLDER, photo.filename)
                if (os.path.exists(os.path.join(FRONT_ROOT, material['photo']))):
                    os.remove(os.path.join(FRONT_ROOT, material['photo']))
                material['photo'] = filename
            
            history_entry = {'name': data.get('name', ''), 'description': data.get('description', ''), 
                             'location': data.get('location', ''), 'timestamp': datetime.datetime.now().isoformat()}

            return_material = {
                'id': id, 
                'photo': material['photo'],
                'name': history_entry['name'], 
                'location': history_entry['location'], 
                'description': history_entry['description'],
            }

            material['history'].append(history_entry)

            # 更新数据文件
            with open(DATA_FILE, 'w') as f:
                json.dump(materials, f)
            return jsonify(return_material), 201

    return jsonify({'error': 'Material not found'}), 404  

# 获取单个物品的信息（包括最新版本的名称、位置、描述）
@app.route('/materials/<string:id>', methods=['GET'])
def get_material(id):
    material = next((m for m in materials if m['id'] == id), None)
    if material:
        latest_version = material['history'][-1] if material['history'] else {}
        return jsonify({
            'id': material['id'],
            'photo': material['photo'],
            'name': latest_version.get('name', ''),
            'location': latest_version.get('location', ''),
            'description': latest_version.get('description', '')
        })
    else:
        return jsonify({'error': 'Material not found'}), 404

# 获取单个物品的历史记录
@app.route('/materials/<string:id>/history', methods=['GET'])
def get_material_history(id):
    material = next((m for m in materials if m['id'] == id), None)
    if material:
        return jsonify(material['history'])
    else:
        return jsonify({'error': 'Material not found'}), 404

@app.route('/verify_token', methods=['POST'])
def verify_token():
    data = request.get_json()
    entered_token = data.get('token')

    if entered_token in valid_tokens:
        return jsonify({'message': 'Token is valid'}), 200
    else:
        return jsonify({'message': 'Invalid token'}), 401


if __name__ == '__main__':
    schedule_thread = threading.Thread(target=schedule_loop)
    schedule_thread.setDaemon(True)
    schedule_thread.start()

    app.run(host='0.0.0.0', port=6001, debug=True)