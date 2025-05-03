// @ts-check

(function () {
  // Get the VS Code API
  const vscode = acquireVsCodeApi();

  // Store state
  let servers = [];
  let currentServerId = null;

  // Wait for the document to load
  document.addEventListener('DOMContentLoaded', () => {
    // Set up event listeners for official server buttons
    document.getElementById('add-github').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'GITHUB'
      });
    });

    document.getElementById('add-docker').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'DOCKER'
      });
    });

    document.getElementById('add-git').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'GIT'
      });
    });

    document.getElementById('add-memory').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'MEMORY'
      });
    });

    document.getElementById('add-filesystem').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'FILESYSTEM'
      });
    });

    document.getElementById('add-all').addEventListener('click', () => {
      vscode.postMessage({
        command: 'addOfficialServer',
        serverType: 'ALL'
      });
    });
  });

  // Handle messages from the extension
  window.addEventListener('message', event => {
    const message = event.data;
    
    switch (message.command) {
      case 'updateServers':
        servers = message.servers;
        currentServerId = message.currentServerId;
        updateServerSelector();
        updateServerConfig();
        break;
    }
  });

  /**
   * Update the server selector
   */
  function updateServerSelector() {
    const selectorContainer = document.getElementById('server-selector');
    selectorContainer.innerHTML = '';

    // Create a select element
    const select = document.createElement('select');
    select.id = 'server-select';
    
    // Add an option for each server
    servers.forEach(server => {
      const option = document.createElement('option');
      option.value = server.id;
      option.textContent = `${server.name} (${server.status})`;
      option.selected = server.id === currentServerId;
      select.appendChild(option);
    });

    // Add event listener
    select.addEventListener('change', () => {
      currentServerId = select.value;
      updateServerConfig();
    });

    // Add to the container
    selectorContainer.appendChild(select);
  }

  /**
   * Update the server configuration
   */
  function updateServerConfig() {
    const configContainer = document.getElementById('server-config');
    configContainer.innerHTML = '';

    // Find the current server
    const server = servers.find(s => s.id === currentServerId);
    if (!server) {
      configContainer.innerHTML = '<p>No server selected</p>';
      return;
    }

    // Create the configuration form
    const form = document.createElement('form');
    form.id = 'config-form';

    // Add server information
    form.innerHTML = `
      <h2>Server Configuration: ${server.name}</h2>
      
      <div class="form-group">
        <label for="name">Name:</label>
        <input type="text" id="name" value="${server.name}" />
      </div>
      
      <div class="form-group">
        <label for="description">Description:</label>
        <textarea id="description">${server.description || ''}</textarea>
      </div>
      
      <div class="form-group">
        <label for="auto-start">Auto Start:</label>
        <input type="checkbox" id="auto-start" ${server.autoStart ? 'checked' : ''} />
      </div>
      
      <div class="form-group">
        <label>Status:</label>
        <span class="status-${server.status}">${server.status}</span>
      </div>
      
      <div class="form-group">
        <label>Health:</label>
        <span class="health-${server.healthStatus || 'unknown'}">${server.healthStatus || 'unknown'}</span>
      </div>
      
      <div class="form-group">
        <label>Endpoint:</label>
        <span>${server.endpoint || 'N/A'}</span>
      </div>
      
      <div class="form-group">
        <label>Repository:</label>
        <span>${server.repoUrl}</span>
      </div>
      
      <div class="form-group">
        <label>Version:</label>
        <span>${server.version}</span>
      </div>
      
      <div class="button-container">
        <button type="button" id="save-config">Save Configuration</button>
        <button type="button" id="start-server" ${server.status === 'running' ? 'disabled' : ''}>Start Server</button>
        <button type="button" id="stop-server" ${server.status !== 'running' ? 'disabled' : ''}>Stop Server</button>
        <button type="button" id="restart-server" ${server.status !== 'running' ? 'disabled' : ''}>Restart Server</button>
        <button type="button" id="check-health">Check Health</button>
        <button type="button" id="view-logs">View Logs</button>
      </div>
    `;

    // Add event listeners
    form.querySelector('#save-config').addEventListener('click', () => {
      const name = form.querySelector('#name').value;
      const description = form.querySelector('#description').value;
      const autoStart = form.querySelector('#auto-start').checked;

      vscode.postMessage({
        command: 'saveConfig',
        serverId: server.id,
        config: {
          name,
          description,
          autoStart
        }
      });
    });

    form.querySelector('#start-server').addEventListener('click', () => {
      vscode.postMessage({
        command: 'startServer',
        serverId: server.id
      });
    });

    form.querySelector('#stop-server').addEventListener('click', () => {
      vscode.postMessage({
        command: 'stopServer',
        serverId: server.id
      });
    });

    form.querySelector('#restart-server').addEventListener('click', () => {
      vscode.postMessage({
        command: 'restartServer',
        serverId: server.id
      });
    });

    form.querySelector('#check-health').addEventListener('click', () => {
      vscode.postMessage({
        command: 'checkHealth',
        serverId: server.id
      });
    });

    form.querySelector('#view-logs').addEventListener('click', () => {
      vscode.postMessage({
        command: 'viewLogs',
        serverId: server.id
      });
    });

    // Add the form to the container
    configContainer.appendChild(form);

    // Add tools section if the server has a schema
    if (server.schema && server.schema.tools && server.schema.tools.length > 0) {
      const toolsContainer = document.createElement('div');
      toolsContainer.className = 'tools-container';
      toolsContainer.innerHTML = `<h3>Available Tools</h3>`;

      const toolsList = document.createElement('ul');
      toolsList.className = 'tools-list';

      server.schema.tools.forEach(tool => {
        const toolItem = document.createElement('li');
        toolItem.className = 'tool-item';
        toolItem.innerHTML = `
          <h4>${tool.name}</h4>
          <p>${tool.description}</p>
        `;
        toolsList.appendChild(toolItem);
      });

      toolsContainer.appendChild(toolsList);
      configContainer.appendChild(toolsContainer);
    }
  }
})();
