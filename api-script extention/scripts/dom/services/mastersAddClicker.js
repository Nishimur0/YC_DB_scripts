(function() {
  const params = window.scriptParams || {
    count: 10,
    interval: 400
  };

  console.log('Запуск с параметрами:', params);

  const buttons = document.querySelectorAll('[data-locator="add_master_button"]');
  let clicksCount = 0;

  const timer = setInterval(() => {
    if (clicksCount >= params.count) {
      clearInterval(timer);
      return;
    }

    buttons.forEach(btn => btn.click());
    clicksCount++;
    console.log(`Клик #${clicksCount}`);
  }, params.interval);
})();