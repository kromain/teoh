//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/********************************************************************
 *                                                                  *
 *  Main SkyNet file: defines the SkyNet remote control methods     *
 *                                                                  *
 ********************************************************************/

RemoteInspector = require("chrome-remote-interface");
RemoteInspectorInstance = null;
WhatsNewQueryAdapter = require("./adapters/query/whatsNew.js");
OrbisStoreQueryAdapter = require("./adapters/query/orbisStore.js");

// SkyNet object defines the main object available during test
var SkyNet = function(){
    this.driver = null;
}

SkyNet.prototype.connectToRemote = function(remoteIp){
    console.log("Connecting to remoteIp: %s", remoteIp);

    // POST to create test instance "SkyNet test xx.xx.xx.xx" <== remoteIp
    // POST to get processID and build DART_URL
    // save DART_URL

    var defered = Q.defer();

    // TODO: defer this to the command adapter

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
            console.warn("\nConnected to PS4 DevKit!".green);
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
        console.error("Cannot connect to Remote PS4 DevKit".red);
        defered.reject();
    });

    return defered.promise;
}

SkyNet.prototype.disconnect = function(){
    RemoteInspectorInstance.disconnect();
    console.warn("\nDisconnected from PS4 DevKit!".green);
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

SkyNet.prototype.press = function(key){
    // TODO: defer this to the command adapter

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


    // POST to DART_URL to send key

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

SkyNet.prototype.whatsNew = new WhatsNewQueryAdapter();
SkyNet.prototype.store = new OrbisStoreQueryAdapter();

function createSkyNet(){
    return new SkyNet();
}

module.exports = {
  rise: createSkyNet
}