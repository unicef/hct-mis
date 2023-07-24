#!/usr/bin/env node
const { execSync } = require("child_process");

function exec(command, timeout = 0) {
  return execSync(command, (timeout = timeout)).toString();
}

const request = require("request");
const fs = require("fs");
const axios = require("axios");
const FormData = require("form-data");

// const SLACK_BOT_USER_TOKEN =
//   "xoxb-5509997426931-5523162721089-IlVaqxdRKRyKftvRAZojd7yZ";
// const CHANNEL = "C05EKHETMT9";

function sendMessage(
  data,
  url = "https://hooks.slack.com/services/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"
) {
  request(
    {
      url: url,
      method: "POST",
      json: data,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        // Authorization: `Bearer ${SLACK_BOT_USER_TOKEN}`,
      },
    },
    function (error, response, body) {
      if (error || response.statusCode !== 200) {
        console.error("Error sending slack response:", error);
      } else if (!response.body.ok) {
        console.error("Slack responded with error:", response.body);
      } else {
        // All good!
      }
    }
  );
}

async function sendFile(file_name) {
  const form = new FormData();
  form.append("file", fs.readFileSync(file_name), file_name);
  // form.append("channels", CHANNEL);
  await axios.post(
    "https://hooks.slack.com/services/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",
    form,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        // Authorization: `Bearer ${SLACK_BOT_USER_TOKEN}`,
      },
    }
  );
}

fs.readFile(
  "./cypress/reports/mochareports/report.json",
  "utf8",
  (err, jsonString) => {
    if (err) {
      console.log("File read failed:", err);
      return;
    }
    try {
      const report = JSON.parse(jsonString);
      let branchName = exec(`echo $BRANCH_NAME`).replace(/\s/g, "");
      let firstMessage = `Branch: <https://github.com/unicef/hct-mis/compare/${branchName}|${branchName}>`;
      if (report.stats.failures == "0") {
        sendMessage({
          text: `:tada: ${firstMessage}\n*PASSED*`,
          // channel: CHANNEL,
        });
      } else {
        const text = `Passed: ${report.stats.passes} \tFailed: ${report.stats.failures} \tToDo: ${report.stats.pending}\n`;
        console.log(`Branch name: ${branchName} Author: Todo`);

        sendMessage({
          text: `:interrobang: ${firstMessage}\n* \t\t\t\t\t\:interrobang:FAILED:interrobang:* \n${text}`,
          // channel: CHANNEL,
        });

        let coverage =
          ((report.stats.tests - report.stats.pending) / report.stats.tests) *
          100;
        const QuickChart = require("quickchart-js");
        const chart = new QuickChart();
        chart.setWidth(500);
        chart.setHeight(200);
        chart.setVersion("2.9.4");
        chart.setConfig({
          type: "doughnut",
          data: {
            datasets: [
              {
                data: [
                  report.stats.passes,
                  report.stats.failures,
                  report.stats.pending,
                ],
                backgroundColor: [
                  "rgb(75, 192, 192)",
                  "rgb(255, 99, 132)",
                  "rgb(54, 162, 235)",
                ],
              },
            ],
            labels: ["Pass", "Failed", "ToDo"],
          },
          options: {
            plugins: {
              datalabels: {
                color: "#000",
                formatter: (value) => {
                  if (value < 1) return "";
                  return value;
                },
              },
              doughnutlabel: {
                labels: [
                  {
                    text: coverage.toFixed(0).toString() + "%",
                    color: "#000",
                    font: { size: 30 },
                  },
                  { text: "Coverage", color: "#000" },
                ],
              },
            },
          },
        });
        const chartUrl = chart.getUrl();
        console.log("\n\n" + chartUrl + "\n\n");

        sendMessage({
          text: "Chart data update",
          // channel: CHANNEL,
          blocks: [
            {
              type: "image",
              title: {
                type: "plain_text",
                text: "Latest data",
              },
              block_id: "quickchart-image",
              image_url: chartUrl,
              alt_text: "Chart showing latest data",
            },
          ],
        });
        sendFile("report.zip");
      }
    } catch (err) {
      console.log("Error parsing JSON string:", err);
    }
  }
);
