# UI_UX.md

**Version:** 1.0.0

**Project:** Forge – AI-Native Project Operating System

**Status:** Draft

**Last Updated:** 2026-07-18

**Owner:** Rahul

**Document Type:** UI/UX Design System

**Audience:** UI/UX Designers, Frontend Developers, Product Engineers

**Dependencies:**
- PRODUCT.md

**Related Documents:**
- TECHNICAL_ARCHITECTURE.md
- AI_SYSTEM.md
- PROJECT_RULES.md

---

## Document History

| Version | Date | Author | Changes |
|----------|------|---------|----------|
| 1.0.0 | 2026-07-18 | Rahul | Initial Design System |

---

# Table of Contents

1. Design Philosophy
2. Core Design Principles
3. Brand Identity
4. Theme System
5. Color System
6. Typography
7. Spacing System
8. Grid System
9. Border Radius
10. Elevation
11. Iconography
12. Illustration Style
13. Design Tokens

---

# 1. Design Philosophy

## Purpose

Forge is not another dashboard.

Forge is an AI-native engineering workspace where developers spend hours writing, understanding, and reviewing code. The interface must remain calm, focused, and distraction-free while exposing powerful capabilities only when they are needed.

The design should reduce cognitive load rather than increase it.

Every screen should help developers maintain flow.

---

## Experience Goals

Forge should feel:

- Fast
- Intelligent
- Minimal
- Professional
- Predictable
- Calm
- Modern
- Premium

Developers should immediately trust the interface.

---

## Design Inspirations

Forge draws inspiration from products that prioritize clarity and productivity.

Primary inspirations:

- Linear
- Vercel
- Cursor
- Arc Browser
- GitHub
- Figma
- Raycast

These products demonstrate excellent hierarchy, spacing, typography, and motion without unnecessary visual complexity.

---

## Design Principles

The interface should communicate confidence through restraint.

Instead of filling every corner with information, Forge prioritizes whitespace, clear hierarchy, and meaningful interactions.

AI should enhance workflows instead of interrupting them.

---

# 2. Core Design Principles

## 2.1 AI First

Artificial Intelligence is a fundamental part of Forge.

AI should always be discoverable.

The AI assistant should never be hidden behind multiple menus.

Users should feel that AI is collaborating with them rather than acting as a separate tool.

---

## 2.2 Human Control

AI may:

- Explain
- Suggest
- Generate
- Refactor
- Review

AI must never:

- Push commits automatically
- Delete repositories
- Merge pull requests
- Modify code without user approval

Every important action requires explicit confirmation.

---

## 2.3 Minimal by Default

Only display information relevant to the user's current task.

Avoid:

- Information overload
- Visual noise
- Duplicate controls
- Unnecessary decorations

---

## 2.4 Progressive Disclosure

Advanced functionality should appear only when appropriate.

Examples:

- Git actions appear only after changes exist.
- Architecture tools appear after repository indexing.
- AI recommendations appear only when context is available.

---

## 2.5 Consistency

Every page should follow the same interaction patterns.

Buttons should behave consistently.

Panels should open consistently.

Animations should use consistent timing.

Typography should never change unexpectedly.

---

## 2.6 Motion With Purpose

Motion communicates:

- Progress
- Focus
- Navigation
- Feedback

Motion should never exist purely for decoration.

---

## 2.7 Accessibility

Accessibility is a first-class requirement.

All users should be able to navigate Forge using:

- Keyboard
- Screen readers
- High-contrast themes
- Reduced motion settings

---

# 3. Brand Identity

## Brand Personality

Forge is:

- Intelligent
- Helpful
- Precise
- Reliable
- Professional

Forge is not:

- Playful
- Noisy
- Cartoonish
- Overly futuristic
- Overly corporate

---

## Visual Style

The interface should resemble a premium desktop application.

Characteristics:

- Clean layouts
- Soft shadows
- Sharp typography
- Generous spacing
- Subtle motion
- High readability

Visual complexity should come from information—not decoration.

---

## Shape Language

Use rounded corners consistently.

Avoid excessive rounding.

Preferred geometry:

- Simple rectangles
- Rounded cards
- Clean dividers
- Consistent spacing

---

## Density

Forge supports medium-density layouts.

Information should feel compact enough for developers while remaining comfortable for long sessions.

---

# 4. Theme System

Forge supports complete theme customization.

Users can switch themes instantly without reloading the application.

---

## Supported Themes

### Light

Optimized for bright environments.

Characteristics:

- White surfaces
- Dark typography
- Soft borders
- Very subtle shadows

---

### Dark

Optimized for extended coding sessions.

Characteristics:

- Neutral backgrounds
- High readability
- Reduced eye strain
- Minimal shadow usage

---

## Accent Themes

Users may personalize Forge using accent colors.

Supported accents:

