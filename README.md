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

## Installation

First, `git clone` this repository, then run `npm install` to get all the dependencies. Execute `./skynet` or `node skynet`. It should show the help screen.

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
 








