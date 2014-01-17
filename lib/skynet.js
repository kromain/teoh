//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/********************************************************************
 *                                                                  *
 *  Main SkyNet file: defines the SkyNet remote control methods     *
 *                                                                  *
 ********************************************************************/

// Base URL to dart server
var dartBaseUrl = "https://ussfrsdart02.am.sony.com/dart/rest/test/";
var dart_URL = null;

// Creating a superagent object to make HTTP requests to DART
var request = require("superagent");

// This will be the remote inspector instance which we use globally for query as well as driver eventually
RemoteInspector = require("chrome-remote-interface");
RemoteInspectorInstance = null;

// These are the abstraction layers to query state from Swordfish
WhatsNewQueryAdapter = require("./adapters/query/whatsNew.js");
OrbisStoreQueryAdapter = require("./adapters/query/orbisStore.js");

// SkyNet object defines the main object available during test
var SkyNet = function(){
    this.driver = null;
}

function connectRemoteInspector(remoteIp) {

    var defered = Q.defer();

    var remote = {
        host: remoteIp,
        port: 860,
        chooseTab: function (tabs) {
            //console.warn("Got tabs list from PS4 WebKit\n\n");
            //console.warn("Current tabs:\n\n", tabs);
            var i, wsUrl;
            for (i=0; i<tabs.length; i++) {
                // On PS4 the remote debugger URL websocket is missing :(
                if (!tabs[i].webSocketDebuggerUrl) {
                    wsUrl = "ws://" + remoteIp + ":860/devtools/page/" + tabs[i].pageID;
                    tabs[i].webSocketDebuggerUrl = wsUrl
                }
                if (tabs[i].processDisplayName === "Live Area / Store / RegCAM") {
                    return i;
                }
            }
            return 0;
        }
    }

    RemoteInspector(remote, function (inspector) {
        with (inspector) {
            console.warn("\nConnected to PS4 Remote Inspector!".green);
            Runtime.enable();
            RemoteInspectorInstance = {
                evaluate: function(jsCode){
                    var fiber = Fiber.current;
                    setTimeout(function(){
                        inspector.Runtime.evaluate({expression: jsCode}, function(err, output){
                            if (!err && output && output.result) {
                                fiber.run(output.result.value);
                            } else {
                                if (output && output.wasThrown && output.result.description) {
                                    throw new Error("Exception thrown in inspector runtime:" + output.result.description)
                                } else {
                                    throw new Error("Unknown error in inspector runtime");
                                }
                            }
                        });
                    }, 500);
                    return Fiber.yield();
                },
                disconnect: function(){
                    inspector.close()
                }
            }

            defered.resolve();
        }
    }).on('error', function (err) {
        console.warn(err)
        console.error("Cannot connect to Remote PS4 Remote Inspector".red);
        defered.reject();
    });

    return defered.promise;
}

function connectDriver(remoteIp, driver) {
    var defered = Q.defer();

    if (driver === "inspector") {
        defered.resolve();
    } else {
        // POST to create test instance "SkyNet test xx.xx.xx.xx" <== remoteIp
        request
        .post(dartBaseUrl + 'definitions/by-name/infinityTest-' + remoteIp +'/run/PS4 Tests')
        .end(function(res){
            testRunId = res.text;
            //console.log(res.text);
            processURL = dartBaseUrl + "instances/by-id/" + testRunId + "/processId";
            //console.log(processURL);

            setTimeout(function(){
                request
                    .get(processURL)
                    .end(function(proc_Id){
                        processId = proc_Id.text;
                        dart_URL = dartBaseUrl + 'instances/process/'+ processId + '/vinput/'
                        console.log("\nConnected to process %s on DART server %s!".green, processId, dart_URL);

                        defered.resolve();

                        request
                            .post(dart_URL + 'close')
                            .end(function(temp){
                                //console.log("closed initial connection");
                                //console.log(temp.text);
                            });
                    });
            },6000);
        });
    }

    return defered.promise;
}


SkyNet.prototype.connectToRemote = function(remoteIp, driver){
    console.log("Connecting to remoteIp: %s", remoteIp);

    this.driver = driver;

    var defered = Q.defer();

    // We always connect to Remote Inspector for now
    connectRemoteInspector(remoteIp).then(function(){
        connectDriver(remoteIp,driver).then(function(){
            console.log("\nConnected to PS4 DevKit! Start tests...".green);
            defered.resolve();
        });
    });

    return defered.promise;
}

