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
        jsCode.push("labels.map(function(l){ return sf.translate(l.text); }).join(' ').trim();");
        return RemoteInspectorInstance.evaluate(jsCode.join("\n"));
    }
});

module.exports = orbisStore;