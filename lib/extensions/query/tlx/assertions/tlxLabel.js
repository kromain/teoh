//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, DriverInstance, module */

chai.use(function (_chai, utils) {
    utils.addMethod(chai.Assertion.prototype, "tlxLabel", function(){
        var expectedId = arguments[0];
        var expectedText = arguments[1];
        var label = tlx.getComponent("#" + expectedId);
        tlx.checkTag(label, "label");
        tlx.checkAttr(label, "text", expectedText);
    });
});