describe("What's New", function(){
	describe("Demo", function(){
		it("should navigate the grid and display story info", function(){
			SkyNet.login("WHATS_NEW");

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, whatsNew.getTileInfo());

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, whatsNew.getTileInfo());

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, whatsNew.getTileInfo());

			SkyNet.press("CROSS");
			SkyNet.wait(5000);

			console.log("\t%s".yellow, whatsNew.getGalleryButtons());
		});
	});
});