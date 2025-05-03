import * as fs from 'fs';
import * as path from 'path';
import * as simpleGit from 'simple-git';
import { GitHubOptions } from '../configuration';

/**
 * Repository information
 */
export interface RepoInfo {
  name: string;
  description?: string;
  version?: string;
  localPath: string;
  hasMcpSchema: boolean;
  hasDockerfile: boolean;
  schemaPath?: string;
  dockerfilePath?: string;
}

/**
 * Manager for GitHub repositories
 */
export class GitHubRepoManager {
  private options: GitHubOptions;

  /**
   * Create a new GitHub repository manager
   * @param options GitHub options
   */
  constructor(options: GitHubOptions) {
    this.options = options;
  }

  /**
   * Clone a repository
   * @param repoUrl Repository URL
   * @param targetDir Target directory
   * @returns Promise that resolves to the repository information
   */
  public async cloneRepository(repoUrl: string, targetDir: string): Promise<RepoInfo> {
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
      } else {
        // Clone the repository
        const git = simpleGit.simpleGit();
        const cloneOptions = {
          '--depth': 1
        };

        // Add token if provided
        if (this.options.token) {
          const tokenUrl = this.addTokenToUrl(repoUrl, this.options.token);
          await git.clone(tokenUrl, localPath, cloneOptions);
        } else {
          await git.clone(repoUrl, localPath, cloneOptions);
        }
      }

      // Get repository information
      const info: RepoInfo = {
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
      } else if (fs.existsSync(pyprojectTomlPath)) {
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
    } catch (error) {
      console.error('Error cloning repository:', error);
      throw error;
    }
  }

  /**
   * Get the repository name from a URL
   * @param repoUrl Repository URL
   * @returns Repository name
   */
  private getRepoNameFromUrl(repoUrl: string): string {
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
  private addTokenToUrl(url: string, token: string): string {
    // Check if the URL is an HTTPS URL
    if (url.startsWith('https://')) {
      // Add the token to the URL
      return url.replace('https://', `https://${token}@`);
    }

    return url;
  }
}
