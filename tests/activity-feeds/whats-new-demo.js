var assert = require("assert")
describe("What's New", function(){
	describe("Demo", function(){
		test("should navigate the grid", function(){
			assert.equal(true, true);

			SkyNet.login("WHATS_NEW")
			//SkyNet.login("STORE")

			SkyNet.press("DOWN");
			// Some assert here

			SkyNet.press("DOWN");
			// Some other assert here

			SkyNet.press("DOWN");
		})
	})
})