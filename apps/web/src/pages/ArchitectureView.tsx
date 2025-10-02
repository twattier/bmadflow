import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function ArchitectureView() {
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Architecture</CardTitle>
          <CardDescription>Technical architecture and design documents</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}
