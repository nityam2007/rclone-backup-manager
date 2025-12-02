# Roadmap

Future plans and feature requests for RClone Backup Manager.

## Planned Features

### Sync with Timestamp Versioning
- **Goal**: Create a mechanism to sync files between a Source (A) and Destination (B).
- **Requirement**: If a file exists in the Destination and is updated in the Source, the old file in the Destination should be renamed instead of overwritten.
- **Naming Convention**: `OldFileName_TimeStamp.XXX` (e.g., `document_20251201_120000.txt`).
- **Implementation**: Likely a new script or a new mode in the existing application.
