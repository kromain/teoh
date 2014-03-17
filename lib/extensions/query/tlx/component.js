//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/* jshint strict: false */
/* global chai, console, DriverInstance, module */

function loadComponent(component, attributes) {
    DriverInstance.evaluate("window.SkyNet.load('" + component + "',"+JSON.stringify(attributes)+");");
}

function goToComponent(url, params) {
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
}

function getComponent(selector){
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

module.exports = {
    loadComponent: loadComponent,
    goToComponent: goToComponent,
    getComponent: getComponent
};