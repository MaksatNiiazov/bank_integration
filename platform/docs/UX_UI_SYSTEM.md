# Turkuaz UX/UI System

This document defines the product experience for Turkuaz Platform and all connected department services.

The goal is one company product, not a collection of unrelated websites.

## Product Model

Turkuaz Platform has three interface layers:

```text
Platform layer
  login, service navigation, branch context, dashboard, module health

Admin layer
  users, roles, permissions, branches, departments, service access, audit

Module layer
  Converter, Payments, Reports, Warehouse, and future department tools
```

Each business module may be an independent frontend and backend, but it must use the same shell, session model, navigation vocabulary, and visual system.

## Naming

Use functional names, not overly broad names:

```text
Converter   not CRM
Payments    not Finance App
Identity    not Users DB
Platform    not Admin Panel
```

The visible product name is:

```text
Turkuaz Platform
```

## Navigation

Every frontend should share the same basic shell:

```text
Left sidebar
  Turkuaz Platform brand
  Overview / module home
  Module-specific pages
  Admin links when permitted

Top bar
  branch selector
  service switcher
  current user
  logout
```

Users should be able to move between services without learning a new layout.

## Roles And Access UX

Access management must always answer four questions:

```text
Who is the user?
Which department do they belong to?
Which branches can they access?
What can they do in each service?
```

Permissions use this pattern:

```text
service.resource.action
```

Examples:

```text
identity.users.manage
converter.orders.read
converter.products.write
payments.transactions.read
payments.qr.create
reports.sales.read
```

Branch-scoped permissions must be visible in the UI. A role assigned only to `bishkek` should not look like a global role.

## Failure States

The platform must degrade gracefully:

```text
One module unavailable -> show that module as unavailable
Platform API unavailable -> show a local fallback state
Identity unavailable -> existing JWT sessions continue until expiry
Permission missing -> show a clear no-access state
```

Never show a blank page for an unavailable module.

## Visual Direction

The UI is operational, calm, and precise.

Use:

```text
white / near-white backgrounds
charcoal text
restrained teal accent
amber warnings
red destructive/error states
subtle borders
8px radius
compact tables
clear selected states
```

Avoid:

```text
marketing hero sections
decorative gradient blobs
purple/blue gradient themes
nested cards
oversized headings inside admin panels
copy that explains obvious UI behavior
```

## Core Components

These should eventually live in `packages/platform-ui`:

```text
PlatformShell
ServiceSwitcher
BranchSelector
UserMenu
PageHeader
Button
IconButton
StatusBadge
PermissionBadge
DataTable
EmptyState
ErrorState
FormPanel
Tabs
Modal
```

## Page Patterns

### Management Page

Used for users, roles, branches, products, clients.

```text
Header
KPI strip
Main table
Right-side create/edit panel
Inline empty/error state
```

### Operational Page

Used for converter, payments, warehouse tasks.

```text
Header
Primary action row
Filters
Table or work queue
Detail panel
Status / history side rail
```

### Executive Page

Used for leadership overview.

```text
Service health
Department summaries
KPI bands
Recent activity
Drill-down links
```

## Responsive Rules

Desktop is optimized for repeated operations. Mobile must remain readable for checks and light admin work.

```text
No horizontal overflow
Tables become stacked rows or scroll inside their own region
Topbar controls wrap before text clips
Buttons keep stable height
Long permission codes wrap or truncate intentionally
```

## Implementation Rule

Do not copy shell components between apps manually.

Short term:

```text
Keep styles consistent across apps.
```

Target:

```text
packages/platform-ui
packages/platform-auth
packages/platform-types
```

All services should consume shared UI and auth packages instead of maintaining their own copies.
