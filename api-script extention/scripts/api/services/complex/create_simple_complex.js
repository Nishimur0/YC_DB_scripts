// Проверяем инициализацию функций логирования
if (!window._loggingFunctionsInitialized) {
    window.showProgress = (message, level = 'info') => {
        if (window.scriptParams?.showProgress) {
            window.scriptParams.showProgress(message, level);
        } else {
            console.log(`[${level}] ${message}`);
        }
    };

    window.showWarning = (message) => showProgress(message, 'warning');
    window.showSuccess = (message) => showProgress(message, 'success');
    window.showError = (message) => showProgress(message, 'error');
    window.showInfo = (message) => showProgress(message, 'info');

    window._loggingFunctionsInitialized = true;
}

async function createSimpleComplex(params = {}) {
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
        if (!currentParams.complexCategoryId || currentParams.createCategory === null || !categoryExist) {
            console.log('Creating new category...');
            const categoryData = await createCategory(cleanBaseUrl, currentParams);
            currentParams.complexCategoryId = categoryData.id;

            await saveToStorage({ complexCategoryId: categoryData.id });
            console.log('New category created, ID:', categoryData.id);

            if (window.scriptParams) {
                window.scriptParams.complexCategoryId = categoryData.id;
            }
        }

        // 5. Создать услугу
        console.log('Параметры услуги:', {
            salonId: currentParams.salonId,
            complexCategoryId: currentParams.complexCategoryId,
            serviceCounter: currentParams.serviceCounter
        });

        let service1, service2, service3;

        let serviceData1 = await createService(cleanBaseUrl, currentParams);
        currentParams.serviceCounter = serviceData1.newServiceCounter;
        await saveToStorage({ serviceCounter: currentParams.serviceCounter });
        service1 = serviceData1.serviceId;
        service1PriceMin = serviceData1.data.data?.price_min;
        service1PriceMax = serviceData1.data.data?.price_max;
        service1duration = serviceData1.data.data?.duration;

        let serviceData2 = await createService(cleanBaseUrl, currentParams);
        currentParams.serviceCounter = serviceData2.newServiceCounter;
        await saveToStorage({ serviceCounter: currentParams.serviceCounter });
        service2 = serviceData2.serviceId;
        service2PriceMin = serviceData2.data.data?.price_min;
        service2PriceMax = serviceData2.data.data?.price_max;
        service2duration = serviceData2.data.data?.duration;

        let serviceData3 = await createService(cleanBaseUrl, currentParams);
        currentParams.serviceCounter = serviceData3.newServiceCounter;
        await saveToStorage({ serviceCounter: currentParams.serviceCounter });
        service3 = serviceData3.serviceId;
        service3PriceMin = serviceData3.data.data?.price_min;
        service3PriceMax = serviceData3.data.data?.price_max;
        service3duration = serviceData3.data.data?.duration;

        console.log('Успех:', serviceData1, serviceData2, serviceData3);

        // 6. Создать комплекс услуг
        let serviceComplexData = await createComplex(cleanBaseUrl, service1, service2, service3,
            service1PriceMin, service1PriceMax, service2PriceMin, service2PriceMax, service3PriceMin,
            service3PriceMax, service1duration, service2duration, service3duration, currentParams);

        showSuccess(`Создан комплекс услуг: ${serviceComplexData.data.title}`)
        return {
            complexCategoryId: currentParams.complexCategoryId,
            serviceData1,
            serviceData2,
            serviceData3
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
            title: params.categoryTitle || `[QA-GEN] New complex category ${newCounter}`,
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
    const requiredServiceParams = ['salonId', 'complexCategoryId'];
    const missing = requiredServiceParams.filter(p => !params[p]);
    if (missing.length) {
        throw new Error(`Нет параметров услуги: ${missing.join(', ')}`);
    }

    let currentServiceCounter = params.serviceCounter || 0;
    let newServiceCounter = currentServiceCounter + 1;

    await saveToStorage({ serviceCounter: newServiceCounter });

    let serviceTitle = !params.serviceTitle || params.serviceTitle === '' || params.serviceTitle === 'undefined'
    ? `[QA-GEN] New complex service ${newServiceCounter}`
    : `[MANUAL] ${params.serviceTitle} ${newServiceCounter}`;

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
            category_id: params.complexCategoryId,
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
            technical_break_duration: 0
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
            data,
            serviceId
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
    if (!params.complexCategoryId) {
        await saveToStorage({ complexCategoryId: null });
        return false;
    }

    const url = `${baseUrl}/api/v1/service_category/${params.salonId}/${params.complexCategoryId}`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        await saveToStorage({ complexCategoryId: null });
        return false;
    }
    return true;
}

