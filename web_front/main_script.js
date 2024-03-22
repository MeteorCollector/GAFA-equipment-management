document.addEventListener('DOMContentLoaded', () => {
    const materialList = document.getElementById('material-list');
    const addMaterialForm = document.getElementById('add-material-form');
    const address = '127.0.0.1:6001'

    // 获取所有物资
    fetch(`${address}/materials`)
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

        const formData = new FormData();
        formData.append('name', name);
        formData.append('photo', photo);
        formData.append('description', description);
        formData.append('location', location);

        fetch(`${address}/materials`, {
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

// 删除物资
function deleteMaterial(id) {
    fetch(`${address}/materials/${id}`, {
        method: 'DELETE'
    })
    .then(() => {
        const materialItem = document.querySelector(`#material-list div[data-id="${id}"]`);
        materialItem.remove();
    });
}

// 更新物资
function updateMaterial(id) {
    const newName = prompt('请输入新的物资名称:');
    const newLocation = prompt('请输入新的位置:');

    fetch(`${address}/materials/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: newName, location: newLocation })
    })
    .then(response => response.json())
    .then(updatedMaterial => {
        const materialItem = document.querySelector(`#material-list div[data-id="${id}"]`);
        materialItem.innerHTML = `
            <p>ID: ${updatedMaterial.id}</p>
            <p>名称: ${updatedMaterial.name}</p>
            <p>位置: ${updatedMaterial.location}</p>
            <button onclick="deleteMaterial('${updatedMaterial.id}')">删除</button>
            <button onclick="updateMaterial('${updatedMaterial.id}')">更新</button>
        `;
    });
}

// 渲染物资
function renderMaterial(material) {
    const materialItem = document.createElement('div');
    materialItem.dataset.id = material.id;
    materialItem.innerHTML = `
        <p>ID: ${material.id}</p>
        <p>名称: ${material.name}</p>
        <p>位置: ${material.location}</p>
        <button onclick="deleteMaterial('${material.id}')">删除</button>
        <button onclick="updateMaterial('${material.id}')">更新</button>
    `;
    materialList.appendChild(materialItem);
}
