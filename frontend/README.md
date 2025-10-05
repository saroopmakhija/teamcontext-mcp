# TeamContext Frontend

A modern Next.js frontend for the TeamContext application with authentication and user management.

## Features

- **Modern UI**: Built with Next.js 15, TypeScript, and Tailwind CSS
- **Authentication**: Login and registration with backend API integration
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Validation**: Client-side form validation with helpful error messages
- **Secure Authentication**: Integrates with backend JWT token system
- **API Key Management**: Displays API keys securely after registration

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Context API

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend server running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Update `.env.local` with your backend URL:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/
│   ├── login/
│   │   └── page.tsx          # Login/Registration page
│   ├── dashboard/
│   │   └── page.tsx          # User dashboard
│   ├── layout.tsx            # Root layout with AuthProvider
│   └── page.tsx              # Home page (redirects to login)
├── contexts/
│   └── AuthContext.tsx       # Authentication context
├── lib/
│   └── api.ts                # API client configuration
└── types/
    └── auth.ts               # TypeScript type definitions
```

## API Integration

The frontend integrates with these backend endpoints:

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/api-key/rotate` - Rotate API key

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Features

### Authentication
- **Login**: Email and password authentication
- **Registration**: Create new accounts with name, email, and password
- **Logout**: Secure logout with token cleanup
- **Session Management**: Automatic token refresh and session persistence

### User Interface
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Modern UI**: Clean, professional interface with smooth animations
- **Form Validation**: Real-time validation with helpful error messages
- **Loading States**: Visual feedback during API calls
- **Error Handling**: User-friendly error messages

### Security
- **HTTP-only Cookies**: JWT tokens stored securely
- **Input Validation**: Client and server-side validation
- **API Key Protection**: Secure display of API keys
- **CORS Support**: Proper cross-origin request handling

## Development

### Adding New Pages
1. Create a new folder in `src/app/`
2. Add a `page.tsx` file
3. Use the `useAuth` hook for authentication state

### API Calls
Use the `authAPI` object from `src/lib/api.ts` for backend communication:

```typescript
import { authAPI } from '@/lib/api';

// Login user
const response = await authAPI.login({ email, password });

// Register user
const response = await authAPI.register({ name, email, password });
```

### Styling
The project uses Tailwind CSS for styling. Customize the design by modifying:
- `src/app/globals.css` - Global styles
- Component files - Inline Tailwind classes
- `tailwind.config.js` - Tailwind configuration

## Deployment

### Build for Production
```bash
npm run build
```

### Environment Variables for Production
Set the following environment variables in your production environment:
- `NEXT_PUBLIC_API_URL` - Your production API URL

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure your backend has CORS enabled for your frontend domain
2. **API Connection**: Verify the `NEXT_PUBLIC_API_URL` is correct
3. **Authentication**: Check that JWT tokens are being set as HTTP-only cookies
4. **Build Errors**: Run `npm run lint` to check for TypeScript errors

### Debug Mode
Enable debug logging by adding `console.log` statements in the API client or context files.