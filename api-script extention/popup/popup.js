document.getElementById('toggleAuth').addEventListener('click', () => {
    const authSection = document.querySelector('.auth-section');
    const toggleBtn = document.getElementById('toggleAuth');

    authSection.classList.toggle('collapsed');
    toggleBtn.textContent = authSection.classList.contains('collapsed') ? '▼' : '▲';
});

// Инициализация состояния (по умолчанию свернуто)
document.querySelector('.auth-section').classList.add('collapsed');
document.getElementById('toggleAuth').textContent = '▼';

// Функция для показа уведомлений
function showNotification(message, type = 'info', timeout = 5000) {
    const notificationsContainer = document.getElementById('notifications') || createNotificationsContainer();
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    notification.innerHTML = `
        <span>${message}</span>
        <button class="close-btn">&times;</button>
    `;

    const closeBtn = notification.querySelector('.close-btn');
    closeBtn.addEventListener('click', () => {
        notification.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    });

    notificationsContainer.appendChild(notification);

    if (timeout > 0) {
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, timeout);
    }

    return notification;
}

function createNotificationsContainer() {
    const container = document.createElement('div');
    container.id = 'notifications';
    container.className = 'notifications-container';
    document.body.appendChild(container);
    return container;
}

document.addEventListener('DOMContentLoaded', () => {
    // Обработчик клика по кнопке очистки
    document.getElementById('clearStorage').addEventListener('click', async () => {
        if (confirm('Вы уверены, что хотите очистить все временные данные (счетчики, ID категорий и т.д.)?')) {
            const notification = showNotification('Очистка временных данных...', 'info', 0);

            try {
                await chrome.storage.local.remove([
                    'categoryId',
                    'categoryCounter',
                    'serviceCounter',
                    'serviceAmount',
                    'recordHash',
                    'recordId',
                    'activityCategoryId',
                    'complexCategoryId',
                    `masterCounter`,
                ]);

                notification.textContent = 'Временные данные успешно очищены!';
                notification.className = 'notification success';
                setTimeout(() => notification.remove(), 3000);
            } catch (error) {
                notification.textContent = `Ошибка очистки: ${error.message}`;
                notification.className = 'notification error';
                setTimeout(() => notification.remove(), 5000);
                console.error('Ошибка очистки:', error);
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

        if (!baseUrl || !bearerToken || !salonId) {
            showNotification('Заполните обязательные поля: URL, Bearer Token и Salon ID', 'error');
            return;
        }

        const notification = showNotification('Сохранение данных...', 'info', 0);

        chrome.storage.local.set({ baseUrl, bearerToken, userToken, salonId }, () => {
            notification.textContent = 'Данные успешно сохранены!';
            notification.className = 'notification success';
            setTimeout(() => notification.remove(), 3000);

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

    // Обработчик сообщений от скриптов
    chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
        if (request.type === 'PROGRESS_NOTIFICATION') {
            showNotification(request.message, request.level || 'info', request.timeout || 5000);
        }
    });
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
            { id: 'login', type: 'text', label: 'Логин', default: 'a.panov@yclients.com' },
            { id: 'password', type: 'password', label: 'Пароль', default: 'apanov' },
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
            {id: 'serviceTitle', type: 'text', label: 'Название услуг/и (Если пусто [QA-GEN]...)', default: null},
            {id: 'includeMasters', type: 'radio', label: 'Привязать мастеров', default: '1',
                options: [
                    {value : '1', label: 'Да'},
                    {value : '0', label: 'Нет'}
                ]}
        ]
    },
    'createSimpleActivityService.js' :{
        params:[
            {id: 'activityCategoryId', type: 'number', label: 'Id категории (Если пусто, создать новую)', default: null},
            {id: 'serviceTitle', type: 'text', label: 'Название услуг/и (Если пусто [QA-GEN]...)', default: null},
            {id: 'includeMasters', type: 'radio', label: 'Привязать мастеров', default: '1',
                options: [
                    {value : '1', label: 'Да'},
                    {value : '0', label: 'Нет'}
                ]}
        ]
    },
    'create_simple_service_tech_breaks.js':{
        params:[
            {id: 'categoryId', type: 'number', label: 'Id категории (Если пусто, создать новую)', default: null},
            {id: 'serviceTitle', type: 'text', label: 'Название услуг/и (Если пусто [QA-GEN]...)', default: null},
            {id: 'includeMasters', type: 'radio', label: 'Привязать мастеров', default: '1',
            options: [
                {value : '1', label: 'Да'},
                {value : '0', label: 'Нет'}
            ]}
        ]
    },
    'create_simple_complex.js':{
        params:[
            {id: 'categoryId', type: 'number', label: 'Id категории (Если пусто, создать новую)', default: null},
            {id: 'serviceTitle', type: 'text', label: 'Название услуг/и (Если пусто [QA-GEN]...)', default: null},
            {id: 'includeMasters', type: 'radio', label: 'Привязать мастеров', default: '1',
                options: [
                    {value : '1', label: 'Да'},
                    {value : '0', label: 'Нет'}
                ]},
            {id: 'serviceProcedure', type: 'radio', label: 'Порядок оказания услуг', default: 'sequential',
            options: [
                {value : 'sequential', label: 'Последовательно одним специалистом'},
                {value : 'parallel', label: 'Одновременно несколькими специалистами' },
                {value : 'sequential_multi', label: 'Последовательно несколькими специалистами'}
            ]},
            {id: 'pricing_type', type: 'radio', label: 'Стоимость комплекса', default: 'sum', options: [
                {value : 'sum', label: 'Суммировать из услуг'},
                {value : 'manual', label: 'Указать вручную'},
                {value : 'discount', label: 'Указать скидку от суммы услуг'}
                ]},
            {id: 'manualPrice', type: 'number', label: 'Стоимость комплекса', default: 1000, min: 0,
                conditional: {
                    on: 'pricing_type',
                    value: 'manual'
                }
            },
            {id: 'discount', type: 'number', label: 'Скидка на комплекс', default: 0, min: 0, max: 100,
            conditional: {
                on: 'pricing_type',
                value: 'discount'
            }
            }
        ]
    },
    'createMaster.js' : {
    params: [
        {id: 'name', type: 'text', label: 'Имя сотрудника', default: null},
        {id: 'addUser', type: 'radio', label: 'Создать пользователя', default: '0', options:[
            {value: '1', label: 'Да'},
            {value: '0', label: 'Нет'}
        ]},
        {id: 'addTimetable', type: 'radio', label: 'Создать расписание', default: '1', options:[
            {value: '1', label: 'Да'},
            {value: '0', label: 'Нет'}]},
        {id: 'linkAllServices', type: 'radio', label: 'Связать все услуги с мастером', default: '0', options:[
            {value: '1', label: 'Да'},
            {value: '0', label: 'Нет'}
        ]},
    ]}
};

// Словарь переводов
const TRANSLATIONS = {
    categories: {
        'services': 'Услуги',
        'auth': 'Авторизация (получение user токена вручную)',
        'createRecords': 'Создание записей',
//        'phone': 'Телефония',
        'masters': 'Сотрудники'
    },
    subcategories: {
        'online': 'Онлайн записи',
        'offline': 'Оффлайн записи',
//        'integration': 'Включить интеграцию',
//        'pushes': 'Отправка пушей',
        'individual': 'Индивидуальные',
        'activity': 'Групповые',
        'complex': 'Комлпексы'
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
        'create_simple_service.js': 'Создать обычную услугу',
        'createSimpleActivityService.js': 'Создать групповую услугу',
        'create_simple_service_tech_breaks.js': 'Создать услугу с тех.перерывом',
        'create_simple_complex.js': 'Создать простой комплекс',
        'createMaster.js': 'Создать сотрудника',

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
                'individual':['create_simple_service.js', 'create_simple_service_tech_breaks.js'],
                'activity':['createSimpleActivityService.js'],
                'complex':['create_simple_complex.js']
            },
            'masters': ['createMaster.js']
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

    // Функция для создания элементов управления
    const createParamField = (param, parent) => {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = `param-field param-${param.id}`;
        fieldDiv.style.marginBottom = '10px';

        const label = document.createElement('label');
        label.textContent = param.label + ': ';
        label.style.display = 'block';
        label.style.marginBottom = '5px';

        fieldDiv.appendChild(label);

        if (param.type === 'radio') {
            param.options.forEach(option => {
                const radioDiv = document.createElement('div');
                radioDiv.style.display = 'flex';
                radioDiv.style.alignItems = 'center';
                radioDiv.style.marginBottom = '5px';

                const radioInput = document.createElement('input');
                radioInput.type = 'radio';
                radioInput.id = `param_${scriptName}_${param.id}_${option.value}`;
                radioInput.name = `param_${scriptName}_${param.id}`;
                radioInput.value = option.value;
                if (param.default === option.value) {
                    radioInput.checked = true;
                }

                // Добавляем обработчик изменения
                radioInput.addEventListener('change', () => {
                    updateConditionalFields();
                });

                const radioLabel = document.createElement('label');
                radioLabel.htmlFor = radioInput.id;
                radioLabel.textContent = option.label;
                radioLabel.style.marginLeft = '5px';

                radioDiv.appendChild(radioInput);
                radioDiv.appendChild(radioLabel);
                fieldDiv.appendChild(radioDiv);
            });
        } else {
            const input = document.createElement('input');
            input.type = param.type;
            input.id = `param_${scriptName}_${param.id}`;
            input.value = param.default;
            if (param.min) input.min = param.min;
            if (param.max) input.max = param.max;
            input.style.width = '100%';
            input.style.padding = '5px';
            fieldDiv.appendChild(input);
        }

        parent.appendChild(fieldDiv);
        return fieldDiv;
    };

    // Функция для обновления видимости полей
    const updateConditionalFields = () => {
        config.params.forEach(param => {
            if (param.conditional) {
                const triggerParam = document.querySelector(
                    `input[name="param_${scriptName}_${param.conditional.on}"]:checked`
                );
                const triggerValue = triggerParam ? triggerParam.value : null;

                const field = document.querySelector(`.param-${param.id}`);
                if (field) {
                    field.style.display = triggerValue === param.conditional.value ? 'block' : 'none';
                }
            }
        });
    };

    // Создаем все поля
    config.params.forEach(param => {
        createParamField(param, modalFields);
    });

    // Первоначальное обновление видимости
    updateConditionalFields();

    modal.style.display = 'block';

    document.getElementById('executeWithSettings').onclick = () => {
        const params = {};
        config.params.forEach(param => {
            if (param.type === 'radio') {
                const selectedRadio = document.querySelector(
                    `input[name="param_${scriptName}_${param.id}"]:checked`
                );
                params[param.id] = selectedRadio ? selectedRadio.value : param.default;
            } else {
                const input = document.getElementById(`param_${scriptName}_${param.id}`);
                if (input && input.style.display !== 'none') {
                    params[param.id] = input.value;
                }
            }
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

    const notification = showNotification(
        `Запуск: ${TRANSLATIONS.scripts[scriptName] || scriptName}`,
        'info',
        0
    );

    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
        const tabId = tabs[0]?.id;
        if (!tabId) {
            showNotification('Ошибка: Не найдена активная вкладка', 'error');
            notification.remove();
            return;
        }

        const handleError = (error) => {
            console.error(`Ошибка выполнения ${scriptName}:`, error);
            notification.textContent = `Ошибка: ${error.message || 'Неизвестная ошибка'}`;
            notification.className = 'notification error';
            setTimeout(() => notification.remove(), 5000);
        };

        let executeWithParams = (allParams) => {
            chrome.scripting.executeScript({
                target: {tabId: tabId},
                func: (p) => {
                    window.scriptParams = {
                        ...p,
                        showProgress: (message, level = 'info') => {
                            chrome.runtime.sendMessage({
                                type: 'PROGRESS_NOTIFICATION',
                                message: message,
                                level: level
                            });
                        },
                        showWarning: (message) => {
                            chrome.runtime.sendMessage({
                                type: 'PROGRESS_NOTIFICATION',
                                message: message,
                                level: 'warning'
                            });
                        },
                        showSuccess: (message) => {
                            chrome.runtime.sendMessage({
                                type: 'PROGRESS_NOTIFICATION',
                                message: message,
                                level: 'success'
                            });
                        },
                        showError: (message) => {
                            chrome.runtime.sendMessage({
                                type: 'PROGRESS_NOTIFICATION',
                                message: message,
                                level: 'error'
                            });
                        }
                    };
                },
                args: [allParams]
            }, () => {
                if (chrome.runtime.lastError) {
                    handleError(chrome.runtime.lastError);
                    return;
                }

                chrome.scripting.executeScript({
                    target: {tabId: tabId},
                    files: [scriptPath]
                }, (results) => {
                    if (chrome.runtime.lastError) {
                        handleError(chrome.runtime.lastError);
                    } else {
                        notification.textContent = `Скрипт "${TRANSLATIONS.scripts[scriptName] || scriptName}" запущен`;
                        notification.className = 'notification success';
                        setTimeout(() => notification.remove(), 3000);
                    }
                });
            });
        };

        if (type === 'api') {
            chrome.storage.local.get(['bearerToken', 'userToken', 'salonId'], (data) => {
                if (!data.bearerToken || !data.salonId) {
                    handleError(new Error('Не указаны Bearer Token или Salon ID'));
                    return;
                }
                executeWithParams({ ...params, ...data });
            });
        } else {
            executeWithParams(params);
        }
    });
}