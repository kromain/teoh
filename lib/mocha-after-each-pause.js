//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

afterEach(function(){
	var pause = SkyNet.option("pause");
	if (pause) {
		SkyNet.wait(pause * 1000);
	}
});