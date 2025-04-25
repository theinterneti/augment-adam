#!/bin/bash
# Script to migrate from the old Dukat structure to the new Augment Adam structure
# This script should be run from the root of the repository

set -e  # Exit on error

echo "Creating new directory structure..."
mkdir -p augment_adam/{ai_agent,cli,context_engine,core,memory,models,plugins,server,utils,web}
mkdir -p augment_adam/ai_agent/{coordination,memory_integration,reasoning,smc,tools,types}
mkdir -p augment_adam/context_engine/{chunking,composition,prompt,retrieval}
mkdir -p docs/{api,development,research,user_guide}
mkdir -p docs/research/ai-digest
mkdir -p tests/{unit,integration,e2e,performance,stress}
mkdir -p docker config/{neo4j,redis} examples scripts/{monitoring,setup,test_utils}

echo "Backing up original files..."
# Create backup directory
mkdir -p backup
# Backup key files
cp -r pyproject.toml README.md backup/

echo "Moving configuration files..."
# Move Docker files
mkdir -p docker
mv Dockerfile.* docker/
mv *docker-compose*.yml docker/

# Move configuration files
mkdir -p config/neo4j config/redis
mv neo4j-config/* config/neo4j/ 2>/dev/null || true
mv redis-config/* config/redis/ 2>/dev/null || true
mv config/* config/ 2>/dev/null || true

echo "Moving documentation..."
# Move and merge documentation
cp -r docs/* docs/ 2>/dev/null || true
cp -r augment-adam/docs/* docs/ 2>/dev/null || true

echo "Moving examples..."
# Consolidate examples
cp -r examples/* examples/ 2>/dev/null || true
cp -r augment-adam/examples/* examples/ 2>/dev/null || true

echo "Moving scripts..."
# Consolidate scripts
cp -r scripts/* scripts/ 2>/dev/null || true
mv setup_*.sh scripts/setup/ 2>/dev/null || true

echo "Moving tests..."
# Consolidate tests
cp -r tests/* tests/ 2>/dev/null || true
cp -r augment-adam/tests/* tests/ 2>/dev/null || true

echo "Moving main package code..."
# Move augment-adam code
cp -r augment-adam/augment_adam/* augment_adam/ 2>/dev/null || true

# Move dukat code (with manual intervention needed)
echo "NOTE: Dukat code needs to be manually migrated to augment_adam/"
echo "Please review the code in the dukat/ directory and merge it into augment_adam/"

echo "Updating configuration..."
# Replace pyproject.toml
mv pyproject.toml.new pyproject.toml
# Replace README.md
mv README.md.new README.md

echo "Migration structure created!"
echo "Next steps:"
echo "1. Manually merge dukat code into augment_adam"
echo "2. Update imports from 'dukat' to 'augment_adam'"
echo "3. Run tests to verify the migration"
echo "4. Update documentation references"
echo "5. Commit the changes"

echo "See MIGRATION_PLAN.md and DIRECTORY_STRUCTURE.md for more details."
