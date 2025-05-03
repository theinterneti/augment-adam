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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ErrorHandler = exports.ErrorType = void 0;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
var ErrorType;
(function (ErrorType) {
    ErrorType["NetworkError"] = "NetworkError";
    ErrorType["AuthenticationError"] = "AuthenticationError";
    ErrorType["RateLimitError"] = "RateLimitError";
    ErrorType["ServerError"] = "ServerError";
    ErrorType["TimeoutError"] = "TimeoutError";
    ErrorType["UnknownError"] = "UnknownError";
})(ErrorType || (exports.ErrorType = ErrorType = {}));
/**
 * Handles API errors and provides user-friendly error messages
 */
class ErrorHandler {
    /**
     * Process an error and return structured error details
     * @param error The error to process
     * @returns Structured error details
     */
    static processError(error) {
        // Default error details
        let errorDetails = {
            type: ErrorType.UnknownError,
            message: 'An unknown error occurred',
            originalError: error instanceof Error ? error : undefined,
            retryable: false
        };
        // Handle Axios errors
        if (axios_1.default.isAxiosError(error)) {
            errorDetails = this.processAxiosError(error);
        }
        // Handle timeout errors
        else if (error instanceof Error && error.message.includes('timeout')) {
            errorDetails = {
                type: ErrorType.TimeoutError,
                message: 'The request timed out. The server might be overloaded.',
                originalError: error,
                retryable: true,
                suggestedAction: 'Try again later or check your internet connection.'
            };
        }
        // Handle other errors
        else if (error instanceof Error) {
            errorDetails = {
                type: ErrorType.UnknownError,
                message: `Error: ${error.message}`,
                originalError: error,
                retryable: false
            };
        }
        return errorDetails;
    }
    /**
     * Process an Axios error and return structured error details
     * @param error The Axios error to process
     * @returns Structured error details
     */
    static processAxiosError(error) {
        // Network errors
        if (error.code === 'ECONNABORTED' || error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
            return {
                type: ErrorType.NetworkError,
                message: 'Could not connect to the API. Please check your internet connection.',
                originalError: error,
                retryable: true,
                suggestedAction: 'Check your network connection and try again.'
            };
        }
        // Handle based on HTTP status code
        switch (error.response?.status) {
            case 401:
            case 403:
                return {
                    type: ErrorType.AuthenticationError,
                    message: 'Authentication failed. Please check your API key.',
                    originalError: error,
                    retryable: false,
                    suggestedAction: 'Update your API key in the extension settings.'
                };
            case 429:
                return {
                    type: ErrorType.RateLimitError,
                    message: 'Rate limit exceeded. Too many requests in a short period.',
                    originalError: error,
                    retryable: true,
                    suggestedAction: 'Wait a moment before trying again.'
                };
            case 500:
            case 502:
            case 503:
            case 504:
                return {
                    type: ErrorType.ServerError,
                    message: `Server error (${error.response.status}). The API service might be experiencing issues.`,
                    originalError: error,
                    retryable: true,
                    suggestedAction: 'Try again later.'
                };
            default:
                // Try to extract error message from response if available
                let message = 'An error occurred while communicating with the API.';
                try {
                    if (error.response?.data) {
                        if (typeof error.response.data === 'string') {
                            message = error.response.data;
                        }
                        else if (typeof error.response.data === 'object' && error.response.data.error) {
                            message = error.response.data.error;
                        }
                    }
                }
                catch (e) {
                    // Ignore parsing errors
                }
                return {
                    type: ErrorType.UnknownError,
                    message,
                    originalError: error,
                    retryable: false
                };
        }
    }
    /**
     * Display an error message to the user
     * @param error The error details to display
     */
    static showErrorToUser(error) {
        const message = `${error.message}${error.suggestedAction ? '\n\n' + error.suggestedAction : ''}`;
        // Show different types of notifications based on error type
        if (error.retryable) {
            vscode.window.showWarningMessage(message, 'Retry').then(selection => {
                if (selection === 'Retry') {
                    // Emit an event that can be listened to for retrying the operation
                    // This will be implemented when we add the retry functionality
                }
            });
        }
        else {
            vscode.window.showErrorMessage(message);
        }
        // Log the error for debugging
        console.error('API Error:', error.type, error.originalError);
    }
    /**
     * Handle an error by processing it and showing a message to the user
     * @param error The error to handle
     * @returns The processed error details
     */
    static handleError(error) {
        const errorDetails = this.processError(error);
        this.showErrorToUser(errorDetails);
        return errorDetails;
    }
}
exports.ErrorHandler = ErrorHandler;
//# sourceMappingURL=errorHandler.js.map