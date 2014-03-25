//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

var Dart = function(){};

// Base URL to dart server
var dartBaseUrl = "https://ussfrsdart02.am.sony.com/dart/rest/test/";
var dart_URL = null;

// Creating a superagent object to make HTTP requests to DART
var request = require("superagent");

// Yo, I heard you like driver in your driver so I put a driver in your driver
var webInspector = require("../webinspector/webinspector.js");
var webInspectorInstance = null;

function connectToWebInspector(remoteIp) {
    webInspectorInstance = new webInspector();
    return webInspectorInstance.connect(remoteIp);
}

function connectToDartServer(remoteIp) {
    var defered = Q.defer();


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
                    dart_URL = dartBaseUrl + 'instances/process/'+ processId + '/vinput/';
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

    return defered.promise;
}

function connectToRemote(remoteIp) {
    var defered = Q.defer();

    // We always connect to Remote Inspector for now
    connectToWebInspector(remoteIp).then(function(){
        connectToDartServer(remoteIp).then(function(){
            console.log("\nConnected to PS4 DevKit! Start tests...".green);
            defered.resolve();
        }, function(){
            defered.reject();
        });
    }, function(){
        defered.reject();
    });

    return defered.promise;
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
                }, 2000);
            });
    },2000);

    Fiber.yield();
}

function diconnectFromRemote(){
    webInspectorInstance.disconnect();
    console.warn("\nDisconnected from PS4 Remote Inspector!".green);

    setTimeout(function(){
        request
            .post(dartBaseUrl + "instances/by-id/" + testRunId + "/stop")
            .end(function(){
                console.warn("\nDisconnected from DART server".green);
            });
    },2000);
}

function evaluateWithInspector(jsCode) {
    return webInspectorInstance.evaluate(jsCode);
}

/**
 * Dart driver public API
 */
Dart.prototype.connect = connectToRemote;
Dart.prototype.pressKey = pressWithDart;
Dart.prototype.evaluate = evaluateWithInspector;
Dart.prototype.navigateTo = function(){};
Dart.prototype.disconnect = diconnectFromRemote;

module.exports = Dart;