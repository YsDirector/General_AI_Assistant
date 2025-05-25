/*
   Copyright 2025 Guan Yushen

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const keySender = require('node-key-sender');
const { Notification } = require('electron');

function callOpenAI(toolname) {
  const aiToolsConfigPath = path.join(process.env.APPDATA, 'general-ai-assistant', 'ai-tools-bar.json');
  const modelsConfigPath = path.join(process.env.APPDATA, 'general-ai-assistant', 'models.json');

  let aiToolsData;
  let modelsData;

  try {
    aiToolsData = JSON.parse(fs.readFileSync(aiToolsConfigPath, 'utf8'));
  } catch (err) {
    console.error("Error reading ai-tools-bar.json:", err);
    new Notification({ title: 'Error', body: "Error reading ai-tools-bar.json" }).show();
    return;
  }

  try {
    modelsData = JSON.parse(fs.readFileSync(modelsConfigPath, 'utf8'));
  } catch (err) {
    console.error("Error reading models.json:", err);
    new Notification({ title: 'Error', body: "Error reading models.json" }).show();
    return;
  }

  const tool = aiToolsData.find(t => t.Toolname === toolname);
  if (!tool) {
    console.error(`Tool with name ${toolname} not found in ai-tools-bar.json`);
    new Notification({ title: 'Error', body: `Tool with name ${toolname} not found in ai-tools-bar.json` }).show();
    return;
  }

  const modelInfo = modelsData.find(m => m.Model === tool.Model);
  if (!modelInfo) {
    console.error(`Model with name ${tool.Model} not found in models.json`);
    new Notification({ title: 'Error', body: `Model with name ${tool.Model} not found in models.json` }).show();
    return;
  }

  const { API_URL, API_Key } = modelInfo;
  const { Prompt, Replace } = tool; // Read the Replace attribute

  // Get clipboard content
  const clipboard = require('electron').clipboard;
  const userInput = clipboard.readText();

  const input = `${Prompt}${userInput}`;

  console.log(`Sending request to OpenAI API with input: ${input}`);

  axios.post(API_URL, {
    messages: [
      {
        role: "system",
        content: "You are a helpful assistant."
      },
      {
        role: "user",
        content: input
      }
    ],
    model: tool.Model
  }, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_Key}`
    },
    // Disable SSL authentication
    httpsAgent: new (require('https')).Agent({
      rejectUnauthorized: false
    })
  })
  .then(response => {
    const output = response.data.choices[0].message.content;
    console.log(`Received response from OpenAI API: ${output}`);

    // Copy the output to clipboard
    clipboard.writeText(output);

    // Execute actions based on the Replace value
    if (Replace) {
      keySender.sendCombination(['control', 'v']);
    } else {
      keySender.sendKey('right');
      keySender.sendCombination(['control', 'v']);
    }

    console.log('Action executed successfully');
  })
  .catch(error => {
    console.error("Error sending request to OpenAI API:", error.response ? error.response.data : error.message);
    new Notification({ title: 'Error', body: "Error sending request to OpenAI API" }).show();
  });
}

module.exports = callOpenAI;






