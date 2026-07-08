---
title: Column Types Reference
type: docs
prev: docs/migrations/schema-builder
sidebar:
  open: true
weight: 32
---

## Type Mapping

The schema builder maps 37 generic column types to database-specific SQL types.

| Generic Type | SQLite | MySQL | PostgreSQL |
|-------------|--------|-------|------------|
| `ColTypeIncrements` | INTEGER | INT UNSIGNED AUTO_INCREMENT | SERIAL |
| `ColTypeBigIncrements` | INTEGER | BIGINT UNSIGNED AUTO_INCREMENT | BIGSERIAL |
| `ColTypeTinyInt` | INTEGER | TINYINT | SMALLINT |
| `ColTypeSmallInt` | INTEGER | SMALLINT | SMALLINT |
| `ColTypeMediumInt` | INTEGER | MEDIUMINT | INTEGER |
| `ColTypeInteger` | INTEGER | INT | INTEGER |
| `ColTypeBigInt` | INTEGER | BIGINT | BIGINT |
| `ColTypeUnsignedInteger` | INTEGER | INT UNSIGNED | INTEGER |
| `ColTypeUnsignedBigInteger` | INTEGER | BIGINT UNSIGNED | BIGINT |
| `ColTypeString` | VARCHAR | VARCHAR | VARCHAR |
| `ColTypeChar` | CHAR | CHAR | CHAR |
| `ColTypeText` | TEXT | TEXT | TEXT |
| `ColTypeMediumText` | TEXT | MEDIUMTEXT | TEXT |
| `ColTypeLongText` | TEXT | LONGTEXT | TEXT |
| `ColTypeBoolean` | INTEGER | TINYINT(1) | BOOLEAN |
| `ColTypeDate` | DATE | DATE | DATE |
| `ColTypeDateTime` | DATETIME | DATETIME | TIMESTAMP |
| `ColTypeDateTimeTz` | DATETIME | DATETIME | TIMESTAMPTZ |
| `ColTypeTime` | TIME | TIME | TIME |
| `ColTypeTimestamp` | DATETIME | TIMESTAMP | TIMESTAMP |
| `ColTypeTimestampTz` | DATETIME | TIMESTAMP | TIMESTAMPTZ |
| `ColTypeDecimal` | numeric | DECIMAL | NUMERIC |
| `ColTypeDouble` | REAL | DOUBLE | DOUBLE PRECISION |
| `ColTypeFloat` | REAL | FLOAT | REAL |
| `ColTypeBinary` | BLOB | BLOB | BYTEA |
| `ColTypeUUID` | TEXT | CHAR(36) | UUID |
| `ColTypeULID` | TEXT | CHAR(26) | CHAR(26) |
| `ColTypeEnum` | TEXT | ENUM('a','b') | VARCHAR + CHECK |
| `ColTypeJson` | TEXT | JSON | JSONB |

## Column Modifier SQL

| Modifier | SQLite | MySQL | PostgreSQL |
|----------|--------|-------|------------|
| `NOT NULL` | NOT NULL | NOT NULL | NOT NULL |
| `DEFAULT val` | DEFAULT val | DEFAULT val | DEFAULT val |
| `UNIQUE` | UNIQUE | UNIQUE | UNIQUE |
| `PRIMARY KEY` | PRIMARY KEY | PRIMARY KEY | PRIMARY KEY |
| `AUTO_INCREMENT` | AUTOINCREMENT | AUTO_INCREMENT | (SERIAL/BIGSERIAL) |
| `UNSIGNED` | — | UNSIGNED | — |

## Best Practices

- Use `BigIncrements("id")` for primary keys in production — it supports up to 9 quintillion rows
- Use `Timestamps()` for created_at/updated_at tracking
- Use `SoftDeletes()` for soft deletion support
- For enums in PostgreSQL, the builder uses VARCHAR with CHECK constraints
- Always wrap string defaults in extra quotes: `Default("'active'")`
