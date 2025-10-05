# Frontend Configuration Guide

## Overview
This document describes how to configure the D-RAG frontend application. All configurable values are centralized in the `src/config/constants.ts` file to avoid hardcoding.

## Configuration File Location
`src/config/constants.ts`

## Available Configuration Options

### Application Information
- `APP_CONFIG.name` - Application name (default: "D-RAG")
- `APP_CONFIG.fullName` - Full application name (default: "Dynamic Retrieval-Augmented Generation")
- `APP_CONFIG.description` - Main description text
- `APP_CONFIG.tagline` - Tagline displayed on login

### Validation Rules
- `APP_CONFIG.validation.minNameLength` - Minimum name length for registration (default: 2)
- `APP_CONFIG.validation.minPasswordLength` - Minimum password length (default: 6)

### Timeouts (milliseconds)
- `APP_CONFIG.timeouts.loginRedirect` - Delay before redirecting after login (default: 1000ms)
- `APP_CONFIG.timeouts.registerMessageDisplay` - How long to show registration success (default: 5000ms)
- `APP_CONFIG.timeouts.copyNotification` - How long to show copy confirmation (default: 2000ms)

### UI Constants
- `APP_CONFIG.ui.gridOpacity` - Background grid opacity hex value (default: "18")
- `APP_CONFIG.ui.chatHeight` - Chat interface height (default: "600px")

### Search Defaults
- `APP_CONFIG.search.similarityThreshold` - Similarity threshold for search (default: 0.5)
- `APP_CONFIG.search.defaultLimit` - Default number of search results (default: 10)

### Messages
All user-facing confirmation and alert messages:
- `confirmDeleteProject`
- `confirmRemoveContributor`
- `confirmRotateApiKey`
- `editFeatureComingSoon`

### Team Members
`TEAM_MEMBERS` array contains team member information with LinkedIn profiles.

### Features
`FEATURES` array defines the key features displayed on the About page.

### Tech Stack
`TECH_STACK` array lists all technologies used in the project.

## Environment Variables

The frontend uses environment variables for API configuration.

### `.env`
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

You can change this to your production API URL when deploying:
```
NEXT_PUBLIC_API_URL=https://your-production-api.com/api/v1
```

## Usage Examples

### Importing Configuration
```typescript
import { APP_CONFIG, TEAM_MEMBERS, FEATURES, TECH_STACK } from '@/config/constants';
```

### Using Configuration Values
```typescript
// Validation
if (name.length < APP_CONFIG.validation.minNameLength) {
  setError(`Name must be at least ${APP_CONFIG.validation.minNameLength} characters`);
}

// Timeouts
setTimeout(() => {
  router.push('/dashboard');
}, APP_CONFIG.timeouts.loginRedirect);

// Search
const results = await contextAPI.search(
  query,
  projectId,
  APP_CONFIG.search.similarityThreshold,
  APP_CONFIG.search.defaultLimit
);
```

## Modifying Configuration

To change any application settings:

1. Open `src/config/constants.ts`
2. Modify the desired value
3. Save the file
4. Rebuild the application if necessary

## Best Practices

1. **Never hardcode values** - Always use the configuration file
2. **Type safety** - The config uses `as const` for type safety
3. **Environment variables** - Use for sensitive or environment-specific data
4. **Documentation** - Update this file when adding new configuration options
5. **Centralization** - Keep all configuration in one place

## Files Using Configuration

- `src/app/login/page.tsx` - Authentication page
- `src/app/about/page.tsx` - About page with team info
- `src/app/api-access/page.tsx` - API key management
- `src/app/projects/page.tsx` - Projects listing
- `src/app/projects/[id]/page.tsx` - Project detail with search
- `src/app/dashboard/page.tsx` - Main dashboard
- `src/app/analytics/page.tsx` - Analytics page

## Notes

- All grid opacity values are now consistent across pages
- API URLs are configured through environment variables
- Team member and feature information is easily updatable
- Confirmation messages are centralized for easy i18n in the future

