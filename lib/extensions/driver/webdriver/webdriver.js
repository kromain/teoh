//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

var WebDriver = function(){};

var WebDriverSync = require("webdriver-http-sync");

var WebDriverInstance = null;

function connectToWebDriver(remoteIp) {

    var defered = Q.defer();

    var capabilities = {
        browserName: "chrome",
        chromeOptions: {
            args: ["--disable-web-security", "--console"],
            prefs: {
                "browser": {
                    "window_placement": {
                        "always_on_top": false,
                        "bottom": 1037,
                        "left": 1926,
                        "maximized": false,
                        "right": 3591,
                        "top": 9,
                        "work_area_bottom": 1050,
                        "work_area_left": 1920,
                        "work_area_right": 3600,
                        "work_area_top": 0
                    },
                    "window_placement_DevToolsApp": {
                        "always_on_top": false,
                        "bottom": 1158,
                        "left": 125,
                        "maximized": true,
                        "right": 1763,
                        "top": 22,
                        "work_area_bottom": 1158,
                        "work_area_left": 0,
                        "work_area_right": 1920,
                        "work_area_top": 22
                    }
                },
               "devtools": {
                    "dock_side": "dock_bottom",
                    "split_location": 607,
                    "v_split_location": 943
               },
            },
            detach: true
        }
    };

    WebDriverInstance = new WebDriverSync("http://" + remoteIp + "/wd/hub", capabilities);

    console.warn("\nConnected to Remote Web Driver!".green);

    // URL should be configurable? or should TLX driver auto start the
    // selenium server and the static server?
    WebDriverInstance.navigateTo("http://localhost:8008/swordfish/SkyNet.html");

    SkyNet.waitFor("window.SkyNet !== undefined", "SkyNet").then(function(){
        defered.resolve();
    }, function(){
        defered.reject();
    });

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
WebDriver.prototype.disconnect = disconnectWebDriver;

module.exports = WebDriver;