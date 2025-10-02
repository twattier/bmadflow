import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

export default function EpicsView() {
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Epics</CardTitle>
          <CardDescription>Epic and story relationships visualization</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Coming soon...</p>
        </CardContent>
      </Card>
    </div>
  );
}
