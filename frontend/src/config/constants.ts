// Application Configuration Constants
// This file contains all configurable constants for the frontend

export const APP_CONFIG = {
  // Application Info
  name: 'D-RAG',
  fullName: 'Dynamic Retrieval-Augmented Generation',
  description: 'Manage your team\'s context and knowledge sharing',
  tagline: 'Share context across your team',

  // Validation Rules
  validation: {
    minNameLength: 2,
    minPasswordLength: 6,
  },

  // Timeouts (in milliseconds)
  timeouts: {
    loginRedirect: 1000,
    registerMessageDisplay: 5000,
    copyNotification: 2000,
  },

  // UI Constants
  ui: {
    gridOpacity: '18', // hex opacity value (00-ff)
    chatHeight: '600px',
  },

  // Search Defaults
  search: {
    similarityThreshold: 0.5,
    defaultLimit: 10,
  },

  // Messages
  messages: {
    confirmDeleteProject: 'This action cannot be undone',
    confirmRemoveContributor: 'Are you sure you want to remove this contributor?',
    confirmRotateApiKey: '⚠️ This will invalidate your current API key. Any applications using it will stop working. Continue?',
    editFeatureComingSoon: 'Edit feature coming soon!',
  },
} as const;

export const TEAM_MEMBERS = [
  {
    name: 'Saroop Makhija',
    color: 'from-blue-400 to-cyan-400',
    linkedin: 'https://www.linkedin.com/in/saroopmakhija/',
  },
  {
    name: 'Meet Patel',
    color: 'from-orange-400 to-red-400',
    linkedin: 'https://www.linkedin.com/in/meet-patel-b2a289276/',
  },
  {
    name: 'Arav Mehta',
    color: 'from-emerald-400 to-teal-400',
    linkedin: 'https://www.linkedin.com/in/aravmehta/',
  },
  {
    name: 'Aiman Koli',
    color: 'from-purple-400 to-pink-400',
    linkedin: 'https://www.linkedin.com/in/aiman-koli-a71638238/',
  },
] as const;

export const FEATURES = [
  {
    title: 'Lightning Fast',
    description: 'Built with modern tech stack for optimal performance and speed',
    color: 'from-yellow-400 to-orange-400',
  },
  {
    title: 'Secure & Private',
    description: 'Enterprise-grade security with API key authentication and JWT tokens',
    color: 'from-green-400 to-emerald-400',
  },
  {
    title: 'Developer Friendly',
    description: 'RESTful API with comprehensive documentation and code examples',
    color: 'from-blue-400 to-indigo-400',
  },
] as const;

export const TECH_STACK = [
  { name: 'Next.js 15', color: 'from-gray-800 to-gray-900' },
  { name: 'FastAPI', color: 'from-green-500 to-teal-500' },
  { name: 'MongoDB', color: 'from-green-600 to-emerald-600' },
  { name: 'TypeScript', color: 'from-blue-600 to-blue-700' },
  { name: 'Tailwind CSS', color: 'from-cyan-500 to-blue-500' },
  { name: 'Framer Motion', color: 'from-purple-500 to-pink-500' },
  { name: 'JWT Auth', color: 'from-orange-500 to-red-500' },
  { name: 'AI/ML', color: 'from-indigo-500 to-purple-600' },
] as const;

