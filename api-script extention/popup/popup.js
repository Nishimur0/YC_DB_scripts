document.getElementById('toggleAuth').addEventListener('click', () => {
    const authSection = document.querySelector('.auth-section');
    const toggleBtn = document.getElementById('toggleAuth');

    authSection.classList.toggle('collapsed');
    toggleBtn.textContent = authSection.classList.contains('collapsed') ? '▼' : '▲';
});

// Инициализация состояния (по умолчанию свернуто)
document.querySelector('.auth-section').classList.add('collapsed');
document.getElementById('toggleAuth').textContent = '▼';

document.addEventListener('DOMContentLoaded', () => {
    // Обработчик клика по кнопке очистки
    document.getElementById('clearStorage').addEventListener('click', async () => {
        if (confirm('Вы уверены, что хотите очистить все временные данные (счетчики, ID категорий и т.д.)?')) {
            try {
                await chrome.storage.local.remove([
                    'categoryId',
                    'categoryCounter',
                    'serviceCounter',
                    'serviceAmount',
                    'recordHash',
                    'recordId'
                ]);

                alert('Временные данные успешно очищены!');
            } catch (error) {
                console.error('Ошибка очистки:', error);
                alert('Произошла ошибка при очистке данных');
            }
        }
    });

    // Загрузка сохраненных данных
    chrome.storage.local.get(['baseUrl', 'bearerToken', 'userToken', 'salonId'], (data) => {
        document.getElementById('baseUrl').value = data.baseUrl || '';
        document.getElementById('bearerToken').value = data.bearerToken || '';
        document.getElementById('userToken').value = data.userToken || '';
        document.getElementById('salonId').value = data.salonId || '';

        // Автоопределение Bearer при загрузке
        updateBearerTokenByUrl(data.baseUrl);
    });

    // Автоопределение при изменении URL
    document.getElementById('baseUrl').addEventListener('input', (e) => {
        updateBearerTokenByUrl(e.target.value);
    });

    // Сохранение данных
    document.getElementById('saveAuth').addEventListener('click', () => {
        const baseUrl = document.getElementById('baseUrl').value;
        const bearerToken = document.getElementById('bearerToken').value;
        const userToken = document.getElementById('userToken').value;
        const salonId = document.getElementById('salonId').value;

        chrome.storage.local.set({ baseUrl, bearerToken, userToken, salonId }, () => {
            alert('Данные сохранены');
            document.querySelector('.auth-section').classList.add('collapsed');
            document.getElementById('toggleAuth').textContent = '▼';
        });
    });

    function updateBearerTokenByUrl(url) {
        if (!url) return;

        let bearerToken = '';
        if (url.includes('yclients.com')) {
            bearerToken = 'u8xzkdpkgfc73uektn64';
        } else if (url.includes('-slt.yclients.cloud')) {
            bearerToken = 'u8xzkdpkgfc73uektn64';
        } else if (url.includes('.teststation.yclients.tech')) {
            bearerToken = 'u8xzkdpkgfc73uektn64';
        }

        if (bearerToken) {
            document.getElementById('bearerToken').value = bearerToken;
        }
    }

    // Переключение вкладок
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
        });
    });

    // Загрузка структуры скриптов
    loadScriptsStructure();
});

// Конфигурация скриптов с параметрами
const SCRIPTS_CONFIG = {
    'mastersAddClicker.js': {
        displayName: 'Добавить сотрудника',
        params: [
            { id: 'count', type: 'number', label: 'Количество раз', default: 10, min: 1 },
            { id: 'interval', type: 'number', label: 'Интервал (мс)', default: 400, min: 100 }
        ]
    },
    'authorize.js': {
        displayName: 'Авторизоваться без 2FA',
        params: [
            { id: 'login', type: 'text', label: 'Логин', default: 'login@gmail.com' },
            { id: 'password', type: 'password', label: 'Пароль', default: 'password' },
        ]
    },
    'callbackPhone.js': {
        params:[
            {id: 'appBearer', type: 'text', label: 'Bearer', default: 'pggze4bbkyejdsue4wcu'},
            {id: 'applicationId', type: 'text', label: 'ApplicationId', default: '38'}
        ]
    },
    'incoming.js': {
        params:[
            {id: 'appBearer', type: 'text', label: 'Bearer', default: 'pggze4bbkyejdsue4wcu'},
            {id: 'crmToken', type: 'text', label: 'crm_token', default: null},
            {id: 'diversionPhone', type: 'text', label: 'diversionPhone', default: null},
            {id: 'clientPhone', type: 'text', label: 'clientPhone', default: null},
            {id: 'callType', type: 'text', label: 'callType', default: 'incoming'}

        ]
    },
    'create_simple_service.js':{
        params:[
            {id: 'categoryId', type: 'number', label: 'Id категории (Если пусто, создать новую)', default: null},
            {id: 'title', type: 'text', label: 'Название услуг/и (Если пусто [QA-GEN]...)', default: null},
            {id: 'includeMasters', type: 'number', label: 'Привязать мастеров (1 - да, 0 - нет)', default: 1}
        ]
    }
};

