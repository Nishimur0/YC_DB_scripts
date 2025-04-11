async function yclientsAuth(params = {}) {
  try {
    // 1. Получаем и объединяем параметры
    const extensionParams = await getExtensionParams();
    const currentParams = {
      ...extensionParams,
      ...params
    };

    // 2. Валидация
    const required = ['baseUrl', 'bearerToken', 'login', 'password'];
    const missing = required.filter(p => !currentParams[p]);
    if (missing.length) throw new Error(`Missing: ${missing.join(', ')}`);

    // 3. Нормализация URL
    const cleanBaseUrl = normalizeUrl(currentParams.baseUrl);

    // 4. Выполнение запроса
    const response = await fetch(`${cleanBaseUrl}/api/v1/auth`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${currentParams.bearerToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        login: currentParams.login,
        password: currentParams.password
      })
    });

    // 5. Обработка ответа
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.meta?.message || `HTTP ${response.status}`);
    }

    // Обрабатываем оба формата ответа
    const userToken = data.user_token || data.data?.user_token;
    if (!userToken) {
      throw new Error('Токен не найден в ответе сервера');
    }

    // 6. Сохранение результата
    await saveToStorage({
      userToken,
      lastAuthData: { // Сохраняем дополнительные данные
        userId: data.id,
        userName: data.name,
        userPhone: data.phone
      }
    });

    console.log('Успешная авторизация. User ID:', data.id);
    return data;

  } catch (error) {
    console.error('Ошибка авторизации:', error.message);
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
    chrome.storage.local.get(['baseUrl', 'bearerToken'], resolve);
  });
}

async function saveToStorage(data) {
  return new Promise(resolve => {
    chrome.storage.local.set(data, resolve);
  });
}

// Автозапуск при наличии параметров
if (window.scriptParams) {
  yclientsAuth(window.scriptParams).catch(e => {
    console.error('Автозапуск не удался:', e);
  });
}

// Для ручного вызова
window.yclientsAuth = yclientsAuth;