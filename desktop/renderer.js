"use strict";

const { app, BrowserWindow } = require("electron");
const path = require("path");

// Keep a global reference of the mainWindowdow object, if you don't, the mainWindowdow will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow = null;
let subpy = null;
let subpyReady = false;

const PY_DIST_FOLDER = "dist-python/run_app"; // python distributable folder
const PY_SRC_FOLDER = "../desktop"; // path to the python source
const PY_MODULE = "run_app.py"; // the name of the main module

const isRunningInBundle = () => {
  return require("fs").existsSync(path.join(__dirname, PY_DIST_FOLDER));
};

const getPythonScriptPath = () => {
  if (!isRunningInBundle()) {
    return path.join(__dirname, PY_SRC_FOLDER, PY_MODULE);
  }
  if (process.platform === "win32") {
    return path.join(
      __dirname,
      PY_DIST_FOLDER,
      PY_MODULE.slice(0, -3) + ".exe"
    );
  } else if (process.platform === "linux" || process.platform === "darwin") {
    return path.join(
      __dirname,
      PY_DIST_FOLDER,
      PY_MODULE.slice(0, -3)
    );
  }
  return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE);
};

const startPythonSubprocess = () => {
  let script = getPythonScriptPath();
  if (isRunningInBundle()) {
    console.log("Running in bundle: " + script);
    subpy = require("child_process").execFile(script, []);
  } else {
    let env = process.env;
    env.PYTHONPATH = path.join(__dirname, "..");
    console.log(`Running in dev mode with PYTHONPATH=${env.PYTHONPATH}`);
    subpy = require("child_process").spawn("python", [script], { cwd: path.join(process.cwd(), ".."), env: env });
  }

  subpy.stdout.on('data', (data) => { console.log(`stdout: ${data}`); });
  subpy.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
    if (data.includes("Running on http")) {
      console.log("Python subprocess is ready to accept connections.");
      subpyReady = true;
      mainWindow.loadURL("http://localhost:4040/");
    }
  });
 
  subpy.on('close', (code) => {
    subpy = null;
    if (code !== 0 && code !== null)
      throw new Error(`Child process failed with code ${code}.`);
  });
};

const killPythonSubprocess = () => {
  if (subpy == null)
    return;
  console.log("Killing python subprocess...");
  process.kill(subpy.pid);
  subpy = null;
};

const createMainWindow = () => {
  // Create the browser mainWindow
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    // transparent: true, // transparent header bar
    icon: __dirname + "/icon.png",
    // fullscreen: true,
    // opacity:0.8,
    // darkTheme: true,
    // frame: false,
    resizeable: true,
  });

  mainWindow.webContents.on("did-fail-load", function () {
    console.log("Failed to load page...");
  });

  mainWindow.webContents.on("did-finish-load", function () {
    let url = mainWindow.webContents.getURL();
    console.log(`Finished loading page ${url}.`);
  });

  if (subpyReady) {
    mainWindow.loadURL("http://localhost:4040/");
  } else {
    mainWindow.loadFile(path.join(__dirname, "spinner.html"));
  }

  // Open the DevTools if flask is running in development mode
  if (process.env.FLASK_ENV === "development") {
    mainWindow.webContents.openDevTools();
  }

  // Emitted when the mainWindow is closed.
  mainWindow.on("closed", function () {
    // Dereference the mainWindow object
    mainWindow = null;
  });
};

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on("ready", function () {
  // start the backend server
  startPythonSubprocess();
  createMainWindow();
});

// disable menu
app.on("browser-window-created", function (e, window) {
  window.setMenu(null);
});

// Quit when all windows are closed.
app.on("window-all-closed", () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== "darwin") {
    killPythonSubprocess();
    app.quit();
  }
});

app.on("activate", () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (subpy == null) {
    startPythonSubprocess();
  }
  if (mainWindow === null) {
    createMainWindow();
  }
});

app.on("quit", function () {
  // kill python subprocess (for MacOS)
  if (subpy != null) {
    killPythonSubprocess();
  }
});