- Nebula (Purple)
- Ocean (Blue)
- Emerald (Green)
- Amber (Gold)
- Crimson (Red)
- Sunset (Orange)

Accent colors influence:

- Buttons
- Focus rings
- Links
- Progress indicators
- Selected navigation items
- Charts
- Highlights

Accent colors should never affect readability.

---

## Theme Persistence

Selected themes should persist across:

- Browser refreshes
- Sessions
- Devices (future)

---

# 5. Color System

The color palette is built around semantic usage rather than arbitrary colors.

Developers should use semantic tokens instead of hardcoded values.

---

## Light Theme

### Background

#FAFAFA

### Surface

#FFFFFF

### Elevated Surface

#FFFFFF

### Primary Text

#111827

### Secondary Text

#6B7280

### Muted Text

#9CA3AF

### Border

#E5E7EB

### Divider

#F3F4F6

### Success

#10B981

### Warning

#F59E0B

### Error

#EF4444

### Info

#3B82F6

---

## Dark Theme

### Background

#0F172A

### Surface

#111827

### Elevated Surface

#1E293B

### Primary Text

#F8FAFC

### Secondary Text

#CBD5E1

### Muted Text

#94A3B8

### Border

#1F2937

### Divider

#334155

### Success

#10B981

### Warning

#FBBF24

### Error

#F87171

### Info

#60A5FA

---

## Semantic Usage Rules

Success colors:

- Completed tasks
- Successful deployments
- AI confirmation
- Repository indexed

Warning colors:

- Merge conflicts
- Unsaved changes
- API rate limits

Error colors:

- Failed commits
- Network failures
- Authentication issues

Info colors:

- Repository analysis
- AI suggestions
- Documentation

---

## Color Usage Guidelines

Do:

- Use semantic colors.
- Maintain contrast ratios.
- Prefer borders over heavy shadows.

Don't:

- Use bright neon colors.
- Place saturated colors behind large text.
- Use color as the only communication method.

---

# 6. Typography

Typography is one of Forge's strongest visual elements.

Readable typography is more valuable than decorative typography.

---

## Font Stack

Primary Font

Geist

Fallback

Inter

Code Font

JetBrains Mono

Fallback

Fira Code

---

## Font Weights

Regular

400

Medium

500

Semibold

600

Bold

700

---

## Type Scale

Display

56px

H1

48px

H2

36px

H3

30px

H4

24px

H5

20px

H6

18px

Body Large

18px

Body

16px

Small

14px

Caption

12px

Code

14px

---

## Line Heights

Headings

120%

Body

160%

Code

150%

---

## Typography Rules

Use sentence case.

Avoid ALL CAPS.

Use bold sparingly.

Keep line lengths between 60–80 characters for readable content.

---

# 7. Spacing System

Forge follows an 8-point spacing system.

All spacing values must derive from this scale.

---

## Base Unit

8px

---

## Scale

4

8

12

16

24

32

40

48

64

80

96

128

---

## Spacing Principles

Whitespace improves readability.

Never compress layouts simply to fit more information.

Consistency is more important than density.

---

# 8. Grid System

Forge uses a responsive 12-column grid.

### Maximum Content Width

1440px

### Comfortable Reading Width

760px

### Standard Page Width

1280px

### Sidebar Width

280px

### AI Panel Width

360px

### Gutter

24px

---

# 9. Border Radius

Small

8px

Medium

12px

Large

16px

Dialog

20px

Floating Panels

24px

Consistency is more important than variation.

---

# 10. Elevation

Forge minimizes heavy shadows.

Hierarchy should primarily be communicated through spacing and borders.

Elevation Levels:

Level 0

Flat

Level 1

Cards

Level 2

Dropdowns

Level 3

Modals

Level 4

Command Palette

Dark mode should rely more on contrast than shadows.

---

# 11. Iconography

Forge uses Lucide Icons as the default icon library.

Guidelines:

- Outline style only
- Consistent stroke width
- Default size: 20px
- Large icons: 24px
- Small icons: 16px

Icons should always accompany text unless universally understood.

---

# 12. Illustration Style

Illustrations should be minimal and functional.

Use illustrations only for:

- Empty states
- Onboarding
- Success pages
- Error explanations

Avoid decorative artwork throughout the workspace.

---

# 13. Design Tokens

Every visual property should map to reusable design tokens.

Token Categories:

- Colors
- Typography
- Radius
- Shadows
- Spacing
- Motion
- Borders
- Icons

No component should use hardcoded values when a design token exists.

---

---

# 14. Layout System

Forge uses a desktop-first layout optimized for developers who spend long periods interacting with repositories.

The interface should remain stable while navigating.

Major layout shifts should be avoided.

---

## Workspace Layout

