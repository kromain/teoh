//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

var WebDriver = function(){};

var WebDriverSync = require("webdriver-http-sync");

var WebDriverInstance = null;

function connectToWebDriver(remoteIp) {

    var defered = Q.defer();

    var left, right, top, bottom;
    var matcher = /^([0-9]+)x([0-9]+),([0-9]+)x([0-9]+)$/;
    var position = SkyNet.option("position");
    if (position && matcher.test(position)) {
        var split = matcher.exec(position);
        left = parseInt(split[1]);
        top = parseInt(split[2]);
        right = left + parseInt(split[3]);
        bottom = top + parseInt(split[4]);
    }

    var capabilities = {
        browserName: "chrome",
        chromeOptions: {
            args: ["--disable-web-security", "--console"],
            prefs: {
                "browser": {
                    "window_placement": {
                        "bottom": bottom,
                        "left": left,
                        "maximized": false,
                        "right": right,
                        "top": top
                    }
                }
            },
            detach: true
        }
    };

    WebDriverInstance = new WebDriverSync("http://" + remoteIp + "/wd/hub", capabilities);

    console.warn("\nConnected to Remote Web Driver!".green);
    defered.resolve();

    return defered.promise;
}

function pressWithWebDriver(key) {

    var keyCode;
    switch (key) {
        case "UP": keyCode = 140; break;
        case "DOWN": keyCode = 141; break;
        case "RIGHT": keyCode = 143; break;
        case "LEFT": keyCode = 142; break;
        case "CROSS": keyCode = 13; break;
        case "CIRCLE": keyCode = 146; break;
        case "TRIANGLE": keyCode = 147; break;
        case "L1": keyCode = 116; break;
        case "R1": keyCode = 117; break;
        case "L2": keyCode = 118; break;
        case "R2": keyCode = 119; break;
        case "L3": keyCode = 120; break;
        case "R3": keyCode = 121; break;
        case "SQUARE": keyCode = 113; break;
        case "OPTIONS": keyCode = 114; break;
        default:
            throw new Error("Key " + key + " is not supported!");
    }

    var trili = WebDriverInstance.getElement("#trili");

    console.log("\tPress %s".grey, key);
    if (trili.type(key)) {
        console.warn("\tPressed %s".grey, key);
    } else {
        console.warn("\tError when pressing key %s".red, key);
    }
}

function evaluateWithWebDriver(jsCode) {
    return WebDriverInstance.evaluate(jsCode);
}

function navigateToWithWebDriver(url) {
    return WebDriverInstance.navigateTo(url);
}

function disconnectWebDriver(){
    WebDriverInstance.close();
    console.warn("\nDisconnected from Web Driver!".green);
}

/**
 * Web Inspector driver public API
 */
WebDriver.prototype.connect = connectToWebDriver;
WebDriver.prototype.pressKey = pressWithWebDriver;
WebDriver.prototype.evaluate = evaluateWithWebDriver;
WebDriver.prototype.navigateTo = navigateToWithWebDriver;
WebDriver.prototype.disconnect = disconnectWebDriver;

module.exports = WebDriver;