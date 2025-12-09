# Frontend Implementation Plan

## Context Search Tool for PDF Files - Frontend

This document outlines the detailed implementation plan for the React + pdf.js frontend of the enterprise PDF vector search engine.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Tech Stack & Dependencies](#2-tech-stack--dependencies)
3. [Design System](#3-design-system)
4. [Module Breakdown](#4-module-breakdown)
5. [API Integration](#5-api-integration)
6. [State Management](#6-state-management)
7. [Component Architecture](#7-component-architecture)
8. [Page Routes](#8-page-routes)
9. [Team Collaboration Guidelines](#9-team-collaboration-guidelines)
10. [Development Phases](#10-development-phases)
11. [Testing Strategy](#11-testing-strategy)

---

## 1. Project Structure

```
search-engine/
├── .github/
│   └── copilot-instructions.md
├── backend/                    # Backend team's workspace
│   ├── app/
│   ├── celery_worker/
│   ├── requirements.txt
│   └── ...
├── frontend/                   # Frontend workspace (React)
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── api/               # API client & endpoints
│   │   │   ├── client.ts      # Axios instance with interceptors
│   │   │   ├── auth.api.ts    # Authentication endpoints
│   │   │   ├── documents.api.ts   # PDF upload/management
│   │   │   └── search.api.ts  # Search endpoints
│   │   ├── assets/            # Static assets (icons, images)
│   │   │   └── icons/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── common/        # Generic components
│   │   │   │   ├── Button/
│   │   │   │   ├── Input/
│   │   │   │   ├── Modal/
│   │   │   │   ├── Loader/
│   │   │   │   ├── Card/
│   │   │   │   └── Toast/
│   │   │   ├── layout/        # Layout components
│   │   │   │   ├── Header/
│   │   │   │   ├── Sidebar/
│   │   │   │   └── PageContainer/
│   │   │   ├── auth/          # Authentication components
│   │   │   │   ├── LoginForm/
│   │   │   │   ├── RegisterForm/
│   │   │   │   └── ProtectedRoute/
│   │   │   ├── documents/     # Document management components
│   │   │   │   ├── DocumentUploader/
│   │   │   │   ├── DocumentList/
│   │   │   │   ├── DocumentCard/
│   │   │   │   └── UploadProgress/
│   │   │   ├── search/        # Search components
│   │   │   │   ├── SearchBar/
│   │   │   │   ├── SearchResults/
│   │   │   │   ├── ResultItem/
│   │   │   │   └── ConfidenceScore/
│   │   │   └── viewer/        # PDF viewer components
│   │   │       ├── PDFViewer/
│   │   │       ├── PageNavigator/
│   │   │       ├── TextHighlighter/
│   │   │       └── ZoomControls/
│   │   ├── contexts/          # React contexts
│   │   │   ├── AuthContext.tsx
│   │   │   ├── DocumentContext.tsx
│   │   │   └── SearchContext.tsx
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useDocuments.ts
│   │   │   ├── useSearch.ts
│   │   │   ├── usePDFViewer.ts
│   │   │   └── useDebounce.ts
│   │   ├── pages/             # Page components (routes)
│   │   │   ├── LoginPage/
│   │   │   ├── RegisterPage/
│   │   │   ├── DashboardPage/
│   │   │   ├── SearchPage/
│   │   │   ├── DocumentsPage/
│   │   │   └── ViewerPage/
│   │   ├── services/          # Business logic services
│   │   │   ├── auth.service.ts
│   │   │   ├── storage.service.ts   # localStorage/sessionStorage
│   │   │   └── pdf.service.ts
│   │   ├── styles/            # Global styles
│   │   │   ├── variables.css  # CSS variables (colors, spacing)
│   │   │   ├── reset.css      # CSS reset
│   │   │   └── global.css     # Global styles
│   │   ├── types/             # TypeScript type definitions
│   │   │   ├── auth.types.ts
│   │   │   ├── document.types.ts
│   │   │   ├── search.types.ts
│   │   │   └── api.types.ts
│   │   ├── utils/             # Utility functions
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   └── constants.ts
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── routes.tsx
│   ├── .env.example           # Environment variables template
│   ├── .env.local             # Local environment (gitignored)
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docker/                    # Docker configurations (shared)
│   ├── docker-compose.yml     # Full stack compose
│   ├── docker-compose.dev.yml # Development compose
│   └── .env.docker            # Docker environment variables
├── docs/                      # Documentation
│   ├── API.md                 # API documentation (backend provides)
│   ├── FRONTEND.md            # Frontend documentation
│   └── SETUP.md               # Setup instructions
├── plan.md                    # This file
└── README.md                  # Project overview
```

---

## 2. Tech Stack & Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `react` | ^18.x | UI library |
| `react-dom` | ^18.x | React DOM renderer |
| `react-router-dom` | ^6.x | Client-side routing |
| `typescript` | ^5.x | Type safety |
| `vite` | ^5.x | Build tool & dev server |

### UI & Styling

| Package | Version | Purpose |
|---------|---------|---------|
| `@emotion/react` or CSS Modules | - | Component styling |
| `react-icons` | ^5.x | Icon library |

### PDF Handling

| Package | Version | Purpose |
|---------|---------|---------|
| `pdfjs-dist` | ^4.x | PDF rendering (pdf.js) |
| `react-pdf` | ^7.x | React wrapper for pdf.js |

### Data Fetching & State

| Package | Version | Purpose |
|---------|---------|---------|
| `axios` | ^1.x | HTTP client |
| `@tanstack/react-query` | ^5.x | Server state management |
| `zustand` | ^4.x | Client state management (optional) |

### Utilities

| Package | Version | Purpose |
|---------|---------|---------|
| `date-fns` | ^3.x | Date formatting |
| `react-hot-toast` | ^2.x | Toast notifications |
| `react-dropzone` | ^14.x | File upload dropzone |

### Development

| Package | Version | Purpose |
|---------|---------|---------|
| `eslint` | ^8.x | Linting |
| `prettier` | ^3.x | Code formatting |
| `vitest` | ^1.x | Unit testing |
| `@testing-library/react` | ^14.x | Component testing |

---

## 3. Design System

### Color Palette

```css
:root {
  /* Primary Colors */
  --color-primary: #2C2C2A;          /* Main accent color (dark grey) */
  --color-primary-light: #4A4A47;    /* Lighter variant */
  --color-primary-dark: #1A1A19;     /* Darker variant */
  
  /* Background Colors */
  --color-bg-primary: #FFFFFF;       /* Main background */
  --color-bg-secondary: #F5F5F5;     /* Secondary background */
  --color-bg-tertiary: #EBEBEB;      /* Tertiary background */
  
  /* Text Colors */
  --color-text-primary: #2C2C2A;     /* Primary text */
  --color-text-secondary: #6B6B6B;   /* Secondary text */
  --color-text-muted: #9B9B9B;       /* Muted text */
  --color-text-inverse: #FFFFFF;     /* Text on dark backgrounds */
  
  /* Border Colors */
  --color-border: #E0E0E0;           /* Default border */
  --color-border-focus: #2C2C2A;     /* Focus state border */
  
  /* Semantic Colors */
  --color-success: #4CAF50;          /* Success states */
  --color-warning: #FF9800;          /* Warning states */
  --color-error: #F44336;            /* Error states */
  --color-info: #2196F3;             /* Info states */
  
  /* Confidence Score Colors */
  --color-score-high: #4CAF50;       /* 80-100% confidence */
  --color-score-medium: #FF9800;     /* 50-79% confidence */
  --color-score-low: #F44336;        /* Below 50% confidence */
  
  /* Highlight Color (for PDF text) */
  --color-highlight: rgba(255, 235, 59, 0.4);  /* Yellow highlight */
}
```

### Typography

```css
:root {
  /* Font Family */
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* Font Sizes */
  --font-size-xs: 0.75rem;    /* 12px */
  --font-size-sm: 0.875rem;   /* 14px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.125rem;   /* 18px */
  --font-size-xl: 1.25rem;    /* 20px */
  --font-size-2xl: 1.5rem;    /* 24px */
  --font-size-3xl: 1.875rem;  /* 30px */
  
  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}
```

### Spacing System

```css
:root {
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  --spacing-2xl: 3rem;     /* 48px */
}
```

### Component Styling Guidelines

1. **Buttons**: Flat design, subtle hover states, clear disabled states
2. **Inputs**: Clean borders, clear focus states, proper validation feedback
3. **Cards**: Minimal shadows, clear hierarchy
4. **Modals**: Centered, backdrop blur, smooth animations

---

## 4. Module Breakdown

### Module 1: Authentication (`/auth`)

**Components:**
- `LoginForm` - Email/password login form with validation
- `RegisterForm` - User registration form
- `ProtectedRoute` - Route wrapper for authenticated pages

**Features:**
- Email + password authentication
- JWT token storage (httpOnly cookie or localStorage)
- Auto-redirect on auth state change
- Form validation with error messages
- "Remember me" functionality
- Password visibility toggle

### Module 2: Document Management (`/documents`)

**Components:**
- `DocumentUploader` - Drag & drop + click to upload PDFs
- `DocumentList` - Grid/list view of uploaded documents
- `DocumentCard` - Individual document display with metadata
- `UploadProgress` - Progress indicator for uploads

**Features:**
- Multi-file upload support
- Upload progress tracking
- Processing status indicators (queued, processing, ready, failed)
- Document metadata display (name, size, pages, upload date)
- Delete document functionality
- Bulk selection and actions

### Module 3: Search (`/search`)

**Components:**
- `SearchBar` - Main search input with search button
- `SearchResults` - Results container with sorting/filtering
- `ResultItem` - Individual search result display
- `ConfidenceScore` - Visual confidence score indicator

**Features:**
- Real-time search with debouncing
- Search history (recent searches)
- Results sorted by confidence score
- Filter by document
- Result preview snippet
- Click to navigate to PDF viewer

### Module 4: PDF Viewer (`/viewer`)

**Components:**
- `PDFViewer` - Main PDF rendering component (pdf.js)
- `PageNavigator` - Page number input + prev/next buttons
- `TextHighlighter` - Overlay for highlighting matched text
- `ZoomControls` - Zoom in/out/fit controls
- `Thumbnail` - Page thumbnails sidebar

**Features:**
- Render PDF pages with pdf.js
- Text layer for selection
- Highlight search matches on page
- Zoom controls (fit width, fit page, custom %)
- Page navigation (input, arrows, thumbnails)
- Smooth scrolling to highlighted sections
- Loading states for large documents

### Module 5: Layout (`/layout`)

**Components:**
- `Header` - App header with navigation and user menu
- `Sidebar` - Navigation sidebar (collapsible)
- `PageContainer` - Consistent page wrapper

**Features:**
- Responsive layout
- Collapsible sidebar
- User dropdown menu (profile, logout)
- Breadcrumb navigation

---

## 5. API Integration

### API Client Setup (`/api/client.ts`)

```typescript
// Axios instance with:
// - Base URL from environment variable
// - Request interceptor for JWT token attachment
// - Response interceptor for error handling & token refresh
// - Request/response typing
```

### Expected Backend Endpoints

**Authentication:**
```
POST   /api/auth/register     - Register new user
POST   /api/auth/login        - Login user
POST   /api/auth/logout       - Logout user
POST   /api/auth/refresh      - Refresh JWT token
GET    /api/auth/me           - Get current user
```

**Documents:**
```
GET    /api/documents         - List user's documents
POST   /api/documents/upload  - Upload PDF file(s)
GET    /api/documents/:id     - Get document metadata
DELETE /api/documents/:id     - Delete document
GET    /api/documents/:id/status - Get processing status
GET    /api/documents/:id/file   - Get PDF file (for viewer)
```

**Search:**
```
POST   /api/search            - Perform semantic search
GET    /api/search/history    - Get search history
```

### Request/Response Types

```typescript
// Example types to be defined in /types/

interface SearchRequest {
  query: string;
  documentIds?: string[];  // Optional filter by documents
  limit?: number;
}

interface SearchResult {
  documentId: string;
  documentName: string;
  pageNumber: number;
  snippet: string;
  confidenceScore: number;  // 0-100
  highlights: TextHighlight[];
}

interface TextHighlight {
  text: string;
  startOffset: number;
  endOffset: number;
  boundingBox?: BoundingBox;
}
```

---

## 6. State Management

### Server State (React Query)

Use `@tanstack/react-query` for:
- Document list fetching & caching
- Search results
- User data
- Automatic refetching & cache invalidation

### Client State (Context + Hooks)

**AuthContext:**
- Current user
- Authentication status
- Login/logout functions

**SearchContext:**
- Current search query
- Search filters
- Active search results

**ViewerContext:**
- Current document
- Current page
- Zoom level
- Active highlights

### Local Storage

- JWT token (if not using httpOnly cookies)
- User preferences (theme, sidebar state)
- Recent searches

---

## 7. Component Architecture

### Component Structure

Each component folder should contain:

```
ComponentName/
├── ComponentName.tsx       # Main component
├── ComponentName.module.css # Scoped styles (CSS Modules)
├── ComponentName.test.tsx  # Unit tests
├── index.ts                # Export barrel
└── types.ts                # Component-specific types (if needed)
```

### Component Guidelines

1. **Props Interface**: Define clear TypeScript interfaces for all props
2. **Default Props**: Use default parameter values
3. **Composition**: Prefer composition over prop drilling
4. **Accessibility**: Include ARIA attributes, keyboard navigation
5. **Loading States**: Handle loading, error, and empty states
6. **Responsiveness**: Mobile-first responsive design

### Example Component Template

```typescript
// ComponentName.tsx
import { FC } from 'react';
import styles from './ComponentName.module.css';

interface ComponentNameProps {
  // Props definition
}

export const ComponentName: FC<ComponentNameProps> = ({
  // Destructured props with defaults
}) => {
  // Component logic
  
  return (
    <div className={styles.container}>
      {/* JSX */}
    </div>
  );
};
```

---

## 8. Page Routes

| Route | Page | Auth Required | Description |
|-------|------|---------------|-------------|
| `/login` | LoginPage | No | User login |
| `/register` | RegisterPage | No | User registration |
| `/` | DashboardPage | Yes | Dashboard/home |
| `/search` | SearchPage | Yes | Main search interface |
| `/documents` | DocumentsPage | Yes | Document management |
| `/viewer/:documentId` | ViewerPage | Yes | PDF viewer with highlights |
| `/viewer/:documentId?page=X&highlight=Y` | ViewerPage | Yes | Direct link to specific page/highlight |

---

## 9. Team Collaboration Guidelines

### For Backend Team

#### API Contract

1. **Create `docs/API.md`** with complete endpoint documentation including:
   - Request/response schemas (JSON)
   - Authentication requirements
   - Error response formats
   - Rate limiting info

2. **Consistent Response Format:**
   ```json
   {
     "success": true,
     "data": { ... },
     "message": "Optional message",
     "errors": []
   }
   ```

3. **Error Response Format:**
   ```json
   {
     "success": false,
     "data": null,
     "message": "Error description",
     "errors": [
       { "field": "email", "message": "Invalid email format" }
     ]
   }
   ```

#### Database Schema Sharing

1. Maintain database schema documentation in `docs/SCHEMA.md`
2. Use migrations for all database changes
3. Seed data scripts for development

#### Environment Variables

Backend should document required environment variables:

```env
# Backend .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/searchdb
QDRANT_URL=http://localhost:6333
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
JWT_SECRET=your-secret-key
```

### For Frontend Team (This Document)

#### Environment Variables

```env
# Frontend .env.example
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=PDF Search Engine
```

#### Development Workflow

1. Use feature branches: `feature/search-bar`, `feature/pdf-viewer`
2. PR reviews required before merging
3. Run linting and tests before commits
4. Follow component naming conventions

### Shared Docker Setup

#### `docker-compose.dev.yml` (Development)

```yaml
version: '3.8'

services:
  # Databases - shared by all team members
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: searchdb
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
  qdrant_data:
  minio_data:
```

#### Running Services

```bash
# Start all infrastructure services
docker-compose -f docker/docker-compose.dev.yml up -d

# Frontend development (separate terminal)
cd frontend && npm run dev

# Backend development (separate terminal)
cd backend && uvicorn app.main:app --reload
```

### Communication Protocol

1. **API Changes**: Backend notifies frontend 24h before breaking changes
2. **Weekly Sync**: Review integration points and blockers
3. **Shared Slack/Discord Channel**: For quick questions
4. **GitHub Issues**: For tracking bugs and features

---

## 10. Development Phases

### Phase 1: Foundation (Week 1)

- [ ] Initialize Vite + React + TypeScript project
- [ ] Set up project structure (folders, configs)
- [ ] Configure ESLint, Prettier
- [ ] Set up CSS variables and global styles
- [ ] Create common components (Button, Input, Card, Modal, Loader)
- [ ] Set up React Router with route structure
- [ ] Create API client with interceptors

### Phase 2: Authentication (Week 2)

- [ ] Implement AuthContext
- [ ] Create LoginForm component
- [ ] Create RegisterForm component
- [ ] Implement ProtectedRoute wrapper
- [ ] Add JWT token handling
- [ ] Create Header with user menu
- [ ] Test authentication flow

### Phase 3: Document Management (Week 3)

- [ ] Create DocumentUploader with drag & drop
- [ ] Implement upload progress tracking
- [ ] Create DocumentList component
- [ ] Create DocumentCard with status indicators
- [ ] Implement document deletion
- [ ] Add processing status polling
- [ ] Test document upload/management flow

### Phase 4: Search Interface (Week 4)

- [ ] Create SearchBar component
- [ ] Implement search with debouncing
- [ ] Create SearchResults container
- [ ] Create ResultItem with confidence score
- [ ] Add search history feature
- [ ] Implement result filtering
- [ ] Test search functionality

### Phase 5: PDF Viewer (Week 5-6)

- [ ] Set up pdf.js integration
- [ ] Create PDFViewer component
- [ ] Implement page navigation
- [ ] Add zoom controls
- [ ] Create text layer for selection
- [ ] Implement text highlighting
- [ ] Add thumbnail sidebar
- [ ] Test viewer with various PDFs

### Phase 6: Integration & Polish (Week 7)

- [ ] Connect search results to PDF viewer
- [ ] Implement deep linking (page + highlight)
- [ ] Add loading states everywhere
- [ ] Implement error boundaries
- [ ] Add toast notifications
- [ ] Responsive design testing
- [ ] Performance optimization
- [ ] Cross-browser testing

### Phase 7: Testing & Documentation (Week 8)

- [ ] Write unit tests for components
- [ ] Write integration tests for flows
- [ ] Create user documentation
- [ ] Update API documentation
- [ ] Performance profiling
- [ ] Bug fixes and polish

---

## 11. Testing Strategy

### Unit Tests

- Test individual components in isolation
- Mock API calls and context providers
- Test form validation logic
- Test utility functions

### Integration Tests

- Test complete user flows (login → search → view PDF)
- Test API integration with mock server
- Test routing and navigation

### E2E Tests (Optional)

- Use Playwright or Cypress
- Test critical paths end-to-end
- Test with real backend (staging)

### Test Coverage Goals

- Components: 80%+
- Hooks: 90%+
- Utilities: 95%+
- Critical flows: 100%

---

## Appendix: Quick Reference

### File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `SearchBar.tsx` |
| Hooks | camelCase, use prefix | `useSearch.ts` |
| Utils | camelCase | `formatters.ts` |
| Types | camelCase, .types suffix | `search.types.ts` |
| Styles | ComponentName.module.css | `SearchBar.module.css` |
| Tests | ComponentName.test.tsx | `SearchBar.test.tsx` |

### Import Order

```typescript
// 1. React and third-party imports
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// 2. Internal absolute imports (if configured)
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/common/Button';

// 3. Relative imports
import { SearchResultItem } from './SearchResultItem';

// 4. Styles
import styles from './SearchResults.module.css';

// 5. Types
import type { SearchResult } from '@/types/search.types';
```

### Git Commit Convention

```
feat: add search bar component
fix: resolve login redirect issue
docs: update API documentation
style: format code with prettier
refactor: extract PDF rendering logic
test: add unit tests for SearchBar
chore: update dependencies
```

---

## Next Steps

Once this plan is approved:

1. **Initialize the frontend project** with Vite + React + TypeScript
2. **Set up the folder structure** as defined above
3. **Configure the design system** (CSS variables)
4. **Create the base components** (Phase 1)
5. **Proceed module by module** following the development phases

---

*Document Version: 1.0*  
*Last Updated: December 9, 2025*  
*Author: Frontend Team*
