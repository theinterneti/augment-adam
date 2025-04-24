#!/usr/bin/env python3

from context_engine.db.embedding import embedding_model

print(f'Embedding model loaded: {embedding_model.model_name}')
vector = embedding_model.encode('Hello, world!')
print(f'Vector dimension: {len(vector)}')
print(f'First 10 values: {vector[:10]}')
