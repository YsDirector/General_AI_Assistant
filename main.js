const { app, BrowserWindow, Tray, Menu, globalShortcut, screen, ipcMain, clipboard, Notification } = require('electron');
const path = require('path');
const fs = require('fs');
const keySender = require('node-key-sender'); // Add node-key-sender 
const callOpenAI = require('./callOpenAI');
const remote = require('@electron/remote/main');

remote.initialize(); // Initialize remote module

let mainWindow;
let tray;
let toolBar;
let modelSettingsWindow;
let toolSettingsWindow;
let aIChatBotWindow;
let aboutWindow;

app.whenReady().then(() => {
  app.commandLine.appendSwitch('ignore-certificate-errors')//Ignore certificate related errors
  // Create main window (can be hidden or minimized)
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    },
    show: false, // Initial window not displayed
  });

  // Set tray icon and context menu
  tray = new Tray(path.join(__dirname, 'icon.png')); // Ensure that there is an icon file named icon.png in the project directory
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Chatbot', type: 'normal' ,click: () => openAIChatBotWindow()},
    { type: 'separator' },
    { label: 'Settings', type: 'normal' , click: () => openToolSettingsWindow() },
    { label: 'About', type: 'normal' , click: () => openAboutWindow()},
    { type: 'separator' },
    { role: 'quit' }
  ]);
  tray.setContextMenu(contextMenu);
  tray.setToolTip('General AI Assistant');

  // Register global shortcut key Alt+F6 to display toolbar
  globalShortcut.register('Alt+F6', () => {
    console.log('Alt+F6 pressed');

    // Send Ctrl+C key combination
    keySender.sendCombination(['control', 'c']);
    console.log('Ctrl+C executed successfully');

    // Retrieve the current clipboard content
    const originalText = clipboard.readText();
    console.log(`Original clipboard content: ${originalText}`);

    // Monitor clipboard changes
    listenForClipboardChange(originalText);
  });

  // Initialize the ai-toools-barjson file
  const aiToolsConfigPath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
  if (!fs.existsSync(aiToolsConfigPath)) {
    ensureDirectoryExistence(aiToolsConfigPath);
    const initialAiToolsData = [
      {
        "Toolname": "Translate(Example)",
        "Prompt": "Translate the following content:",
        "Model": "gpt-3.5-turbo",
        "Replace":true
      }
    ];
    fs.writeFileSync(aiToolsConfigPath, JSON.stringify(initialAiToolsData, null, 2));
  }

  // Initialize the models.json file
  const modelsConfigPath = path.join(app.getPath('appData'), 'general-ai-assistant', 'models.json');
  if (!fs.existsSync(modelsConfigPath)) {
    ensureDirectoryExistence(modelsConfigPath);
    const initialModelsData = [
      {
        "API_URL": "TYPE YOUR API URL",
        "Model": "TYPE YOUR MODEL",
        "API_Key": "sk-xxxxxxxx"
      }
    ];
    fs.writeFileSync(modelsConfigPath, JSON.stringify(initialModelsData, null, 2));
  }

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });

  // Monitor call open messages
  ipcMain.on('call-openai', (event, toolname) => {
    callOpenAI(toolname);
  });
});

  // Load model data
ipcMain.handle('load-models', async (event) => {
    try {
        const modelsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'models.json');
        if (!fs.existsSync(modelsFilePath)) {
            // If the file does not exist, create an empty array and write it to the file
            fs.mkdirSync(path.dirname(modelsFilePath), { recursive: true });
            fs.writeFileSync(modelsFilePath, JSON.stringify([]), 'utf8');
        }
        const modelsJson = fs.readFileSync(modelsFilePath, 'utf8');
        return JSON.parse(modelsJson);
    } catch (error) {
        console.error("Error loading models:", error);
        throw error;
    }
});

module.exports = { openAIChatBotWindow };

  // Save model data
  ipcMain.handle('save-model', async (event, apiUrl, model, apiKey, index) => {
    try {
      const modelsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'models.json')
      const modelsJson = fs.readFileSync(modelsFilePath, 'utf8');
      let models = JSON.parse(modelsJson);

      if (index === -1) {
        // Add new model
        models.push({ API_URL: apiUrl, Model: model, API_Key: apiKey });
      } else {
        // Edit existing model
        models[index] = { API_URL: apiUrl, Model: model, API_Key: apiKey };
      }

      fs.writeFileSync(modelsFilePath, JSON.stringify(models, null, 2), 'utf8');
      return { success: true };
    } catch (error) {
      console.error("Error saving model:", error);
      return { success: false, message: 'Error saving model, please retry.' };
    }

});

//Save tool bar settings

ipcMain.handle('get-model', async (event, index) => {
    try {
        const modelsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'models.json');
        const modelsJson = fs.readFileSync(modelsFilePath, 'utf8');
        const models = JSON.parse(modelsJson);
        if (index >= 0 && index < models.length) {
            return models[index];
        } else {
            throw new Error('Invalid model index');
        }
    } catch (error) {
        console.error("Error getting model:", error);
        throw error;
    }
});

