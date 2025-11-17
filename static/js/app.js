// 全局变量
let currentApps = [];
let installedApps = [];
let filteredInstalledApps = [];

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    loadApps();
    loadInstalledApps();
});

// 加载当前启动项
async function loadApps() {
    try {
        const response = await fetch('/api/apps');
        const data = await response.json();
        currentApps = data.apps;
        renderAppList();
    } catch (error) {
        showToast('加载配置失败', 'error');
        console.error(error);
    }
}

// 渲染启动项列表
function renderAppList() {
    const listEl = document.getElementById('app-list');
    const countEl = document.getElementById('app-count');

    countEl.textContent = `${currentApps.length} 个应用`;

    if (currentApps.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state">
                <div class="icon">📭</div>
                <p>还没有添加任何启动项</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = currentApps.map((app, index) => `
        <div class="app-item">
            <div>
                <span class="number">${index + 1}.</span>
                <span class="name">${app}</span>
            </div>
            <div class="app-controls">
                <button class="btn-icon" onclick="moveUp(${index})" title="上移" ${index === 0 ? 'disabled' : ''}>↑</button>
                <button class="btn-icon" onclick="moveDown(${index})" title="下移" ${index === currentApps.length - 1 ? 'disabled' : ''}>↓</button>
                <button class="btn-icon delete" onclick="removeApp(${index})" title="删除">🗑️</button>
            </div>
        </div>
    `).join('');
}

// 加载已安装应用
async function loadInstalledApps() {
    try {
        const response = await fetch('/api/installed');
        const data = await response.json();
        installedApps = data.apps;
        filteredInstalledApps = installedApps;
        renderInstalledList();
    } catch (error) {
        showToast('加载应用列表失败', 'error');
        console.error(error);
    }
}

// 渲染已安装应用列表
function renderInstalledList() {
    const listEl = document.getElementById('installed-list');

    if (filteredInstalledApps.length === 0) {
        listEl.innerHTML = `
            <div class="empty-state">
                <div class="icon">🔍</div>
                <p>未找到应用</p>
            </div>
        `;
        return;
    }

    listEl.innerHTML = filteredInstalledApps.map(app => `
        <div class="installed-item">
            <span class="name">${app}</span>
            <button class="add-btn" onclick="addApp('${app}')">➕ 添加</button>
        </div>
    `).join('');
}

// 过滤已安装应用
function filterInstalledApps() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    filteredInstalledApps = installedApps.filter(app =>
        app.toLowerCase().includes(searchTerm)
    );
    renderInstalledList();
}

// 刷新已安装应用
async function refreshInstalledApps() {
    showToast('正在扫描应用...', 'info');
    await loadInstalledApps();
    showToast('刷新完成', 'success');
}

// 添加应用
async function addApp(appName) {
    if (currentApps.includes(appName)) {
        showToast(`${appName} 已在启动列表中`, 'error');
        return;
    }

    try {
        const response = await fetch('/api/apps/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: appName})
        });

        const data = await response.json();

        if (data.success) {
            currentApps = data.apps;
            renderAppList();
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('添加失败', 'error');
        console.error(error);
    }
}

// 删除应用
async function removeApp(index) {
    if (!confirm(`确定要删除 ${currentApps[index]} 吗？`)) {
        return;
    }

    try {
        const response = await fetch('/api/apps/remove', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({index: index})
        });

        const data = await response.json();

        if (data.success) {
            currentApps = data.apps;
            renderAppList();
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('删除失败', 'error');
        console.error(error);
    }
}

// 上移
async function moveUp(index) {
    if (index === 0) return;

    try {
        const response = await fetch('/api/apps/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({from: index, to: index - 1})
        });

        const data = await response.json();

        if (data.success) {
            currentApps = data.apps;
            renderAppList();
        }
    } catch (error) {
        showToast('移动失败', 'error');
        console.error(error);
    }
}

// 下移
async function moveDown(index) {
    if (index === currentApps.length - 1) return;

    try {
        const response = await fetch('/api/apps/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({from: index, to: index + 1})
        });

        const data = await response.json();

        if (data.success) {
            currentApps = data.apps;
            renderAppList();
        }
    } catch (error) {
        showToast('移动失败', 'error');
        console.error(error);
    }
}

// 保存配置
async function saveConfig() {
    try {
        const response = await fetch('/api/apps', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({apps: currentApps})
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('保存失败', 'error');
        console.error(error);
    }
}

// 恢复默认
async function restoreDefaults() {
    if (!confirm('确定要恢复到默认配置吗？\n当前配置将被覆盖。')) {
        return;
    }

    try {
        const response = await fetch('/api/apps/restore', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            currentApps = data.apps;
            renderAppList();
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('恢复失败', 'error');
        console.error(error);
    }
}

// 生成脚本
async function generateScript() {
    if (currentApps.length === 0) {
        showToast('启动列表为空，请先添加应用', 'error');
        return;
    }

    try {
        const response = await fetch('/api/script/generate', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    } catch (error) {
        showToast('生成失败', 'error');
        console.error(error);
    }
}

// 执行启动
async function runStartup() {
    if (currentApps.length === 0) {
        showToast('启动列表为空，请先添加应用', 'error');
        return;
    }

    showToast('正在执行启动脚本...', 'info');
    showLog('正在启动应用，请稍候...\n\n');

    try {
        const response = await fetch('/api/script/run', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showLog(data.output);
            showToast('执行完成', 'success');
        } else {
            showLog('错误: ' + data.message);
            showToast(data.message, 'error');
        }
    } catch (error) {
        showLog('错误: ' + error.message);
        showToast('执行失败', 'error');
        console.error(error);
    }
}

// 显示手动添加对话框
function showAddDialog() {
    const dialog = document.getElementById('add-dialog');
    const input = document.getElementById('app-name-input');

    dialog.style.display = 'flex';
    input.value = '';
    input.focus();

    // 按回车添加
    input.onkeypress = function(e) {
        if (e.key === 'Enter') {
            addManualApp();
        }
    };
}

// 关闭添加对话框
function closeAddDialog() {
    document.getElementById('add-dialog').style.display = 'none';
}

// 手动添加应用
async function addManualApp() {
    const input = document.getElementById('app-name-input');
    const appName = input.value.trim();

    if (!appName) {
        showToast('应用名称不能为空', 'error');
        return;
    }

    closeAddDialog();
    await addApp(appName);
}

// 显示日志
function showLog(message) {
    const panel = document.getElementById('log-panel');
    const output = document.getElementById('log-output');

    panel.style.display = 'block';
    output.textContent = message;

    // 滚动到底部
    output.scrollTop = output.scrollHeight;
}

// 关闭日志
function closeLog() {
    document.getElementById('log-panel').style.display = 'none';
}

// 显示Toast通知
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');

    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
