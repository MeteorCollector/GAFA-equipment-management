const materialList = document.getElementById('material-list');
const editForm = document.getElementById('edit-form');
const editMaterialForm = document.getElementById('edit-material-form');
const addMaterialForm = document.getElementById('add-material-form');
const address = "127.0.0.1";

document.addEventListener('DOMContentLoaded', () => {
    // 获取所有物资
    fetch(`http://${address}:6001/materials`)
        .then(response => response.json())
        .then(materials => {
            materials.forEach(material => {
                renderMaterial(material);
            });
        });

    // 添加物资
    addMaterialForm.addEventListener('submit', event => {
        event.preventDefault();
        const name = document.getElementById('material-name').value;
        const photoInput = document.getElementById('material-photo');
        const photo = photoInput.files[0]; // 获取用户选择的文件
        const description = document.getElementById('material-description').value;
        const location = document.getElementById('material-location').value;
        const timestamp = new Date().toISOString(); // 获取当前时间

        const formData = new FormData();
        formData.append('name', name);
        formData.append('photo', photo);
        formData.append('description', description);
        formData.append('location', location);
        formData.append('timestamp', timestamp); // 将时间信息添加到表单中

        fetch(`http://${address}:6001/materials`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(material => {
            renderMaterial(material);
        });

        addMaterialForm.reset();
    });

    
});

// 渲染物资
function renderMaterial(material) {
    const materialItem = document.createElement('div');
    materialItem.dataset.id = material.id;
    materialItem.innerHTML = `
        <img src="${material.photo}" alt="${material.name}">
        <p>ID: ${material.id}</p>
        <p>名称: ${material.name}</p>
        <p>位置: ${material.location}</p>
        <p>描述: ${material.description}</p>
        <button onclick="deleteMaterial('${material.id}', '${material.name}')">删除</button>
        <button onclick="showEditForm('${material.id}', '${material.name}', '${material.description}', '${material.location}')">编辑</button>
    `;
    materialList.appendChild(materialItem);
}

// 显示编辑表单
function showEditForm(id, name, description, location) {
    document.getElementById('edit-material-id').value = id;
    document.getElementById('edit-material-name').value = name;
    document.getElementById('edit-material-description').value = description;
    document.getElementById('edit-material-location').value = location;
    editForm.style.display = 'block';
}

// 更新物资信息
editMaterialForm.addEventListener('submit', event => {
    event.preventDefault();
    const id = document.getElementById('edit-material-id').value;
    const name = document.getElementById('edit-material-name').value;
    const photoInput = document.getElementById('edit-material-photo');
    const photo = photoInput.files[0];
    const description = document.getElementById('edit-material-description').value;
    const location = document.getElementById('edit-material-location').value;
    const timestamp = new Date().toISOString(); // 获取当前时间

    const formData = new FormData();
    formData.append('name', name);
    formData.append('photo', photo);
    formData.append('description', description);
    formData.append('location', location);
    formData.append('timestamp', timestamp); // 将时间信息添加到表单中

    fetch(`http://${address}:6001/materials/${id}`, {
        method: 'PUT',
        body: formData
    })
    .then(response => response.json())
    .then(updatedMaterial => {
        const materialItem = document.querySelector(`#material-list div[data-id="${id}"]`);
        materialItem.innerHTML = `
            <img src="${updatedMaterial.photo}" alt="${updatedMaterial.name}">
            <p>ID: ${updatedMaterial.id}</p>
            <p>名称: ${updatedMaterial.name}</p>
            <p>位置: ${updatedMaterial.location}</p>
            <p>描述: ${updatedMaterial.description}</p>

            <button onclick="deleteMaterial('${updatedMaterial.id}', '${updatedMaterial.name}')">删除</button>
            <button onclick="showEditForm('${updatedMaterial.id}', '${updatedMaterial.name}', '${updatedMaterial.description}', '${updatedMaterial.location}')">编辑</button>
        `;
        editForm.style.display = 'none';
    });

    
});

// 取消编辑
function cancelEdit() {
    editForm.style.display = 'none';
}

// 删除物资
function deleteMaterial(id, name) {
    const confirmDelete = confirm(`确定要删除 ${name} 吗？这件物品会消失很久（真的很久！）`); // 弹出确认框

    if (confirmDelete) {
        fetch(`http://${address}:6001/materials/${id}`, {
            method: 'DELETE'
        })
        .then(() => {
            const materialItem = document.querySelector(`#material-list div[data-id="${id}"]`);
            materialItem.remove();
        });
    }
}