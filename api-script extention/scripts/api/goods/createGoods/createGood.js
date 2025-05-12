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

// Запускаем скрипт
async function createGoods(params = {}) {
    try {
        const extensionParams = await getExtensionParams();
        const currentParams = {
            ...params,
            ...extensionParams
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

        if (currentParams.goodCounter === undefined) {
            const storageData = await chrome.storage.local.get('goodCounter');
            currentParams.goodCounter = storageData.goodCounter || 0;
            await saveToStorage({ goodCounter: currentParams.goodCounter });
        }
        if (currentParams.goodCategoryCounter === undefined) {
            const storageData = await chrome.storage.local.get('goodCategoryCounter');
            currentParams.goodCategoryCounter = storageData.goodCategoryCounter || 0;
            await saveToStorage({ goodCategoryCounter: currentParams.goodCategoryCounter });
        }

        // Включаем маркировку товара
        await goodMarkEnabled(cleanBaseUrl, currentParams);
        let goodsCategoryData = await createCategoryTree(cleanBaseUrl, currentParams, currentParams.levels);

        await createGoodsInCategories(cleanBaseUrl, currentParams, goodsCategoryData);

    } catch (error) {
        showError(`Создание товаров не выполнено. Ошибка: ${error.message}`);
        throw error;
    }
}

//Создать категорию товара
async function createCategory(baseUrl, params, parentId, level) {
    let title = await generateCategoryTitle(params, level);
    let response = await fetch(`${baseUrl}/api/v1/goods_categories/${params.salonId}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'},
        body: JSON.stringify({
            title: title,
            parent_category_id: parentId
        })
    });

    if (!response.ok) throw new Error(`Ошибка создания категории: ${response.status}`);

    response = await response.json();
    console.log(response)
    return response;

}

// Генерация названия категории
function generateCategoryTitle(params, level) {
    let title = `[QA-GEN] Category ${params.goodCategoryCounter}`;
    if (params.category_name) {
        title = `[QA-GEN] ${params.category_name} ${params.goodCategoryCounter}`
    } else {
        let title = `[QA-GEN] Category ${params.goodCategoryCounter}`;
        saveToStorage({ goodCategoryCounter: ++params.goodCategoryCounter });
    };
    if (level > 0) title += ` Глубина ${level}`;
    return title;
}

// Создаем иерархию категорий
async function createCategoryTree(baseUrl, params, depth, parentId, currentLevel = 0) {
    const category = await createCategory(
        baseUrl,
        params,
        parentId,
        currentLevel
    );

    const result = {
        id: category.data.id,
        title: category.data.title,
        children: []
    };

    if (currentLevel < depth) {
        const child = await createCategoryTree(
            baseUrl,
            params,
            depth,
            category.data.id,
            currentLevel + 1
        );
        result.children.push(child);
    }

    return result;
}

// Создаем товары в категориях
async function createGoodsInCategories(baseUrl, params, categoryTree) {
    if (params.goodInEveryCategory === '1' || categoryTree.children.length === 0) {
        if (params.goodMarkCategory === '0') {
            await createGoodNotMarked(baseUrl, params, categoryTree.id);
        } else {
            await createGoodMarked(baseUrl, params, categoryTree.id);
        }
    }

    for (const child of categoryTree.children) {
        await createGoodsInCategories(baseUrl, params, child);
    }
}

function replacer(key, value) {
    if (typeof value === 'number') {
        return value.toFixed(2);  // Принудительно добавляем .00
    }
    return value;
}

//Создать товар
async function createGoodNotMarked(baseUrl, params, categoryId) {
    let actual_price = Math.floor(Math.random() * 1000);
    let price = actual_price + Math.floor(Math.random() * 100);
    let article = await generateArticle();
    let barcode = await generateBarcode();
    let title = `[QA-GEN] `;

    if (params.goodName) {
        title += `${params.goodName} ${params.goodCounter}`;
    } else {
        title += `custom good ${params.goodCounter}`;
    }
    saveToStorage({ goodCounter: ++params.goodCounter });

    try {
        const url = `${baseUrl}/api/v1/goods/${params.salonId}`;
        const body = {
            title: title,
            print_title: title,
            article: article,
            barcode: barcode,
            category_id: categoryId,
            cost: parseFloat(price.toFixed(2)) + 0.000001,
            actual_cost: parseFloat(actual_price.toFixed(2)) + 0.000001,
            sale_unit_id: 216760,
            service_unit_id: 216763,
            unit_equals: parseFloat((Math.floor(Math.random() * 1000) + 1).toFixed(2)) + 0.0000001,
            comment: "Товар создан с помощью скрипта"
        };

        console.log("Request Body:", body); // Логируем тело запроса

        const headers = {
            'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
            'Content-Type': 'application/json'
        };

        // Преобразуем body в строку JSON
        let response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(body)
        });

        if (response.status !== 200 && response.status !== 201) {
            const errorData = await response.json();
            if (response.status === 403) {
                showWarning(`Недостаточно прав (${response.status}): ${errorData.message || 'Нет доступа'}`);
            } else {
                showError(`Ошибка при создании товара (${response.status}): ${JSON.stringify(errorData.errors)}`);
            }
            return;
        }

        const responseData = await response.json();
        showSuccess(`Товар создан успешно: ${responseData.title || title}`);
    }
    catch (error) {
        showError(`Произошла ошибка: ${error.message}`);
    }
}


//Создать товар маркированный
async function createGoodMarked(baseUrl, params, categoryId) {
    let url = `${baseUrl}/goods/save/${params.salonId}/0/0/`;
    let actual_price = Math.floor(Math.random() * 1000);
    let price = actual_price + Math.floor(Math.random() * 100);
    let article = await generateArticle();
    let barcode = await generateBarcode();
    let title = `[QA-GEN] `;


    if (params.goodName) {
        title += `${params.goodName} ${params.goodCounter}`;
    } else {
        title += `custom good ${params.goodCounter}`;
    }
    switch (params.goodMarkCategory) {
        case '1':
            title += ' (Медицинские препараты / Лекарств)';
            break;
        case '2':
            title += ` (Духи / Туалетная вода)`;
            break;
        case '3':
            title += ` (Вода)`;
            break;
        case '4':
            title += ` (Обувь)`;
            break;
        case '6':
            title += ` (БАД)`;
            break;
        case '7':
            title += ` (Товары легкой промышленности)`;
            break;
    }
    saveToStorage({ goodCounter: ++params.goodCounter });

    let formData = new FormData();
    formData.append('title', title);
    formData.append('print_title', title);
    formData.append('article', article);
    formData.append('barcode', barcode);
    formData.append('category_id', categoryId);
    formData.append('sale_unit_id', 216760);
    formData.append('unit_equals', parseFloat(actual_price.toFixed(2)) + 0.0000001);
    formData.append('service_unit_id', 216763);
    formData.append('netto', '');
    formData.append('brutto', '');
    formData.append('cost', parseFloat(price.toFixed(2)) + 0.0000001);
    formData.append('actual_cost', parseFloat(actual_price.toFixed(2)) + 0.0000001);
    formData.append('is_goods_mark_enabled', '1');
    formData.append('goods_mark_category_id', params.goodMarkCategory);
    formData.append('kkm_settings_id', 0);
    formData.append('tax_variant', -1);
    formData.append('vat_id', -1);
    formData.append('critical_amount', 0);
    formData.append('desired_amount', 0);
    formData.append('comment', 'Создано с помощью скрипта');

    try {
        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Accept': 'application/json'
            },
            body: formData
        });

        if (!response.ok) {
            let errorData = await response.json();
            throw new Error(`Не удалось создать товар: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        showError(`Ошибка при создании маркированного товара: ${error.message}`);
        throw error;
    }
}

//Включить маркировку товара
async function goodMarkEnabled(baseUrl, params) {
    let url = `${baseUrl}/api/v1/company/${params.salonId}/goods_mark/settings/enable`
    try {
        let response = await fetch(url, {
            method: `POST`,
            headers: {
                'Authorization': `Bearer ${params.bearerToken}, User ${params.userToken}`,
                'Content-Type': 'application/json'}
        });
        if (response.status !== 200) {
            showError(`Ошибка при включении маркировки товара. Код ошибки: ${response.status}`);
        }
    } catch {}
}

async function generateArticle() {
    const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const prefix = letters.charAt(Math.floor(Math.random() * letters.length)) +
    letters.charAt(Math.floor(Math.random() * letters.length));
    const numbers = Math.floor(1000 + Math.random() * 9000); // 1000-9999
    return `${prefix}${numbers}`;
}

async function generateBarcode() {
    let barcode = '';
    for (let i = 0; i < 12; i++) {
        barcode += Math.floor(Math.random() * 10);
    }
    let sum = 0;
    for (let i = 0; i < 12; i++) {
        sum += parseInt(barcode[i]) * (i % 2 === 0 ? 1 : 3);
    }
    const checksum = (10 - (sum % 10)) % 10;

    return barcode + checksum;
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

// Автозапуск при наличии параметров
if (window.scriptParams) {
    createGoods(window.scriptParams).catch(e => {
        console.error('Автозапуск не удался:', e);
    });
}

// Для ручного вызова
window.createGoods = createGoods;