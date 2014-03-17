//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/********************************************************************
 *                                                                  *
 *  SkyNet bootstrap file: bootstraps and runs mocha based on args  *
 *                                                                  *
 ********************************************************************/

var Mocha = require("mocha");
var fs = require("fs");
var path = require("path");
var nomnom = require("nomnom");
var colors = require("colors");

// Globally expose our test tools
Q = require("q");
sinon = require("sinon");
chai = require("chai");
should = require("chai").Should();
sinonChai = require("sinon-chai");
chai.use(sinonChai);
Fiber = require('fibers');

// SkyNet object defines the main object available during test
SkyNet = require("./skynet.js").rise();

require("./mocha-fiber-hack.js");

function parseArgs(){
    var options = {
        location: {abbr: "l", position: 0, required: true, help: "Location of test files (directories or single file)."},
        target: {abbr: "t", required: true, help: "Target IP address."},
        driver: {abbr: "d", required: true, help: "Driver to use (inspector or dart or selenium).", choices: ["inspector","dart", "selenium"]},
        debug: {flag: true, help: "Print debugging info"}
    };
    return nomnom.options(options).script("./skynet").parse();
}

function findTestFiles(location) {
    var testFiles = [];
    try {
        if (location.substr(-3) === ".js") {
            if (fs.existsSync(location)) {
                testFiles.push(location);
            } else {
                throw new Error("file does not exits");
            }
        } else {
            fs.readdirSync(location).filter(function(file){
                return file.substr(-3) === ".js";
            }).forEach(function(file){
                testFiles.push(path.join(location, file));
            });
        }
    } catch (e) {
        console.log("Invalid test location: %s (%s)".red, location, e.message);
        process.exit(1);
    }
    return testFiles;
}

function skynetRun(options){
    console.log("\nSkyNet: The PlayStation remote control.\n".bold);

    var opts = options || parseArgs();
    var mocha = new Mocha({
        timeout: 10*60*1000,
        slow: 5*60*1000,
        reporter: "list",
        ui: "tdd"
    });
    var testFiles = findTestFiles(opts.location);

    testFiles.forEach(function(file){
        mocha.addFile(file);
    });

    var disconnect = SkyNet.disconnect.bind(SkyNet);

    var runMocha = function(){
        var defered = Q.defer();
        mocha.run(function(failures){
            process.on("exit", function() {
                process.exit(failures);
            });
            defered.resolve();
        });
        return defered.promise;
    };

    var remoteConnectFailed = function(){
        console.warn("Failed to connect to remote!".red);
    };

    // Load required driver
    switch (opts.driver) {
        case "inspector":
            SkyNet.use("inspector", "./extensions/driver/webinspector/webinspector.js");
            break;
        case "dart":
            SkyNet.use("dart", "./extensions/driver/dart/dart.js");
            break;
        case "selenium":
            SkyNet.use("selenium", "./extensions/driver/webdriver/webdriver.js");
            break;
    }

    // Load all the other extensions too for now (ideally,
    // it should be specified by the tester as an option)
    SkyNet.use("tlx", "./extensions/query/tlx/tlx.js");
    SkyNet.use("whatsNew", "./extensions/query/swordfish/whatsNew.js");
    SkyNet.use("psStore", "./extensions/query/swordfish/orbisStore.js");

    SkyNet.connectToRemote(opts.target, opts.driver)
        .then(runMocha, remoteConnectFailed)
        .then(disconnect);
}

module.exports = {
  run: skynetRun
};