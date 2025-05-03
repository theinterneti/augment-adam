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
const assert = __importStar(require("assert"));
const symbolExtractor_1 = require("../../context/symbolExtractor");
suite('Symbol Extractor Test Suite', () => {
    let symbolExtractor;
    setup(() => {
        symbolExtractor = new symbolExtractor_1.SymbolExtractor();
    });
    test('JavaScript Symbol Extraction', async () => {
        const jsCode = `
      import { useState } from 'react';
      import axios from 'axios';
      
      function calculateTotal(items) {
        return items.reduce((total, item) => total + item.price, 0);
      }
      
      class ShoppingCart {
        constructor(items = []) {
          this.items = items;
        }
        
        addItem(item) {
          this.items.push(item);
        }
        
        getTotal() {
          return calculateTotal(this.items);
        }
      }
      
      const cart = new ShoppingCart();
      const fetchItems = async () => {
        const response = await axios.get('/api/items');
        return response.data;
      };
    `;
        const result = await symbolExtractor.extractSymbols(jsCode, 'javascript');
        // Check symbols
        assert.ok(result.symbols.includes('calculateTotal'), 'Should extract function declaration');
        assert.ok(result.symbols.includes('ShoppingCart'), 'Should extract class declaration');
        assert.ok(result.symbols.includes('cart'), 'Should extract variable declaration');
        assert.ok(result.symbols.includes('fetchItems'), 'Should extract arrow function');
        assert.ok(result.symbols.includes('addItem'), 'Should extract method declaration');
        assert.ok(result.symbols.includes('getTotal'), 'Should extract method declaration');
        // Check imports
        assert.ok(result.imports.includes('react'), 'Should extract ES module import');
        assert.ok(result.imports.includes('axios'), 'Should extract default import');
    });
    test('Python Symbol Extraction', async () => {
        const pyCode = `
      import os
      import sys
      from datetime import datetime
      
      CONSTANT_VALUE = 42
      
      def calculate_age(birth_date):
          today = datetime.now()
          age = today.year - birth_date.year
          return age
      
      class Person:
          def __init__(self, name, birth_date):
              self.name = name
              self.birth_date = birth_date
          
          def get_age(self):
              return calculate_age(self.birth_date)
      
      @staticmethod
      def format_date(date):
          return date.strftime("%Y-%m-%d")
    `;
        const result = await symbolExtractor.extractSymbols(pyCode, 'python');
        // Check symbols
        assert.ok(result.symbols.includes('CONSTANT_VALUE'), 'Should extract constant');
        assert.ok(result.symbols.includes('calculate_age'), 'Should extract function declaration');
        assert.ok(result.symbols.includes('Person'), 'Should extract class declaration');
        assert.ok(result.symbols.includes('get_age'), 'Should extract method declaration');
        assert.ok(result.symbols.includes('format_date'), 'Should extract decorated function');
        // Check imports
        assert.ok(result.imports.includes('os'), 'Should extract simple import');
        assert.ok(result.imports.includes('sys'), 'Should extract simple import');
        assert.ok(result.imports.includes('datetime'), 'Should extract from import');
    });
    test('Java Symbol Extraction', async () => {
        const javaCode = `
      package com.example.app;
      
      import java.util.List;
      import java.util.ArrayList;
      
      public class UserManager {
          private List<User> users;
          
          public UserManager() {
              this.users = new ArrayList<>();
          }
          
          public void addUser(User user) {
              users.add(user);
          }
          
          public User findUserById(int id) {
              return users.stream()
                  .filter(user -> user.getId() == id)
                  .findFirst()
                  .orElse(null);
          }
      }
    `;
        const result = await symbolExtractor.extractSymbols(javaCode, 'java');
        // Check symbols
        assert.ok(result.symbols.includes('UserManager'), 'Should extract class declaration');
        assert.ok(result.symbols.includes('users'), 'Should extract field declaration');
        assert.ok(result.symbols.includes('addUser'), 'Should extract method declaration');
        assert.ok(result.symbols.includes('findUserById'), 'Should extract method declaration');
        // Check imports
        assert.ok(result.imports.includes('java.util.List'), 'Should extract import');
        assert.ok(result.imports.includes('java.util.ArrayList'), 'Should extract import');
    });
    test('Language Detection from Path', () => {
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.js'), 'javascript');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.ts'), 'typescript');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.py'), 'python');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.java'), 'java');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.cpp'), 'cpp');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.cs'), 'csharp');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.go'), 'go');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.rb'), 'ruby');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.php'), 'php');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.rs'), 'rust');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.swift'), 'swift');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.kt'), 'kotlin');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.html'), 'html');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.css'), 'css');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.json'), 'json');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.xml'), 'xml');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.yaml'), 'yaml');
        assert.strictEqual(symbolExtractor_1.SymbolExtractor.detectLanguageFromPath('/path/to/file.md'), 'markdown');
    });
});
//# sourceMappingURL=symbolExtractor.test.js.map