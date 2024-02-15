"use strict"

/* credit: https://stackoverflow.com/a/15934766 */
var realFs = require('fs')
var gracefulFs = require('graceful-fs')
gracefulFs.gracefulify(realFs)

const package_data = require('./package.json');

const builder = require("electron-builder")
const Platform = builder.Platform

/**
* @type {import('electron-builder').Configuration}
* @see https://www.electron.build/configuration/configuration
*/
const options = package_data.build;

builder.build({
  config: options
})
.then((result) => {
  console.log(JSON.stringify(result))
})
.catch((error) => {
  console.error(error)
})
