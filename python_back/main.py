from flask import Flask, request, jsonify
from uuid import uuid4
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

FRONT_ROOT = '../web_front/'
UPLOAD_FOLDER = 'uploads'  # 设置上传文件存储目录
if not os.path.exists(FRONT_ROOT + UPLOAD_FOLDER):
    os.makedirs(FRONT_ROOT + UPLOAD_FOLDER)

materials = []

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
    return jsonify(new_material), 201

# 删除物资
@app.route('/materials/<string:id>', methods=['DELETE'])
def delete_material(id):
    global materials
    materials = [material for material in materials if material['id'] != id]
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
            return jsonify(material), 201

    return jsonify({'error': 'Material not found'}), 404  

if __name__ == '__main__':
    app.run(port=6001, debug=True)
