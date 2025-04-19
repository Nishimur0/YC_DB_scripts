async function incomingPush(params = {}) {
    try {
        // 1. Получаем параметры из хранилища и объединяем с переданными
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...extensionParams,
            ...params
        };

        // 2. Проверяем обязательные параметры
        const required = ['baseUrl', 'appBearer', 'diversionPhone', 'crmToken'];
        const missing = required.filter(p => !currentParams[p]);
        if (missing.length) {
            throw new Error(`Отсутствуют обязательные параметры: ${missing.join(', ')}`);
        }

        // 3. Устанавливаем значения по умолчанию для необязательных параметров
        if (!currentParams.clientPhone) {
            currentParams.clientPhone = `7${Math.floor(100000000 + Math.random() * 900000000)}`;
            console.log('Используется сгенерированный номер:', currentParams.clientPhone);
        }

        if (!currentParams.callType) {
            currentParams.callType = 'incoming';
        }

        // 4. Нормализуем URL
        const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

        // 5. Подготавливаем заголовки
        const headers = {
            'Authorization': `Bearer ${currentParams.appBearer}`,
            'Accept': 'application/vnd.yclients.v2+json',
            'Content-Type': 'application/json'
        };

        // 6. Выполняем запрос
        await makeCallPush(
            cleanBaseUrl,
            headers,
            currentParams.crmToken,
            currentParams.diversionPhone,
            currentParams.clientPhone,
            currentParams.callType
        );

        // 7. Сохраняем параметры для будущих вызовов
        await saveCurrentParams(currentParams);

        return { success: true, phone: currentParams.clientPhone };

    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error;
    }
}

async function makeCallPush(baseUrl, headers, crmToken, diversion, phone, callType) {
    try {
        const result = await fetch(`${baseUrl}/api/v1/voip/integration`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                "command": "event",
                "type": `${callType}`,
                "crmToken": `${crmToken}`,
                "phone": `${phone}`,
                "diversion": `${diversion}`
            })
        });

        if (!result.ok) {
            const errorData = await result.json();
            throw new Error(errorData.meta?.message || `Ошибка HTTP: ${result.status}`);
        }

        console.log('Запрос выполнен успешно');
        return await result.json();

    } catch (error) {
        console.error('Ошибка при выполнении запроса:', error);
        throw error;
    }
}

function normalizeUrl(url) {
    try {
        const urlObj = new URL(url.includes('://') ? url : `https://${url}`);
        return `${urlObj.protocol}//${urlObj.hostname}`;
    } catch (error) {
        throw new Error(`Некорректный URL: ${url}`);
    }
}

async function saveCurrentParams(params) {
    return new Promise(resolve => {
        chrome.storage.local.set({
            crmToken: params.crmToken,
            diversionPhone: params.diversionPhone,
            callType: params.callType,
            appBearer: params.appBearer,
            baseUrl: params.baseUrl
        }, resolve);
    });
}

async function getExtensionParams() {
    return new Promise(resolve => {
        chrome.storage.local.get(
            ['baseUrl', 'appBearer', 'crmToken', 'clientPhone', 'diversionPhone', 'callType'],
            resolve
        );
    });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
    incomingPush(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}

// Для ручного вызова
window.incomingPush = incomingPush;