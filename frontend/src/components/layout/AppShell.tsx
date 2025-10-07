import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Breadcrumbs } from './Breadcrumbs';

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <div className="px-6 pt-4 pb-2">
          <Breadcrumbs />
        </div>
        <main className="flex-1 overflow-auto px-6 pb-6">{children}</main>
      </div>
    </div>
  );
}
