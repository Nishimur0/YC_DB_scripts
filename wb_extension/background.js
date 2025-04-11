chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked, sending message to content script.");
  
  chrome.tabs.sendMessage(tab.id, { action: "getIssueKey" }, (response) => {
    if (chrome.runtime.lastError) {
      console.error("Error sending message:", chrome.runtime.lastError.message);
      return;
    }
    
    if (response && response.issueKey) {
      const issueKey = response.issueKey;
      const newUrl = `https://t4u.yclients.tech/create_wb/${issueKey}`;
      console.log("Issue key found:", issueKey);
      console.log("Opening new URL:", newUrl);
      chrome.tabs.create({ url: newUrl });
    } else {
      console.log("Issue key not found.");
    }
  });
});
