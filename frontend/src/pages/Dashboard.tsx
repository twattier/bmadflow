import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { getHelloMessage } from '@/api/services/helloService';
import type { HelloResponse } from '@/api/services/helloService';

export function Dashboard() {
  const [helloData, setHelloData] = useState<HelloResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHelloMessage() {
      try {
        const data = await getHelloMessage();
        setHelloData(data);
      } catch (err) {
        console.error('Failed to fetch hello message:', err);
        setError('Failed to connect to backend API');
      } finally {
        setLoading(false);
      }
    }

    fetchHelloMessage();
  }, []);

  if (loading) {
    return <div className="p-6">Loading...</div>;
  }

  if (error) {
    return <div className="p-6 text-destructive">Error: {error}</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">{helloData?.message}</h1>
        <p className="text-muted-foreground mt-2">
          Welcome to BMADFlow - Your Documentation Hub for BMAD Method Projects
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Server timestamp: {helloData?.timestamp}
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Getting Started</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            BMADFlow is a RAG-powered documentation hub that synchronizes GitHub documentation,
            processes it with Docling, indexes it with pgvector, and provides an AI chatbot
            interface for intelligent Q&A.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