The default workspace consists of three persistent regions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Top Navigation Bar                                                         │
├──────────────┬──────────────────────────────────────┬──────────────────────┤
│              │                                      │                      │
│              │                                      │                      │
│   Sidebar    │         Main Workspace               │      AI Panel        │
│              │                                      │                      │
│              │                                      │                      │
├──────────────┴──────────────────────────────────────┴──────────────────────┤
│ Status Bar                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Layout Regions

### Left Sidebar

Purpose:

Primary navigation.

Contains:

- Logo
- Project Switcher
- Navigation
- Team
- Settings

Width:

280px

Collapsed Width:

72px

Resizable:

No

Sticky:

Yes

---

### Main Workspace

Purpose:

Primary working area.

Contains:

- Dashboard
- Repository
- Editor
- Git Diff
- Architecture
- Settings

Maximum Width:

Fluid

Minimum Width:

800px

---

### AI Panel

Purpose:

Repository-aware AI assistant.

Width:

360px

Resizable:

Yes

Minimum:

320px

Maximum:

480px

Users may hide the AI panel.

The panel should remember its previous width.

---

### Status Bar

Purpose:

Display workspace information.

Contains:

- Git Branch
- Repository Status
- Sync State
- AI Status
- Notifications
- Connection State

Height:

36px

Always visible.

---

# 15. Navigation System

Forge prioritizes predictable navigation.

Users should always know:

- Where they are
- What project is active
- What actions are available

---

## Primary Navigation

Items:

Dashboard

Projects

Repository

Architecture (Future)

Tasks (Future)

Discussion (Future)

Timeline (Future)

Settings

Only one item may be active.

---

## Secondary Navigation

Appears within pages.

Examples:

Repository

- Files
- Branches
- Pull Requests (Future)

Settings

- General
- Members
- Appearance
- AI

---

## Breadcrumbs

Display:

Project

↓

Module

↓

Current Page

Example:

Forge

>

Interview AI

>

Repository

>

backend/parser

---

## Search

Accessible from:

Top Navigation

Shortcut:

Ctrl + K

Capabilities:

- Search files
- Search documentation
- Search conversations
- Search commands
- Search projects

---

# 16. Top Navigation

Height:

64px

Contains:

Left

- Logo
- Current Project

Center

- Global Search

Right

- Notifications
- Theme Toggle
- AI Status
- User Avatar

The top navigation remains fixed while scrolling.

---

# 17. Sidebar

The sidebar is the primary navigation component.

---

## Sections

Project Switcher

Navigation

Favorites

Recent Projects

Settings

---

## Collapse Behavior

Expanded

280px

Collapsed

72px

Animation

250ms

When collapsed:

Icons remain visible.

Labels disappear.

Hover reveals tooltips.

---

## Project Switcher

Displays:

- Current Project
- Repository
- Team Avatar

Allows:

- Switch project
- Create project
- Import repository

---

# 18. Dashboard

Purpose:

Provide a high-level overview of projects.

The dashboard should answer:

"What should I work on today?"

---

## Dashboard Sections

### Welcome Header

Displays:

Greeting

Current Project

Quick Actions

---

### Quick Actions

Cards:

Import Repository

Create Project

Open Recent

Ask AI

---

### Recent Projects

Displays:

Project Name

Repository

Last Updated

Members (Future)

Health Score (Future)

---

### AI Suggestions

Examples:

"Review pending pull request" (Future)

"Architecture has changed" (Future)

"Dependency update available"

"Repository indexing completed"

---

### Activity Feed

Displays:

Recent Commits

AI Conversations

Repository Imports

Team Activity

Team Activity is future and must not appear in the MVP dashboard.

---

### Project Health (Future)

Metrics:

Open Tasks

Repository Size

AI Coverage

Recent Activity

Documentation Score

---

# 19. Project Workspace

The workspace is where users spend most of their time.

It should minimize navigation and maximize productivity.

---

## Workspace Sections

Repository Explorer

Editor

AI Panel

Status Bar

---

## Layout Rules

Opening files never closes AI.

AI never blocks editing.

Repository explorer may collapse.

Editor receives remaining width.

---

# 20. Repository Explorer

Purpose:

Navigate repository structure.

---

## Displays

Folders

Files

Git Status

Search

Pinned Files

Favorites

---

## Features

Expand folders

Collapse folders

Context menu

Rename

Delete

Create file

Create folder

Drag & Drop

Search

---

## Search

Supports:

File names

Extensions

Paths

Recently opened

---

# 21. Code Editor

Primary editor:

Monaco Editor

---

## Features

Syntax Highlighting

Multiple Tabs

Split View

Auto Save

Undo

Redo

Search

Replace

Format

Go To Definition

Minimap

Line Numbers

Word Wrap

Bracket Pairing

Git Decorations

---

## AI Integration

Inline explanations

Generate code

Refactor

Fix bugs

Improve performance

Explain selection

Generate comments

Every AI action opens a preview before applying changes.

