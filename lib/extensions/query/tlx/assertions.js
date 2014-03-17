//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, DriverInstance, module */

// TODO: as we add more assertions, figure a way to autoload or lazy load them!

require("./assertions/tlxImage");
require("./assertions/tlxLabel");
require("./assertions/text");

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

module.exports = {
	checkTag: checkTag,
	checkAttr: checkAttr,
	checkText: checkText
};