describe("Store", function(){
	describe("PS+ purchase flow", function(){
		test("should allow user to purchase 12 months sub", function(){
			SkyNet.store.open();
			SkyNet.wait(2000);
			SkyNet.store.activeElementText.should.equal("Welcome");
			SkyNet.press("DOWN");
			SkyNet.store.activeElementText.should.equal("PlayStation®Plus");
			SkyNet.press("RIGHT");
			SkyNet.wait(500);
			SkyNet.press("RIGHT");
			SkyNet.wait(500);
			SkyNet.press("DOWN");
			SkyNet.wait(500);
			SkyNet.press("CROSS");

			// TODO assert that button is Subscribe and that it goes to checkout?

		});
	});
});