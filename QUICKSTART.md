# Data Pipeline Quick Start Guide

## Prerequisites

- Node.js v18 or higher
- Git

## Installation

No additional dependencies required - uses Node.js built-in modules only.

## Quick Start

### 1. Run the Complete Pipeline

```bash
# Fetch data from sources
node scripts/fetch_source.mjs

# Process and validate data
node scripts/process_data.mjs

# Generate seed files
node scripts/generate_seeds.mjs
```

### 2. Run Tests

```bash
node scripts/test_pipeline.mjs
```

### 3. Validate Configuration

```bash
# Check syntax of all scripts
node --check scripts/fetch_source.mjs
node --check scripts/process_data.mjs
node --check scripts/generate_seeds.mjs
```

## Configuration

Edit `data/config/source.config.json` to configure your data sources.

### Enable/Disable Sources

Set the `enabled` field to `true` or `false`:

```json
{
  "id": "example-api",
  "enabled": true,
  ...
}
```

### Configure REST API Source

```json
{
  "type": "REST_API",
  "config": {
    "baseUrl": "https://your-api.com/api",
    "endpoints": [
      {
        "name": "records",
        "path": "/records",
        "pagination": {
          "maxPages": 5
        }
      }
    ]
  }
}
```

### Configure Anonymization

```json
{
  "anonymization": {
    "enabled": true,
    "fields": ["email", "phone", "ssn", "address"]
  }
}
```

### Configure Schema Validation

```json
{
  "schemaValidation": {
    "enabled": true,
    "schemaFile": "records_schema.json"
  }
}
```

## Output Locations

- **Raw Data**: `data/raw/` - Original fetched data
- **Processed Data**: `data/processed/` - Validated and anonymized data
- **Seed Data**: `data/seeds/` - Final seed files
- **Metadata**: `data/metadata/` - Execution metadata and lineage

## CI/CD Integration

The pipeline includes GitHub Actions workflow that runs automatically on:

- Push to main/develop branches
- Pull requests
- Daily at 2 AM UTC
- Manual trigger

## Troubleshooting

### Script Won't Run

Check Node.js version:
```bash
node --version  # Should be v18 or higher
```

### Configuration Errors

Validate JSON syntax:
```bash
node -e "require('fs').readFileSync('data/config/source.config.json', 'utf8')"
```

### Permission Errors

Make scripts executable:
```bash
chmod +x scripts/*.mjs
```

## Security Notes

1. **Never commit sensitive data** to git
2. The `data/.gitignore` excludes raw and processed files by default
3. **Always enable anonymization** for production data
4. Review seed files before committing

## Next Steps

1. Configure your actual data sources in `source.config.json`
2. Create appropriate schemas in `data/schema/`
3. Run the pipeline
4. Review and commit seed files

For detailed documentation, see `data/README.md`.
