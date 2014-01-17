describe("What's New", function(){
	describe("Demo", function(){
		test("should navigate the grid and display story info", function(){
			SkyNet.login("WHATS_NEW");

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, SkyNet.whatsNew.getTileInfo());

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, SkyNet.whatsNew.getTileInfo());

			SkyNet.press("DOWN");
			console.log("\t%s".yellow, SkyNet.whatsNew.getTileInfo());

			SkyNet.press("CROSS");
			SkyNet.wait(2000);
			console.log("\t%s".yellow, SkyNet.whatsNew.getGalleryButtons());
		});
	});
});