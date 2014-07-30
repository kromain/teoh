// Copyright (c) 2014 Sony Network Entertainment Intl., all rights reserved.
(function() {
	var ver_id = "$Id: js_ex.js 9480 2013-02-06 07:56:39Z udagawa $";
    var userAgent = window.navigator.userAgent.toLowerCase();
	var callbacks = {};
	var system_event_listeners = {};
	var registry = {};

	var platform;
    // For Orbis
    if ("sce" in window.navigator) {
		platform = {
			name: "ORBIS",

			postMessage : function(s) {
				window.navigator.sce.postMessage(s);
			},

			sendMessage : function(s) {
				return window.navigator.sce.sendMessage(s);
			}
		}
	}
    // For Generic browser
	else {
		platform = {
			name: "BRWOSER",

			postMessage : function(s) {
                prompt(s);
			},

			sendMessage : function(s) {
				return prompt(s);
			}
		}
	};

	var private = {
		// generate unique ID string
		create_next_guid: function () {
			var date_in_msec = new Date().valueOf();
			var MAX_SEQ = Math.pow(2, 32);
			var num = 0;
			return date_in_msec + "_" + (num < MAX_SEQ ? num++ : 0);
		},

		// call a system process API asynchronously
		call_async: function(api_name, args, callback) {
			var cbid;
			if (typeof(callback) == "function") {
				cbid = private.create_next_guid();
				callbacks[cbid] = callback;
			}
			var s = JSON.stringify({name: api_name, cbid: cbid, args: args});
			platform.postMessage(s);
			return cbid;
		},

		// call a system process API synchronously
		call_sync: function(api_name, args) {
			var s = JSON.stringify({name: api_name, args: args});
			var r = platform.sendMessage(s);
			return JSON.parse(r);
		},

		// kicked by system process:
		// call listners corresponing to the event type
		do_callback: function(cbid, res) {
			var f = callbacks[cbid];
			delete callbacks[cbid];
			if (f) {
				f(res);
			}
		},

		// kicked by system process:
		// call listners corresponing to the event type
		send_system_event: function(system_event) {
			var type = system_event.type;
			var listners = system_event_listeners[type];
			if (Array.isArray(listners)) {
				for (i = 0; i < listners.length; ++i) {
					listners[i](system_event);
				}
			}
		},

		readRegistry_cache: function(reg_name) {
			var val;
			if (reg_name in registry) {
				val = registry[reg_name];
			}
			return val;
		},

		readRegistry_sync: function(reg_name) {
			return private.call_sync("readRegistry", { name: reg_name});
		},
	}

	// Setup onMessage handler which is called if the system process
	// calls WKContextPostMessageToInjectedBundle()
	if (platform.name == "ORBIS") {
		window.navigator.sce.onmessage = function(message_obj) {
			var message = JSON.parse(message_obj.data);
			if (message.type == "callback") {
				private.do_callback(message.cbid, message.res);
			} else if (message.type == "system_event") {
				private.send_system_event(message.event);
			}
		}
	}

	var public =  {
		ver_id: ver_id,

		platform: platform.name,

		abort: function(cbid) {
			if (cbid) {
				private.call_async("abort", { cbid: cbid });
			}
		},

		// app_notifcation = { name: string, data: {...} }
		// exit
		// app_notifcation = { name: "exit", data: { status: status...} }
		appNotifyToSystem: function(app_notification) {
			return private.call_async("appNotifyToSystem", app_notification, null);
		},

		// see bug 6580 for the detail.
		exit: function(status, option) {
			var an = { name: "exit", data: { status: status, option: option }};
			public.appNotifyToSystem(an);
		},

		// see bug 6580 for the detail.
		makeAccountInfoOption: function(signin_id, sso_cookie, vsh_login_json) {
			return {
				signin_id: signin_id,
				sso_cookie: sso_cookie,
				vsh_login_json: vsh_login_json
			}
		},

		getAccessToken: function(callback) {
			var args;
			return private.call_async("getAccessToken", args, callback);
		},

		// add an event lister for the event type
		addSystemEventListener: function(type, listener) {
			var listners = system_event_listeners[type];
			if (Array.isArray(listners)) {
				if (listners.indexOf(listener) < 0) {
					listners.push(listener);
				}
			} else {
				system_event_listeners[type] = [ listener ];
			}
		},

		// remove an event lister for the event type
		removeSystemEventListener: function(type, listener) {
			var listners = system_event_listeners[type];
			if (Array.isArray(listners)) {
				var i = listners.indexOf(listener);
				if (i < listners.length) {
					listners.splice(i, 1);
				}
			}
		},

		notify: {
			ready: function(option) {
				var an = { name: "notifyReady", data: { option: option }};
				public.appNotifyToSystem(an);
			}
		},

		echo: function(option) {
			var an = { name: "echo", data: { option: option }};
			public.appNotifyToSystem(an);
		},
		
		// see bug 7515 for the detail
		//  var param = {
		//     content_url : "http://xxx/xxx.pkg",
		//     icon_url : "http://xxx/xxx.png",
		//     title_id : "TEST1234",
		//     content_id : "XX1234-TEST1234_00-SAMPLEAPP0000000",
		//     content_name : "Sample App"
		//  }
		//  reqid = sce.bgft.registerDownloadTask(callback, param)
		bgft: {
			registerDownloadTask: function(callback, args) {
				return private.call_async("bgft.registerDownloadTask", args, callback);
			}
		},

		readAllRegistries: function() {
			function callback(res) {
				registry = res;
			}
			var args;
			return private.call_async("readAllRegistries", args, callback);
		},

		readRegistry : private.readRegistry_sync,
	};

	//public.readAllRegistries();
    window.sce = public;
    //window.sce.private = private;

})();
