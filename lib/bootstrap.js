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
var glob = require("glob");
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
        debug: {flag: true, help: "Print debugging info"},
        reporter: {help: "Alias to Mocha --reporter option"},
        grep: {help: "Alias to Mocha --grep option"},
        pause: {help: "Pause given amount of seconds between each test"},
        position: {help: "Specify location of remote window (optional, requires driver support)"}
    };
    return nomnom.options(options).script("./skynet").parse();
}

function findTestFiles(location) {
    return lookupFiles(location, true);
}

/**
 * Note: adapted from bin/_mocha source code.
 * Is there a npm module to accomplish this recursive lookup?
 */
function lookupFiles(location, recursive) {
  var files = [];

  if (!fs.existsSync(location)) {
    if (fs.existsSync(location + ".js")) {
      location += ".js";
    } else {
      files = glob.sync(location);
      if (!files.length) {
        throw new Error("cannot resolve path (or pattern) '" + location + "'");
      }
      return files;
    }
  }

  var stat = fs.statSync(location);
  if (stat.isFile()) {
    return [ location ];
  }

  fs.readdirSync(location).forEach(function(file){
    file = path.join(location, file);
    var stat = fs.statSync(file);
    if (stat.isDirectory()) {
      if (recursive) files = files.concat(lookupFiles(file, recursive));
      return;
    }
    if (!stat.isFile() || path.basename(file)[0] == ".") {
        return;
    }
    files.push(file);
  });

  return files;
}

function skynetRun(options){
    console.log("\nSkyNet: The PlayStation remote control.\n".bold);

    var opts = options || parseArgs();

    var mocha = new Mocha({
        timeout: 10*60*1000,
        slow: 5*60*1000,
        reporter: opts.reporter || "list",
        grep: opts.grep || false,
        ui: "tdd"
    });
    var testFiles = findTestFiles(opts.location);

    if (opts.pause > 0) {
        mocha.addFile(__dirname + path.sep + "mocha-after-each-pause.js");
        SkyNet.markPause(opts.pause);
    }

    testFiles.forEach(function(file){
        mocha.addFile(file);
    });

    var disconnect = function(failures){
        SkyNet.disconnect.call(SkyNet);
        return Q.resolve(failures);
    };

    var runMocha = function(){
        var defered = Q.defer();
        mocha.run(function(failures){
            process.on("exit", function() {
                process.exit(failures);
            });
            defered.resolve(failures);
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

    // Return promise chain for the case where SkyNet was
    // programmatically called by another script
    return SkyNet.connectToRemote(opts.target, opts.driver, opts.position)
        .then(runMocha, remoteConnectFailed)
        .then(disconnect);
}

module.exports = {
  run: skynetRun
};