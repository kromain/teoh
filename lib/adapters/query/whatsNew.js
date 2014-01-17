var whatsNew = function(){}

whatsNew.prototype.getTileInfo = function(){

    var jsCode = [];
    jsCode.push('var grid = window.sf.currentView.query("#feed_grid")[0];');
    jsCode.push('var tile = grid.selected.tileData;');
    jsCode.push('"Found " + tile.storyType + " story at " + tile.debugId + ": \\"" + tile.caption.replace(tile.debugId,"").trim() + "\\""');

    return RemoteInspectorInstance.evaluate(jsCode.join("\n"));
};

whatsNew.prototype.getGalleryButtons = function() {

    var jsCode = [];
    jsCode.push('var buttons = [];');
    jsCode.push('var galleryView = window.sf.currentView;');
    jsCode.push('galleryView.query("#button_area")[0].childNodes.forEach(function(button, idx){');
    jsCode.push('    var text = button.query("#button_text")[0].text;');
    jsCode.push('    var label = require("I18n").lang(text.substring(2, text.length - 1))');
    jsCode.push('    buttons.push("Button " + (idx+1) + " is \\"" + label + "\\"");');
    jsCode.push('});');
    jsCode.push('buttons.join(", ");');

    return RemoteInspectorInstance.evaluate(jsCode.join("\n"));
};

module.exports = whatsNew;