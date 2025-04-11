async function createOnlineRecord(params = {}) {
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

    //4.1 Наборы данных
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

    //Вне контекста. Отключить задержку перед записью
    let response = await fetch(`${cleanBaseUrl}/api/v1/company/${currentParams.salonId}/settings/timeslots`, {
      method: `PUT`,
      headers: userTokenHeaders,
      body: JSON.stringify({
          "weekdays_settings": [
            {
              "weekday": 1,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 2,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 3,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 4,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 5,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 6,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            },
            {
              "weekday": 7,
              "timeslots": [],
              "setting": {
                "grid_first_timeslot": 0,
                "grid_last_timeslot": 86400,
                "grid_display_step": 5400,
                "grid_nearest_timeslot_delay": 0,
                "grid_base_type": "timeslots",
                "is_grid_flexible": null
              }
            }
          ],
          "dates_settings": []

      })
    })
    let data = await response.json();
    if (!response.ok) {
      throw new Error(data.meta?.message || `HTTP ${response.status}`);
    }
    console.log(`Отключена задержка перед записью`)

    //5. Выполнение запроса
    response = await fetch(`${cleanBaseUrl}/api/v1/book_services/${currentParams.salonId}`, {
      method: 'GET',
      headers: bearerHeaders
    })

    //6. Обработка ответа
    data = await response.json();

    if (!response.ok) {
      throw new Error(data.meta?.message || `HTTP ${response.status}`);
    }
    console.log(`Получены услуги:`, data.success)

    let servicesWithoutPrepaid = data.data?.services.filter(service => service.prepaid == 'forbidden');
    if (servicesWithoutPrepaid.length == 0) {
      throw new Error(`Нет доступных услуг без предоплаты`)
    }
    console.log(`Услуги без предоплаты:`, servicesWithoutPrepaid) //На всякий вывести которые доступны

    let serviceId = servicesWithoutPrepaid[Math.floor(Math.random() * servicesWithoutPrepaid.length)].id; //Выбираем
    //случайную услугу

    // 7. Выбираем сотрудника
    response = await fetch(`${cleanBaseUrl}/api/v1/book_staff/${currentParams.salonId}?service_ids=${serviceId}`, {
      method: 'GET',
      headers: bearerHeaders
    })
    // Обработка ответа
    data = await response.json();
    if (!response.ok) {
      throw new Error(data.meta?.message || `HTTP ${response.status}`);
    }
    console.log(`Получены сотрудники:`, data.success)
    let staffWithoutPrepaid = data.data?.filter(staff => staff.prepaid == 'forbidden');
    if (staffWithoutPrepaid.length == 0) {
      throw new Error(`Нет доступных сотрудников без предоплаты`)
    }
    console.log(`Сотрудники без предоплаты:`, staffWithoutPrepaid) //На всякий вывести которые доступны
    masterId = staffWithoutPrepaid[Math.floor(Math.random() * staffWithoutPrepaid.length)].id; //Выбираем случайного мастера

    // 8. Найти свободные даты
    response = await fetch(`${cleanBaseUrl}/api/v1/book_dates/${currentParams.salonId}?service_ids=${serviceId}&staff_ids=${masterId}`, {
      method: 'GET',
      headers: bearerHeaders
    })

    // Обработка ответа
    data = await response.json();
    if (!response.ok) {
      throw new Error(data.meta?.message || `HTTP ${response.status}`);
    }
    console.log(`Получены свободные даты:`, data.success)
    if (data.data?.booking_dates.length == 0) {
      console.log(`Нет свободных дат`) //На всякий вывести что нет свободных дат
    }
    console.log(`Найденные даты:`, data.data?.booking_dates)
    let nearestDate = data.data?.booking_dates[0]
    console.log(`Ближайшая дата:`, nearestDate) //На всякий вывести ближайшую дату

    //9. Найти ближайший сеанс
    response = await fetch(`${cleanBaseUrl}/api/v1/book_times/${currentParams.salonId}/${masterId}/${nearestDate}?service_ids=${serviceId}`, {
      method: 'GET',
      headers: bearerHeaders
    })
    // Обработка ответа
    data = await response.json();
    if (!response.ok) {
      throw new Error(data.meta?.message || 'HTTP ' + response.status
      )}
    if (data.data?.length == 0 ) {
      throw new Error(`Нет свободного времени`)
    }
    let nearestTime = data.data?.[0].time
    console.log(`Дата: ${nearestDate}, Сеанс: ${nearestTime}`)

    // 10. Создать запись
    let fullname = maleNames[Math.floor(Math.random() * maleNames.length)]
    let surname = maleSurnames[Math.floor(Math.random() * maleSurnames.length)]
    let patronymic = malePatronymics[Math.floor(Math.random() * maleSurnames.length)]

    response = await fetch(`${cleanBaseUrl}/api/v1/book_record/${currentParams.salonId}`, {
      method: 'POST',
      headers: userTokenHeaders,
      body: JSON.stringify({
        "phone": `7${Math.floor(1000000000 + Math.random() * 9000000000)}`,
        "fullname": `${fullname}`,
        "surname": `${surname}`,
        "patronymic": `${patronymic}`,
        "email": `${surname}@example.com`,
        "comment": "Онлайн запись из коллекции",
        "type": "mobile",
        "notify_by_sms": 6,
        "notify_by_email": 24,
        "appointments": [
          {
            "id": "",
            "services": [
              serviceId
            ],
            "staff_id": masterId,
            "datetime": `${nearestDate} ${nearestTime}`
          }
        ]
      })
    })
    data = await response.json();
    console.log(`Запись создана:`, data.success)
    chrome.storage.local.set(
      { recordHash: data.data?.[0].record_hash,
        recordId: data.data?.[0].record_id },
      () => {
        console.log(`hash записи: ${data.data?.[0].record_hash}, record_id: ${data.data?.[0].record_id}`);
      }
    );

  //выбрасываем ошибку если все плохо
  } catch (error) {
    console.error('Ошибка в цепочке:', error);
    throw error;
  }
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
  createOnlineRecord(window.scriptParams).catch(e => {
    console.error('Автозапуск не удался:', e);
  });
}

// Для ручного вызова
window.createOnlineRecord = createOnlineRecord;