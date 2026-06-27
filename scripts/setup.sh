#!/bin/sh
# Run this once after cloning: sh scripts/setup.sh

# Install git hooks
git config core.hooksPath .githooks
echo "Git hooks installed."

# Create .env from example
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created from .env.example — fill in your credentials."
fi

echo "Setup complete."
