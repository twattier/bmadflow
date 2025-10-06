export function Header() {
  return (
    <header className="border-b bg-card px-6 py-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <div className="flex items-center gap-4">
          {/* User menu, notifications can be added here */}
        </div>
      </div>
    </header>
  );
}
