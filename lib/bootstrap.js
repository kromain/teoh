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

// Global wrapper around Mocha it method to synchronise async code via Fiber
test = function(description, testCase) {
    it(description, function(done){
        Fiber(function(){
            testCase();
            done();
        }).run();
    })
}

function parseArgs(){
    var options = {
        location: {abbr: "l", position: 0, required: true, help: "Location of test files (directories or single file)."},
        target: {abbr: "t", required: true, help: "Target IP address."},
        debug: {abbr: "d", flag: true, help: "Print debugging info"}
    }
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

function skynetRun(){
    console.log("\nSkyNet: The PlayStation remote control.\n".bold)

    var opts = parseArgs();
    var mocha = new Mocha({timeout: 10*60*1000, slow: 5*60*1000, reporter: "list"});
    var testFiles = findTestFiles(opts.location);

    testFiles.forEach(function(file){
        mocha.addFile(file);
    });

    var runMocha = function(){
        var defered = Q.defer();
        mocha.run(function(failures){
            process.on("exit", function () {
                process.exit(failures);
            });
            defered.resolve();
        });
        return defered.promise;
    }

    SkyNet.connectToRemote(opts.target).then(runMocha).then(SkyNet.disconnect);
}

module.exports = {
  run: skynetRun
}