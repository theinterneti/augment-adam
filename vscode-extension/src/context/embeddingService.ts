import axios from 'axios';
import { getConfiguration } from '../configuration';

export class EmbeddingService {
  private apiEndpoint: string;
  private apiKey: string;
  
  constructor() {
    const config = getConfiguration();
    this.apiEndpoint = config.apiEndpoint;
    this.apiKey = config.apiKey;
  }
  
  public async generateEmbedding(text: string): Promise<number[]> {
    try {
      const response = await axios.post(
        `${this.apiEndpoint}/embeddings`,
        {
          input: text,
          model: 'qwen3-embedding'
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return response.data.data[0].embedding;
    } catch (error) {
      console.error('Error generating embedding:', error);
      throw new Error('Failed to generate embedding');
    }
  }
  
  public async generateBatchEmbeddings(texts: string[]): Promise<number[][]> {
    try {
      const response = await axios.post(
        `${this.apiEndpoint}/embeddings`,
        {
          input: texts,
          model: 'qwen3-embedding'
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      return response.data.data.map((item: any) => item.embedding);
    } catch (error) {
      console.error('Error generating batch embeddings:', error);
      throw new Error('Failed to generate batch embeddings');
    }
  }
}
