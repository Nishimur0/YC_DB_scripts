async function createOfflineRecord(params = {}) {
    try {
        // 1. Получаем и объединяем параметры
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...extensionParams,
            ...params
        };

        // 2. Валидация
        const required = ['baseUrl', 'bearerToken', 'userToken', 'salonId'];
        const missing = required.filter(p => !currentParams[p]);
        if (missing.length) throw new Error(`Missing: ${missing.join(', ')}`);

        // 3. Нормализация URL
        const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

        // 4. Заголовки
        const bearerHeaders = {
            'Authorization': `Bearer ${currentParams.bearerToken}`,
            'Accept': 'application/vnd.yclients.v2+json'
        };

        const userTokenHeaders = {
            'Authorization': `Bearer ${currentParams.bearerToken}, User ${currentParams.userToken}`,
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.api.v2+json'
        };

        //выбор мастера
        let master = await getAvailableMaster(cleanBaseUrl, currentParams.salonId, userTokenHeaders);
        console.log('Выбран мастер:', master.name);

        //выбор даты
        let dates = await getAvailableDate(cleanBaseUrl, currentParams.salonId, userTokenHeaders, master);
        console.log(`найденные даты:`, dates)

        //выбор слота
        let timeslotsArray = await getAvailableTime(cleanBaseUrl, currentParams.salonId, userTokenHeaders, master, dates);

        // Создание записи
        await createRecord(cleanBaseUrl, currentParams.salonId, userTokenHeaders, master, timeslotsArray, dates);

        //выбрасываем ошибку если все плохо
    } catch (error) {
        console.error('Ошибка в цепочке:', error);
        throw error;
    }
}


// Выборка мастера. Условие: не уволен, не удален, есть расписание на будущее, есть услуги
async function getAvailableMaster(baseUrl, salonId, headers) {
    let response = await fetch(`${baseUrl}/api/v1/company/${salonId}/staff`, {
        method: 'GET',
        headers: headers
    });

    let data = await response.json();

    if (!response.ok) {
        throw new Error(data.meta?.message || `Ошибка при получении списка мастеров`);
    }

    let availableStaff = data.data?.filter(master =>
    master.fired === 0 &&
    master.is_deleted === false &&
    new Date(master.schedule_till) > new Date() &&
    master.services_links?.length > 0
    );

    if (!availableStaff?.length) {
        throw new Error('Нет доступных мастеров для записи');
    }

    return availableStaff[Math.floor(Math.random() * availableStaff.length)];
}

// Выборка свободной даты в журнале
async function getAvailableDate(baseUrl, salonId, headers, masterData) {
    let today = new Date().toISOString().split('T')[0];
    let response = await fetch(`${baseUrl}/api/v1/timetable/dates/${salonId}/${today}?staff_id=${masterData.id}`, {
        method: 'GET',
        headers: headers
    });

    let data = await response.json();

    if (!response.ok) {
        throw new Error(data.meta?.message || `Ошибка при получении списка дат`);
    }
    let futureDates = data.data?.filter(date => date >= today);

    if (!futureDates?.length) {
        throw new Error(`Нет доступных дат для записи`);
    }
    return futureDates;
}

// Выборка свободного времени в журнале
async function getAvailableTime(baseUrl, salonId, headers, masterData, datesArray) {
    if (datesArray.length == 0) {
        throw new Error(`Нет доступных дат для записи`);
    }
    let date = datesArray.shift();
    let response = await fetch(`${baseUrl}/api/v1/timetable/seances/${salonId}/${masterData.id}/${date}` , {
        method: 'GET',
        headers: headers
    });

    let data = await response.json();

    if (!response.ok) {
        throw new Error(data.meta?.message || `Ошибка при получении списка дат`);
    }
    let availableSlots = data.data?.filter(time => time.is_free === true)
    if (availableSlots.length == 0) {
        return await getAvailableTime(baseUrl, salonId, headers, masterData, datesArray)
    }
    return availableSlots;
}

