var whatsNew = function(){}

whatsNew.prototype.getTileInfo = function(){

    var fiber = Fiber.current;

    setTimeout(function(){
	    var jsCode = [];
	    jsCode.push('var tile = window.debugFeedGrid.selected.tileData;');
	    jsCode.push('"Found " + tile.storyType + " story at " + tile.debugId + ": \\"" + tile.caption.replace(tile.debugId,"").trim() + "\\""');
        RemoteInspectorInstance.Runtime.evaluate({expression: jsCode.join("\n") }, function(err, output){
            if (output && output.result && output.result.type === "string" && output.result.value) {
            	fiber.run(output.result.value);
            } else {
             	if (output && output.wasThrown && output.result.description) {
             		throw new Error("Exception thrown in inspector runtime:" + output.result.description)
             	} else {
             		throw new Error("Unknown error in inspector runtime");
             	}
            }
        });
    }, 500)

	return Fiber.yield()
}

module.exports = whatsNew;