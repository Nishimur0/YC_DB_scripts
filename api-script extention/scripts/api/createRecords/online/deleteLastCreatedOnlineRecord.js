async function deleteLastCreatedOnlineRecord(params = {}) {
    try {
        // 1. Получаем и объединяем параметры
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...extensionParams,
            ...params
        };

        // 2. Валидация
        const required = ['baseUrl', 'bearerToken', 'userToken', 'salonId', 'recordHash', 'recordId'];
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

        //5. Включить досутп к удалению и переносу записей
        let data = await fetch (`${cleanBaseUrl}/api/v1/company/${currentParams.salonId}/settings/online/record`, {
            method: 'PUT',
            headers: userTokenHeaders,
            body: JSON.stringify({
                "is_allow_change_record": true,
                "is_allow_change_prepaid_record": false,
                "allow_change_record_delay_step": 0,
                "is_allow_delete_record": true,
                "is_allow_delete_prepaid_record": false,
                "allow_delete_record_delay_step": 0
            })
        })
        let result = await data.json()
        if (!result.success) {
            throw new Error(`Ошибка включения доступа к удалению записей: ${result.error.message}`);
        }

        //6. Удаляем запись
        data = await fetch(`${cleanBaseUrl}/api/v1/user/records/${currentParams.recordId}/${currentParams.recordHash}`, {
            method: 'DELETE',
            headers: bearerHeaders
        })
        result = await data.json()
        if (!result.success) {
            throw new Error(`Ошибка при удалении записи: ${result.error.message}`);
        }

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
        chrome.storage.local.get(['baseUrl', 'bearerToken', 'salonId', 'userToken', 'recordHash', 'recordId'], resolve);
    });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
    deleteLastCreatedOnlineRecord(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}

// Для ручного вызова
window.deleteLastCreatedOnlineRecord = deleteLastCreatedOnlineRecord;