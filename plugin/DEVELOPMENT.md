# Plugin Development Notes

## Quick Summary

**You don't need Node.js to use this plugin!**

The plugin is pre-compiled as `main.js` and ready to use.

## File Overview

### Required Files (for users)
- `main.js` - Pre-compiled plugin code ✓
- `manifest.json` - Plugin metadata ✓
- `styles.css` - UI styles ✓

### Optional Files (for developers only)
- `src/*.ts` - TypeScript source code (if you want to rebuild)
- `package.json` - Node.js dependencies (for building)
- `tsconfig.json` - TypeScript config (for building)
- `esbuild.config.mjs` - Build script (for building)
- `version-bump.mjs` - Version management (for releases)
- `versions.json` - Version history (for releases)

## Modifying the Plugin

### Option 1: Direct Edit (No Build Needed)

1. Edit `main.js` directly
2. Copy to your vault
3. Reload Obsidian (Ctrl+R)

This is the simplest approach for small changes.

### Option 2: TypeScript Development (Build Required)

If you want to work with the TypeScript source:

1. **Install Node.js**
   ```bash
   # Download from https://nodejs.org
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Edit TypeScript files**
   ```bash
   # Edit files in src/
   ```

4. **Build**
   ```bash
   npm run build
   # Creates main.js
   ```

5. **Development mode (auto-rebuild)**
   ```bash
   npm run dev
   # Watches for changes
   ```

## Why Pre-compile?

For end users:
- ✓ No Node.js installation required
- ✓ Faster installation (no build step)
- ✓ Simpler for non-developers
- ✓ Works out of the box

For developers:
- ✓ Can still edit TypeScript if desired
- ✓ Or just edit JavaScript directly
- ✓ Flexibility for both approaches

## Deployment

When making changes:

1. **For yourself**: Just copy `main.js` to your vault
2. **For others**: Commit updated `main.js` to repository
3. **For releases**: Update version in `manifest.json` and rebuild

## TypeScript Source Structure

```
src/
├── main.ts          # Plugin entry point
├── settings.ts      # Settings UI
└── backendClient.ts # Backend API client
```

Compiles to: `main.js` (single file)

## Questions?

- **Do I need to rebuild?** Only if you modify TypeScript files
- **Can I skip Node.js?** Yes! Just use the pre-built `main.js`
- **How do I update?** Copy new `main.js` to your vault