ipcMain.handle('delete-model', async (event, index) => {
    try {
        const modelsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'models.json');
        if (!fs.existsSync(modelsFilePath)) {
            fs.writeFileSync(modelsFilePath, JSON.stringify([]), 'utf8');
        }
        const modelsJson = fs.readFileSync(modelsFilePath, 'utf8');
        let models = JSON.parse(modelsJson);

        if (index >= 0 && index < models.length) {
            models.splice(index, 1);
            fs.writeFileSync(modelsFilePath, JSON.stringify(models, null, 2), 'utf8');
        } else {
            throw new Error('Invalid model index');
        }
    } catch (error) {
        console.error("Error deleting model:", error);
        throw error;
    }
});

ipcMain.handle('load-tools', async (event) => {
    try {
        const toolsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
        if (!fs.existsSync(toolsFilePath)) {
            fs.writeFileSync(toolsFilePath, JSON.stringify([]), 'utf8');
        }
        const toolsJson = fs.readFileSync(toolsFilePath, 'utf8');
        return JSON.parse(toolsJson);
    } catch (error) {
        console.error("Error loading tools:", error);
        throw error;
    }
});

ipcMain.handle('get-tool', async (event, index) => {
    try {
        const toolsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
        const toolsJson = fs.readFileSync(toolsFilePath, 'utf8');
        const tools = JSON.parse(toolsJson);
        if (index >= 0 && index < tools.length) {
            return tools[index];
        } else {
            throw new Error('Invalid tool index');
        }
    } catch (error) {
        console.error("Error getting tool:", error);
        throw error;
    }
});

ipcMain.handle('save-tool', async (event, toolname, prompt, model, replace, index) => {
    try {
        const toolsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
        if (!fs.existsSync(toolsFilePath)) {
            fs.writeFileSync(toolsFilePath, JSON.stringify([]), 'utf8');
        }
        const toolsJson = fs.readFileSync(toolsFilePath, 'utf8');
        let tools = JSON.parse(toolsJson);

        const tool = { Toolname: toolname, Prompt: prompt, Model: model, Replace: replace };

        if (index === -1) {
            tools.push(tool);
        } else {
            tools[index] = tool;
        }

        fs.writeFileSync(toolsFilePath, JSON.stringify(tools, null, 2), 'utf8');
    } catch (error) {
        console.error("Error saving tool:", error);
        throw error;
    }
});

ipcMain.handle('delete-tool', async (event, index) => {
    try {
        const toolsFilePath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
        if (!fs.existsSync(toolsFilePath)) {
            fs.writeFileSync(toolsFilePath, JSON.stringify([]), 'utf8');
        }
        const toolsJson = fs.readFileSync(toolsFilePath, 'utf8');
        let tools = JSON.parse(toolsJson);

        if (index >= 0 && index < tools.length) {
            tools.splice(index, 1);
            fs.writeFileSync(toolsFilePath, JSON.stringify(tools, null, 2), 'utf8');
        } else {
            throw new Error('Invalid tool index');
        }
    } catch (error) {
        console.error("Error deleting tool:", error);
        throw error;
    }
});

function sendStartupNotification() {
    const notification = new Notification({
        title: 'General AI Assistant has successfully started!',
        body: 'Now you can use Alt+F6 to invoke the AI toolbar.',
    });

    notification.show();
}

// Get the path to key-sender.jar
function getKeySenderJarPath() {
    let jarPath;
    if (process.env.NODE_ENV === 'development') {
        // Debug
        jarPath = path.join(__dirname, 'node_modules', 'node-key-sender', 'jar', 'key-sender.jar');
    } else {
        // Release
        jarPath = path.join(process.resourcesPath, 'jar', 'key-sender.jar');
    }
    return jarPath;
}


app.whenReady().then(() => {
    sendStartupNotification(); // Send notifications after the application is ready

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) openAIChatBotWindow();
    });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

//AI Chat Bot Window
function openAIChatBotWindow() {
  if (aIChatBotWindow) {
    aIChatBotWindow.focus();
    return;
  }

  aIChatBotWindow = new BrowserWindow({
    width: 600,
    height: 700,
    title: 'AI Chat Bot-General AI Assistant',
    icon: iconPath, // Set window icon
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, 
      enableRemoteModule: true, 
      webSecurity: false,//Ignore certificate related errors
    },
  });

  remote.enable(aIChatBotWindow.webContents); // Enable remote model

  aIChatBotWindow.loadFile('AIChatBot.html');

  aIChatBotWindow.on('closed', () => {
    aIChatBotWindow = null;
  });
}

//About window
function openAboutWindow() {
  if (aboutWindow) {
    aboutWindow.focus();
    return;
  }

  aboutWindow = new BrowserWindow({
    width: 400,
    height: 550,
    title: 'About-General AI Assistant',
    icon: iconPath, // Set window icon
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, 
      enableRemoteModule: true, 
    },
  });

  aboutWindow.loadFile('about.html');

  aboutWindow.on('closed', () => {
    aboutWindow = null;
  });
}