---

# 22. AI Panel

The AI panel is Forge's defining feature.

It remains available throughout the application.

---

## Layout

Header

Conversation

Suggested Actions

Pinned Memory

Prompt Box

---

## Header

Displays:

Current AI Model

Repository Status

Memory Status

Clear Conversation

---

## Conversation

Supports:

Markdown

Code Blocks

Tables

Diffs

Images (future)

Architecture References

Clickable Files

---

## Suggested Actions

Examples:

Explain Repository

Review Current File

Find Bug

Generate Tests

Refactor

Summarize Changes

---

## Prompt Box

Supports:

Multi-line input

Slash Commands

File Mentions

Code Mentions

Repository Mentions

---

## Slash Commands

/help

/explain

/refactor

/test

/review

/bug

/docs

/commit

---

## AI Memory

Shows:

Recent Decisions

Architecture Notes

Important Files

Pinned Context

Users may pin AI responses.

---

# 23. Git Diff View

Purpose:

Review generated changes.

---

Displays:

Added Lines

Removed Lines

Modified Files

Changed Functions

AI Summary

---

Actions

Accept

Reject

Edit

Copy

Commit

---

AI should explain every generated change before commit.

---

# 24. Architecture View (Future)

Architecture visualization is a future capability and has no MVP API contract.

Displays project architecture visually.

Visualization:

Interactive graph.

Nodes:

Folders

Services

APIs

Databases

Dependencies

Edges:

Imports

API Calls

Database Relations

---

Capabilities:

Zoom

Pan

Search

Focus

Expand

Collapse

Highlight Dependencies

---

# 25. Team Collaboration (Future)

Team collaboration is a future capability and has no MVP API contract.

Displays:

Members

Roles

Online Status

Invitations

---

Roles

Owner

Admin

Member

Viewer (Future)

---

Actions

Invite

Remove

Transfer Ownership

Change Role

---

# 26. Notifications

Notification Types

Repository Imported

Commit Successful

AI Finished

Member Joined

Repository Indexed

Error

---

Notifications disappear automatically after five seconds unless they require user action.

---

# 27. Responsive Behavior

## Desktop

Full experience.

Three-column layout.

---

## Laptop

Sidebar collapses automatically if needed.

AI panel remains visible.

---

## Tablet

Sidebar becomes drawer.

AI panel becomes overlay.

Editor remains primary.

---

## Mobile

Purpose:

Project monitoring only.

Supports:

Dashboard

AI Chat

Tasks

Notifications

Settings

Repository overview

The Monaco editor is not available on mobile.

---

# 28. Screen Specifications

Every screen in Forge should define:

Purpose

Primary User Goal

Required Components

Primary Actions

Secondary Actions

Keyboard Shortcuts

Loading State

Empty State

Error State

Responsive Behavior

Accessibility Notes

Success Feedback

This standard must be followed for every future screen added to Forge.

---

## End of Part 2

---

# 29. Component Library

The Forge Component Library provides reusable UI components that maintain
consistency across the application.

Every component should:

- Be reusable.
- Be fully keyboard accessible.
- Support both Light and Dark themes.
- Use design tokens instead of hardcoded values.
- Be responsive by default.
- Include loading and disabled states.
- Support accessibility attributes.

---

# 30. Buttons

Buttons represent the primary method of user interaction.

Every button should clearly communicate its importance through visual hierarchy.

---

## Usage Principles

Use buttons to:

- Trigger actions
- Submit forms
- Navigate workflows
- Confirm operations

Avoid using buttons for simple navigation where links are more appropriate.

---

## Variants

### Primary Button

Purpose

Primary action on a page.

Examples

- Create Project
- Import Repository
- Commit Changes
- Push Branch

Appearance

- Filled background
- Accent color
- White text
- Medium shadow
- Medium radius

---

### Secondary Button

Purpose

Alternative actions.

Examples

- Cancel
- Back
- View Details

Appearance

- Transparent background
- Border
- Surface hover

---

### Ghost Button

Purpose

Low-priority actions.

Examples

- Copy
- Open
- Rename

Appearance

- No border
- Transparent
- Hover background only

---

### Danger Button

Purpose

Destructive actions.

Examples

- Delete Project
- Remove Member
- Discard Changes

Appearance

- Error color
- Confirmation required

---

## Sizes

Small

32px height

Medium

40px height

Large

48px height

Icon Button

40 × 40

---

## States

Default

Hover

Active

Focused

Disabled

Loading

Success

---

## Loading State

Replace label with:

Spinner

↓

"Importing..."

Button width must remain constant.

---

## Keyboard

Enter

Activates

Space

Activates

Tab

Moves focus

---

## Accessibility

Icon buttons require:

aria-label

Disabled buttons:

- Removed from tab order
- Cannot receive focus

Focus ring:

2px Accent

---

