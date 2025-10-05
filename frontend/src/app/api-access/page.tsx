'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { ArrowLeft, Key, Copy, RefreshCw, CheckCircle, AlertTriangle, Code, Loader2 } from 'lucide-react';

export default function ApiAccessPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [newApiKey, setNewApiKey] = useState('');
  const [rotating, setRotating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const handleRotateKey = async () => {
    if (!confirm('⚠️ This will invalidate your current API key. Any applications using it will stop working. Continue?')) {
      return;
    }

    try {
      setRotating(true);
      setError('');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/api-key/rotate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to rotate API key');
      }

      const data = await response.json();
      setNewApiKey(data.api_key);
    } catch (err: any) {
      console.error('Error rotating API key:', err);
      setError(err.message || 'Failed to rotate API key');
    } finally {
      setRotating(false);
    }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 relative overflow-hidden">
      {/* Animated gradient mesh background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-96 h-96 bg-gradient-to-br from-blue-400/30 to-cyan-400/30 rounded-full blur-3xl animate-blob"></div>
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-purple-400/30 to-pink-400/30 rounded-full blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-40 left-1/3 w-96 h-96 bg-gradient-to-br from-cyan-400/30 to-teal-400/30 rounded-full blur-3xl animate-blob animation-delay-4000"></div>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-gradient-to-br from-indigo-400/30 to-blue-400/30 rounded-full blur-3xl animate-blob animation-delay-6000"></div>
        
        <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/40 rounded-full animate-float"></div>
        <div className="absolute top-1/3 right-1/3 w-3 h-3 bg-purple-400/40 rounded-full animate-float animation-delay-1000"></div>
        <div className="absolute bottom-1/3 left-1/2 w-2 h-2 bg-cyan-400/40 rounded-full animate-float animation-delay-2000"></div>
        <div className="absolute top-2/3 right-1/4 w-2 h-2 bg-pink-400/40 rounded-full animate-float animation-delay-3000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-3 h-3 bg-teal-400/40 rounded-full animate-float animation-delay-4000"></div>
        
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:64px_64px]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),rgba(255,255,255,0))]"></div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-8 relative z-10">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/70 rounded-3xl shadow-lg p-6 mb-6 border border-white/60 hover:shadow-[0_20px_60px_-15px_rgba(59,130,246,0.3)] transition-all duration-500">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-blue-100/50 rounded-xl transition-all duration-300 hover:scale-110 active:scale-95"
            >
              <ArrowLeft className="w-6 h-6 text-blue-600" />
            </button>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-1">API Access</h1>
              <p className="text-blue-600/70 text-sm font-light tracking-wide">Manage your API key for programmatic access</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="backdrop-blur-xl bg-red-50/80 border border-red-300/50 text-red-700 px-4 py-3 rounded-xl mb-6">
            {error}
          </div>
        )}

        {/* Current Status */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-xl flex items-center justify-center shadow-lg">
              <Key className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">API Key Status</h2>
              <p className="text-sm text-gray-600">Your API key is active and ready to use</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-50/80 to-emerald-50/80 border border-green-300/50 rounded-xl p-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
            <div>
              <p className="font-semibold text-green-900">Active</p>
              <p className="text-xs text-green-700">
                API key was generated on {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                }) : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* New API Key Display */}
        {newApiKey && (
          <div className="backdrop-blur-xl bg-gradient-to-br from-amber-50/90 to-orange-50/90 rounded-2xl shadow-xl p-6 border border-amber-300/50 mb-6">
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-amber-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg font-bold text-amber-900 mb-1">⚠️ Save Your New API Key Now!</h3>
                <p className="text-sm text-amber-700">This is the only time you'll see this key. Copy it and store it securely.</p>
              </div>
            </div>
            
            <div className="bg-white/80 rounded-xl p-4 font-mono text-sm break-all text-gray-900 mb-3">
              {newApiKey}
            </div>

            <button
              onClick={() => handleCopy(newApiKey)}
              className="w-full bg-gradient-to-r from-amber-400 to-orange-400 hover:from-amber-500 hover:to-orange-500 text-white px-4 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
            >
              {copied ? <CheckCircle className="w-5 h-5" /> : <Copy className="w-5 h-5" />}
              {copied ? 'Copied!' : 'Copy API Key'}
            </button>
          </div>
        )}

        {/* Rotate API Key */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 mb-6">
          <div className="flex items-start gap-3 mb-4">
            <RefreshCw className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Rotate API Key</h2>
              <p className="text-sm text-gray-600 mb-4">
                Generate a new API key if your current key has been compromised or you need to revoke access.
              </p>
              <div className="bg-red-50/80 border border-red-300/50 rounded-xl p-3 mb-4">
                <p className="text-sm text-red-700 font-medium">⚠️ Warning: This action will immediately invalidate your current API key.</p>
              </div>
            </div>
          </div>

          <button
            onClick={handleRotateKey}
            disabled={rotating}
            className="w-full bg-gradient-to-r from-red-400 to-pink-400 hover:from-red-500 hover:to-pink-500 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {rotating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Rotating...
              </>
            ) : (
              <>
                <RefreshCw className="w-5 h-5" />
                Rotate API Key
              </>
            )}
          </button>
        </div>

        {/* Usage Documentation */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300">
          <div className="flex items-center gap-3 mb-4">
            <Code className="w-6 h-6 text-blue-600" />
            <h2 className="text-xl font-bold text-gray-900">How to Use Your API Key</h2>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Authentication Header</h3>
              <p className="text-sm text-gray-600 mb-2">Include your API key in the Authorization header:</p>
              <div className="bg-gray-900 rounded-xl p-4 font-mono text-sm text-green-400 overflow-x-auto">
                Authorization: Bearer YOUR_API_KEY
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Example Request (cURL)</h3>
              <div className="bg-gray-900 rounded-xl p-4 font-mono text-xs text-green-400 overflow-x-auto">
                curl -X GET "{process.env.NEXT_PUBLIC_API_URL}/auth/me" \<br/>
                &nbsp;&nbsp;-H "Authorization: Bearer YOUR_API_KEY"
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Example Request (Python)</h3>
              <div className="bg-gray-900 rounded-xl p-4 font-mono text-xs text-green-400 overflow-x-auto">
                import requests<br/><br/>
                headers = &#123;"Authorization": "Bearer YOUR_API_KEY"&#125;<br/>
                response = requests.get(<br/>
                &nbsp;&nbsp;"{process.env.NEXT_PUBLIC_API_URL}/auth/me",<br/>
                &nbsp;&nbsp;headers=headers<br/>
                )
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Example Request (JavaScript)</h3>
              <div className="bg-gray-900 rounded-xl p-4 font-mono text-xs text-green-400 overflow-x-auto">
                fetch('{process.env.NEXT_PUBLIC_API_URL}/auth/me', &#123;<br/>
                &nbsp;&nbsp;headers: &#123;<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;'Authorization': 'Bearer YOUR_API_KEY'<br/>
                &nbsp;&nbsp;&#125;<br/>
                &#125;)
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

