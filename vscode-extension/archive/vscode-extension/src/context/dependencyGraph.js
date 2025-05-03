"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DependencyGraph = void 0;
class DependencyGraph {
    constructor() {
        this.nodes = new Map();
    }
    addChunk(chunk) {
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
        }
        else {
            // Update existing node
            const node = this.nodes.get(nodeId);
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
    buildGraph() {
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
    getRelatedFiles(filePath, depth = 1) {
        const node = this.nodes.get(filePath);
        if (!node) {
            return [];
        }
        const visited = new Set();
        const result = [];
        // Add direct dependencies
        this.traverseGraph(node, visited, result, depth, true);
        // Add direct dependents
        this.traverseGraph(node, visited, result, depth, false);
        return result;
    }
    traverseGraph(node, visited, result, depth, isDependency) {
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
exports.DependencyGraph = DependencyGraph;
//# sourceMappingURL=dependencyGraph.js.map