const iconPath = path.join(__dirname, 'icon.png'); // Icon Path
//Model Settings Window
function openModelSettingsWindow() {
  if (modelSettingsWindow) {
    modelSettingsWindow.focus();
    return;
  }

  modelSettingsWindow = new BrowserWindow({
    width: 600,
    height: 800,
    title: 'Settings-General AI Assistant',
    icon: iconPath, // Set window icon
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, 
      enableRemoteModule: false, 
    },
  });

  remote.enable(modelSettingsWindow.webContents); // Enable remote mode

  modelSettingsWindow.loadFile('ModelsSettings.html');

  modelSettingsWindow.on('closed', () => {
    modelSettingsWindow = null;
  });
}
//Prompt word setting window
function openToolSettingsWindow() {
  if (toolSettingsWindow) {
    toolSettingsWindow.focus();
    return;
  }

  const iconPath = path.join(__dirname, 'icon.png'); // Icon path

  toolSettingsWindow = new BrowserWindow({
    width: 600,
    height: 800,
    title: 'Settings-General AI Assistant',
    icon: iconPath, // Set window icon
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true, 
      enableRemoteModule: false, 
    },
  });

  remote.enable(toolSettingsWindow.webContents); // Enable remote mode

  toolSettingsWindow.loadFile('ToolbarSettings.html');

  toolSettingsWindow.on('closed', () => {
    toolSettingsWindow = null;
  });
}

function displayToolBar() {
  if (toolBar) {
    toolBar.destroy();
  }

  // Get mouse position
  const cursorPos = screen.getCursorScreenPoint();

  // Create toolbar window
  toolBar = new BrowserWindow({
    x: cursorPos.x,
    y: cursorPos.y + 10,
    width: 200,
    height: 400,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: iconPath, // Set window icon
  });

  // Load tools from config
  const tools = loadToolsFromConfig();
  let htmlContent = `
    <style>
      ul { list-style-type:none; padding:0; margin:0; }
      li a { display:block; padding:4npm startpx; background-color:#f0f0f0; text-decoration:none; color:black; border-bottom:1px solid #ddd; border-radius:2px}
      @keyframes fadeInUp {
        100% {
          opacity: 0;
          transform: translateY(400px);
        }
        50% {
          opacity: 2;
          transform: translateY(200px);
        }
        0% {
          opacity: 4;
          transform: translateY(0);
        }
      }
      </style>
    <ul id="toolbar">
  `;
  tools.forEach(tool => {
    htmlContent += `<li><a href="#" onclick="handleClick('${tool.Toolname}'); return false;">${tool.Toolname}</a></li>`;
  });
  htmlContent += '</ul>';

  toolBar.loadURL(`data:text/html;charset=UTF-8,${encodeURIComponent(htmlContent)}`);

  // Add scripts to handle click events
  toolBar.webContents.executeJavaScript(`
    const { ipcRenderer } = require('electron');

    function handleClick(toolname) {
      ipcRenderer.send('call-openai', toolname);
      window.close();
    }

    document.addEventListener('click', (event) => {
      const toolbarElement = document.getElementById('toolbar');
      if (!toolbarElement.contains(event.target)) {
        window.close();
      }
    }, { capture: true });
  `);

  // Hide toolbar when clicking outside the toolbar
  toolBar.on('blur', () => {
    toolBar.close();
  });
}

function listenForClipboardChange(originalText) {
  let timeoutId;

  const checkClipboard = setInterval(() => {
    const currentText = clipboard.readText();
    console.log(`Current clipboard content: ${currentText}`);
    if (currentText !== originalText && currentText.trim() !== '') {
      clearInterval(checkClipboard);
      clearTimeout(timeoutId);
      console.log('Clipboard content changed');
      displayToolBar();
    }
  }, 100); // Check clipboard contents every 100 milliseconds

  // Set timeout mechanism, force toolbar to pop up after 1500ms and display system notification
  timeoutId = setTimeout(() => {
    clearInterval(checkClipboard);
    console.log('Timeout reached, forcing toolbar display and showing notification');
    displayToolBar();
    showClipboardTimeoutNotification(originalText);
  }, 1500);
}

function showClipboardTimeoutNotification(originalText) {
  const notification = new Notification({
    title: 'The clipboard update timed out',
    body: `Please check if the selected content is the same as the clipboard content:\n${originalText}`,
    silent: false
  });

  notification.show();
}

function loadToolsFromConfig() {
  const configPath = path.join(app.getPath('appData'), 'general-ai-assistant', 'ai-tools-bar.json');
  try {
    const data = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(data);
  } catch (err) {
    console.error("Error reading configuration file:", err);
    return [];
  }
}

function ensureDirectoryExistence(filePath) {
  var dirname = path.dirname(filePath);
  if (fs.existsSync(dirname)) {
    return true;
  }
  ensureDirectoryExistence(dirname);
  fs.mkdirSync(dirname);
}



