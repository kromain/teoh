//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, WebDriverInstance, module */

var TLX = function(){};

// Test for WebDriveInstance
// We need to require selenium

function getElement(selector){
    var result = DriverInstance.evaluate("return window.SkyNet.getComponent('" + selector + "');");

    var found = new chai.Assertion(selector);
    found.assert(result !== false, "Could not find component #{this}");

    function component(id, tagName, attributes, text){
        this.id = id;
        this.tagName = tagName;
        this.attributes = attributes;
        this.text = text;
    }

    component.prototype.toString = function(){
        return this.tagName + "#" + this.id;
    };

    return new component(result.id, result.tagName, result.attributes, result.text);
}

function checkTag(component, tag) {
    var hasTag = new chai.Assertion(component.toString());
    hasTag.assert(
        component.tagName === tag,
        "expected #{this} component to be a <" + tag + ">",
        "expected #{this} component to not be a <" + tag + ">"
    );
}

function checkAttr(component, attr, value) {
    var hasAttr = new chai.Assertion(component.toString());
    hasAttr.assert(
        !!component.attributes[attr],
        "expected #{this} component to have an attribute " + attr
    );

    var hasValue = new chai.Assertion(component.toString() + "." + attr);
    hasValue.assert(
        component.attributes[attr] === value,
        "expected #{this} to be: " + value,
        "expected #{this} to not be: " + value,
        component.attributes[attr],
        value
    );
}

function checkText(component, text) {
    var check = new chai.Assertion(component.toString());
    check.assert(
        component.text === text, // TODO: regex
        "expected #{this} to contain text",
        "expected #{this} to not contain text",
        component.text,
        text
    );
}



/*
 *
 * Extract to TLX assertions
 *
 */
chai.use(function (_chai, utils) {

    utils.addMethod(chai.Assertion.prototype, "tlxImage", function(){
        var expectedId = arguments[0];
        var expectedUrl = arguments[1];
        var image = getElement("#" + expectedId);
        checkTag(image, "img");
        checkAttr(image, "src", expectedUrl);
    });

    utils.addMethod(chai.Assertion.prototype, "tlxLabel", function(){
        var expectedId = arguments[0];
        var expectedText = arguments[1];
        var label = getElement("#" + expectedId);
        checkTag(label, "label");
        checkAttr(label, "text", expectedText);
    });

    utils.addMethod(chai.Assertion.prototype, "text", function(){
        var expectedId = arguments[0];
        var expectedText = arguments[1];
        var comp = getElement("#" + expectedId);
        checkText(comp, expectedText);
    });
});

TLX.prototype.load = function(component, attributes) {
        console.warn(component);
        DriverInstance.evaluate("window.SkyNet.load('" + component + "',"+JSON.stringify(attributes)+");");
    };

TLX.prototype.goTo =function(url, params) {
        if (params instanceof Object) {
            var attributes = [];
            var value;
            Object.keys(params).forEach(function(attr){
                if (typeof params[attr] === "string") {
                    value = encodeURIComponent(params[attr]);
                } else if (params[attr] instanceof Object) {
                    value = encodeURIComponent(JSON.stringify(params[attr]));
                } else {
                    value = params[attr];
                }
                attributes.push(attr + "=" + value);
            });
            if (attributes.length) {
                url += "?" + attributes.join("&");
            }
        }
        console.warn("Open TLX URL: %s\n", url.grey);
        DriverInstance.evaluate("window.SkyNet.goTo('"+url+"');");
        SkyNet.waitFor("window.SkyNet.tlxLoaded", "TLX URL to load");
    };

TLX.prototype.component = {};

module.exports = TLX;