// Создание записи в журнале
async function createRecord(baseUrl, salonId, headers, masterData, timeslotsArray, datesArray) {
    let choosenSlot = timeslotsArray[Math.floor(Math.random() * timeslotsArray.length)]
    // Имена
    let maleNames = [
        "Aleksandr", "Dmitriy", "Maksim",
        "Sergey", "Andrey", "Aleksey",
        "Artyom", "Ilya", "Kirill",
        "Mikhail", "Nikita", "Yegor",
        "Matvey", "Roman", "Vladimir"
    ];

    // Фамилии
    let maleSurnames = [
        "Ivanov", "Petrov", "Sidorov",
        "Smirnov", "Kuznetsov", "Krysolov",
        "Vasilyev", "Fyodorov", "Morozov",
        "Novikov", "Volkov", "Pavlov",
        "Semyonov", "Golubev", "Vinogradov"
    ];

    // Отчества
    let malePatronymics = [
        "Aleksandrovich", "Dmitriyevich", "Maksimovich",
        "Sergeyevich", "Andreyevich", "Alekseyevich",
        "Artyomovich", "Ilyich", "Kirillovich",
        "Mikhailovich", "Nikitych", "Yegorovich",
        "Matveyevich", "Romanovich", "Vladimirovich"
    ];
    let fullname = maleNames[Math.floor(Math.random() * maleNames.length)]
    let surname = maleSurnames[Math.floor(Math.random() * maleSurnames.length)]
    let patronymic = malePatronymics[Math.floor(Math.random() * maleSurnames.length)]

    let response = await fetch(`${baseUrl}/api/v2/companies/${salonId}/attendance/records`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({

            "records": [
                {
                    "id": null,
                    "external_id": "",
                    "date": `${datesArray[0]}T${choosenSlot.time}:00`,
                    "staff_id": Number(`${masterData.id}`),
                    "client_id": null,
                    "length": 3600,
                    "comment": "",
                    "custom_color": "f44336",
                    "attendance_status": 0,
                    "is_instant_sms_notification_required": true,
                    "resource_instance_ids": [],
                    "label_ids": [],
                    "comer": null,
                    "custom_field_values": null,
                    "client_notification_settings": {
                        "sms_hours_before_visit": 1,
                        "email_hours_before_visit": 12
                    },
                    "attendance_service_items": [
                        {
                            "id": null,
                            "cost_per_unit": 2500,
                            "service_id": Number(`${masterData
                            .services_links[Math.floor(Math.random() * masterData.services_links.length)]
                            .service_id}`),
                            "quantity": 1,
                            "manual_cost": 1250,
                            "discount_percent": 50
                        }
                    ],
                    "attendance_good_items": [],
                    "clients_count": 1
                }
            ],
            "client": {
                "id": null,
                "phone": `7${Math.floor(1000000000 + Math.random() * 9000000000)}`,
                "name": `${fullname}`,
                "surname": `${surname}`,
                "patronymic": `${patronymic}`,
                "email": `${surname}@example.com`,
                "gender": null,
                "birthday": null,
                "custom_field_values": null,
                "agreements": null
            },
            "ignore_conflicts": true,
            "include": [
                "labels",
                "staff",
                "staff.employee",
                "transactions",
                "transactions.account",
                "attendance_good_items",
                "attendance_good_items.good",
                "attendance_good_items.staff",
                "attendance_service_items",
                "attendance_service_items.service",
                "attendance_service_items.resource_instances",
                "attendance_service_items.attendance_service",
                "attendance_service_items.attendance_service_composite",
                "attendance_service_items.attendance_service_composite.composite_service",
                "attendance_good_items.loyalty_abonement",
                "attendance_good_items.loyalty_certificate",
                "attendance_good_items.marks",
                "attendance_document",
                "resource_instances",
                "custom_field_values",
                "client_notification_settings",
                "comer",
                "comer.person",
                "client.agreements"
            ]

        })
    });
    let data = await response.json();
    if (!response.ok) {
        throw new Error(data.meta?.message || `Ошибка при создании записи`);
    }
    console.log(`Запись создана на ${data.data?.date} к ${masterData.name}`);
}

// Вспомогательные функции
function normalizeUrl(url) {
    try {
        const urlObj = new URL(url.includes('://') ? url : `https://${url}`);
        return `${urlObj.protocol}//${urlObj.hostname}`;
    } catch {
        throw new Error('Некорректный URL');
    }
}

async function getExtensionParams() {
    return new Promise(resolve => {
        chrome.storage.local.get(['baseUrl', 'bearerToken', 'salonId', 'userToken'], resolve);
    });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
    createOfflineRecord(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}


// Для ручного вызова
window.createOfflineRecord = createOfflineRecord;