# Product Overview

## Velog Auto Blog Generator

An AI-powered blog writing assistant that automatically generates and publishes blog posts to Velog (Korean blogging platform).

### Core Features
- Takes simple text input and transforms it into structured blog posts
- Uses Perplexity AI to enhance content with proper formatting, titles, summaries, and tags
- Automatically publishes to Velog via GraphQL API
- Web interface for content input and cookie management
- Supports Korean language content optimization

### User Flow
1. User inputs raw content/ideas in the frontend
2. User provides Velog authentication cookies
3. Backend processes content through Perplexity AI
4. AI generates title, summary, enhanced body content, and relevant tags
5. System automatically posts to Velog using GraphQL mutation
6. User receives confirmation with direct link to published post

### Target Users
Korean developers and content creators who want to streamline their technical blog writing process on Velog.