async function callbackPhone(params = {}) {
    try {
        // 1. Получаем и объединяем параметры
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...extensionParams,
            ...params
        };

        // 2. Валидация
        const required = ['baseUrl', 'salonId', 'appBearer', 'applicationId'];
        const missing = required.filter(p => !currentParams[p]);
        if (missing.length) throw new Error(`Missing: ${missing.join(', ')}`);

        // 3. Нормализация URL
        const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

        // 4. Заголовки
        const bearerHeaders = {
            'Authorization': `Bearer ${currentParams.appBearer}`,
            'Accept': 'application/vnd.yclients.v2+json',
            'Content-Type': 'application/json'
        };

        await callbackPhoneRequest(cleanBaseUrl, currentParams.salonId, bearerHeaders, currentParams.applicationId)

        //выбрасываем ошибку если все плохо
    } catch (error) {
        console.error('Ошибка в цепочке:', error);
        throw error;
    }
}


async function callbackPhoneRequest(baseUrl, salonId, headers, applicationId) {
    result = await fetch(`${baseUrl}/marketplace/partner/callback`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            "salon_id": Number(`${salonId}`),
            "application_id": 38,
            "api_key": "eqw",
            "webhook_urls": []
    })
    })

    if (!result.ok) {
        throw new Error(data.meta?.message || `HTTP ${response.status}`);
    } else {
        console.log(`Подключено`)
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
        chrome.storage.local.get(['baseUrl', 'salonId'], resolve);
    });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
    callbackPhone(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}

// Для ручного вызова
window.callbackPhone = callbackPhone;