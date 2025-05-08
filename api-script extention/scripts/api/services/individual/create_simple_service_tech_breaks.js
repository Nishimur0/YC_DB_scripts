async function createSimpleService(params = {}) {
    try {
        // 1. Получение параметров с дефолтным значением для serviceCounter
        const extensionParams = await getExtensionParams();
        let currentParams = {
            serviceCounter: 0,
            ...extensionParams,
            ...params
        };

        // 2. Валидация
        const required = ['baseUrl', 'bearerToken', 'userToken', 'salonId'];
        const missing = required.filter(p => !currentParams[p]);
        if (missing.length) {
            throw new Error(`Missing required parameters: ${missing.join(', ')}`);
        }

        // 3. Нормализация URL
        const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

        // 4. Создать категорию, если ее нет
        let categoryExist = await checkCategory(cleanBaseUrl, currentParams);
        if (!currentParams.categoryId || currentParams.createCategory === null || !categoryExist) {
            console.log('Creating new category...');
            const categoryData = await createCategory(cleanBaseUrl, currentParams);
            currentParams.categoryId = categoryData.id;

            await saveToStorage({ categoryId: categoryData.id });
            console.log('New category created, ID:', categoryData.id);

            if (window.scriptParams) {
                window.scriptParams.categoryId = categoryData.id;
            }
        }

        // 5. Создать услугу
        console.log('Параметры услуги:', {
            salonId: currentParams.salonId,
            categoryId: currentParams.categoryId,
            serviceCounter: currentParams.serviceCounter
        });
        const serviceData = await createService(cleanBaseUrl, currentParams);
        currentParams.serviceCounter = serviceData.newServiceCounter;
        await saveToStorage({ serviceCounter: currentParams.serviceCounter });

        console.log('Успех:', serviceData);

        return {
            categoryId: currentParams.categoryId,
            serviceData
        };

    } catch (error) {
        console.error('Error in createSimpleService:', error.message);
        throw error;
    }
}

async function createCategory(baseUrl, params) {
    let currentCounter = params.categoryCounter || 0;
    let newCounter = currentCounter + 1;

    const url = `${baseUrl}/api/v1/service_categories/${params.salonId}`;

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: params.categoryTitle || `[QA-GEN] New category ${newCounter}`,
            salon_id: params.salonId
        })
    });

    const responseText = await response.text();
    if (!response.ok) {
        throw new Error(`Ошибка создания категории: ${response.status} ${response.statusText} - ${responseText}`);
    }

    try {
        const data = responseText ? JSON.parse(responseText) : {};
        await saveToStorage({ categoryCounter: newCounter });
        return data;
    } catch (e) {
        throw new Error(`Не удалось распарсить ответ: ${responseText}`);
    }
}

async function createService(baseUrl, params) {
    let price = Math.floor(Math.random() * (5000 - 100 + 1)) + 100;
    const requiredServiceParams = ['salonId', 'categoryId'];
    const missing = requiredServiceParams.filter(p => !params[p]);
    if (missing.length) {
        throw new Error(`Нет параметров услуги: ${missing.join(', ')}`);
    }

    let currentServiceCounter = params.serviceCounter || 0;
    let newServiceCounter = currentServiceCounter + 1;

    await saveToStorage({ serviceCounter: newServiceCounter });

    let serviceTitle = !params.serviceTitle || params.serviceTitle === '' || params.serviceTitle === 'undefined'
    ? `[QA-GEN] New simple service ${newServiceCounter}`
    : `[MANUAL] ${params.serviceTitle} ${newServiceCounter}`;

    const tech_break = 300 + 300 * Math.floor(Math.random() * 12);
    console.log('Технический перерыв:', tech_break);

    const response = await fetch(`${baseUrl}/api/v1/company/${params.salonId}/services`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title: serviceTitle,
            booking_title: serviceTitle,
            print_title: serviceTitle,
            category_id: params.categoryId,
            price_max: price,
            price_min: price,
            comment: '',
            capacity: 0,
            autopayment_before_visit_time: 1,
            schedule_template_type: 2,
            seance_search_finish: 86400,
            seance_search_start: 0,
            seance_search_step: 900,
            service_type: 1,
            is_abonement_autopayment_enabled: 1,
            date_from: "1970-01-01",
            date_to: "1970-01-01",
            dates: [],
            duration: 3600,
            is_multi: false,
            is_need_limit_date: false,
            repeat_visit_days_step: null,
            resources: [],
            step: 0,
            tax_variant: -1,
            vat_id: -1,
            price_prepaid_amount: 0,
            price_prepaid_percent: "0",
            online_invoicing_status: 0,
            technical_break_duration: tech_break
        })
    });

    const responseText = await response.text();
    if (!response.ok) {
        throw new Error(`Ошибка создания услуги: ${response.status} ${response.statusText} - ${responseText}`);
    }

    try {
        const data = responseText ? JSON.parse(responseText) : {};
        let serviceId = data.data?.id;

        if (params.includeMasters == true && serviceId) {
            await setMastersInServices(baseUrl, params, serviceId);
        }

        return {
            newServiceCounter,
            data
        };
    } catch (e) {
        throw new Error(`Не удалось распарсить ответ: ${responseText}`);
    }
}

