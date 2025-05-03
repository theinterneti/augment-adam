import { CodeChunk } from './types';

interface DependencyNode {
  id: string;
  filePath: string;
  symbols: string[];
  imports: string[];
  dependencies: string[];
  dependents: string[];
}

export class DependencyGraph {
  private nodes: Map<string, DependencyNode> = new Map();
  
  public addChunk(chunk: CodeChunk): void {
    const nodeId = chunk.filePath;
    
    if (!this.nodes.has(nodeId)) {
      this.nodes.set(nodeId, {
        id: nodeId,
        filePath: chunk.filePath,
        symbols: [...chunk.symbols],
        imports: [...chunk.imports],
        dependencies: [],
        dependents: []
      });
    } else {
      // Update existing node
      const node = this.nodes.get(nodeId)!;
      chunk.symbols.forEach(symbol => {
        if (!node.symbols.includes(symbol)) {
          node.symbols.push(symbol);
        }
      });
      chunk.imports.forEach(imp => {
        if (!node.imports.includes(imp)) {
          node.imports.push(imp);
        }
      });
    }
  }
  
  public buildGraph(): void {
    // Clear existing dependencies
    for (const node of this.nodes.values()) {
      node.dependencies = [];
      node.dependents = [];
    }
    
    // Build dependencies based on imports and symbols
    for (const [id, node] of this.nodes.entries()) {
      for (const [otherId, otherNode] of this.nodes.entries()) {
        if (id === otherId) {
          continue;
        }
        
        // Check if this node imports symbols from the other node
        for (const imp of node.imports) {
          if (otherNode.symbols.some(symbol => imp.includes(symbol))) {
            if (!node.dependencies.includes(otherId)) {
              node.dependencies.push(otherId);
            }
            if (!otherNode.dependents.includes(id)) {
              otherNode.dependents.push(id);
            }
          }
        }
      }
    }
  }
  
  public getRelatedFiles(filePath: string, depth: number = 1): string[] {
    const node = this.nodes.get(filePath);
    if (!node) {
      return [];
    }
    
    const visited = new Set<string>();
    const result: string[] = [];
    
    // Add direct dependencies
    this.traverseGraph(node, visited, result, depth, true);
    
    // Add direct dependents
    this.traverseGraph(node, visited, result, depth, false);
    
    return result;
  }
  
  private traverseGraph(
    node: DependencyNode,
    visited: Set<string>,
    result: string[],
    depth: number,
    isDependency: boolean
  ): void {
    if (depth <= 0 || visited.has(node.id)) {
      return;
    }
    
    visited.add(node.id);
    if (node.id !== result[0]) { // Don't add the starting node
      result.push(node.id);
    }
    
    const nextNodes = isDependency ? node.dependencies : node.dependents;
    for (const nextId of nextNodes) {
      const nextNode = this.nodes.get(nextId);
      if (nextNode) {
        this.traverseGraph(nextNode, visited, result, depth - 1, isDependency);
      }
    }
  }
}
