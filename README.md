SNEI SkyNet
===========

The PlayStation remote control

## What?

SkyNet is a platform & application agnostic test framework

## Why?

Humans don’t scale. Computers do.

Avoid repetition & automate!

During development: feature testing & TDD

During QA cycles: smoke & regression testing

## Goals

Multi platforms (Win, OSX, …)

Multi devices (PS4, …)

Multi applications (Swordfish, …)

Easy to use

Easy to write tests

Easy to extend

## Installation

First, `git clone` this repository, then run `npm install` to get all the dependencies. Execute `./skynet` or `node skynet`. It should show the help screen.

###DART  

####Introduction

DART stands for Debug and Regression Test. It is a tool that lets you control and run tests on various devices like the PS3, PS4, PS Vita, etc.  
- DART Server Link: https://ussfrsdart02.am.sony.com/dart/
- DART Server Documentation : https://ussfrsdart02.am.sony.com/dart/doc/  

####DART setup to run Skynet  
1. **Get access to the DART server**  
Contact Vikram.Bhat@am.sony.com for access to the DART server. Please send an email with the following information.  
      - `Full Name`
      - `AM Domain Id`
      - `Roles required(if available)`
      - `Manager Name`
      - `Reason for requesting access`  

2. **Registering your device** *(Need Admin Access)*  
TODO: Register a system using API using SKYNET
  - Click on the `Target Management` tab in DART
  - On the Right side pane, Click on `Add` (Green + sign)
  - Select the type as `PS4`
  - Enter the device IP address
  - Enter a `description`
  - Click on `Submit`

3. **Setting up the test**  
  - Click on the `Test Configuration` tab.
	- On the Left side pane which lists the tests, look for a folder named `Navigation`.
	- Look for the `infinityTest-XX.XX.XX.XX` and click on it.
	- On the right side pane, click on the option to `Duplicate Test`.
	- Set the "NAME" of the new test as `infinityTest-<ip_address>` where the `<ip_address>` is the ip address of the device that you want to run the tests on.
	- Click on `Advanced`.
	- Select `Process 1`
	- In the Right side pane, under the option Targets, click on `Any PS4`. You should see a drop down listing all the devices. If you have registered your device, the device should show up in the drop down. Select your device and then click on Save in the bottom.  
	



## Write tests

Add your test file under `tests` directory

## Current limitations & to do

 * Only PS4 currently supported but other drivers can be added
   * To use the `dart` driver, you need to register your DevKit on a DART server (one time setup)
   * Using the `inspector` driver requires the focus to be on the web view
   * The `inspector` driver is limited to the web view and the `dart` driver is pretty slow. Future development would include a low level `DECI4` driver
   * Driver code is not self contained, it needs to be extracted from the main library
 * Code base & API needs clean up
   * Need to make SkyNet standalone: tests should not be included in the distribution. Maybe something like `./skynet init`?
   * Screenshot capture is not fully integrated yet and does not allow visual image comparison (coming soon)
   * API is not flushed out for querying Swordfish state
   * Also need to flush out extension API for drivers & adapters
 * Documentation & training
   * Need to write tutorial about how to use SkyNet
   * Training engineers?
 * Note: release 1.7.0 is minimum supported for Swordfish (it exposes new hooks for SkyNet)
 








