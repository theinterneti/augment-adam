import * as vscode from 'vscode';
import * as os from 'os';
import * as fs from 'fs';
import * as path from 'path';
import * as dns from 'dns';
import { McpServerManager } from '../mcpServerManager';
import { GitHubRepoManager } from '../../github-integration/githubRepoManager';

/**
 * Server discovery result
 */
export interface ServerDiscoveryResult {
  name: string;
  description: string;
  repoUrl: string;
  version: string;
  source: 'registry' | 'github' | 'local' | 'network';
  official: boolean;
  installed: boolean;
  serverId?: string;
}

/**
 * Server discovery options
 */
export interface ServerDiscoveryOptions {
  includeRegistry?: boolean;
  includeGitHub?: boolean;
  includeLocal?: boolean;
  includeNetwork?: boolean;
  searchQuery?: string;
  maxResults?: number;
}

/**
 * Server discovery for MCP servers
 */
export class ServerDiscovery implements vscode.Disposable {
  private serverManager: McpServerManager;
  private githubManager: GitHubRepoManager;
  private registryUrl: string;
  private _onDidDiscoverServers = new vscode.EventEmitter<ServerDiscoveryResult[]>();

  /**
   * Event that fires when servers are discovered
   */
  public readonly onDidDiscoverServers = this._onDidDiscoverServers.event;

  /**
   * Create a new server discovery
   * @param serverManager MCP server manager
   * @param githubManager GitHub repository manager
   * @param options Server discovery options
   */
  constructor(
    serverManager: McpServerManager,
    githubManager: GitHubRepoManager,
    options: {
      registryUrl?: string;
    } = {}
  ) {
    this.serverManager = serverManager;
    this.githubManager = githubManager;
    this.registryUrl = options.registryUrl || 'https://registry.modelcontextprotocol.io';
  }

  /**
   * Dispose of resources
   */
  public dispose(): void {
    this._onDidDiscoverServers.dispose();
  }

  /**
   * Discover servers
   * @param options Discovery options
   * @returns Promise that resolves to the discovered servers
   */
  public async discoverServers(options: ServerDiscoveryOptions = {}): Promise<ServerDiscoveryResult[]> {
    const results: ServerDiscoveryResult[] = [];
    const maxResults = options.maxResults || 100;

    // Get installed servers
    const installedServers = this.serverManager.getServers();
    const installedRepoUrls = new Set(installedServers.map(server => server.repoUrl));

    // Discover servers from the registry
    if (options.includeRegistry !== false) {
      try {
        const registryResults = await this.discoverFromRegistry(options.searchQuery);
        for (const result of registryResults) {
          // Check if the server is already installed
          result.installed = installedRepoUrls.has(result.repoUrl);
          if (result.installed) {
            const server = installedServers.find(s => s.repoUrl === result.repoUrl);
            if (server) {
              result.serverId = server.id;
            }
          }

          results.push(result);

          // Check if we've reached the maximum number of results
          if (results.length >= maxResults) {
            break;
          }
        }
      } catch (error) {
        console.error('Error discovering servers from registry:', error);
      }
    }

    // Discover servers from GitHub
    if (options.includeGitHub !== false && results.length < maxResults) {
      try {
        const githubResults = await this.discoverFromGitHub(options.searchQuery);
        for (const result of githubResults) {
          // Check if the server is already installed
          result.installed = installedRepoUrls.has(result.repoUrl);
          if (result.installed) {
            const server = installedServers.find(s => s.repoUrl === result.repoUrl);
            if (server) {
              result.serverId = server.id;
            }
          }

          // Check if the result is already in the list
          if (!results.some(r => r.repoUrl === result.repoUrl)) {
            results.push(result);
          }

          // Check if we've reached the maximum number of results
          if (results.length >= maxResults) {
            break;
          }
        }
      } catch (error) {
        console.error('Error discovering servers from GitHub:', error);
      }
    }

    // Discover servers from the local network
    if (options.includeNetwork !== false && results.length < maxResults) {
      try {
        const networkResults = await this.discoverFromNetwork();
        for (const result of networkResults) {
          // Check if the result is already in the list
          if (!results.some(r => r.repoUrl === result.repoUrl)) {
            results.push(result);
          }

          // Check if we've reached the maximum number of results
          if (results.length >= maxResults) {
            break;
          }
        }
      } catch (error) {
        console.error('Error discovering servers from network:', error);
      }
    }

    // Discover servers from the local filesystem
    if (options.includeLocal !== false && results.length < maxResults) {
      try {
        const localResults = await this.discoverFromLocal();
        for (const result of localResults) {
          // Check if the server is already installed
          result.installed = installedRepoUrls.has(result.repoUrl);
          if (result.installed) {
            const server = installedServers.find(s => s.repoUrl === result.repoUrl);
            if (server) {
              result.serverId = server.id;
            }
          }

          // Check if the result is already in the list
          if (!results.some(r => r.repoUrl === result.repoUrl)) {
            results.push(result);
          }

          // Check if we've reached the maximum number of results
          if (results.length >= maxResults) {
            break;
          }
        }
      } catch (error) {
        console.error('Error discovering servers from local filesystem:', error);
      }
    }

    // Filter results by search query if provided
    if (options.searchQuery) {
      const query = options.searchQuery.toLowerCase();
      const filteredResults = results.filter(result => {
        return (
          result.name.toLowerCase().includes(query) ||
          result.description.toLowerCase().includes(query) ||
          result.repoUrl.toLowerCase().includes(query)
        );
      });
      
      // Notify listeners
      this._onDidDiscoverServers.fire(filteredResults);
      
      return filteredResults;
    }

    // Notify listeners
    this._onDidDiscoverServers.fire(results);

    return results;
  }