// Словарь переводов
const TRANSLATIONS = {
    categories: {
        'services': 'Услуги',
        'auth': 'Авторизация',
        'createRecords': 'Создание записей',
//        'phone': 'Телефония'
    },
    subcategories: {
        'online': 'Онлайн записи',
        'offline': 'Оффлайн записи',
//        'integration': 'Включить интеграцию',
//        'pushes': 'Отправка пушей',
        'individual': 'Индивидуальные'
    },
    scripts: {
        'authorize.js': 'Авторизоваться',
        'mastersAddClicker.js': 'Добавить сотрудника',
        'createOnlineRecord.js': 'Создать онлайн запись',
        'deleteLastCreatedOnlineRecord.js': 'Удалить последнюю запись',
        'createOfflineRecord.js': 'Создать оффлайн запись',
        'createOfflineRecordApiV2.js': 'Создать оффлайн запись (API v2)',
 //       'callbackPhone.js': 'Подключить',
 //       'incoming.js': '(push) Входящий звонок'
        'create_simple_service.js': 'Создать обычную услугу'

    }
};

async function loadScriptsStructure() {
    // Загружаем сохранённый конфиг (если есть)
    const { scriptsConfig } = await chrome.storage.local.get('scriptsConfig');

    // Обновляем SCRIPTS_CONFIG, если есть сохранённые данные
    if (scriptsConfig) {
        Object.assign(SCRIPTS_CONFIG, scriptsConfig);
    }

    // Далее рендерим интерфейс как обычно
    const apiStructure = await fetchScriptsStructure('api');
    renderCategories('api-categories', apiStructure, 'api');

    const domStructure = await fetchScriptsStructure('dom');
    renderCategories('dom-categories', domStructure, 'dom');
}

async function fetchScriptsStructure(type) {
    if (type === 'api') {
        return {
            'auth': ['authorize.js'],
            'createRecords': {
                'online': ['createOnlineRecord.js', 'deleteLastCreatedOnlineRecord.js'],
                'offline': ['createOfflineRecord.js', 'createOfflineRecordApiV2.js']
            },
 //           'phone': {
 //               'integration': ['callbackPhone.js'],
 //               'pushes': ['incoming.js']
 //           }
            'services': {
                'individual':['create_simple_service.js']}
        };
    } else {
        return {
            'services': ['mastersAddClicker.js']
        };
    }
}


function renderCategories(containerId, structure, type) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';

    for (const [category, content] of Object.entries(structure)) {
        const categoryElement = document.createElement('div');
        categoryElement.className = 'category';

        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'category-header';
        categoryHeader.innerHTML = `
            <span>${TRANSLATIONS.categories[category] || category}</span>
            <span class="toggle-icon">▼</span>
        `;

        const contentContainer = document.createElement('div');
        contentContainer.className = 'category-content collapsed';

        categoryHeader.addEventListener('click', (e) => {
            // Игнорируем клик по иконке настроек
            if (e.target.tagName === 'BUTTON') return;

            contentContainer.classList.toggle('collapsed');
            const icon = categoryHeader.querySelector('.toggle-icon');
            icon.textContent = contentContainer.classList.contains('collapsed') ? '▼' : '▲';
        });

        if (typeof content === 'object' && !Array.isArray(content)) {
            // Обработка подкатегорий
            for (const [subcategory, scripts] of Object.entries(content)) {
                const subcategoryElement = document.createElement('div');
                subcategoryElement.className = 'subcategory';

                const subcategoryHeader = document.createElement('div');
                subcategoryHeader.className = 'subcategory-header';
                subcategoryHeader.innerHTML = `
                    <span>${TRANSLATIONS.subcategories[subcategory] || subcategory}</span>
                    <span class="toggle-icon">▼</span>
                `;

                const subContentContainer = document.createElement('div');
                subContentContainer.className = 'subcategory-content collapsed';

                subcategoryHeader.addEventListener('click', (e) => {
                    if (e.target.tagName === 'BUTTON') return;

                    subContentContainer.classList.toggle('collapsed');
                    const icon = subcategoryHeader.querySelector('.toggle-icon');
                    icon.textContent = subContentContainer.classList.contains('collapsed') ? '▼' : '▲';
                });

                const scriptsList = createScriptsList(scripts, type, category, subcategory);
                subContentContainer.appendChild(scriptsList);

                subcategoryElement.appendChild(subcategoryHeader);
                subcategoryElement.appendChild(subContentContainer);
                contentContainer.appendChild(subcategoryElement);
            }
        } else {
            // Обработка обычных скриптов
            const scriptsList = createScriptsList(content, type, category);
            contentContainer.appendChild(scriptsList);
        }

        categoryElement.appendChild(categoryHeader);
        categoryElement.appendChild(contentContainer);
        container.appendChild(categoryElement);
    }
}

