//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/********************************************************************
 *                                                                  *
 *  Main SkyNet file: defines the SkyNet remote control methods     *
 *                                                                  *
 ********************************************************************/

DriverInstance = null;

function connectToRemote(remoteIp, driver){
    console.log("Connecting to remote %s using %s", remoteIp, driver);

    if (extensions[driver]) {
        this.driver = driver;
        DriverInstance = new extensions[driver]();
        return DriverInstance.connect(remoteIp);
    } else {
        console.warn("Could not find driver module".red);
        return Q.reject();
    }
}

function disconnect(){
    DriverInstance.disconnect();
}

function login(location) {
    // TODO!

    /*var dartScript = "TODO";
    if (location === "WHATS_NEW") {
        location = "What's New";
        //dartScript = "";
    } else if (location === "STORE") {
        location = "Swordfish Store";
        //dartScript = "";
    } else {
        console.log("\tInvalid location specified after login %s".red, location);
        return;
    }

    var fiber = Fiber.current;

    console.log("\n\tLog in to PS4 and got to %s".grey, location);
    setTimeout(function(location){
        // TODO: Execute DART script
        console.log("\tLogged in %s".grey, location);
        fiber.run();

    }, 500, location);

    Fiber.yield();*/
}

/**
 * Wait for a given period of time in milliseconds
 */
function wait(timeout){
    var fiber = Fiber.current;
    setTimeout(function(){
        fiber.run();
    }, timeout);
    Fiber.yield();
}

/**
 * Wait for a specific expression to become true
 *
 * Log will show message if specified otherwise expression
 *
 * You can specify the amount of time to wait in milliseconds using
 * timeout (default 3s) and you can tweak the polling interval (default
 * is 25ms)
 *
 * If we are running in a Fiber, waitFor can be call synchronously. If
 * we do not detect a Fiber, it will return a promise.
 *
 */
function waitFor(expression, message, timeout, interval){
    var usePromise = false, defered;
    var fiber = Fiber.current;
    if (!fiber) {
        usePromise = true;
        defered = Q.defer();
    }
    timeout = timeout || 3000;
    interval = interval || 25;
    var totalTime = 0;
    console.warn("Waiting up to %dms for %s".grey, timeout, message ? message : expression);
    var waitForInterval = setInterval(function(){
        var result = DriverInstance.evaluate("return ("+ expression + ");");
        //console.warn(result);
        if (result === true) {
            //console.warn("success");
            if (usePromise) {
                defered.resolve();
            } else {
                fiber.run();
            }
            clearInterval(waitForInterval);
        }
        totalTime += interval;
        if (totalTime >= timeout) {
            //console.warn("fail");
            if (usePromise) {
                defered.reject();
            } else {
                console.warn(this.test);
                throw new Error("Failed to wait for condition");
            }
            clearInterval(waitForInterval);
        }
    }, interval);
    if (usePromise) {
        return defered.promise;
    } else {
        Fiber.yield();
    }
}

/**
 * Key handling will be handled by the driver
 */
function pressKey(key){
    DriverInstance.pressKey(key);
}

/**
 * Include extensions/drivers/plugins on demand
 */
var extensions = function(){};
function use(namespace, modulePath){
    if (!/^[a-zA-Z]{3,}$/.test(namespace)) {
        throw new Error("Invalid extension namespace name: " + namespace);
    } else if (extensions[namespace]) {
        throw new Error("An extension is already in use at: " + namespace);
    } else {
        var mod = require(modulePath);
        Object.defineProperty(extensions, namespace, { value: mod });
        global[namespace] = new extensions[namespace]();
        Object.defineProperty(global[namespace], "SkyNet", { value: this});
    }
}

/**
 * Public API
 */

var SkyNet = function(){
    this.driver = null;
};

SkyNet.prototype.connectToRemote = connectToRemote;
SkyNet.prototype.disconnect = disconnect;
SkyNet.prototype.login = login;
SkyNet.prototype.press = pressKey;
SkyNet.prototype.wait = wait;
SkyNet.prototype.waitFor = waitFor;
SkyNet.prototype.use = use;

function createSkyNet(){
    var _skynet = new SkyNet();

    // Load all the drivers per default
    _skynet.use("inspector", "./extensions/driver/webinspector/webinspector.js");
    _skynet.use("dart", "./extensions/driver/dart/dart.js");
    _skynet.use("selenium", "./extensions/driver/webdriver/webdriver.js");

    // Load all the other extensions too for now (should be specified by the tester)
    _skynet.use("tlx", "./extensions/query/tlx/tlx.js");
    _skynet.use("whatsNew", "./extensions/query/swordfish/whatsNew.js");
    _skynet.use("psStore", "./extensions/query/swordfish/orbisStore.js");

    return _skynet;
}

module.exports = {
  rise: createSkyNet
};