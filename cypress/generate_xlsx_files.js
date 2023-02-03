#!/usr/bin/env node
const { execSync } = require("child_process");

const exec = (command) => {
  execSync(command, {
    stdio: "inherit",
  });
};

const args = process.argv.slice(2);

const serverAddress = args[0];
const size = args[1];
const seed = args[2];

const command = `curl -X POST ${serverAddress}/api/cypress/ --data "command=generate-xlsx-files&size=${size}&seed=${seed}"`;
exec(command);

// const copy = require("copy");
// copy("../backend/generated/*", "cypress/fixtures", function (err, files) {
//   if (err) throw err;
//   console.log("Files copied successfully");
// });

// move to cypress/fixtures and call curl -OJ http://localhost:8082/api/cypress/xlsx/<seed>/ there

const copyCommand = `cd cypress/fixtures && curl -OJ http://localhost:8082/api/cypress/xlsx/${seed}/`;
exec(copyCommand);
