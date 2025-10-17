# Data Pipeline Documentation

## Overview

This automated data pipeline fetches, validates, anonymizes, and transforms data from various sources into seed data suitable for database initialization.

## Directory Structure

```
data/
├── config/              # Configuration files
│   └── source.config.json
├── raw/                 # Raw data from sources (before processing)
├── processed/           # Validated and anonymized data
├── seeds/               # Final seed data for database initialization
├── schema/              # JSON schemas for validation
└── metadata/            # Pipeline execution metadata and lineage
```

## Configuration

### Source Configuration (`data/config/source.config.json`)

Defines data sources with the following properties:

- **id**: Unique identifier for the source
- **type**: Source type (`REST_API`, `FILE`, `MANUAL`)
- **name**: Human-readable name
- **enabled**: Whether the source is active
- **config**: Source-specific configuration
- **anonymization**: Anonymization settings
- **schemaValidation**: Schema validation settings

#### Example REST API Source

```json
{
  "id": "example-api",
  "type": "REST_API",
  "enabled": true,
  "config": {
    "baseUrl": "https://example.com/api",
    "endpoints": [
      {
        "name": "records",
        "path": "/records",
        "method": "GET",
        "pagination": {
          "type": "offset",
          "pageParam": "page",
          "limitParam": "limit",
          "defaultLimit": 100,
          "maxPages": 10
        }
      }
    ]
  },
  "anonymization": {
    "enabled": true,
    "fields": ["email", "phone", "address"]
  },
  "schemaValidation": {
    "enabled": true,
    "schemaFile": "records_schema.json"
  }
}
```

## Pipeline Scripts

### 1. `fetch_source.mjs` - Data Fetcher

Fetches data from configured sources and saves to `data/raw/`.

**Usage:**
```bash
node scripts/fetch_source.mjs
```

**Features:**
- REST API pagination support
- Rate limiting
- Retry logic with exponential backoff
- Metadata tracking
- Extensible to support FILE and MANUAL import types

### 2. `process_data.mjs` - Data Processor

Validates and anonymizes raw data, saving to `data/processed/`.

**Usage:**
```bash
node scripts/process_data.mjs
```

**Features:**
- JSON Schema validation
- Field anonymization (hashing-based)
- Error reporting
- Validation error tracking

### 3. `generate_seeds.mjs` - Seed Generator

Transforms processed data into seed format for database initialization.

**Usage:**
```bash
node scripts/generate_seeds.mjs
```

**Features:**
- Seed format transformation
- Lineage tracking
- Metadata generation

## Complete Pipeline Execution

Run the complete pipeline in sequence:

```bash
# 1. Fetch data from sources
node scripts/fetch_source.mjs

# 2. Process and validate
node scripts/process_data.mjs

# 3. Generate seeds
node scripts/generate_seeds.mjs
```

## Schema Validation

Schemas are defined in `data/schema/` using JSON Schema format.

### Example Schema (`records_schema.json`)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RecordData",
  "type": "object",
  "required": ["id", "createdAt"],
  "properties": {
    "id": { "type": "string" },
    "createdAt": { "type": "string", "format": "date-time" },
    "email": { "type": "string", "format": "email" },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "pending"]
    }
  }
}
```

## Anonymization

The pipeline supports field-level anonymization using SHA-256 hashing.

**Anonymized Fields:**
- `email` → `anon-{hash}@anonymized.local`
- `phone` → `+1-XXX-XXX-{hash}`
- `address` → `[REDACTED-{hash}]`
- Other fields → `[ANONYMIZED-{hash}]`

## CI Integration

The pipeline includes GitHub Actions workflow (`.github/workflows/data-pipeline.yml`) that:

1. Validates configuration files
2. Checks directory structure
3. Validates script syntax
4. Runs security scans
5. Verifies anonymization settings

**Triggers:**
- Push to main/develop branches
- Pull requests
- Manual workflow dispatch
- Scheduled daily runs (2 AM UTC)

## Extending the Pipeline

### Adding a New Data Source Type

1. Update `source.config.json` with new source configuration
2. Implement handler in `fetch_source.mjs`:
   ```javascript
   case 'NEW_TYPE':
     await processNewType(source);
     break;
   ```

### Adding Custom Validation Rules

1. Create schema in `data/schema/`
2. Reference schema in source configuration
3. Extend `validateAgainstSchema()` in `process_data.mjs` if needed

### Custom Anonymization

Modify `anonymizeField()` function in `process_data.mjs`:

```javascript
function anonymizeField(value, fieldName) {
  // Custom anonymization logic
  if (fieldName === 'customField') {
    return customAnonymization(value);
  }
  // ... existing logic
}
```

## Metadata & Lineage

Each processing step generates metadata files in `data/metadata/` that track:

- Source information
- Timestamp
- Record counts
- Processing results
- File lineage

This enables full traceability from raw data to final seeds.

## Security Best Practices

1. **Never commit real API keys** - Use environment variables
2. **Enable anonymization** for all sensitive data
3. **Validate schemas** before processing
4. **Review processed data** before using as seeds
5. **Use `.gitignore`** to exclude raw data with PII

## Troubleshooting

### Script Syntax Errors
```bash
node --check scripts/fetch_source.mjs
```

### Validation Failures
Check `data/metadata/validation-errors-*.json` for details

### Missing Dependencies
Ensure Node.js v18+ is installed

### Rate Limiting Issues
Adjust `rateLimit` settings in source configuration

## Future Enhancements

- Database direct import support
- CSV/Excel file support
- Advanced pagination strategies
- Custom transformation functions
- Data quality metrics
- Incremental updates
- Parallel processing
