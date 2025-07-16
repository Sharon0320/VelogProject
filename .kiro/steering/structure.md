# Project Structure

## Root Level
```
├── docker-compose.yml          # Multi-service orchestration
├── BackEnd/                    # Python Flask API
└── FrontEnd/                   # Next.js React application
```

## Backend Structure (`BackEnd/`)
```
BackEnd/
├── .env                        # Environment variables (API keys)
├── Dockerfile                  # Container configuration
├── Velog.py                    # Main Flask application
├── requirements.in             # Direct dependencies
└── requirements.txt            # Pinned dependencies
```

### Backend Architecture
- **Single file application**: All logic in `Velog.py`
- **Main functions**:
  - `get_summary_title_body_tags()`: Perplexity AI integration
  - `post_to_velog()`: Velog GraphQL mutation
  - `remove_references()`: Text cleaning utility
- **Single endpoint**: `/post` (POST) - handles full blog generation pipeline

## Frontend Structure (`FrontEnd/`)
```
FrontEnd/
├── app/
│   ├── api/generate-blog/      # API route handler
│   ├── globals.css             # Global styles
│   ├── layout.tsx              # Root layout
│   └── page.tsx                # Main application page
├── components/
│   ├── ui/                     # shadcn/ui components
│   ├── cookie-helper.tsx       # Velog cookie management
│   └── theme-provider.tsx      # Theme context
├── hooks/                      # Custom React hooks
├── lib/                        # Utility functions
├── public/                     # Static assets
└── styles/                     # Additional stylesheets
```

### Frontend Architecture
- **App Router**: Next.js 13+ file-based routing
- **Single page application**: Main UI in `app/page.tsx`
- **API proxy**: `/api/generate-blog` proxies to Flask backend
- **Component organization**: UI components in `components/ui/`, custom components at root level

## Key Conventions

### File Naming
- **Frontend**: kebab-case for files, PascalCase for React components
- **Backend**: snake_case for Python files and functions
- **Config files**: lowercase with extensions

### Code Organization
- **Frontend**: Functional components with hooks, TypeScript interfaces
- **Backend**: Flask app with utility functions, environment-based configuration
- **Shared**: Docker configuration for consistent deployment

### API Communication
- **Frontend → Backend**: JSON over HTTP
- **Backend → External**: REST (Perplexity) and GraphQL (Velog)
- **Error handling**: Try-catch with user-friendly messages

### Environment Management
- **Development**: Local servers (Next.js dev server + Flask)
- **Production**: Docker containers with port mapping
- **Configuration**: Environment variables for API keys and URLs