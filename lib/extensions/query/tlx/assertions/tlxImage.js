//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, DriverInstance, module */

chai.use(function (_chai, utils) {
    utils.addMethod(chai.Assertion.prototype, "tlxImage", function(){
        var expectedId = arguments[0];
        var expectedUrl = arguments[1];
        var image = tlx.getComponent("#" + expectedId);
        tlx.checkTag(image, "img");
        tlx.checkAttr(image, "src", expectedUrl);
    });
});