describe("Store", function(){
	describe("PS+ purchase flow", function(){
		test("should allow user to purchase 12 months sub", function(){

			// Deeplink to the store
			SkyNet.store.open();
			SkyNet.wait(3000);

			// Go back to global menu
			SkyNet.press("TRIANGLE");
			SkyNet.press("LEFT");
			SkyNet.press("LEFT");
			SkyNet.press("CROSS");

			// Navigate in menu and verify entry labels
			SkyNet.store.activeElementText.should.equal("Welcome", "Welcome entry is missing in store menu");
			SkyNet.press("DOWN");
			SkyNet.store.activeElementText.should.equal("PlayStation®Plus", "PS+ entry is missing in store menu");

			// Navigate the caroussel
			SkyNet.press("RIGHT");
			SkyNet.wait(500);
			SkyNet.press("RIGHT");
			SkyNet.wait(500);
			SkyNet.press("DOWN");
			SkyNet.wait(500);
			SkyNet.press("CROSS");

			SkyNet.wait(2000);

			SkyNet.store.activeElementText.should.equal("Join PS+ $49.99", "PDP should show a Subscribe button with price")
		});
	});
});