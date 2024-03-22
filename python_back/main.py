from flask import Flask, request, jsonify
from uuid import uuid4
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

# 定义存储数据的文件路径
DATA_FILE = 'materials.json'

FRONT_ROOT = '../web_front/'
UPLOAD_FOLDER = 'uploads'  # 设置上传文件存储目录
if not os.path.exists(FRONT_ROOT + UPLOAD_FOLDER):
    os.makedirs(FRONT_ROOT + UPLOAD_FOLDER)

materials = []

# 如果数据文件不存在，则创建一个空列表
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# 读取数据文件中的数据到内存中
with open(DATA_FILE, 'r') as f:
    materials = json.load(f)

# 获取所有物资
@app.route('/materials', methods=['GET'])
def get_materials():
    return jsonify(materials)

# 添加物资
@app.route('/materials', methods=['POST'])
def add_material():
    data = request.form
    id = str(uuid4())  # 自动生成唯一ID
    name = data['name']
    description = data.get('description', '')
    location = data['location']
    
    # 保存上传的图片
    if 'photo' in request.files:
        photo = request.files['photo']
        filename = os.path.join(FRONT_ROOT, UPLOAD_FOLDER, photo.filename)
        photo.save(filename)
        filename = os.path.join(UPLOAD_FOLDER, photo.filename)
    else:
        filename = ''

    new_material = {'id': id, 'name': name, 'photo': filename, 'description': description, 'location': location}
    materials.append(new_material)
    # 更新数据文件
    with open(DATA_FILE, 'w') as f:
        json.dump(materials, f)
    
    return jsonify(new_material), 201

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
            material['name'] = data.get('name', material['name'])
            material['description'] = data.get('description', material['description'])
            material['location'] = data.get('location', material['location'])
        
            if 'photo' in request.files:
                photo = request.files['photo']
                filename = os.path.join(FRONT_ROOT, UPLOAD_FOLDER, photo.filename)
                photo.save(filename)
                filename = os.path.join(UPLOAD_FOLDER, photo.filename)
                if (os.path.exists(os.path.join(FRONT_ROOT, material['photo']))):
                    os.remove(os.path.join(FRONT_ROOT, material['photo']))
                material['photo'] = filename

            # 更新数据文件
            with open(DATA_FILE, 'w') as f:
                json.dump(materials, f)
            return jsonify(material), 201

    return jsonify({'error': 'Material not found'}), 404  

if __name__ == '__main__':
    app.run(port=6001, debug=True)
