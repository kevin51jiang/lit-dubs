chrome.browserAction.onClicked.addListener(function(activeTab){
    var url = "";
    chrome.tabs.query({'active': true, 'windowId': chrome.windows.WINDOW_ID_CURRENT},
    function(tabs){
        url = tabs[0].url;
        var newURL = "http://visualyze.tech/#" + url;
        chrome.tabs.create({ url: newURL });
    }
    );
  });