async function setMastersInServices(baseUrl, params, serviceId) {
    let url = `${baseUrl}/api/v1/company/${params.salonId}/staff/`;

    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        }
    });

    const responseText = await response.text();
    if (!response.ok) {
        throw new Error(`Ошибка: ${response.status} ${response.statusText} - ${responseText}`);
    }

    try {
        const mastersData = responseText ? JSON.parse(responseText) : {};
        let listOfMastersArray = mastersData.data?.filter(master =>
        master.fired === 0 && master.is_deleted === false
        ) || [];

        if (listOfMastersArray.length === 0) {
            throw new Error('Нет доступных мастеров');
        }

        let mastersIdArray = listOfMastersArray.map(master => master.id);
        await setMasters(baseUrl, params, serviceId, mastersIdArray);
    } catch (e) {
        throw new Error(`Не удалось обработать список мастеров: ${responseText}`);
    }
}

async function setMasters(baseUrl, params, serviceId, mastersList) {
    if (!mastersList || mastersList.length === 0) {
        throw new Error('Список мастеров пуст');
    }

    const resultArray = mastersList.map(masterId => ({
        master_id: parseInt(masterId),
        technological_card_id: 0,
        hours: 1,
        minutes: 0
    }));

    const requestData = {
        service_id: serviceId,
        master_settings: resultArray,
        resource_ids: [],
        translations: []
    };

    const url = `${baseUrl}/api/v1/company/${params.salonId}/services/links`;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const responseText = await response.text();
        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status} ${response.statusText} - ${responseText}`);
        }

        // Пустой ответ считается успешным
        return responseText ? JSON.parse(responseText) : { success: true };
    } catch (error) {
        console.error('Ошибка в setMasters:', error);
        throw new Error(`Не удалось назначить мастеров: ${error.message}`);
    }
}

async function checkCategory(baseUrl, params) {
    if (!params.categoryId) {
        await saveToStorage({ categoryId: null });
        return false;
    }

    const url = `${baseUrl}/api/v1/service_category/${params.salonId}/${params.categoryId}`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        await saveToStorage({ categoryId: null });
        return false;
    }
    return true;
}

// Helper functions
function normalizeUrl(url) {
    try {
        const urlObj = new URL(url.includes('://') ? url : `https://${url}`);
        return `${urlObj.protocol}//${urlObj.hostname}`;
    } catch (e) {
        throw new Error(`Invalid URL: ${url}`);
    }
}

async function getExtensionParams() {
    try {
        if (chrome?.storage?.local?.get) {
            return new Promise(resolve => {
                chrome.storage.local.get([
                    'baseUrl',
                    'bearerToken',
                    'salonId',
                    'userToken',
                    'categoryId',
                    'categoryCounter',
                    'includeMasters',
                    'serviceCounter',
                    'serviceAmount'
                ], resolve);
            });
        }
        return {};
    } catch (e) {
        console.warn('Failed to get extension params:', e);
        return {};
    }
}

async function saveToStorage(data) {
    try {
        if (chrome?.storage?.local?.set) {
            return new Promise(resolve => {
                chrome.storage.local.set(data, resolve);
            });
        }
    } catch (e) {
        console.warn('Failed to save to storage:', e);
    }
}

// Автозапуск
if (window.scriptParams) {
    createSimpleService(window.scriptParams).catch(e => {
        console.error('Auto-start failed:', e);
    });
}

window.createSimpleService = createSimpleService;