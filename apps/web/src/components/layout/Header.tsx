export default function Header() {
  return (
    <header className="border-b bg-background">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-6">
            {/* BMADFlow Logo */}
            <h1 className="text-2xl font-bold text-primary">BMADFlow</h1>

            {/* Project Name (hardcoded for POC) */}
            <div className="text-sm text-muted-foreground">
              Project: <span className="font-medium text-foreground">Demo Project</span>
            </div>
          </div>

          {/* Sync Status Indicator */}
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500"></div>
            <span className="text-sm text-muted-foreground">Synced</span>
          </div>
        </div>
      </div>
    </header>
  );
}
