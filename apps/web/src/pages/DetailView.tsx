import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function DetailView() {
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Detail</CardTitle>
          <CardDescription>Document detail view with markdown rendering</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}
