const path = require("path");

const spawn = require("child_process").spawn;
let env = process.env;
env.PYTHONPATH = path.join(__dirname, "..");
console.log(`Packaging python backend with PYTHONPATH=${env.PYTHONPATH}...`);
let pyinstaller_proc = spawn(
  "pyinstaller",
  [
    "--distpath desktop/dist-python",
    "desktop/racine-backend.spec",
  ],
  {
    cwd: path.join(__dirname, ".."),
    env: env,
    shell: true,
  }
);

pyinstaller_proc.stdout.on("data", function (data) {
  console.log("[PYINSTALLER] " + data.toString().trim());
});

pyinstaller_proc.stderr.on("data", function (data) {
  console.log("[PYINSTALLER] " + data.toString().trim());
});

pyinstaller_proc.on("exit", function (code) {
  console.log("child process exited with code " + code.toString());
  if (code !== 0)
    throw new Error("Packaging failed with code " + code.toString() + ".");
});
