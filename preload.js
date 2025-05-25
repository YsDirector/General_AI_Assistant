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
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  callOpenAI: (toolname, prompt, model, replace) => ipcRenderer.invoke('call-openai', toolname, prompt, model, replace),
  loadSelectedText: () => ipcRenderer.invoke('load-selected-text'),
  loadModels: () => ipcRenderer.invoke('load-models'),
  saveModel: (apiUrl, model, apiKey, index) => ipcRenderer.invoke('save-model', apiUrl, model, apiKey, index),
  getModel: (index) => ipcRenderer.invoke('get-model', index),
  deleteModel: (index) => ipcRenderer.invoke('delete-model', index),
  loadTools: () => ipcRenderer.invoke('load-tools'),
  getTool: (index) => ipcRenderer.invoke('get-tool', index),
  saveTool: (toolname, prompt, model, index, replace) => ipcRenderer.invoke('save-tool', toolname, prompt, model, index, replace),
  deleteTool: (index) => ipcRenderer.invoke('delete-tool', index)
});