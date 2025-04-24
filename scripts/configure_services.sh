#!/bin/bash
# Configure services for Dukat

set -e  # Exit on error

echo "Configuring services..."

# Configure Neo4j
echo "Configuring Neo4j..."
docker exec -it dukat-neo4j cypher-shell -u neo4j -p dukatpassword \
  "CREATE CONSTRAINT unique_file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE"

# Configure ChromaDB
echo "Configuring ChromaDB..."
cat > create_collection.py << 'PYEOF'
import chromadb

client = chromadb.HttpClient(host="dukat-chroma", port=8000)
collection = client.create_collection(
    name="dukat_code",
    metadata={"description": "Dukat code embeddings"}
)
print(f"Created collection: {collection.name}")
PYEOF

docker cp create_collection.py dukat-dev:/tmp/
docker exec -it dukat-dev python /tmp/create_collection.py

echo "Service configuration complete!"
