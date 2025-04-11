// Проверка загрузки контентного скрипта
console.log("Content script loaded");

// Извлечение ключа задачи из URL
function getIssueKeyFromUrl() {
  const url = window.location.href;
  console.log("Current URL:", url);
  const issueKeyMatch = url.match(/tracker\.yandex\.ru\/([^/?#]+)/);
  const issueKey = issueKeyMatch ? issueKeyMatch[1] : null;
  console.log("Extracted issue key:", issueKey);
  return issueKey;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received in content script:", request);
  if (request.action === "getIssueKey") {
    const issueKey = getIssueKeyFromUrl();
    sendResponse({ issueKey: issueKey });
  }
});