## Motion

Hover

120ms

Press

100ms

Focus

Instant

---

## Design Tokens

Uses

- Accent
- Radius-md
- Spacing-4
- Motion-hover
- Elevation-1

---

# 31. Cards

Cards group related information.

Cards should always represent a single object.

Never overload cards with unrelated information.

---

## Card Variants

### Project Card

Displays

- Project Name
- Repository
- Members (Future)
- Last Updated
- Health Score (Future)

Actions

Open

Rename

Delete

---

### Repository Card

Displays

Repository information.

Status.

Branch.

Indexing.

---

### Task Card

Displays

Task title

Status

Priority

Assignee

Due date

---

### AI Response Card

Displays

AI output.

Supports:

Markdown

Code

Tables

Lists

Diffs

---

## States

Default

Hover

Selected

Loading

Syncing

Completed

Error

---

## Interaction

Hover

Subtle elevation

Selected

Accent border

Loading

Skeleton

---

## Design Tokens

Radius-md

Border

Surface

Elevation-1

Spacing-4

---

# 32. Inputs

Inputs collect structured information.

All inputs must support keyboard navigation.

---

## Text Input

Used for

Names

Project titles

Search

URLs

Settings

---

### States

Empty

Focused

Filled

Disabled

Error

Success

---

### Validation

Validate on:

Blur

Never interrupt typing.

---

### Error Message

Displayed below input.

Never rely on color alone.

---

## Search Input

Purpose

Global search.

Repository search.

Command search.

---

### Features

Search icon

Clear button

Recent searches

Autocomplete

Keyboard shortcuts

---

### Keyboard

Arrow keys

Navigate results

Enter

Select

Esc

Close

---

## Textarea

Purpose

Descriptions

AI prompts

Commit messages

Notes

---

### Features

Auto-grow

Spell check

Character counter

Maximum height

Markdown support (AI)

---

### States

Focused

Disabled

Error

Filled

---

## Dropdown

Purpose

Single selection.

---

### Features

Keyboard navigation

Searchable

Grouped options

Multi-select (future)

---

### States

Closed

Open

Focused

Selected

Disabled

---

### Keyboard

Arrow Up

Arrow Down

Enter

Esc

Home

End

---

## Checkbox

Purpose

Multiple selection.

---

### States

Unchecked

Checked

Indeterminate

Disabled

---

### Accessibility

Label required.

Clickable area minimum

44 × 44

---

## Toggle

Purpose

Enable or disable settings.

Examples

Dark Mode

Notifications

AI Suggestions

---

### States

On

Off

Disabled

---

### Motion

250ms transition

---

## Input Validation

Validation should be:

Immediate for formatting.

Deferred for business rules.

Helpful.

Never punitive.

---

## Error Messages

Good

"Repository name is required."

Bad

"Validation failed."

---

## Success Messages

Use only when necessary.

Example

"Repository connected successfully."

---

## Design Tokens

Inputs use

Border

Surface

Accent

Radius-md

Spacing-3

Text-primary

Text-secondary

---

# 33. Search Components

Search is a first-class interaction in Forge.

Users should be able to locate anything quickly.

---

## Global Search

Shortcut

Ctrl + K

Searches

Projects

Files

Commands

AI Conversations

Tasks (Future)

Documentation

---

## Repository Search

Supports

Filename

Extension

Folder

Content (future)

---

## Search Results

Each result displays

Icon

Title

Location

Category

Shortcut

---

## Empty Search

Show

"No matching results."

Suggest:

- Check spelling
- Search another project

---

## Keyboard

↑ ↓

Navigate

Enter

Open

Esc

Close

---

# 34. Form Guidelines

Forms should minimize user effort.

---

## Rules

Group related fields.

Avoid unnecessary required fields.

Provide sensible defaults.

Use inline validation.

---

## Required Fields

Marked with:

*

---

## Optional Fields

Never marked.

---

## Labels

Always above the input.

Never use placeholders as labels.

---

## Submit Buttons

Remain disabled until required fields are valid.

---

## Confirmation

Critical operations require confirmation.

Examples

Delete Repository

Remove Member

Discard Changes

---

## Form Feedback

Success

Inline confirmation

Failure

Specific explanation

Loading

Disable submit button

Show progress indicator

---

## End of Part 3A

---

# 35. Tables

Tables should only be used when information is inherently tabular.

For most dashboard content, cards provide a better user experience.

---

## Use Cases

Tables are appropriate for:

- Team Members
- Repository Files
- Pull Requests (Future)
- Commit History
- Activity Logs
- API Keys
- Audit Logs

Avoid using tables for project overviews or AI-generated content.

---

## Table Structure

Each table consists of:

- Header
- Rows
- Cells
- Pagination (when necessary)
- Search
- Filters
- Bulk Actions

---

## States

Default

Loading

Empty

Sorted

