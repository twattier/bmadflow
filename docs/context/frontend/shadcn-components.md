# shadcn/ui Component Patterns

This document provides essential shadcn/ui component patterns for BMADFlow frontend development.

## Table Component

The Table component is essential for displaying document lists, project metadata, and sync status.

### Installation

```bash
npx shadcn@latest add table
```

### Basic Usage

```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface Document {
  id: number
  name: string
  path: string
  lastModified: string
  size: number
}

export function DocumentTable({ documents }: { documents: Document[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Path</TableHead>
          <TableHead>Last Modified</TableHead>
          <TableHead className="text-right">Size</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell className="font-medium">{doc.name}</TableCell>
            <TableCell className="text-muted-foreground">{doc.path}</TableCell>
            <TableCell>{doc.lastModified}</TableCell>
            <TableCell className="text-right">{doc.size} KB</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

### Interactive Table with Actions

```tsx
import { Button } from "@/components/ui/button"
import { Eye, Download, Trash2 } from "lucide-react"

export function DocumentTableWithActions({ documents }: { documents: Document[] }) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Name</TableHead>
          <TableHead>Path</TableHead>
          <TableHead>Last Modified</TableHead>
          <TableHead className="text-right">Actions</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell className="font-medium">{doc.name}</TableCell>
            <TableCell className="text-muted-foreground">{doc.path}</TableCell>
            <TableCell>{doc.lastModified}</TableCell>
            <TableCell className="text-right">
              <div className="flex justify-end gap-2">
                <Button variant="ghost" size="icon">
                  <Eye className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Download className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
```

## Dashboard Layout Pattern

shadcn/ui provides a comprehensive Dashboard template with sidebar navigation and header.

```tsx
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        <div className="flex flex-1 flex-col">
          <header className="border-b">
            <div className="flex h-16 items-center gap-4 px-6">
              <SidebarTrigger />
              <h1 className="text-xl font-semibold">BMADFlow</h1>
            </div>
          </header>
          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  )
}
```

## Card Component for Project Display

Cards are ideal for displaying project summaries and metadata.

```tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GitBranch, Calendar } from "lucide-react"

interface Project {
  id: number
  name: string
  repoUrl: string
  lastSynced: string
  documentCount: number
  syncStatus: "synced" | "syncing" | "error"
}

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>{project.name}</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-2">
              <GitBranch className="h-4 w-4" />
              {project.repoUrl}
            </CardDescription>
          </div>
          <Badge variant={project.syncStatus === "synced" ? "default" : "secondary"}>
            {project.syncStatus}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            Last synced: {project.lastSynced}
          </div>
          <div className="text-sm">
            {project.documentCount} documents
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <Button size="sm">View Documents</Button>
          <Button size="sm" variant="outline">Sync Now</Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

## Form Components for Project Creation

shadcn/ui form components integrate with react-hook-form for validation.

```tsx
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

const projectSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  repoUrl: z.string().url("Must be a valid URL"),
  description: z.string().optional(),
})

export function ProjectForm() {
  const form = useForm<z.infer<typeof projectSchema>>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: "",
      repoUrl: "",
      description: "",
    },
  })

  function onSubmit(values: z.infer<typeof projectSchema>) {
    console.log(values)
    // Call API to create project
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Project Name</FormLabel>
              <FormControl>
                <Input placeholder="my-awesome-project" {...field} />
              </FormControl>
              <FormDescription>
                A unique name for your project
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="repoUrl"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Repository URL</FormLabel>
              <FormControl>
                <Input placeholder="https://github.com/user/repo" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea placeholder="Project description..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Create Project</Button>
      </form>
    </Form>
  )
}
```

## Dialog for Confirmation Actions

Dialogs are essential for delete confirmations and settings.

```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

export function DeleteProjectDialog({ projectName }: { projectName: string }) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="destructive">Delete Project</Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This will permanently delete the project "{projectName}" and all associated documents.
            This action cannot be undone.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={() => console.log("Deleting...")}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
```

## Accessibility Features

All shadcn/ui components are WCAG 2.1 AA compliant with proper ARIA attributes.

```tsx
// Example: Accessible button with keyboard navigation
<Button
  aria-label="Sync project documents"
  onClick={handleSync}
>
  <RefreshCw className="h-4 w-4 mr-2" />
  Sync Now
</Button>

// Example: Accessible table with screen reader support
<Table>
  <TableCaption>A list of all project documents</TableCaption>
  <TableHeader>
    <TableRow>
      <TableHead scope="col">Document Name</TableHead>
    </TableRow>
  </TableHeader>
</Table>
```

## Related Documentation

- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Architecture UX Design](/docs/ux-specification.md)
- [Frontend Architecture](/docs/architecture.md#frontend-architecture)
