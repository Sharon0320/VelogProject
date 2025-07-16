# Technology Stack

## Frontend
- **Framework**: Next.js 15.2.4 with App Router
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS with custom animations
- **UI Components**: Radix UI primitives with shadcn/ui
- **State Management**: React hooks (useState, custom hooks)
- **Forms**: React Hook Form with Zod validation
- **Notifications**: Sonner for toast notifications
- **Theme**: next-themes for dark/light mode support

## Backend
- **Framework**: Flask 3.0.3 (Python)
- **HTTP Client**: requests 2.31.0
- **Environment**: python-dotenv for configuration
- **Text Processing**: kiwipiepy 0.20.4 (Korean NLP)
- **Numerical**: numpy 1.26.4

## External APIs
- **Perplexity AI**: Content enhancement and generation
- **Velog GraphQL**: Blog post publishing

## Development & Deployment
- **Containerization**: Docker with docker-compose
- **Package Management**: 
  - Frontend: pnpm (preferred), npm fallback
  - Backend: pip with requirements.txt
- **Build Output**: Static export for frontend

## Common Commands

### Development
```bash
# Start full stack
docker-compose up

# Frontend only
cd FrontEnd && pnpm dev
# or
cd FrontEnd && npm run dev

# Backend only
cd BackEnd && python Velog.py
```

### Build & Deploy
```bash
# Frontend build
cd FrontEnd && pnpm build
cd FrontEnd && pnpm export

# Docker build
docker-compose build
```

### Dependencies
```bash
# Frontend
cd FrontEnd && pnpm install

# Backend
cd BackEnd && pip install -r requirements.txt
```

## Environment Variables
- Backend requires `.env` file with Perplexity API credentials
- Frontend connects to backend via localhost:5000 in development