Filtered

Selected

Hover

Error

---

## Interaction Rules

- Rows highlight on hover.
- Clicking a row opens details.
- Checkboxes enable bulk actions.
- Sorting indicators remain visible.
- Sticky headers on vertical scroll.

---

## Keyboard Support

Tab

Move focus

Arrow Keys

Navigate cells (future)

Enter

Open selected row

Space

Toggle row selection

---

## Accessibility

- Use semantic `<table>` elements.
- Every column requires `<th scope="col">`.
- Announce sorting direction.
- Maintain keyboard navigation.

---

## Design Tokens

Surface

Border

Radius-sm

Spacing-3

Text-primary

---

# 36. Tabs

Tabs organize related content without changing pages.

---

## Use Cases

- Repository
- Settings
- AI History
- Architecture Views (Future)
- Team Management (Future)

---

## Variants

Standard

Underlined

Segmented

---

## States

Default

Hover

Active

Disabled

Focused

---

## Behavior

Only one tab may be active.

Tab content loads lazily when appropriate.

The active tab persists when returning to the page.

---

## Keyboard Support

Arrow Left

Arrow Right

Home

End

Enter

---

## Accessibility

Use proper ARIA tab roles.

The active tab must be announced by screen readers.

---

## Motion

Underline transition

200ms

---

# 37. Accordions

Accordions progressively reveal information.

---

## Use Cases

- Documentation
- Settings
- Logs
- AI Explanations
- Advanced Options

---

## Behavior

Supports:

Single Expand

Multiple Expand

Remember expanded state while on the page.

---

## States

Collapsed

Expanded

Disabled

---

## Motion

Height transition

200ms

Chevron rotates

180°

---

## Accessibility

Enter

Toggle

Space

Toggle

Arrow Keys

Navigate sections

---

# 38. Context Menus

Context menus provide secondary actions.

---

## Trigger

Desktop

Right Click

Mobile

Long Press

---

## Examples

Repository

Rename

Delete

Clone

Open

AI

Explain

Review

Refactor

---

## Behavior

Appears near cursor.

Automatically adjusts to viewport boundaries.

Closes when:

- Clicking outside
- Pressing Escape
- Selecting an item

---

## Accessibility

Every action must also be available elsewhere in the UI.

Context menus cannot be the only method of accessing functionality.

---

# 39. Modals

Modals interrupt the current workflow for important decisions.

---

## Use Cases

Delete Confirmation

Invite Members

Repository Import

Settings

Authentication

---

## Structure

Header

Title

Description

Content

Footer

Primary Action

Secondary Action

---

## Sizes

Small

Medium

Large

Fullscreen

---

## Behavior

Centered

Backdrop

Scroll locking

Escape closes (unless destructive)

Focus trapped inside modal

Return focus to trigger on close

---

## Accessibility

- `role="dialog"`
- `aria-modal="true"`
- Focus management required

---

## Motion

Fade

Scale

250ms

---

# 40. Drawers

Drawers present contextual information without leaving the current page.

---

## Use Cases

Mobile AI Panel

Project Details

Notifications

Settings

---

## Placement

Right (default)

Left (navigation)

Bottom (mobile)

---

## Behavior

Slide animation

Overlay background

Dismiss on outside click

Remember scroll position

---

## Motion

250ms

Ease-out

---

# 41. Tooltips

Tooltips provide short contextual guidance.

---

## Use Cases

Icon Buttons

Keyboard Shortcuts

Status Indicators

---

## Rules

Maximum:

2 lines

Never include critical information.

Delay:

400ms

Disappear immediately when pointer leaves.

---

## Accessibility

Visible on:

Hover

Focus

---

# 42. Toast Notifications

Toasts communicate temporary system feedback.

---

## Types

Success

Warning

Error

Info

---

## Position

Desktop

Bottom Right

Mobile

Top Center

---

## Duration

5 seconds

Errors requiring action remain visible.

---

## Actions

Undo

Retry

View Details

---

## Motion

Slide

Fade

200ms

---

# 43. Command Palette

The Command Palette is the fastest way to interact with Forge.

---

## Shortcut

Ctrl + K

---

## Capabilities

Search Projects

Open Files

Run Commands

Ask AI

Switch Theme

Navigate Settings

Recent Files

Recent Conversations

---

## Layout

Search Bar

Recent Items

Suggestions

Results

Keyboard Shortcuts

---

## Keyboard

↑ ↓

Navigate

Enter

Execute

Esc

Close

Tab

Autocomplete

---

## Empty State

"No matching command."

Suggest similar commands.

---

## Accessibility

Fully keyboard accessible.

Supports screen readers.

---

# 44. Notifications

Notifications keep users informed without interrupting workflow.

---

## Types

Repository Indexed

Commit Successful

AI Response Ready

Repository Import Failed

Member Joined

Update Available

