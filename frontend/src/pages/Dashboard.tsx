import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Hello BMADFlow</h1>
        <p className="text-muted-foreground mt-2">
          Welcome to BMADFlow - Your Documentation Hub for BMAD Method Projects
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
