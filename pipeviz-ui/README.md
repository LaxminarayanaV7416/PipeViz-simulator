## Setup with Bun

This project uses [Bun](https://bun.sh/) for package management and running scripts, which provides better performance than npm.

### Installing Bun

If you don't have Bun installed, follow the official [installation guide](https://bun.sh/docs/installation).

### Getting Started with Bun

1. **Install dependencies:**
   ```bash
   bun install

### 3. **Delete `package-lock.json`**
Remove this file from the repository. When you run `bun install`, it will automatically generate `bun.lockb` (Bun's binary lock file).

### 4. **`package.json` stays the same**
Your current `package.json` is already compatible with bun—no changes needed! All your dependencies and scripts will work seamlessly.

## After Migration:

Once you've made these changes, here's what users should do:

```bash
# Install bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies using bun
bun install

# Run development server
bun dev

# Build for production
bun run build
