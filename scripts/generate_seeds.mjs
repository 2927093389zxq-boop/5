#!/usr/bin/env node

/**
 * Seed Data Generator
 * Transforms processed data into seed format for database initialization
 */

import { readFile, writeFile, readdir } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = join(__dirname, '..');

// Directory paths
const PROCESSED_DATA_DIR = join(PROJECT_ROOT, 'data', 'processed');
const SEEDS_DIR = join(PROJECT_ROOT, 'data', 'seeds');
const METADATA_DIR = join(PROJECT_ROOT, 'data', 'metadata');

/**
 * Transform processed records to seed format
 */
function transformToSeedFormat(records, sourceId) {
  return records.map((record, index) => ({
    ...record,
    seedId: `${sourceId}-${index + 1}`,
    seedGeneratedAt: new Date().toISOString()
  }));
}

/**
 * Generate seed file from processed data
 */
async function generateSeedFile(processedFilename) {
  console.log(`\n📦 Generating seed from: ${processedFilename}`);
  
  const processedPath = join(PROCESSED_DATA_DIR, processedFilename);
  const rawData = await readFile(processedPath, 'utf8');
  const records = JSON.parse(rawData);
  
  console.log(`  Found ${records.length} records`);
  
  // Extract source ID from filename (format: processed-{sourceId}-{timestamp}.json)
  const sourceId = processedFilename.split('-')[1];
  
  // Transform to seed format
  const seedRecords = transformToSeedFormat(records, sourceId);
  
  // Generate seed filename
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const seedFilename = `seed-${sourceId}-${timestamp}.json`;
  const seedPath = join(SEEDS_DIR, seedFilename);
  
  // Save seed file
  await writeFile(seedPath, JSON.stringify(seedRecords, null, 2), 'utf8');
  console.log(`  ✓ Saved seed file: ${seedFilename}`);
  
  // Generate metadata
  const metadata = {
    seedFile: seedFilename,
    sourceFile: processedFilename,
    sourceId: sourceId,
    recordCount: seedRecords.length,
    generatedAt: new Date().toISOString(),
    lineage: {
      processedFile: processedFilename,
      processedAt: timestamp
    }
  };
  
  const metadataFilename = `seed-metadata-${sourceId}-${timestamp}.json`;
  const metadataPath = join(METADATA_DIR, metadataFilename);
  
  await writeFile(metadataPath, JSON.stringify(metadata, null, 2), 'utf8');
  console.log(`  ✓ Saved metadata: ${metadataFilename}`);
  
  return {
    seedFile: seedFilename,
    recordCount: seedRecords.length
  };
}

/**
 * Find all processed files
 */
async function findProcessedFiles() {
  try {
    const files = await readdir(PROCESSED_DATA_DIR);
    return files.filter(f => f.startsWith('processed-') && f.endsWith('.json'));
  } catch (error) {
    return [];
  }
}

/**
 * Main execution
 */
async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║              Seed Data Generator v1.0                      ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  
  try {
    // Find processed files
    console.log('\n🔍 Searching for processed data files...');
    const processedFiles = await findProcessedFiles();
    
    if (processedFiles.length === 0) {
      console.log('\n⚠ No processed data files found');
      console.log('Run process_data.mjs first to generate processed data\n');
      return;
    }
    
    console.log(`Found ${processedFiles.length} processed file(s)`);
    
    // Generate seed files
    const results = [];
    
    for (const file of processedFiles) {
      const result = await generateSeedFile(file);
      results.push(result);
    }
    
    // Print summary
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                    Generation Summary                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    
    for (const result of results) {
      console.log(`\n${result.seedFile}:`);
      console.log(`  Records: ${result.recordCount}`);
    }
    
    console.log('\n✓ All seed files generated successfully\n');
    
  } catch (error) {
    console.error('\n✗ Seed generation failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  }
}

// Run the script
main();