async function createComplex(baseUrl, service1, service2, service3,
service1PriceMin, service1PriceMax, service2PriceMin, service2PriceMax, service3PriceMin, service3PriceMax,
service1length, service2length, service3length, params) {

    let complexDuration;
    if (params.serviceProcedure === "sequential" || params.serviceProcedure === "sequential_multi") {
        complexDuration = service1length + service2length + service3length;
    } else {complexDuration = Math.max(service1length, service2length, service3length);}

    let prices = [service1PriceMin, service2PriceMin, service3PriceMin]
    let priceMin = 0;
    if (params.pricing_type === "manual") {
        let newPrices = distributeTotal(prices, params.manualPrice)
        service1PriceMin = newPrices[0];
        service2PriceMin = newPrices[1];
        service3PriceMin = newPrices[2];
        service1PriceMax = newPrices[0];
        service2PriceMax = newPrices[1];
        service3PriceMax = newPrices[2];
        priceMin = service1PriceMin + service2PriceMin + service3PriceMin;
        let discount = 0;
    } else if (params.pricing_type === "discount") {
        let totalMin = service1PriceMin + service2PriceMin + service3PriceMin;
        priceMin = Math.floor(totalMin * (1 - parseFloat(params.discount) / 100));
        newPrices = distributeTotal(prices, priceMin)
        service1PriceMin = newPrices[0];
        service2PriceMin = newPrices[1];
        service3PriceMin = newPrices[2];
        service1PriceMax = newPrices[0];
        service2PriceMax = newPrices[1];
        service3PriceMax = newPrices[2];
        discount = params.discount;
    } else if (params.pricing_type === "sum") {
        priceMin = 0;
        service1PriceMin = service1PriceMin;
        service2PriceMin = service2PriceMin;
        service3PriceMin = service3PriceMin;
        service1PriceMax = service1PriceMax;
        service2PriceMax = service2PriceMax;
        service3PriceMax = service3PriceMax;
        discount = 0;
    }


    const complexUrl = `${baseUrl}/api/v1/company/${params.salonId}/services/composites?
    include[]=translations&include[]=salon_group_title&include[]=salon_group_service_link
    &include[]=kkm_settings_id&include[]=composite_details`;

    let title = '[QA-GEN] Complex';
    const procedureTitles = {
        sequential: ' Последовательный (1 спец.)',
        sequential_multi: ' Последовательный (разн. спец-ты)',
        parallel: ' Параллельный'
    };
    if (params.serviceProcedure && procedureTitles[params.serviceProcedure]) {
        title += procedureTitles[params.serviceProcedure];
    }

    if (params.pricing_type) {
        switch (params.pricing_type) {
            case 'sum':
                title += ' Суммарная стоимость';
                break;
            case 'discount':
                title += ` Со скидкой ${params.discount || 0}%`;
                break;
            case 'manual':
                title += ` Ручная стоимость ${params.manualPrice || 0}`;
                break;
        }
    }

    const requestComplexData = {
        title: `${title}`,
        duration: complexDuration,
        category_id: params.complexCategoryId,
        is_multi: false,
        price_min: priceMin,
        price_max: priceMin,
        booking_details: {
            is_online_available: true,
            description: "",
            dates: [],
            date_from: "1970-01-01",
            date_to: "1970-01-01",
            seance_search_start: 0,
            seance_search_finish: 86400,
            booking_title: `${title}`,
            online_invoicing_status: 0,
            price_prepaid_amount: 0,
            price_prepaid_percent: 0,
            schedule_template_type: 2
        },
        description: "",
        price_discount_percent: discount,
        exec_order: `${params.serviceProcedure}`,
        pricing_type: `${params.pricing_type}`,
        links: [
            {
                service_id: service1,
                position: 1,
                price_min: service1PriceMin,
                price_max: service1PriceMax
            },
            {
                service_id: service2,
                position: 2,
                price_min: service2PriceMin,
                price_max: service2PriceMax
            },
            {
                service_id: service3,
                position: 3,
                price_min: service3PriceMin,
                price_max: service3PriceMax
            }
        ]
    };
    try {
        const response = await fetch(complexUrl, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestComplexData)
        });

        const responseText = await response.text();
        if (!response.ok) {
            throw new Error(`Ошибка: ${response.status} ${response.statusText} - ${responseText}`);
        }

        // Пустой ответ считается успешным
        return responseText ? JSON.parse(responseText) : { success: true };
    } catch (error) {
        throw new Error(`Не удалось создать комплекс: ${error.message}`);
    }
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
                    'complexCategoryId',
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

function distributeTotal(prices, total) {
    // Проверки
    if (prices.some(p => p <= 0)) throw new Error("Все цены должны быть положительными");
    if (total < prices.length) throw new Error(`Сумма не может быть меньше ${prices.length}`);

    const sum = prices.reduce((a, b) => a + b, 0);
    let distributed = prices.map(p => Math.floor((p / sum) * total));

    // Распределение остатка
    let remainder = total - distributed.reduce((a, b) => a + b, 0);

    if (remainder > 0) {
        const fractions = prices.map((p, i) => ({
            index: i,
            fraction: ((p / sum) * total) % 1
        })).sort((a, b) => b.fraction - a.fraction);

        for (let i = 0; i < remainder; i++) {
            distributed[fractions[i].index]++;
        }
    }

    return distributed;
}

// Автозапуск
if (window.scriptParams) {
    createSimpleComplex(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}

window.createSimpleComplex = createSimpleComplex;