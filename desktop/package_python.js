const path = require("path");

const spawn = require("child_process").spawn,
  ls = spawn(
    "pyinstaller",
    [
      "-w",
      "--onefile",
      `--add-data app/templates${path.delimiter}templates`,
      `--add-data app/static${path.delimiter}static`,
      "--distpath desktop/dist-python",
      "app/__init__.py",
    ],
    {
      cwd: path.join(__dirname, ".."),
      shell: true,
    }
  );

ls.stdout.on("data", function (data) {
  console.log(data.toString());
});

ls.stderr.on("data", function (data) {
  console.log("Packaging error: " + data.toString());
});

ls.on("exit", function (code) {
  console.log("child process exited with code " + code.toString());
  if (code !== 0)
    throw new Error("Packaging failed with code " + code.toString() + ".");
});
