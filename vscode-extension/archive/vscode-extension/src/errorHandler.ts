import * as vscode from 'vscode';
import axios, { AxiosError } from 'axios';

export enum ErrorType {
  NetworkError = 'NetworkError',
  AuthenticationError = 'AuthenticationError',
  RateLimitError = 'RateLimitError',
  ServerError = 'ServerError',
  TimeoutError = 'TimeoutError',
  UnknownError = 'UnknownError'
}

export interface ErrorDetails {
  type: ErrorType;
  message: string;
  originalError?: Error;
  retryable: boolean;
  suggestedAction?: string;
}

/**
 * Handles API errors and provides user-friendly error messages
 */
export class ErrorHandler {
  /**
   * Process an error and return structured error details
   * @param error The error to process
   * @returns Structured error details
   */
  public static processError(error: unknown): ErrorDetails {
    // Default error details
    let errorDetails: ErrorDetails = {
      type: ErrorType.UnknownError,
      message: 'An unknown error occurred',
      originalError: error instanceof Error ? error : undefined,
      retryable: false
    };

    // Handle Axios errors
    if (axios.isAxiosError(error)) {
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
  private static processAxiosError(error: AxiosError): ErrorDetails {
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
            } else if (typeof error.response.data === 'object' && error.response.data.error) {
              message = error.response.data.error;
            }
          }
        } catch (e) {
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
  public static showErrorToUser(error: ErrorDetails): void {
    const message = `${error.message}${error.suggestedAction ? '\n\n' + error.suggestedAction : ''}`;
    
    // Show different types of notifications based on error type
    if (error.retryable) {
      vscode.window.showWarningMessage(message, 'Retry').then(selection => {
        if (selection === 'Retry') {
          // Emit an event that can be listened to for retrying the operation
          // This will be implemented when we add the retry functionality
        }
      });
    } else {
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
  public static handleError(error: unknown): ErrorDetails {
    const errorDetails = this.processError(error);
    this.showErrorToUser(errorDetails);
    return errorDetails;
  }
}
