# Vercel Deployment Guide

## Prerequisites
- Vercel account (sign up at https://vercel.com)
- Your backend API deployed and accessible

## Deployment Steps

### 1. Install Vercel CLI (Optional)
```bash
npm i -g vercel
```

### 2. Environment Variables
Before deploying, set up your environment variables in Vercel:

**Required Variables:**
- `NEXT_PUBLIC_API_URL` - Your backend API URL (e.g., `https://your-api.com/api/v1`)

### 3. Deploy via Vercel Dashboard (Recommended)

1. Go to https://vercel.com and sign in
2. Click "Add New Project"
3. Import your Git repository
4. Vercel will auto-detect Next.js
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

6. Add environment variables:
   - Go to "Environment Variables"
   - Add `NEXT_PUBLIC_API_URL` with your backend URL
   - Click "Deploy"

### 4. Deploy via CLI (Alternative)

```bash
cd frontend
vercel
```

Follow the prompts and add environment variables when asked.

### 5. Configure Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Configuration Files

### next.config.ts
The Next.js configuration is already optimized for Vercel deployment.

### package.json
Build scripts are configured for standard Next.js (no Turbopack).

## Post-Deployment

### 1. Test the Deployment
- Visit your Vercel deployment URL
- Test login/registration
- Verify API connection
- Check all pages load correctly

### 2. Monitor Deployments
- Vercel provides automatic deployment previews for PRs
- Production deployments happen on main branch commits
- View logs and analytics in Vercel dashboard

## Troubleshooting

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Ensure backend allows CORS from your Vercel domain
- Check backend is accessible from Vercel's servers

### Build Failures
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify no TypeScript/ESLint errors locally

### Environment Variables
- Remember: `NEXT_PUBLIC_` prefix makes variables accessible client-side
- Changes to environment variables require redeployment

## Vercel Configuration Options

### vercel.json (Optional)
You can create a `vercel.json` file for advanced configuration:

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install",
  "framework": "nextjs",
  "outputDirectory": ".next"
}
```

## Performance

Vercel optimizes Next.js automatically:
- ✅ Automatic code splitting
- ✅ Image optimization
- ✅ Edge caching
- ✅ Serverless functions
- ✅ Automatic HTTPS

## Updates

To deploy updates:
1. Push code to your Git repository
2. Vercel automatically builds and deploys
3. Preview deployments for branches
4. Production deployment for main branch

## Support

- Vercel Documentation: https://vercel.com/docs
- Next.js Documentation: https://nextjs.org/docs
- Vercel Support: https://vercel.com/support

