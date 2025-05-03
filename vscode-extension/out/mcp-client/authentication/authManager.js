"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthManager = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Authentication manager for MCP servers
 */
class AuthManager {
    /**
     * Create a new authentication manager
     * @param context Extension context
     */
    constructor(context) {
        this._onDidChangeAuth = new vscode.EventEmitter();
        /**
         * Event that fires when authentication changes for a server
         */
        this.onDidChangeAuth = this._onDidChangeAuth.event;
        this.secretStorage = context.secrets;
    }
    /**
     * Dispose of resources
     */
    dispose() {
        this._onDidChangeAuth.dispose();
    }
    /**
     * Get the authentication configuration for a server
     * @param serverId Server ID
     * @returns Promise that resolves to the authentication configuration
     */
    async getAuthConfig(serverId) {
        try {
            const authJson = await this.secretStorage.get(`${AuthManager.SECRET_STORAGE_PREFIX}${serverId}`);
            if (!authJson) {
                return undefined;
            }
            return JSON.parse(authJson);
        }
        catch (error) {
            console.error(`Error getting auth config for server ${serverId}:`, error);
            return undefined;
        }
    }
    /**
     * Set the authentication configuration for a server
     * @param serverId Server ID
     * @param config Authentication configuration
     * @returns Promise that resolves when the configuration is saved
     */
    async setAuthConfig(serverId, config) {
        try {
            await this.secretStorage.store(`${AuthManager.SECRET_STORAGE_PREFIX}${serverId}`, JSON.stringify(config));
            // Notify listeners
            this._onDidChangeAuth.fire(serverId);
        }
        catch (error) {
            console.error(`Error setting auth config for server ${serverId}:`, error);
            throw error;
        }
    }
    /**
     * Delete the authentication configuration for a server
     * @param serverId Server ID
     * @returns Promise that resolves when the configuration is deleted
     */
    async deleteAuthConfig(serverId) {
        try {
            await this.secretStorage.delete(`${AuthManager.SECRET_STORAGE_PREFIX}${serverId}`);
            // Notify listeners
            this._onDidChangeAuth.fire(serverId);
        }
        catch (error) {
            console.error(`Error deleting auth config for server ${serverId}:`, error);
            throw error;
        }
    }
    /**
     * Check if a server has authentication configured
     * @param serverId Server ID
     * @returns Promise that resolves to true if the server has authentication configured
     */
    async hasAuthConfig(serverId) {
        try {
            const authJson = await this.secretStorage.get(`${AuthManager.SECRET_STORAGE_PREFIX}${serverId}`);
            return !!authJson;
        }
        catch (error) {
            console.error(`Error checking auth config for server ${serverId}:`, error);
            return false;
        }
    }
    /**
     * Get authentication headers for a server
     * @param serverId Server ID
     * @returns Promise that resolves to the authentication headers
     */
    async getAuthHeaders(serverId) {
        try {
            const config = await this.getAuthConfig(serverId);
            if (!config) {
                return undefined;
            }
            switch (config.type) {
                case 'token':
                    return {
                        'Authorization': `Bearer ${config.token}`
                    };
                case 'basic':
                    const credentials = Buffer.from(`${config.username}:${config.password}`).toString('base64');
                    return {
                        'Authorization': `Basic ${credentials}`
                    };
                case 'api_key':
                    return {
                        [config.headerName || 'X-API-Key']: config.apiKey
                    };
                case 'oauth2':
                    return {
                        'Authorization': `Bearer ${config.accessToken}`
                    };
                default:
                    return undefined;
            }
        }
        catch (error) {
            console.error(`Error getting auth headers for server ${serverId}:`, error);
            return undefined;
        }
    }
    /**
     * Check if a token needs to be refreshed
     * @param serverId Server ID
     * @returns Promise that resolves to true if the token needs to be refreshed
     */
    async needsTokenRefresh(serverId) {
        try {
            const config = await this.getAuthConfig(serverId);
            if (!config || config.type !== 'oauth2' || !config.expiresAt) {
                return false;
            }
            // Check if the token expires in less than 5 minutes
            const expiresAt = new Date(config.expiresAt).getTime();
            const now = Date.now();
            const fiveMinutesMs = 5 * 60 * 1000;
            return expiresAt - now < fiveMinutesMs;
        }
        catch (error) {
            console.error(`Error checking token refresh for server ${serverId}:`, error);
            return false;
        }
    }
    /**
     * Refresh an OAuth2 token
     * @param serverId Server ID
     * @returns Promise that resolves when the token is refreshed
     */
    async refreshOAuthToken(serverId) {
        try {
            const config = await this.getAuthConfig(serverId);
            if (!config || config.type !== 'oauth2' || !config.refreshToken || !config.tokenUrl) {
                throw new Error('Invalid OAuth2 configuration');
            }
            // Prepare the request
            const params = new URLSearchParams();
            params.append('grant_type', 'refresh_token');
            params.append('refresh_token', config.refreshToken);
            if (config.clientId) {
                params.append('client_id', config.clientId);
            }
            if (config.clientSecret) {
                params.append('client_secret', config.clientSecret);
            }
            // Make the request
            const response = await fetch(config.tokenUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: params.toString()
            });
            if (!response.ok) {
                throw new Error(`Token refresh failed: ${response.statusText}`);
            }
            // Parse the response
            const data = await response.json();
            if (!data.access_token) {
                throw new Error('Token refresh response missing access_token');
            }
            // Update the configuration
            const updatedConfig = {
                ...config,
                accessToken: data.access_token,
                expiresAt: data.expires_in ? new Date(Date.now() + data.expires_in * 1000).toISOString() : undefined,
                refreshToken: data.refresh_token || config.refreshToken
            };
            // Save the updated configuration
            await this.setAuthConfig(serverId, updatedConfig);
        }
        catch (error) {
            console.error(`Error refreshing OAuth token for server ${serverId}:`, error);
            throw error;
        }
    }
    /**
     * Handle authentication for a server
     * @param server Server
     * @returns Promise that resolves when authentication is handled
     */
    async handleAuthentication(server) {
        try {
            // Check if the server requires authentication
            if (!server.schema?.authentication?.required) {
                return;
            }
            // Check if we have authentication configured
            const hasAuth = await this.hasAuthConfig(server.id);
            if (!hasAuth) {
                // Prompt the user to configure authentication
                const configureNow = 'Configure Now';
                const response = await vscode.window.showWarningMessage(`Server ${server.name} requires authentication. Would you like to configure it now?`, configureNow);
                if (response === configureNow) {
                    await this.promptForAuthentication(server);
                }
                else {
                    throw new Error('Authentication required but not configured');
                }
            }
            // Check if we need to refresh the token
            const needsRefresh = await this.needsTokenRefresh(server.id);
            if (needsRefresh) {
                await this.refreshOAuthToken(server.id);
            }
        }
        catch (error) {
            console.error(`Error handling authentication for server ${server.id}:`, error);
            throw error;
        }
    }
    /**
     * Prompt the user to configure authentication for a server
     * @param server Server
     * @returns Promise that resolves when authentication is configured
     */
    async promptForAuthentication(server) {
        try {
            // Check if the server has authentication information
            if (!server.schema?.authentication) {
                throw new Error('Server does not have authentication information');
            }
            const authType = server.schema.authentication.type;
            switch (authType) {
                case 'token':
                    await this.promptForTokenAuth(server);
                    break;
                case 'basic':
                    await this.promptForBasicAuth(server);
                    break;
                case 'api_key':
                    await this.promptForApiKeyAuth(server);
                    break;
                case 'oauth2':
                    await this.promptForOAuth2Auth(server);
                    break;
                default:
                    throw new Error(`Unsupported authentication type: ${authType}`);
            }
        }
        catch (error) {
            console.error(`Error prompting for authentication for server ${server.id}:`, error);
            throw error;
        }
    }
    /**
     * Prompt the user for token authentication
     * @param server Server
     * @returns Promise that resolves when authentication is configured
     */
    async promptForTokenAuth(server) {
        const token = await vscode.window.showInputBox({
            prompt: `Enter token for ${server.name}`,
            password: true,
            ignoreFocusOut: true
        });
        if (!token) {
            throw new Error('Token is required');
        }
        const config = {
            type: 'token',
            token
        };
        await this.setAuthConfig(server.id, config);
    }
    /**
     * Prompt the user for basic authentication
     * @param server Server
     * @returns Promise that resolves when authentication is configured
     */
    async promptForBasicAuth(server) {
        const username = await vscode.window.showInputBox({
            prompt: `Enter username for ${server.name}`,
            ignoreFocusOut: true
        });
        if (!username) {
            throw new Error('Username is required');
        }
        const password = await vscode.window.showInputBox({
            prompt: `Enter password for ${server.name}`,
            password: true,
            ignoreFocusOut: true
        });
        if (!password) {
            throw new Error('Password is required');
        }
        const config = {
            type: 'basic',
            username,
            password
        };
        await this.setAuthConfig(server.id, config);
    }
    /**
     * Prompt the user for API key authentication
     * @param server Server
     * @returns Promise that resolves when authentication is configured
     */
    async promptForApiKeyAuth(server) {
        const apiKey = await vscode.window.showInputBox({
            prompt: `Enter API key for ${server.name}`,
            password: true,
            ignoreFocusOut: true
        });
        if (!apiKey) {
            throw new Error('API key is required');
        }
        const headerName = await vscode.window.showInputBox({
            prompt: `Enter header name for API key (default: X-API-Key)`,
            value: 'X-API-Key',
            ignoreFocusOut: true
        });
        const config = {
            type: 'api_key',
            apiKey,
            headerName: headerName || 'X-API-Key'
        };
        await this.setAuthConfig(server.id, config);
    }
    /**
     * Prompt the user for OAuth2 authentication
     * @param server Server
     * @returns Promise that resolves when authentication is configured
     */
    async promptForOAuth2Auth(server) {
        // This is a simplified implementation
        // A real implementation would use the OAuth2 flow with a web view
        const clientId = await vscode.window.showInputBox({
            prompt: `Enter client ID for ${server.name}`,
            ignoreFocusOut: true
        });
        if (!clientId) {
            throw new Error('Client ID is required');
        }
        const clientSecret = await vscode.window.showInputBox({
            prompt: `Enter client secret for ${server.name}`,
            password: true,
            ignoreFocusOut: true
        });
        if (!clientSecret) {
            throw new Error('Client secret is required');
        }
        const authUrl = await vscode.window.showInputBox({
            prompt: `Enter authorization URL for ${server.name}`,
            ignoreFocusOut: true
        });
        if (!authUrl) {
            throw new Error('Authorization URL is required');
        }
        const tokenUrl = await vscode.window.showInputBox({
            prompt: `Enter token URL for ${server.name}`,
            ignoreFocusOut: true
        });
        if (!tokenUrl) {
            throw new Error('Token URL is required');
        }
        const scopes = await vscode.window.showInputBox({
            prompt: `Enter scopes for ${server.name} (space-separated)`,
            ignoreFocusOut: true
        });
        // In a real implementation, we would now start the OAuth2 flow
        // For now, we'll just store the configuration without the tokens
        const config = {
            type: 'oauth2',
            clientId,
            clientSecret,
            authUrl,
            tokenUrl,
            scopes: scopes?.split(' ') || [],
            accessToken: '',
            refreshToken: '',
            expiresAt: new Date(Date.now()).toISOString()
        };
        await this.setAuthConfig(server.id, config);
        // Show a message to the user
        vscode.window.showInformationMessage('OAuth2 configuration saved. You will need to authenticate the first time you use this server.');
    }
}
exports.AuthManager = AuthManager;
AuthManager.SECRET_STORAGE_PREFIX = 'qwen-coder-assistant.mcp-auth.';
//# sourceMappingURL=authManager.js.map