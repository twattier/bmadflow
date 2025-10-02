import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function ScopingView() {
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Scoping</CardTitle>
          <CardDescription>Product requirements and project scoping documents</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}
