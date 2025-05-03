"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ResponseCache = void 0;
exports.generateCacheKey = generateCacheKey;
/**
 * A simple cache implementation for storing API responses
 */
class ResponseCache {
    constructor(maxEntries = 100, ttlMinutes = 30) {
        this.cache = new Map();
        this.maxEntries = maxEntries;
        this.ttl = ttlMinutes * 60 * 1000;
    }
    /**
     * Get the singleton instance of the cache
     */
    static getInstance() {
        if (!ResponseCache.instance) {
            ResponseCache.instance = new ResponseCache();
        }
        return ResponseCache.instance;
    }
    /**
     * Set cache configuration
     * @param maxEntries Maximum number of entries to store
     * @param ttlMinutes Time to live in minutes
     */
    configure(maxEntries, ttlMinutes) {
        this.maxEntries = maxEntries;
        this.ttl = ttlMinutes * 60 * 1000;
        this.cleanup();
    }
    /**
     * Get a value from the cache
     * @param key Cache key
     * @returns The cached value or undefined if not found or expired
     */
    get(key) {
        const entry = this.cache.get(key);
        if (!entry) {
            return undefined;
        }
        // Check if entry has expired
        if (Date.now() > entry.expiry) {
            this.cache.delete(key);
            return undefined;
        }
        // Update access time
        entry.lastAccessed = Date.now();
        return entry.value;
    }
    /**
     * Set a value in the cache
     * @param key Cache key
     * @param value Value to cache
     */
    set(key, value) {
        // If cache is full, remove least recently used entry
        if (this.cache.size >= this.maxEntries) {
            this.removeLRU();
        }
        this.cache.set(key, {
            value,
            expiry: Date.now() + this.ttl,
            lastAccessed: Date.now()
        });
    }
    /**
     * Check if a key exists in the cache and is not expired
     * @param key Cache key
     * @returns True if the key exists and is not expired
     */
    has(key) {
        const entry = this.cache.get(key);
        if (!entry) {
            return false;
        }
        // Check if entry has expired
        if (Date.now() > entry.expiry) {
            this.cache.delete(key);
            return false;
        }
        return true;
    }
    /**
     * Remove a key from the cache
     * @param key Cache key
     */
    delete(key) {
        this.cache.delete(key);
    }
    /**
     * Clear the entire cache
     */
    clear() {
        this.cache.clear();
    }
    /**
     * Get the number of entries in the cache
     */
    size() {
        return this.cache.size;
    }
    /**
     * Remove expired entries from the cache
     */
    cleanup() {
        const now = Date.now();
        for (const [key, entry] of this.cache.entries()) {
            if (now > entry.expiry) {
                this.cache.delete(key);
            }
        }
    }
    /**
     * Remove the least recently used entry from the cache
     */
    removeLRU() {
        let oldest = null;
        let oldestTime = Date.now();
        for (const [key, entry] of this.cache.entries()) {
            if (entry.lastAccessed < oldestTime) {
                oldest = key;
                oldestTime = entry.lastAccessed;
            }
        }
        if (oldest) {
            this.cache.delete(oldest);
        }
    }
}
exports.ResponseCache = ResponseCache;
/**
 * Generate a cache key from a request
 * @param prompt The prompt text
 * @param options Additional options that affect the response
 * @returns A string key for caching
 */
function generateCacheKey(prompt, options = {}) {
    // Create a stable representation of the options
    const optionsStr = Object.keys(options)
        .sort()
        .map(key => `${key}:${JSON.stringify(options[key])}`)
        .join('|');
    // Combine prompt and options into a single key
    return `${prompt}|${optionsStr}`;
}
//# sourceMappingURL=cache.js.map