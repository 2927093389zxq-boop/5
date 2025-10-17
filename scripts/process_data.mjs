#!/usr/bin/env node

/**
 * Data Processor & Validator
 * Validates raw data against schemas and applies anonymization
 * Transforms validated data into processed format
 */

import { readFile, writeFile, readdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createHash } from 'crypto';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');

// Directory paths
const RAW_DATA_DIR = join(PROJECT_ROOT, 'data', 'raw');
const PROCESSED_DATA_DIR = join(PROJECT_ROOT, 'data', 'processed');
const SCHEMA_DIR = join(PROJECT_ROOT, 'data', 'schema');
const METADATA_DIR = join(PROJECT_ROOT, 'data', 'metadata');
const CONFIG_PATH = join(PROJECT_ROOT, 'data', 'config', 'source.config.json');

/**
 * Load configuration
 */
async function loadConfig() {
  const configData = await readFile(CONFIG_PATH, 'utf8');
  return JSON.parse(configData);
}

/**
 * Load schema file
 */
async function loadSchema(schemaFile) {
  const schemaPath = join(SCHEMA_DIR, schemaFile);
  const schemaData = await readFile(schemaPath, 'utf8');
  return JSON.parse(schemaData);
}

/**
 * Simple schema validator (basic implementation)
 * In production, consider using ajv or similar library
 */
function validateAgainstSchema(data, schema) {
  const errors = [];
  
  // Check required fields
  if (schema.required) {
    for (const field of schema.required) {
      if (!(field in data)) {
        errors.push(`Missing required field: ${field}`);
      }
    }
  }
  
  // Check property types
  if (schema.properties) {
    for (const [key, propSchema] of Object.entries(schema.properties)) {
      if (key in data) {
        const value = data[key];
        const expectedType = propSchema.type;
        
        if (expectedType === 'string' && typeof value !== 'string') {
          errors.push(`Field '${key}' should be string, got ${typeof value}`);
        } else if (expectedType === 'number' && typeof value !== 'number') {
          errors.push(`Field '${key}' should be number, got ${typeof value}`);
        } else if (expectedType === 'boolean' && typeof value !== 'boolean') {
          errors.push(`Field '${key}' should be boolean, got ${typeof value}`);
        } else if (expectedType === 'object' && (typeof value !== 'object' || value === null)) {
          errors.push(`Field '${key}' should be object, got ${typeof value}`);
        } else if (expectedType === 'array' && !Array.isArray(value)) {
          errors.push(`Field '${key}' should be array, got ${typeof value}`);
        }
        
        // Check enum values
        if (propSchema.enum && !propSchema.enum.includes(value)) {
          errors.push(`Field '${key}' value '${value}' not in allowed values: ${propSchema.enum.join(', ')}`);
        }
      }
    }
  }
  
  return errors;
}

/**
 * Anonymize sensitive field
 * Uses SHA-256 with field-specific salt for anonymization
 * Note: For production use with highly sensitive data, consider using bcrypt or PBKDF2
 */
function anonymizeField(value, fieldName) {
  if (value === null || value === undefined) {
    return value;
  }
  
  // Convert to string for hashing
  const strValue = String(value);
  
  // Use a field-specific salt to prevent rainbow table attacks
  // In production, use environment variable or secure key management
  const salt = `ANON_SALT_${fieldName}_v1`;
  
  // Create a hash-based anonymization
  const hash = createHash('sha256')
    .update(salt + strValue + fieldName)
    .digest('hex')
    .substring(0, 16);
  
  // Return anonymized value based on field type
  if (fieldName === 'email') {
    return `anon-${hash}@anonymized.local`;
  } else if (fieldName === 'phone') {
    return `+1-XXX-XXX-${hash.substring(0, 4)}`;
  } else if (fieldName === 'address') {
    return `[REDACTED-${hash.substring(0, 8)}]`;
  } else {
    return `[ANONYMIZED-${hash.substring(0, 8)}]`;
  }
}

/**
 * Apply anonymization to a record
 */
function anonymizeRecord(record, fieldsToAnonymize) {
  const anonymized = { ...record };
  
  for (const field of fieldsToAnonymize) {
    if (field in anonymized) {
      anonymized[field] = anonymizeField(anonymized[field], field);
    }
  }
  
  return anonymized;
}

/**
 * Process a single raw data file
 */
