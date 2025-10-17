#!/usr/bin/env node

/**
 * Data Source Fetcher
 * Reads source.config.json and fetches data from configured sources
 * Supports REST API, FILE, and MANUAL import types
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');

// Configuration paths
const CONFIG_PATH = join(PROJECT_ROOT, 'data', 'config', 'source.config.json');
const RAW_DATA_DIR = join(PROJECT_ROOT, 'data', 'raw');
const METADATA_DIR = join(PROJECT_ROOT, 'data', 'metadata');

/**
 * Sleep utility for rate limiting
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Load configuration file
 */
async function loadConfig() {
  try {
    const configData = await readFile(CONFIG_PATH, 'utf8');
    return JSON.parse(configData);
  } catch (error) {
    console.error(`Failed to load config from ${CONFIG_PATH}:`, error.message);
    throw error;
  }
}

/**
 * Ensure directory exists
 */
async function ensureDirectory(dirPath) {
  if (!existsSync(dirPath)) {
    await mkdir(dirPath, { recursive: true });
  }
}

/**
 * Fetch data from REST API with pagination support
 */
async function fetchFromRestAPI(source) {
  console.log(`\n=== Fetching from REST API: ${source.name} ===`);
  
  const { baseUrl, endpoints, headers = {}, rateLimit = {} } = source.config;
  const { requestsPerSecond = 1, retryAttempts = 3, retryDelay = 1000 } = rateLimit;
  const delayBetweenRequests = 1000 / requestsPerSecond;
  
  for (const endpoint of endpoints) {
    console.log(`Fetching endpoint: ${endpoint.name}`);
    
    const url = `${baseUrl}${endpoint.path}`;
    const pagination = endpoint.pagination || {};
    const { pageParam = 'page', limitParam = 'limit', defaultLimit = 100, maxPages = 1 } = pagination;
    
    let allRecords = [];
    let currentPage = 1;
    let hasMorePages = true;
    
    while (hasMorePages && currentPage <= maxPages) {
      const params = new URLSearchParams({
        [pageParam]: currentPage,
        [limitParam]: defaultLimit
      });
      
      const requestUrl = `${url}?${params.toString()}`;
      console.log(`  Page ${currentPage}/${maxPages}: ${requestUrl}`);
      
      let attempt = 0;
      let success = false;
      let data = null;
      
      while (attempt < retryAttempts && !success) {
        try {
          const response = await fetch(requestUrl, {
            method: endpoint.method || 'GET',
            headers
          });
          
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }
          
          data = await response.json();
          success = true;
          
          // Handle different response formats
          const records = Array.isArray(data) ? data : (data.data || data.records || data.results || []);
          allRecords.push(...records);
          
          console.log(`    ✓ Fetched ${records.length} records`);
          
          // Check if there are more pages
          hasMorePages = records.length === defaultLimit;
          
        } catch (error) {
          attempt++;
          console.error(`    ✗ Attempt ${attempt}/${retryAttempts} failed: ${error.message}`);
          
          if (attempt < retryAttempts) {
            await sleep(retryDelay * attempt);
          } else {
            console.error(`    Failed after ${retryAttempts} attempts`);
            hasMorePages = false;
          }
        }
      }
      
      currentPage++;
      
      // Rate limiting between requests
      if (hasMorePages) {
        await sleep(delayBetweenRequests);
      }
    }
    
    // Save raw data
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `source-${source.id}-${endpoint.name}-${timestamp}.json`;
    const filepath = join(RAW_DATA_DIR, filename);
    
    await ensureDirectory(RAW_DATA_DIR);
    await writeFile(filepath, JSON.stringify(allRecords, null, 2), 'utf8');
    
    console.log(`\n✓ Saved ${allRecords.length} records to: ${filename}`);
    
    // Save metadata
    const metadata = {
      sourceId: source.id,
      sourceName: source.name,
      sourceType: source.type,
      endpoint: endpoint.name,
      timestamp: new Date().toISOString(),
      recordCount: allRecords.length,
      pagesProcessed: currentPage - 1,
      rawDataFile: filename
    };
    
    const metadataFilename = `metadata-${source.id}-${endpoint.name}-${timestamp}.json`;
    const metadataPath = join(METADATA_DIR, metadataFilename);
    
    await ensureDirectory(METADATA_DIR);
    await writeFile(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');
    
    console.log(`✓ Saved metadata to: ${metadataFilename}`);
  }
}

/**
 * Process file-based import
 */
async function processFileImport(source) {
  console.log(`\n=== Processing File Import: ${source.name} ===`);
  console.log('File import type - waiting for manual file placement');
  console.log(`Expected location: ${source.config.path}`);
  console.log('This is a placeholder for future file-based data import functionality');
}

/**
 * Process manual import
 */
async function processManualImport(source) {
  console.log(`\n=== Processing Manual Import: ${source.name} ===`);
  console.log(`Target directory: ${source.config.targetDirectory}`);
  console.log('This is a placeholder for manual data import functionality');
}

/**
 * Process a single data source
 */
async function processSource(source) {
  if (!source.enabled) {
    console.log(`\n⊘ Skipping disabled source: ${source.name}`);
    return;
  }
  
  try {
    switch (source.type) {
      case 'REST_API':
        await fetchFromRestAPI(source);
        break;
      case 'FILE':
        await processFileImport(source);
        break;
      case 'MANUAL':
        await processManualImport(source);
        break;
      default:
        console.error(`Unknown source type: ${source.type}`);
    }
  } catch (error) {
    console.error(`\n✗ Error processing source ${source.name}:`, error.message);
    throw error;
  }
}

/**
 * Main execution function
 */
async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║           Data Source Fetcher v1.0                         ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  
  try {
    // Load configuration
    console.log('\n📋 Loading configuration...');
    const config = await loadConfig();
    console.log(`Found ${config.sources.length} data source(s)`);
    
    // Process each enabled source
    for (const source of config.sources) {
      await processSource(source);
    }
    
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                  ✓ All sources processed                   ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');
    
  } catch (error) {
    console.error('\n╔════════════════════════════════════════════════════════════╗');
    console.error('║                     ✗ Process failed                       ║');
    console.error('╚════════════════════════════════════════════════════════════╝');
    console.error('\nError:', error.message);
    process.exit(1);
  }
}

// Run the script
main();