SkyNet.prototype.disconnect = function(){
    RemoteInspectorInstance.disconnect();
    console.warn("\nDisconnected from PS4 Remote Inspector!".green);

    if (this.driver === "dart") {
        setTimeout(function(){
            request
                .post(dartBaseUrl + "instances/by-id/" + testRunId + "/stop")
                .end(function(){
                    console.warn("\nDisconnected from DART server".green);
                });
        },2000);
    }
}

SkyNet.prototype.wait = function(ms){
    var fiber = Fiber.current;
    setTimeout(function(){
        fiber.run();
    }, ms);
    Fiber.yield();
}

SkyNet.prototype.login = function(location) {
    var dartScript = "TODO";
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

    console.log("\n\tLog in to PS4 and got to %s".grey, location)
    setTimeout(function(location){
        // TODO: Execute DART script
        console.log("\tLogged in %s".grey, location);
        fiber.run();

    }, 500, location);

    Fiber.yield();
}

function pressWithInspector(key) {

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
            return;
    }

    var jsCode = [];
    jsCode.push('var keyDown = document.createEvent("Events");');
    jsCode.push('keyDown.initEvent("keydown", true, true, window, false, false, false, false, ' + keyCode + ', ' + keyCode + ');');
    jsCode.push('keyDown.keyCode = ' + keyCode + ';');
    jsCode.push('keyDown.which = ' + keyCode + ';');
    jsCode.push('keyDown.charCode = ' + keyCode + ';');
    jsCode.push('document.getElementById("trili").dispatchEvent(keyDown);');

    jsCode.push('var keyUp = document.createEvent("Events");');
    jsCode.push('keyUp.initEvent("keyup", true, true, window, false, false, false, false, ' + keyCode + ', ' + keyCode + ');');
    jsCode.push('keyUp.keyCode = ' + keyCode + ';');
    jsCode.push('keyUp.which = ' + keyCode + ';');
    jsCode.push('keyUp.charCode = ' + keyCode + ';');
    jsCode.push('document.getElementById("trili").dispatchEvent(keyUp);');

    console.log("\tPress %s".grey, key);
    if (RemoteInspectorInstance.evaluate(jsCode.join("\n"))) {
        console.warn("\tPressed %s".grey, key);
    } else {
        console.warn("\tError when pressing key %s".red, key);
    }
}

function pressWithDart(key) {

    var keyCode;
    switch (key) {
        case "UP": keyCode = "up"; break;
        case "DOWN": keyCode = "down"; break;
        case "RIGHT": keyCode = "right"; break;
        case "LEFT": keyCode = "left"; break;
        case "CROSS": keyCode = "cross"; break;
        case "CIRCLE": keyCode = "circle"; break;
        case "TRIANGLE": keyCode = "triangle"; break;
        case "SQUARE": keyCode = "square"; break;
        case "L1": keyCode = "l1"; break;
        case "R1": keyCode = "r1"; break;
        case "L2": keyCode = "l2"; break;
        case "R2": keyCode = "r2"; break;
        case "L3": keyCode = "l3"; break;
        case "R3": keyCode = "r3"; break;
        case "OPTIONS": keyCode = "start"; break;
        case "PLAYSTATION": keyCode = "playstation"; break;
        default:
            throw new Error("Key " + key + " is not supported!");
            return;
    }

    var fiber = Fiber.current;

    console.log("\tPress %s".grey, key);

    // console.log("keyCode: " + keyCode);
    // console.log("dart_URL : " + dart_URL);
    // console.log("data : press(" + keyCode + ",once)");

    setTimeout(function(){
        request
            .post(dart_URL + 'open')
            .send('press(' + keyCode + ',once)')
            .end(function(status_resp){
                //console.log("response: " + status_resp.text);
                console.warn("\tPressed %s".grey, key);
                setTimeout(function(){
                    fiber.run();
                }, 2000)
            });
    },2000);

    Fiber.yield();
}

SkyNet.prototype.press = function(key){
    if (this.driver === "inspector") {
        pressWithInspector(key);
    } else {
        pressWithDart(key);
    }

}

SkyNet.prototype.whatsNew = new WhatsNewQueryAdapter();
SkyNet.prototype.store = new OrbisStoreQueryAdapter();

function createSkyNet(){
    return new SkyNet();
}

module.exports = {
  rise: createSkyNet
}