async function processRawFile(filename, sourceConfig) {
  console.log(`\n📄 Processing: ${filename}`);
  
  const rawFilePath = join(RAW_DATA_DIR, filename);
  const rawData = await readFile(rawFilePath, 'utf8');
  const records = JSON.parse(rawData);
  
  if (!Array.isArray(records)) {
    console.error(`  ✗ Data is not an array, skipping`);
    return null;
  }
  
  console.log(`  Found ${records.length} records`);
  
  // Load schema if validation is enabled
  let schema = null;
  if (sourceConfig.schemaValidation?.enabled && sourceConfig.schemaValidation?.schemaFile) {
    try {
      schema = await loadSchema(sourceConfig.schemaValidation.schemaFile);
      console.log(`  ✓ Loaded schema: ${sourceConfig.schemaValidation.schemaFile}`);
    } catch (error) {
      console.error(`  ✗ Failed to load schema: ${error.message}`);
    }
  }
  
  // Process each record
  const processedRecords = [];
  const validationErrors = [];
  let anonymizedCount = 0;
  
  for (let i = 0; i < records.length; i++) {
    let record = records[i];
    
    // Validate if schema is loaded
    if (schema) {
      const errors = validateAgainstSchema(record, schema);
      if (errors.length > 0) {
        console.log(`    ⚠ Record ${i} validation failed: ${errors[0]}`);
        validationErrors.push({ recordIndex: i, errors });
        continue; // Skip invalid records
      }
    }
    
    // Anonymize if enabled
    if (sourceConfig.anonymization?.enabled && sourceConfig.anonymization?.fields) {
      record = anonymizeRecord(record, sourceConfig.anonymization.fields);
      anonymizedCount++;
    }
    
    processedRecords.push(record);
  }
  
  console.log(`  ✓ Valid records: ${processedRecords.length}`);
  if (validationErrors.length > 0) {
    console.log(`  ⚠ Invalid records: ${validationErrors.length}`);
  }
  if (anonymizedCount > 0) {
    console.log(`  🔒 Anonymized: ${anonymizedCount} records`);
  }
  
  // Save processed data
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const processedFilename = `processed-${sourceConfig.id}-${timestamp}.json`;
  const processedPath = join(PROCESSED_DATA_DIR, processedFilename);
  
  await writeFile(processedPath, JSON.stringify(processedRecords, null, 2), 'utf8');
  console.log(`  ✓ Saved to: ${processedFilename}`);
  
  // Save validation report if there were errors
  if (validationErrors.length > 0) {
    const reportFilename = `validation-errors-${sourceConfig.id}-${timestamp}.json`;
    const reportPath = join(METADATA_DIR, reportFilename);
    await writeFile(reportPath, JSON.stringify(validationErrors, null, 2), 'utf8');
    console.log(`  ⚠ Validation errors saved to: ${reportFilename}`);
  }
  
  return {
    originalCount: records.length,
    processedCount: processedRecords.length,
    errorCount: validationErrors.length,
    processedFile: processedFilename
  };
}

/**
 * Find raw files for a specific source
 */
async function findRawFilesForSource(sourceId) {
  try {
    const files = await readdir(RAW_DATA_DIR);
    return files.filter(f => f.startsWith(`source-${sourceId}-`) && f.endsWith('.json'));
  } catch (error) {
    return [];
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║         Data Processor & Validator v1.0                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  
  try {
    // Load configuration
    console.log('\n📋 Loading configuration...');
    const config = await loadConfig();
    
    // Process each source
    const results = [];
    
    for (const source of config.sources) {
      if (!source.enabled) {
        console.log(`\n⊘ Skipping disabled source: ${source.name}`);
        continue;
      }
      
      console.log(`\n=== Processing source: ${source.name} ===`);
      
      // Find raw files for this source
      const rawFiles = await findRawFilesForSource(source.id);
      
      if (rawFiles.length === 0) {
        console.log(`  No raw data files found for source: ${source.id}`);
        continue;
      }
      
      console.log(`  Found ${rawFiles.length} raw file(s)`);
      
      for (const file of rawFiles) {
        const result = await processRawFile(file, source);
        if (result) {
          results.push({ source: source.name, ...result });
        }
      }
    }
    
    // Print summary
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                    Processing Summary                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    
    for (const result of results) {
      console.log(`\n${result.source}:`);
      console.log(`  Original records: ${result.originalCount}`);
      console.log(`  Processed records: ${result.processedCount}`);
      console.log(`  Validation errors: ${result.errorCount}`);
      console.log(`  Output: ${result.processedFile}`);
    }
    
    console.log('\n✓ All data processed successfully\n');
    
  } catch (error) {
    console.error('\n✗ Processing failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the script
main();
