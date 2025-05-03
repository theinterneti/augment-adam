export interface CodeChunk {
  id: string;
  filePath: string;
  content: string;
  startLine: number;
  endLine: number;
  symbols: string[];
  imports: string[];
  language: string;
  embedding?: number[];
}
