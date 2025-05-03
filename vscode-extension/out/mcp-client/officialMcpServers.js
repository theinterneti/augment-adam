"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OfficialMcpServersManager = exports.OFFICIAL_MCP_SERVERS = void 0;
/**
 * Official MCP server repository URLs
 */
exports.OFFICIAL_MCP_SERVERS = {
    GITHUB: 'https://github.com/modelcontextprotocol/mcp-server-github',
    DOCKER: 'https://github.com/modelcontextprotocol/mcp-server-docker',
    GIT: 'https://github.com/modelcontextprotocol/mcp-server-git',
    MEMORY: 'https://github.com/modelcontextprotocol/mcp-server-memory',
    FILESYSTEM: 'https://github.com/modelcontextprotocol/mcp-server-filesystem'
};
/**
 * Manager for official MCP servers
 */
class OfficialMcpServersManager {
    /**
     * Create a new official MCP servers manager
     * @param serverManager MCP server manager
     */
    constructor(serverManager) {
        this.serverManager = serverManager;
    }
    /**
     * Add the GitHub MCP server
     * @returns Promise that resolves to the server ID
     */
    async addGitHubServer() {
        try {
            const server = await this.serverManager.addServerFromGitHub(exports.OFFICIAL_MCP_SERVERS.GITHUB);
            return server.id;
        }
        catch (error) {
            console.error('Error adding GitHub MCP server:', error);
            throw new Error(`Failed to add GitHub MCP server: ${error}`);
        }
    }
    /**
     * Add the Docker MCP server
     * @returns Promise that resolves to the server ID
     */
    async addDockerServer() {
        try {
            const server = await this.serverManager.addServerFromGitHub(exports.OFFICIAL_MCP_SERVERS.DOCKER);
            return server.id;
        }
        catch (error) {
            console.error('Error adding Docker MCP server:', error);
            throw new Error(`Failed to add Docker MCP server: ${error}`);
        }
    }
    /**
     * Add the Git MCP server
     * @returns Promise that resolves to the server ID
     */
    async addGitServer() {
        try {
            const server = await this.serverManager.addServerFromGitHub(exports.OFFICIAL_MCP_SERVERS.GIT);
            return server.id;
        }
        catch (error) {
            console.error('Error adding Git MCP server:', error);
            throw new Error(`Failed to add Git MCP server: ${error}`);
        }
    }
    /**
     * Add the Memory MCP server
     * @returns Promise that resolves to the server ID
     */
    async addMemoryServer() {
        try {
            const server = await this.serverManager.addServerFromGitHub(exports.OFFICIAL_MCP_SERVERS.MEMORY);
            return server.id;
        }
        catch (error) {
            console.error('Error adding Memory MCP server:', error);
            throw new Error(`Failed to add Memory MCP server: ${error}`);
        }
    }
    /**
     * Add the Filesystem MCP server
     * @returns Promise that resolves to the server ID
     */
    async addFilesystemServer() {
        try {
            const server = await this.serverManager.addServerFromGitHub(exports.OFFICIAL_MCP_SERVERS.FILESYSTEM);
            return server.id;
        }
        catch (error) {
            console.error('Error adding Filesystem MCP server:', error);
            throw new Error(`Failed to add Filesystem MCP server: ${error}`);
        }
    }
    /**
     * Add all official MCP servers
     * @returns Promise that resolves to an array of server IDs
     */
    async addAllOfficialServers() {
        const serverIds = [];
        try {
            // Add GitHub server
            const githubId = await this.addGitHubServer();
            serverIds.push(githubId);
        }
        catch (error) {
            console.error('Error adding GitHub MCP server:', error);
        }
        try {
            // Add Docker server
            const dockerId = await this.addDockerServer();
            serverIds.push(dockerId);
        }
        catch (error) {
            console.error('Error adding Docker MCP server:', error);
        }
        try {
            // Add Git server
            const gitId = await this.addGitServer();
            serverIds.push(gitId);
        }
        catch (error) {
            console.error('Error adding Git MCP server:', error);
        }
        try {
            // Add Memory server
            const memoryId = await this.addMemoryServer();
            serverIds.push(memoryId);
        }
        catch (error) {
            console.error('Error adding Memory MCP server:', error);
        }
        try {
            // Add Filesystem server
            const filesystemId = await this.addFilesystemServer();
            serverIds.push(filesystemId);
        }
        catch (error) {
            console.error('Error adding Filesystem MCP server:', error);
        }
        return serverIds;
    }
    /**
     * Check if a server is an official MCP server
     * @param repoUrl Repository URL
     * @returns True if the server is an official MCP server
     */
    isOfficialMcpServer(repoUrl) {
        const officialUrls = Object.values(exports.OFFICIAL_MCP_SERVERS);
        return officialUrls.includes(repoUrl);
    }
    /**
     * Get the type of an official MCP server
     * @param repoUrl Repository URL
     * @returns Server type or undefined if not an official server
     */
    getOfficialServerType(repoUrl) {
        for (const [type, url] of Object.entries(exports.OFFICIAL_MCP_SERVERS)) {
            if (url === repoUrl) {
                return type.toLowerCase();
            }
        }
        return undefined;
    }
}
exports.OfficialMcpServersManager = OfficialMcpServersManager;
//# sourceMappingURL=officialMcpServers.js.map