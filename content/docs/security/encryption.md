---
title: Encryption
type: docs
prev: docs/security/csrf
sidebar:
  open: true
weight: 45
---

## Overview

The `encryption` package provides AES-256-GCM authenticated encryption for secure data storage. It uses a singleton pattern initialized from the `APP_KEY` environment variable.

## Configuration

The app key is generated during project creation and stored in `.env`:

```shell
APP_KEY=base64:abc123... (32 bytes base64-encoded)
```

You can regenerate the app key:

```shell
lemmego appkey
```

This replaces the `APP_KEY` value in your `.env` file with a new 32-byte random key.

## Basic Usage

```go
import "github.com/lemmego/api/encryption"
```

### Encrypt

```go
ciphertext, err := encryption.Encrypt([]byte("sensitive data"))
// Returns base64-encoded ciphertext
```

### Decrypt

```go
plaintext, err := encryption.Decrypt(ciphertext)
// Returns []byte
```

### Encrypt/Decrypt Strings

```go
encrypted, err := encryption.Get().EncryptString("sensitive data")
decrypted, err := encryption.Get().DecryptString(encrypted)
```

## Manual Initialization

```go
key := []byte("32-bytes-exactly-for-aes-256-key!")
enc, err := encryption.NewEncrypter(key)

ciphertext, err := enc.Encrypt([]byte("data"))
plaintext, err := enc.Decrypt(ciphertext)
```

## How It Works

1. **AES-256-GCM** — Authenticated encryption with associated data (AEAD)
2. **Random Nonce** — A 12-byte random nonce is generated for each encryption operation
3. **Nonce Prepend** — The nonce is prepended to the ciphertext
4. **Base64 Encoding** — The combined nonce+ciphertext is base64-encoded for transport

```
Encrypt(plaintext):
  nonce = random(12 bytes)
  ciphertext = AES-256-GCM.Seal(nonce, plaintext)
  return base64(nonce + ciphertext)

Decrypt(ciphertext):
  raw = base64_decode(ciphertext)
  nonce = raw[:12]
  ciphertext = raw[12:]
  return AES-256-GCM.Open(nonce, ciphertext)
```

## Key Requirements

- The key must be exactly **32 bytes** for AES-256
- The `APP_KEY` in `.env` is base64-encoded before use
- Never commit the real `APP_KEY` to version control

## Use Cases

- Encrypting sensitive user data (PII, payment info)
- Encrypting API tokens stored in the database
- Secure cookie values
- Encrypting data at rest
