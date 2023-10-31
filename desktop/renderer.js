"use strict";

const { app, BrowserWindow } = require("electron");
const path = require("path");
const { env } = require("process");

// Keep a global reference of the mainWindowdow object, if you don't, the mainWindowdow will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow = null;
let subpy = null;

const PY_DIST_FOLDER = "dist-python"; // python distributable folder
const PY_SRC_FOLDER = "../desktop"; // path to the python source
// temporary hack to get the dist exe to run in the right place
const PY_MODULE = "run_app/run_app.py"; // the name of the main module

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
  } else if (process.platform === "linux") {
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
  // TODO: should make SURE that these processes are killed when the app is closed
  if (isRunningInBundle()) {
    console.log("Running in bundle");
    subpy = require("child_process").execFile(script, [], (error, stdout, stderr) => {
      if (error) {
        throw error;
      }
    });
    subpy.stdout.on('data', (data) => { console.log(`stdout: ${data.trim()}`); });
    subpy.stderr.on('data', (data) => {
      console.error(`stderr: ${data.trim()}`);
      if (data.includes("Running on http")) {
        console.log("Python subprocess is ready to accept connections.");
        mainWindow.loadURL("http://localhost:4040/");
      }
    });
  } else {
    let env = process.env;
    env.PYTHONPATH = path.join(__dirname, "..");
    console.log(`Running in dev mode with PYTHONPATH=${env.PYTHONPATH}`);
    subpy = require("child_process").spawn("python", [script], { cwd: path.join(process.cwd(), ".."), env: env });
    subpy.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });
    
    subpy.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });
    
    subpy.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
      if (code !== 0)
        // TODO: why does this not kill the app?
        throw new Error("Child process failed with code " + code.toString() + ".");
    });
  }
};

const killPythonSubprocesses = (main_pid) => {
  const python_script_name = path.basename(getPythonScriptPath());
  let cleanup_completed = false;
  const psTree = require("ps-tree");
  psTree(main_pid, function (err, children) {
    let python_pids = children
      .filter(function (el) {
        return el.COMMAND == python_script_name;
      })
      .map(function (p) {
        return p.PID;
      });
    // kill all the spawned python processes
    python_pids.forEach(function (pid) {
      process.kill(pid);
    });
    subpy = null;
    cleanup_completed = true;
  });
  return new Promise(function (resolve, reject) {
    (function waitForSubProcessCleanup() {
      if (cleanup_completed) return resolve();
      setTimeout(waitForSubProcessCleanup, 30);
    })();
  });
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

  mainWindow.loadFile(path.join(__dirname, "spinner.html"));

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
    let main_process_pid = process.pid;
    killPythonSubprocesses(main_process_pid).then(() => {
      app.quit();
    });
  }
});

app.on("activate", () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (subpy == null) {
    startPythonSubprocess();
  }
  if (win === null) {
    createMainWindow();
  }
});

app.on("quit", function () {
  // do some additional cleanup
});