---

## Categories

Success

Warning

Error

Information

---

## Behavior

Stack vertically.

Newest appears first.

Critical notifications persist until dismissed.

---

# 45. Component Development Standards

Every component in Forge must follow the same engineering standards.

---

## Naming Convention

Components

PascalCase

Example

ProjectCard.tsx

Hooks

camelCase

Example

useProject.ts

Files

kebab-case

Example

project-card.tsx

---

## Folder Structure

Each reusable component should contain:

- Component
- Styles
- Types
- Tests
- Stories (future)

Example:

components/
└── Button/
    ├── Button.tsx
    ├── Button.types.ts
    ├── Button.test.tsx
    └── index.ts

---

## Development Principles

Every component should be:

- Reusable
- Stateless where possible
- Theme-aware
- Responsive
- Accessible
- Typed
- Tested

---

## Design Token Usage

Never use:

Hardcoded colors

Hardcoded spacing

Hardcoded radius

Always reference design tokens.

---

## Performance Guidelines

Lazy-load heavy components.

Memoize expensive renders.

Avoid unnecessary re-renders.

Virtualize long lists.

---

## Documentation Requirements

Every component should document:

Purpose

Props

Variants

Accessibility

Examples

Known Limitations

---

## Anti-Patterns

Avoid:

- Nested modals
- Multiple floating dialogs
- Hidden actions
- Inconsistent spacing
- Magic numbers
- Hardcoded colors
- Duplicate components

---

## End of Part 3

---

# 46. Global UI States

Global states define how every component and screen behaves during different stages of user interaction.

Consistency across these states is essential to maintaining a predictable user experience.

---

## Loading State

Loading should always communicate progress.

Users should understand:

- What is happening
- Why it is happening
- What will happen next

### Guidelines

Use:

- Skeleton loaders
- Progressive rendering
- Placeholder content

Avoid:

- Infinite loading indicators
- Empty white screens
- Blocking the entire interface

---

### AI Loading

AI actions must always describe their current activity.

Examples:

✓ Analyzing repository...

✓ Searching project memory...

✓ Reading project architecture...

✓ Generating code changes...

Avoid generic messages like:

✗ Loading...

✗ Please wait...

---

### Repository Loading

Repository import consists of multiple visible stages.

1. Connecting to GitHub
2. Cloning Repository
3. Parsing Files
4. Building Project Graph
5. Generating Embeddings
6. Indexing Complete

Each completed stage should provide visual feedback.

---

## Empty States

Every empty state should answer three questions:

1. Why is this empty?
2. What can I do?
3. What's the next step?

---

### Empty Dashboard

Illustration

↓

"No projects yet"

↓

Create Project

Import Repository

---

### Empty Repository

"No repository connected."

Action:

Import Repository

---

### Empty AI Chat

Ask your first repository question.

Suggested prompts:

- Explain this repository
- Show project architecture
- Find authentication flow

---

### Empty Notifications

You're all caught up.

---

### Empty Search

No matching results.

Suggestions:

- Check spelling
- Search another project
- Use fewer keywords

---

## Error States

Errors should be informative instead of alarming.

Never expose raw stack traces.

---

### Structure

Error Title

Short Explanation

Suggested Solution

Retry Button

Support Link (future)

---

### Good Examples

Unable to import repository.

Please check repository permissions and try again.

Retry

---

Authentication expired.

Please sign in again.

Sign In

---

### Bad Examples

Error 500

Unknown Exception

Validation Failed

---

## Success States

Success feedback should be lightweight.

Examples:

✓ Repository imported.

✓ Changes committed.

✓ AI response generated.

✓ Settings saved.

Use animations sparingly.

---

## Disabled States

Disabled components indicate temporary unavailability.

Rules:

- Reduced opacity
- Cursor not-allowed
- No pointer events
- Removed from keyboard focus

Provide explanation when appropriate.

Example:

Push disabled until changes are committed.

---

# 47. Motion System

Motion reinforces hierarchy and provides feedback.

Animation should feel responsive but never distracting.

---

## Principles

Motion communicates:

- Navigation
- Focus
- Progress
- Confirmation

Motion must never exist solely for decoration.

---

## Timing

Hover

120ms

Button Press

100ms

Dropdown

180ms

Accordion

200ms

Sidebar

250ms

Drawer

250ms

Modal

250ms

Page Transition

300ms

Theme Switch

400ms

Toast

200ms

---

## Easing

Default

ease-in-out

Entrance

ease-out

Exit

ease-in

---

## Motion Rules

Avoid:

Large bounces

Elastic animations

Overshoot

Long transitions

Prefer:

Opacity

Scale

Translate

Fade

---

## Reduced Motion

Respect:

prefers-reduced-motion

Disable:

Page transitions

Floating animations

Large scaling effects

Keep:

Essential feedback

Focus changes

