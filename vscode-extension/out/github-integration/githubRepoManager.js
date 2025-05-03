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
exports.GitHubRepoManager = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const simpleGit = __importStar(require("simple-git"));
/**
 * Manager for GitHub repositories
 */
class GitHubRepoManager {
    /**
     * Create a new GitHub repository manager
     * @param options GitHub options
     */
    constructor(options) {
        this.options = options;
    }
    /**
     * Clone a repository
     * @param repoUrl Repository URL
     * @param targetDir Target directory
     * @returns Promise that resolves to the repository information
     */
    async cloneRepository(repoUrl, targetDir) {
        try {
            // Parse the repository URL to get the name
            const repoName = this.getRepoNameFromUrl(repoUrl);
            // Create the target directory if it doesn't exist
            if (!fs.existsSync(targetDir)) {
                fs.mkdirSync(targetDir, { recursive: true });
            }
            // Set the local path
            const localPath = path.join(targetDir, repoName);
            // Check if the repository already exists
            if (fs.existsSync(localPath)) {
                // Pull the latest changes
                const git = simpleGit.simpleGit(localPath);
                await git.pull();
            }
            else {
                // Clone the repository
                const git = simpleGit.simpleGit();
                const cloneOptions = {
                    '--depth': 1
                };
                // Add token if provided
                if (this.options.token) {
                    const tokenUrl = this.addTokenToUrl(repoUrl, this.options.token);
                    await git.clone(tokenUrl, localPath, cloneOptions);
                }
                else {
                    await git.clone(repoUrl, localPath, cloneOptions);
                }
            }
            // Get repository information
            const info = {
                name: repoName,
                localPath,
                hasMcpSchema: false,
                hasDockerfile: false
            };
            // Check for MCP schema file
            const schemaFiles = [
                'mcp-schema.json',
                'schema.json',
                'mcp.json',
                'mcp-schema.yaml',
                'schema.yaml',
                'mcp.yaml'
            ];
            for (const schemaFile of schemaFiles) {
                const schemaPath = path.join(localPath, schemaFile);
                if (fs.existsSync(schemaPath)) {
                    info.hasMcpSchema = true;
                    info.schemaPath = schemaPath;
                    break;
                }
            }
            // Check for Dockerfile
            const dockerfileFiles = [
                'Dockerfile',
                'docker/Dockerfile',
                '.docker/Dockerfile'
            ];
            for (const dockerfileFile of dockerfileFiles) {
                const dockerfilePath = path.join(localPath, dockerfileFile);
                if (fs.existsSync(dockerfilePath)) {
                    info.hasDockerfile = true;
                    info.dockerfilePath = dockerfilePath;
                    break;
                }
            }
            // Try to get description and version from package.json or pyproject.toml
            const packageJsonPath = path.join(localPath, 'package.json');
            const pyprojectTomlPath = path.join(localPath, 'pyproject.toml');
            if (fs.existsSync(packageJsonPath)) {
                const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
                info.description = packageJson.description;
                info.version = packageJson.version;
            }
            else if (fs.existsSync(pyprojectTomlPath)) {
                const pyprojectToml = fs.readFileSync(pyprojectTomlPath, 'utf8');
                // Try to parse the version from pyproject.toml
                const versionMatch = pyprojectToml.match(/version\s*=\s*["']([^"']+)["']/);
                if (versionMatch) {
                    info.version = versionMatch[1];
                }
                // Try to parse the description from pyproject.toml
                const descriptionMatch = pyprojectToml.match(/description\s*=\s*["']([^"']+)["']/);
                if (descriptionMatch) {
                    info.description = descriptionMatch[1];
                }
            }
            return info;
        }
        catch (error) {
            console.error('Error cloning repository:', error);
            throw error;
        }
    }
    /**
     * Get the repository name from a URL
     * @param repoUrl Repository URL
     * @returns Repository name
     */
    getRepoNameFromUrl(repoUrl) {
        // Remove .git extension if present
        const url = repoUrl.endsWith('.git') ? repoUrl.slice(0, -4) : repoUrl;
        // Get the last part of the URL
        const parts = url.split('/');
        return parts[parts.length - 1];
    }
    /**
     * Add a token to a URL
     * @param url URL
     * @param token Token
     * @returns URL with token
     */
    addTokenToUrl(url, token) {
        // Check if the URL is an HTTPS URL
        if (url.startsWith('https://')) {
            // Add the token to the URL
            return url.replace('https://', `https://${token}@`);
        }
        return url;
    }
}
exports.GitHubRepoManager = GitHubRepoManager;
//# sourceMappingURL=githubRepoManager.js.map