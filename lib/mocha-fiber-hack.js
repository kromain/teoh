//  SONY CONFIDENTIAL MATERIAL. DO NOT DISTRIBUTE.
//  SNEI SkyNet
//  Copyright (C) Sony Network Entertainment Inc
//  All Rights Reserved

/**
 * Wraps Mocha interface so that we can use Fibers to make the test
 * code synchronous where needed.
 *
 * To be able to "pause" a given portion of the test code you can do:
 *
 * var fiber = Fiber.current;
 * setTimeout(function(){
 *   // Do something async after 2sec
 *   fiber.run();
 * }, 2000);
 * return Fiber.yield();
 *
 * To use the above syntax, the code must be wrapped in a Fiber().run()
 * block.
 *
 * Because most of the test code will happen within Mocha, the solution is
 * to wrap every Mocha call inside a Fiber().run() block. I could not find
 * a way to redefine the various it/define/before/after/beforeEach/afterEach
 * blocks of the BDD interface on the fly. As a workaround, I set Mocha to
 * use the TDD interface instead and I create my own BDD blocks globally
 * here which wrap around the TDD block within a Fiber().run().
 *
 * From the test case perspective, it looks like the real Mocha BDD interface.
 */

var _fiberWrap = function(fn) {
    return function(done){
        Fiber(function(){
            fn();
            if (done) {
                done();
            }
        }).run();
    };
};

/**
 * Execute before running tests.
 */

global.before = function(fn){
    suiteSetup(_fiberWrap(fn));
};

/**
 * Execute after running tests.
 */

global.after = function(fn){
    suiteTeardown(_fiberWrap(fn));
};

/**
 * Execute before each test case.
 */

global.beforeEach = function(fn){
    setup(_fiberWrap(fn));
};

/**
 * Execute after each test case.
 */

global.afterEach = function(fn){
    teardown(_fiberWrap(fn));
};

/**
 * Describe a "suite" with the given `title`
 * and callback `fn` containing nested suites
 * and/or tests.
 */

global.describe = global.context = function(title, fn){
    return suite(title, _fiberWrap(fn));
};

/**
 * Pending describe.
 */

global.xdescribe =
global.xcontext =
global.describe.skip = function(title, fn){
    suite.skip(title, _fiberWrap(fn));
};

/**
 * Exclusive suite.
 */

global.describe.only = function(title, fn){
    suite.only(title, _fiberWrap(fn));
};

/**
 * Describe a specification or test-case
 * with the given `title` and callback `fn`
 * acting as a thunk.
 */

global.it = global.specify = function(title, fn){
    return test(title, _fiberWrap(fn));
};

/**
 * Exclusive test-case.
 */

global.it.only = function(title, fn){
    test.only(title, _fiberWrap(fn));
};

/**
 * Pending test case.
 */

global.xit =
global.xspecify =
global.it.skip = function(title){
    test.skip(title, _fiberWrap(fn));
};
