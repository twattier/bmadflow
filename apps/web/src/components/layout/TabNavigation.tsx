import { NavLink } from 'react-router-dom';
import { ClipboardList, Building2, BarChart3, Search } from 'lucide-react';
import { cn } from '../../lib/utils';

const tabs = [
  { to: '/scoping', label: 'Scoping', icon: ClipboardList },
  { to: '/architecture', label: 'Architecture', icon: Building2 },
  { to: '/epics', label: 'Epics', icon: BarChart3 },
  { to: '/detail', label: 'Detail', icon: Search },
];

export default function TabNavigation() {
  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-6">
        <div className="flex gap-8">
          {tabs.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2 px-4 py-3 text-sm transition-colors',
                  'border-b-2 border-transparent',
                  'hover:text-foreground',
                  isActive
                    ? 'border-primary font-bold text-foreground'
                    : 'text-muted-foreground'
                )
              }
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  );
}