  /**
   * Discover servers from the MCP registry
   * @param searchQuery Search query
   * @returns Promise that resolves to the discovered servers
   */
  private async discoverFromRegistry(searchQuery?: string): Promise<ServerDiscoveryResult[]> {
    try {
      // Construct the registry URL
      let url = `${this.registryUrl}/api/servers`;
      if (searchQuery) {
        url += `?q=${encodeURIComponent(searchQuery)}`;
      }

      // Fetch the servers from the registry
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error fetching servers from registry: ${response.statusText}`);
      }

      const data = await response.json();
      if (!Array.isArray(data)) {
        throw new Error('Invalid response from registry');
      }

      // Convert the registry data to discovery results
      return data.map(item => ({
        name: item.name,
        description: item.description,
        repoUrl: item.repoUrl,
        version: item.version,
        source: 'registry' as const,
        official: item.official || false,
        installed: false
      }));
    } catch (error) {
      console.error('Error discovering servers from registry:', error);
      return [];
    }
  }

  /**
   * Discover servers from GitHub
   * @param searchQuery Search query
   * @returns Promise that resolves to the discovered servers
   */
  private async discoverFromGitHub(searchQuery?: string): Promise<ServerDiscoveryResult[]> {
    try {
      // Construct the search query
      const query = searchQuery
        ? `mcp-server ${searchQuery} in:name,description,readme`
        : 'mcp-server in:name,description,readme';

      // Search for repositories on GitHub
      const repositories = await this.githubManager.searchRepositories(query);

      // Convert the GitHub data to discovery results
      return repositories.map(repo => ({
        name: repo.name,
        description: repo.description || '',
        repoUrl: repo.html_url,
        version: '',
        source: 'github' as const,
        official: repo.owner.login === 'modelcontextprotocol',
        installed: false
      }));
    } catch (error) {
      console.error('Error discovering servers from GitHub:', error);
      return [];
    }
  }

  /**
   * Discover servers from the local network
   * @returns Promise that resolves to the discovered servers
   */
  private async discoverFromNetwork(): Promise<ServerDiscoveryResult[]> {
    try {
      // This is a placeholder implementation
      // In a real implementation, you would use mDNS or a similar protocol to discover MCP servers on the local network
      
      // Get the local IP addresses
      const interfaces = os.networkInterfaces();
      const localIps: string[] = [];
      
      for (const name in interfaces) {
        const networkInterface = interfaces[name];
        if (!networkInterface) {
          continue;
        }
        
        for (const iface of networkInterface) {
          if (iface.family === 'IPv4' && !iface.internal) {
            localIps.push(iface.address);
          }
        }
      }
      
      // Scan the local network for MCP servers
      const results: ServerDiscoveryResult[] = [];
      
      // This is a simplified implementation that just checks a few common ports
      // In a real implementation, you would use a more sophisticated discovery mechanism
      const ports = [8080, 8081, 8082, 8083, 8084, 8085];
      
      for (const ip of localIps) {
        // Get the network prefix
        const parts = ip.split('.');
        const prefix = `${parts[0]}.${parts[1]}.${parts[2]}`;
        
        // Scan the local network
        for (let i = 1; i <= 10; i++) {
          const targetIp = `${prefix}.${i}`;
          
          // Skip the local IP
          if (targetIp === ip) {
            continue;
          }
          
          // Check if the host is reachable
          try {
            await new Promise<void>((resolve, reject) => {
              dns.lookup(targetIp, (err) => {
                if (err) {
                  reject(err);
                } else {
                  resolve();
                }
              });
            });
            
            // Check common ports for MCP servers
            for (const port of ports) {
              try {
                const url = `http://${targetIp}:${port}/health`;
                const response = await fetch(url, {
                  method: 'GET',
                  headers: {
                    'Accept': 'application/json'
                  },
                  timeout: 1000
                });
                
                if (response.ok) {
                  // Try to get the server information
                  const infoUrl = `http://${targetIp}:${port}/info`;
                  const infoResponse = await fetch(infoUrl, {
                    method: 'GET',
                    headers: {
                      'Accept': 'application/json'
                    },
                    timeout: 1000
                  });
                  
                  if (infoResponse.ok) {
                    const info = await infoResponse.json();
                    
                    results.push({
                      name: info.name || `MCP Server at ${targetIp}:${port}`,
                      description: info.description || 'Discovered on local network',
                      repoUrl: info.repoUrl || `http://${targetIp}:${port}`,
                      version: info.version || '',
                      source: 'network' as const,
                      official: false,
                      installed: false
                    });
                  } else {
                    // Add a generic result
                    results.push({
                      name: `MCP Server at ${targetIp}:${port}`,
                      description: 'Discovered on local network',
                      repoUrl: `http://${targetIp}:${port}`,
                      version: '',
                      source: 'network' as const,
                      official: false,
                      installed: false
                    });
                  }
                }
              } catch (error) {
                // Ignore errors - the server might not be running on this port
              }
            }
          } catch (error) {
            // Ignore errors - the host might not be reachable
          }
        }
      }
      
      return results;
    } catch (error) {
      console.error('Error discovering servers from network:', error);
      return [];
    }
  }

  /**
   * Discover servers from the local filesystem
   * @returns Promise that resolves to the discovered servers
   */
  private async discoverFromLocal(): Promise<ServerDiscoveryResult[]> {
    try {
      const results: ServerDiscoveryResult[] = [];
      
      // Check common directories for MCP servers
      const homeDir = os.homedir();
      const directories = [
        path.join(homeDir, 'mcp-servers'),
        path.join(homeDir, 'Documents', 'mcp-servers'),
        path.join(homeDir, 'Projects', 'mcp-servers'),
        path.join(homeDir, 'git', 'mcp-servers')
      ];
      
      for (const directory of directories) {
        if (!fs.existsSync(directory)) {
          continue;
        }
        
        // Get all subdirectories
        const subdirs = fs.readdirSync(directory, { withFileTypes: true })
          .filter(dirent => dirent.isDirectory())
          .map(dirent => dirent.name);
        
        for (const subdir of subdirs) {
          const serverDir = path.join(directory, subdir);
          
          // Check if this is an MCP server
          const schemaPath = path.join(serverDir, 'mcp.json');
          if (!fs.existsSync(schemaPath)) {
            continue;
          }
          
          try {
            // Read the schema file
            const schemaData = fs.readFileSync(schemaPath, 'utf8');
            const schema = JSON.parse(schemaData);
            
            // Check if this is a valid MCP schema
            if (!schema.name || !schema.description || !schema.tools || !Array.isArray(schema.tools)) {
              continue;
            }
            
            // Check if there's a package.json file with repository information
            let repoUrl = '';
            const packagePath = path.join(serverDir, 'package.json');
            if (fs.existsSync(packagePath)) {
              try {
                const packageData = fs.readFileSync(packagePath, 'utf8');
                const packageJson = JSON.parse(packageData);
                
                if (packageJson.repository) {
                  if (typeof packageJson.repository === 'string') {
                    repoUrl = packageJson.repository;
                  } else if (packageJson.repository.url) {
                    repoUrl = packageJson.repository.url;
                  }
                }
              } catch (error) {
                // Ignore errors reading package.json
              }
            }
            
            // Add the result
            results.push({
              name: schema.name,
              description: schema.description,
              repoUrl: repoUrl || `file://${serverDir}`,
              version: schema.version || '',
              source: 'local' as const,
              official: false,
              installed: false
            });
          } catch (error) {
            // Ignore errors reading the schema file
          }
        }
      }
      
      return results;
    } catch (error) {
      console.error('Error discovering servers from local filesystem:', error);
      return [];
    }
  }
}
