// deviceBrowserCheck.js
function deviceBrowserCheck() {
  const ua = navigator.userAgent;
  let browser = "";

  // --- Browser-Erkennung ---
  if (ua.indexOf("Chrome") !== -1 && ua.indexOf("Edge") === -1 && ua.indexOf("OPR") === -1) {
    browser = "Google Chrome";
  } else if (ua.indexOf("Firefox") !== -1) {
    browser = "Mozilla Firefox";
  } else if (ua.indexOf("Edge") !== -1) {
    browser = "Microsoft Edge";
  } else if (ua.indexOf("Safari") !== -1 && ua.indexOf("Chrome") === -1) {
    browser = "Safari";
  } else if (ua.indexOf("Opera") !== -1 || ua.indexOf("OPR") !== -1) {
    browser = "Opera";
  } else if (ua.indexOf("YaBrowser") !== -1) {
    browser = "YaBrowser";
  } else {
    browser = "Andere";
  }

  // --- Mobilgeräte-Erkennung ---
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua);

  // --- Kompatibilitätsprüfung ---
  if (isMobile) {
    document.body.innerHTML = `
      <div class="jspsych-display-element" style="max-width:600px;margin:2em auto;text-align:center;">
        <p><strong>Dieses Experiment kann nur auf einem Desktop- oder Laptop-Computer durchgeführt werden.</strong></p>
        <p>Bitte wechseln Sie zu einem kompatiblen Gerät, um fortzufahren.</p>
      </div>
    `;
    return false;
  }

  if (browser === "Safari") {
    document.body.innerHTML = `
      <div class="jspsych-display-element" style="max-width:600px;margin:2em auto;text-align:center;">
        <p><strong>Diese Studie ist mit Safari nicht kompatibel.</strong></p>
        <p>Bitte verwenden Sie <b>Chrome</b> oder <b>Firefox</b> auf einem Desktop- oder Laptop-Computer, um fortzufahren.</p>
      </div>
    `;
    return false;
  }

  // --- Wenn alle Prüfungen bestanden sind ---
  window.browserName = browser;
  return true;
}


/*let browser = "";

// CHROME
if (navigator.userAgent.indexOf("Chrome") !== -1) {
    console.log("Google Chrome");
    browser = "Google Chrome";
}
// FIREFOX
else if (navigator.userAgent.indexOf("Firefox") !== -1) {
    console.log("Mozilla Firefox");
    browser = "Mozilla Firefox";
}
// INTERNET EXPLORER
else if (navigator.userAgent.indexOf("MSIE") !== -1) {
    console.log("Internet Exploder");
    browser = "Internet Exploder";
}
// EDGE
else if (navigator.userAgent.indexOf("Edge") !== -1) {
    console.log("Internet Exploder");
    browser = "Internet Exploder";
}
// SAFARI
else if (navigator.userAgent.indexOf("Safari") !== -1) {
    console.log("Safari");
    browser = "Safari";
}
// OPERA
else if (navigator.userAgent.indexOf("Opera") !== -1) {
    console.log("Opera");
    browser = "Opera";
}
// YANDEX BROWSER
else if (navigator.userAgent.indexOf("YaBrowser") !== -1) {
    console.log("YaBrowser");
    browser = "YaBrowser";
}
// OTHERS
else {
    console.log("Others");
    browser = "Others";
}

// Remove fullscreen if Safari
if (browser === "Safari") {
    alert("This study is not compatible with Safari. Please use another browser.");
}*/