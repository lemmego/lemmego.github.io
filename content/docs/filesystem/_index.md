---
title: File System
type: docs
prev: docs/security/encryption
next: docs/testing/
sidebar:
  open: true
weight: 46
---

## Overview

The `fsys` package provides a unified file storage abstraction with multiple provider backends. The `api/fs` package integrates this into the framework with multi-disk management.

## Architecture

```
Application Code
      |
      v
+------------------+
|  fs.FileSystem   |  <-- Multi-disk manager (api/fs)
+------------------+
      |
      v
+------------------+
|  fsys.FS         |  <-- Unified interface
+------------------+
      |
      +-- LocalStorage   (local filesystem)
      +-- S3Storage      (Amazon S3)
      +-- GCSStorage     (Google Cloud Storage)
      +-- MemoryStorage  (in-memory, for testing)
```

## FS Interface

All providers implement a common interface:

```go
type FS interface {
    Driver() string
    Read(path string) (io.ReadCloser, error)
    Write(path string, contents []byte) error
    Delete(path string) error
    Exists(path string) (bool, error)
    Rename(oldPath, newPath string) error
    Copy(sourcePath, destinationPath string) error
    CreateDirectory(path string) error
    GetUrl(path string) (string, error)
    Open(path string) (*os.File, error)
    Upload(file multipart.File, header *multipart.FileHeader, dir string) (*os.File, error)
}
```

## Framework Integration

### Provider

The filesystem is registered via the `fs.Provider` in `bootstrap/providers.go`:

```go
func LoadProviders() []app.Provider {
    return []app.Provider{
        &fs.Provider{},
    }
}
```

### Access

```go
filesys := app.Get[*fs.FileSystem](a)

// Get a specific disk
disk, err := filesys.Disk("s3")
disk, err := filesys.Disk() // Returns default disk (from FILESYSTEM_DISK env)
```

## Usage

```go
disk, _ := filesys.Disk("local")

// Write
disk.Write("uploads/report.pdf", data)

// Read
reader, _ := disk.Read("uploads/report.pdf")
defer reader.Close()

// Check existence
exists, _ := disk.Exists("uploads/report.pdf")

// Delete
disk.Delete("uploads/report.pdf")

// Get URL
url, _ := disk.GetUrl("uploads/report.pdf")

// Upload from request
disk.Upload(file, header, "avatars")
```

## Configuration

Configuration is set in `internal/configs/filesystems.go`:

```go
config.Set("filesystems", config.M{
    "default": config.MustEnv("FILESYSTEM_DISK", "local"),
    "disks": config.M{
        "local": config.M{
            "driver": "local",
            "root":   "storage/app",
        },
        "s3": config.M{
            "driver": "s3",
            "key":    config.MustEnv("AWS_ACCESS_KEY_ID", ""),
            "secret": config.MustEnv("AWS_SECRET_ACCESS_KEY", ""),
            "region": config.MustEnv("AWS_DEFAULT_REGION", "us-east-1"),
            "bucket": config.MustEnv("AWS_BUCKET", ""),
        },
        "r2": config.M{
            "driver": "s3",
            "key":    config.MustEnv("R2_ACCESS_KEY_ID", ""),
            "secret": config.MustEnv("R2_SECRET_ACCESS_KEY", ""),
            "region": "auto",
            "bucket": config.MustEnv("R2_BUCKET", ""),
            "endpoint": config.MustEnv("R2_ENDPOINT", ""),
        },
    },
})
```

## Providers

### Local Storage

Stores files on the local filesystem. Configured with a root directory.

```go
storage := fsys.NewLocalStorage("./storage/app")
```

Features: Read, Write, Delete, Exists, Rename, Copy, CreateDirectory, Open, Upload.

### S3 Storage

Stores files on Amazon S3 (or S3-compatible services like Cloudflare R2).

```go
storage := fsys.NewS3Storage(s3Config)
```

URLs are generated as pre-signed URLs with 15-minute expiry by default.

### GCS Storage

Stores files on Google Cloud Storage.

```go
storage := fsys.NewGCSStorage(gcsConfig)
```

URLs use the standard `https://storage.googleapis.com/<bucket>/<path>` format.

### Memory Storage

In-memory storage for testing purposes.

```go
storage := fsys.NewMemoryStorage()
```

All operations work in memory. `GetUrl` returns mock `mem://` URLs. `Open` is not supported.