Toast appearance

---

# 48. Micro-interactions

Small interactions improve perceived responsiveness.

---

## Buttons

Hover

Slight elevation

Press

Scale 0.98

Loading

Spinner replaces icon

---

## Cards

Hover

Subtle elevation

Selected

Accent border

---

## Sidebar

Collapse

Smooth width animation

Tooltips appear after 400ms

---

## AI Messages

Stream response progressively.

Automatically scroll while generating.

Highlight referenced files.

---

## Search

Results appear immediately.

Keyboard navigation updates selection.

---

## Git Diff

Changed lines animate into view.

Accepted changes briefly highlight.

---

# 49. Accessibility Standards

Accessibility is mandatory.

Forge targets WCAG 2.2 AA compliance.

---

## Keyboard Navigation

Every feature must be accessible without a mouse.

Common shortcuts:

Tab

Shift + Tab

Enter

Space

Escape

Arrow Keys

Ctrl + K

---

## Focus

Visible focus indicator:

2px Accent Ring

Offset

2px

Never remove browser focus without replacement.

---

## Color

Never rely solely on color.

Pair color with:

Icons

Labels

Badges

---

## Contrast

Text

≥ 4.5 : 1

Large Text

≥ 3 : 1

---

## Screen Readers

Every interactive component must provide:

Accessible name

Role

State

Description

Examples:

aria-label

aria-describedby

aria-expanded

aria-selected

aria-live

---

## Icon Buttons

Always require:

aria-label

---

## Forms

Inputs require:

Label

Description

Validation message

Associated helper text

---

# 50. Responsive Design

Forge is optimized for desktop development.

Mobile provides project awareness rather than full development.

---

## Desktop

≥ 1280px

Three-column layout

Sidebar

Workspace

AI Panel

---

## Laptop

1024–1279px

Sidebar collapses automatically.

AI panel remains docked.

---

## Tablet

768–1023px

Sidebar becomes drawer.

AI panel overlays workspace.

Repository explorer collapses.

---

## Mobile

<768px

Supported:

Dashboard

Notifications

AI Chat

Repository Overview

Settings

Tasks (Future)

Unsupported:

Monaco Editor

Architecture Graph

Split View

---

## Breakpoints

sm

640px

md

768px

lg

1024px

xl

1280px

2xl

1536px

---

# 51. Design Tokens

Every component must consume design tokens.

Never hardcode values.

---

## Colors

background

surface

surface-elevated

text-primary

text-secondary

text-muted

border

divider

accent

success

warning

error

info

---

## Typography

display

h1

h2

h3

h4

body-lg

body

small

caption

code

---

## Spacing

4

8

12

16

24

32

40

48

64

80

96

128

---

## Radius

sm

md

lg

dialog

floating

---

## Elevation

0

1

2

3

4

---

## Motion

hover

press

panel

page

theme

toast

---

## Icons

16

20

24

32

---

# 52. UX Principles

Every screen in Forge should satisfy these principles.

---

## Clarity

Users always understand:

- Where they are
- What happened
- What happens next

---

## Speed

Interactions should feel immediate.

UI feedback should occur within 100ms whenever possible.

---

## Consistency

Every component behaves predictably.

Users should never relearn interactions.

---

## AI-First

AI remains available throughout the application.

Users should never leave their workflow to access AI.

---

## Human Control

AI recommends.

Humans decide.

Every destructive action requires confirmation.

---

## Progressive Disclosure

Show advanced functionality only when relevant.

Avoid overwhelming users with rarely used controls.

---

## Trust

Never exaggerate AI capabilities.

If AI is uncertain, communicate uncertainty clearly.

---

# 53. Implementation Guidelines

These guidelines ensure consistency across the codebase.

---

## Component Standards

Every component must:

- Be reusable
- Be responsive
- Be theme-aware
- Be keyboard accessible
- Support loading and disabled states
- Use design tokens
- Include TypeScript types

---

## Performance

Prefer:

Lazy loading

Memoization

Virtualized lists

Code splitting

Avoid:

Large unnecessary re-renders

Blocking the main thread

Heavy animations

---

## State Management

Keep UI state local where possible.

Promote shared state only when multiple components require it.

Avoid deeply nested state.

---

## Error Handling

All async operations should provide:

Loading

Success

Failure

Retry

---

## AI Features

Every AI action should provide:

Current status

Cancel option (where feasible)

Confidence explanation (future)

Human approval before code modification

---

## Final Principle

Forge should never feel like multiple tools stitched together.

It should feel like **one cohesive AI-native development environment** where repositories, collaboration, and artificial intelligence work together seamlessly.

---

# End of UI/UX Design System

This document serves as the single source of truth for the visual design, interaction patterns, accessibility standards, and user experience of Forge.

All frontend implementations should conform to this specification unless explicitly superseded by future design revisions.
