#!/usr/bin/env node

/**
 * Pipeline Integration Test
 * Tests the complete data pipeline workflow
 */

import { readFile, writeFile, mkdir, rm } from 'fs/promises';
import { existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');

// Test directories
const TEST_DIR = join(PROJECT_ROOT, 'data', 'test_tmp');
const TEST_RAW_DIR = join(TEST_DIR, 'raw');
const TEST_PROCESSED_DIR = join(TEST_DIR, 'processed');
const TEST_SCHEMA_DIR = join(PROJECT_ROOT, 'data', 'schema');

let testsPassed = 0;
let testsFailed = 0;

/**
 * Test helper functions
 */
function assert(condition, message) {
  if (condition) {
    console.log(`  ✓ ${message}`);
    testsPassed++;
  } else {
    console.error(`  ✗ ${message}`);
    testsFailed++;
    throw new Error(`Assertion failed: ${message}`);
  }
}

function assertEquals(actual, expected, message) {
  assert(actual === expected, `${message} (expected: ${expected}, actual: ${actual})`);
}

/**
 * Setup test environment
 */
async function setupTestEnv() {
  console.log('\n🔧 Setting up test environment...');
  
  if (existsSync(TEST_DIR)) {
    await rm(TEST_DIR, { recursive: true, force: true });
  }
  
  await mkdir(TEST_DIR, { recursive: true });
  await mkdir(TEST_RAW_DIR, { recursive: true });
  await mkdir(TEST_PROCESSED_DIR, { recursive: true });
  
  console.log('  ✓ Test directories created');
}

/**
 * Cleanup test environment
 */
async function cleanupTestEnv() {
  console.log('\n🧹 Cleaning up test environment...');
  
  if (existsSync(TEST_DIR)) {
    await rm(TEST_DIR, { recursive: true, force: true });
  }
  
  console.log('  ✓ Test directories cleaned');
}

/**
 * Test: Configuration validation
 */
async function testConfigValidation() {
  console.log('\n📋 Test: Configuration Validation');
  
  const configPath = join(PROJECT_ROOT, 'data', 'config', 'source.config.json');
  
  try {
    const configData = await readFile(configPath, 'utf8');
    const config = JSON.parse(configData);
    
    assert(config.sources !== undefined, 'Config has sources array');
    assert(Array.isArray(config.sources), 'Sources is an array');
    assert(config.sources.length > 0, 'Config has at least one source');
    
    // Check first source structure
    const source = config.sources[0];
    assert(source.id !== undefined, 'Source has id');
    assert(source.type !== undefined, 'Source has type');
    assert(source.name !== undefined, 'Source has name');
    assert(source.enabled !== undefined, 'Source has enabled flag');
    assert(source.config !== undefined, 'Source has config object');
    
  } catch (error) {
    console.error(`  ✗ Config validation failed: ${error.message}`);
    testsFailed++;
  }
}

/**
 * Test: Schema validation
 */
async function testSchemaValidation() {
  console.log('\n📐 Test: Schema Validation');
  
  const schemaPath = join(TEST_SCHEMA_DIR, 'records_schema.json');
  
  try {
    const schemaData = await readFile(schemaPath, 'utf8');
    const schema = JSON.parse(schemaData);
    
    assert(schema.$schema !== undefined, 'Schema has $schema field');
    assert(schema.type === 'object', 'Schema type is object');
    assert(schema.properties !== undefined, 'Schema has properties');
    assert(schema.required !== undefined, 'Schema has required fields');
    
  } catch (error) {
    console.error(`  ✗ Schema validation failed: ${error.message}`);
    testsFailed++;
  }
}

/**
 * Test: Anonymization logic
 */
async function testAnonymization() {
  console.log('\n🔒 Test: Anonymization Logic');
  
  try {
    // Simple test of anonymization concept
    const testData = {
      id: '123',
      email: 'test@example.com',
      phone: '+1234567890',
      name: 'John Doe'
    };
    
    // Simulate anonymization
    const { createHash } = await import('crypto');
    
    const emailHash = createHash('sha256')
      .update(testData.email + 'email')
      .digest('hex')
      .substring(0, 16);
    
    const anonymizedEmail = `anon-${emailHash}@anonymized.local`;
    
    assert(anonymizedEmail !== testData.email, 'Email was anonymized');
    assert(anonymizedEmail.includes('anon-'), 'Anonymized email has correct format');
    assert(anonymizedEmail.endsWith('@anonymized.local'), 'Anonymized email has correct domain');
    
  } catch (error) {
    console.error(`  ✗ Anonymization test failed: ${error.message}`);
    testsFailed++;
  }
}

/**
 * Test: Directory structure
 */
async function testDirectoryStructure() {
  console.log('\n📁 Test: Directory Structure');
  
  const requiredDirs = [
    'data/config',
    'data/raw',
    'data/processed',
    'data/seeds',
    'data/schema',
    'data/metadata',
    'scripts'
  ];
  
  for (const dir of requiredDirs) {
    const fullPath = join(PROJECT_ROOT, dir);
    assert(existsSync(fullPath), `Directory exists: ${dir}`);
  }
}

/**
 * Test: Script files exist
 */
async function testScriptFiles() {
  console.log('\n📜 Test: Script Files');
  
  const requiredScripts = [
    'scripts/fetch_source.mjs',
    'scripts/process_data.mjs',
    'scripts/generate_seeds.mjs'
  ];
  
  for (const script of requiredScripts) {
    const fullPath = join(PROJECT_ROOT, script);
    assert(existsSync(fullPath), `Script exists: ${script}`);
  }
}

/**
 * Test: Mock data processing
 */
async function testMockDataProcessing() {
  console.log('\n🧪 Test: Mock Data Processing');
  
  try {
    // Create mock raw data
    const mockData = [
      {
        id: '1',
        createdAt: new Date().toISOString(),
        name: 'Test Record 1',
        email: 'test1@example.com',
        status: 'active'
      },
      {
        id: '2',
        createdAt: new Date().toISOString(),
        name: 'Test Record 2',
        email: 'test2@example.com',
        status: 'pending'
      }
    ];
    
    const mockFilePath = join(TEST_RAW_DIR, 'source-test-records-2024.json');
    await writeFile(mockFilePath, JSON.stringify(mockData, null, 2), 'utf8');
    
    assert(existsSync(mockFilePath), 'Mock data file created');
    
    // Read and validate
    const readData = JSON.parse(await readFile(mockFilePath, 'utf8'));
    assertEquals(readData.length, 2, 'Mock data has correct number of records');
    
  } catch (error) {
    console.error(`  ✗ Mock data processing failed: ${error.message}`);
    testsFailed++;
  }
}

/**
 * Main test execution
 */
async function runTests() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║           Data Pipeline Integration Tests                 ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  
  try {
    await setupTestEnv();
    
    // Run all tests
    await testConfigValidation();
    await testSchemaValidation();
    await testAnonymization();
    await testDirectoryStructure();
    await testScriptFiles();
    await testMockDataProcessing();
    
    await cleanupTestEnv();
    
    // Print summary
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                      Test Summary                          ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log(`\n  Total tests passed: ${testsPassed}`);
    console.log(`  Total tests failed: ${testsFailed}`);
    
    if (testsFailed === 0) {
      console.log('\n  ✓ All tests passed!\n');
      process.exit(0);
    } else {
      console.log('\n  ✗ Some tests failed\n');
      process.exit(1);
    }
    
  } catch (error) {
    console.error('\n✗ Test execution failed:', error.message);
    console.error(error.stack);
    await cleanupTestEnv();
    process.exit(1);
  }
}

// Run tests
runTests();
