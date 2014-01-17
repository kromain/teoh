var orbisStore = function(){}

orbisStore.prototype.open = function(product) {
    var deepLink = "psns:browse?";
    if (!product) {
        deepLink += "top=game";
    } else {
        deepLink += "product=" + product;
    }

    RemoteInspectorInstance.evaluate("sce.launchApp('" + deepLink + "')");
}

Object.defineProperty(orbisStore.prototype, "activeElementText", {
    get: function getActiveElementText(){
        var jsCode = [];
        jsCode.push("var labels = [].concat(sf.activeElement.query('marquee_hl'),sf.activeElement.query('marquee_horizontal'),sf.activeElement.query('label'));");
        jsCode.push("var I18N = require('I18n');");
        jsCode.push("labels.map(function(l){ if (l.text[l.text.length - 1] !== '}') { return l.text; } else { return I18N.lang(l.text.substring(2, l.text.length - 1)); } }).join(' ').trim();");
        return RemoteInspectorInstance.evaluate(jsCode.join("\n"));
    }
});

module.exports = orbisStore;