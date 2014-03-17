//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, DriverInstance, module */

var component = require("./component");
var assertions = require("./assertions");

var TLX = function(){};

TLX.prototype.load = component.loadComponent;
TLX.prototype.goTo = component.goToComponent;
TLX.prototype.getComponent = component.getComponent;

TLX.prototype.checkTag = assertions.checkTag;
TLX.prototype.checkAttr = assertions.checkAttr;
TLX.prototype.checkText = assertions.checkText;

// Dummy placeholder object for chainable mocha BDD syntax
TLX.prototype.component = {};

module.exports = TLX;