function createScriptsList(scripts, type, category, subcategory = null) {
    const scriptsList = document.createElement('div');
    scriptsList.className = 'scripts-list';

    scripts.forEach(script => {
        const scriptElement = document.createElement('div');
        scriptElement.className = 'script-item';

        const scriptNameElement = document.createElement('span');
        scriptNameElement.textContent = TRANSLATIONS.scripts[script] || script;

        const controlsDiv = document.createElement('div');
        controlsDiv.style.display = 'flex';
        controlsDiv.style.alignItems = 'center';

        const runBtn = document.createElement('button');
        runBtn.textContent = '▶';
        runBtn.style.marginRight = '5px';
        runBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            executeScript(type, category, script, subcategory);
        });

        controlsDiv.appendChild(runBtn);

        if (SCRIPTS_CONFIG[script]) {
            const settingsBtn = document.createElement('button');
            settingsBtn.textContent = '⚙';
            settingsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                showSettingsModal(type, category, script, subcategory);
            });
            controlsDiv.appendChild(settingsBtn);
        }

        scriptElement.appendChild(scriptNameElement);
        scriptElement.appendChild(controlsDiv);
        scriptsList.appendChild(scriptElement);
    });

    return scriptsList;
}


function showSettingsModal(type, category, scriptName, subcategory = null) {
    const config = SCRIPTS_CONFIG[scriptName];
    const modal = document.getElementById('settingsModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalFields = document.getElementById('modalFields');

    modalTitle.textContent = `${TRANSLATIONS.scripts[scriptName] || scriptName} - Настройки`;
    modalFields.innerHTML = '';

    config.params.forEach(param => {
        const fieldDiv = document.createElement('div');
        fieldDiv.style.marginBottom = '10px';

        const label = document.createElement('label');
        label.textContent = param.label + ': ';
        label.style.display = 'block';
        label.style.marginBottom = '5px';

        const input = document.createElement('input');
        input.type = param.type;
        input.id = `param_${scriptName}_${param.id}`;
        input.value = param.default;
        if (param.min) input.min = param.min;
        if (param.max) input.max = param.max;
        input.style.width = '100%';
        input.style.padding = '5px';

        fieldDiv.appendChild(label);
        fieldDiv.appendChild(input);
        modalFields.appendChild(fieldDiv);
    });

    modal.style.display = 'block';

    document.getElementById('executeWithSettings').onclick = () => {
        const params = {};
        config.params.forEach(param => {
            params[param.id] = document.getElementById(`param_${scriptName}_${param.id}`).value;
        });

        executeScriptWithParams(type, category, scriptName, params, subcategory);
        modal.style.display = 'none';
    };

    document.querySelector('.close-modal').onclick = () => {
        modal.style.display = 'none';
    };
}

function executeScript(type, category, scriptName, subcategory = null) {
    const defaultParams = SCRIPTS_CONFIG[scriptName]?.params.reduce((acc, param) => {
        acc[param.id] = param.default;
        return acc;
    }, {});

    executeScriptWithParams(type, category, scriptName, defaultParams || {}, subcategory);
}

function executeScriptWithParams(type, category, scriptName, params, subcategory = null) {
    const scriptPath = subcategory
    ? `scripts/${type}/${category}/${subcategory}/${scriptName}`
    : `scripts/${type}/${category}/${scriptName}`;

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const tabId = tabs[0].id;

        if (type === 'api') {
            chrome.storage.local.get(['bearerToken', 'userToken'], (data) => {
                const allParams = { ...params, ...data };
                chrome.scripting.executeScript({
                    target: {tabId: tabId},
                    func: (p) => { window.scriptParams = p; },
                    args: [allParams]
                }, () => {
                    chrome.scripting.executeScript({
                        target: {tabId: tabId},
                        files: [scriptPath]
                    });
                });
            });
        } else {
            chrome.scripting.executeScript({
                target: {tabId: tabId},
                func: (p) => { window.scriptParams = p; },
                args: [params]
            }, () => {
                chrome.scripting.executeScript({
                    target: {tabId: tabId},
                    files: [scriptPath]
                });
            });
        }
    });
}