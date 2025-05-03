"use strict";
/**
 * Type definitions for the hierarchical agent system
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ThinkingMode = exports.TaskComplexity = exports.ModelSize = exports.AgentType = void 0;
/**
 * Agent types supported by the system
 */
var AgentType;
(function (AgentType) {
    AgentType["Coordinator"] = "coordinator";
    AgentType["Development"] = "development";
    AgentType["Testing"] = "testing";
    AgentType["CICD"] = "ci_cd";
    AgentType["GitHub"] = "github";
    AgentType["Documentation"] = "documentation";
    AgentType["Architecture"] = "architecture";
    AgentType["Security"] = "security";
    AgentType["Performance"] = "performance";
    AgentType["Simple"] = "simple";
    AgentType["DevOps"] = "devops";
    AgentType["ML"] = "machine_learning";
    AgentType["WebDev"] = "web_development";
})(AgentType || (exports.AgentType = AgentType = {}));
/**
 * Model sizes available for agents
 */
var ModelSize;
(function (ModelSize) {
    ModelSize["Tiny"] = "Qwen3-0.6B";
    ModelSize["Small"] = "Qwen3-1.7B";
    ModelSize["Medium"] = "Qwen3-4B";
    ModelSize["Large"] = "Qwen3-8B";
    ModelSize["XLarge"] = "Qwen3-14B";
    ModelSize["XXLarge"] = "Qwen3-32B";
    ModelSize["MoESmall"] = "Qwen3-30B-A3B";
    ModelSize["MoELarge"] = "Qwen3-235B-A22B";
})(ModelSize || (exports.ModelSize = ModelSize = {}));
/**
 * Task complexity levels
 */
var TaskComplexity;
(function (TaskComplexity) {
    TaskComplexity["Low"] = "low";
    TaskComplexity["Medium"] = "medium";
    TaskComplexity["High"] = "high";
    // New complexity levels for dynamic agent selection
    TaskComplexity["Simple"] = "simple";
    TaskComplexity["Moderate"] = "moderate";
    TaskComplexity["Complex"] = "complex";
    TaskComplexity["VeryComplex"] = "very_complex";
})(TaskComplexity || (exports.TaskComplexity = TaskComplexity = {}));
/**
 * Thinking mode options
 */
var ThinkingMode;
(function (ThinkingMode) {
    ThinkingMode["Enabled"] = "enabled";
    ThinkingMode["Disabled"] = "disabled";
    ThinkingMode["Auto"] = "auto";
})(ThinkingMode || (exports.ThinkingMode = ThinkingMode = {}));
//# sourceMappingURL=types.js.map