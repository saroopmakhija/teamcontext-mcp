'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft, Users, Zap, Shield, Code, Linkedin } from 'lucide-react';
import { APP_CONFIG, TEAM_MEMBERS, FEATURES, TECH_STACK } from '@/config/constants';

export default function AboutPage() {
  const router = useRouter();

  const featuresWithIcons = FEATURES.map((feature, index) => ({
    ...feature,
    icon: [Zap, Shield, Code][index],
  }));

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
        
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808018_1px,transparent_1px),linear-gradient(to_bottom,#80808018_1px,transparent_1px)] bg-[size:64px_64px]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),rgba(255,255,255,0))]"></div>
      </div>

      <div className="max-w-6xl mx-auto px-8 py-8 relative z-10">
        {/* Header */}
        <div className="backdrop-blur-xl bg-white/70 rounded-3xl shadow-lg p-6 mb-8 border border-white/60 hover:shadow-[0_20px_60px_-15px_rgba(59,130,246,0.3)] transition-all duration-500">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="p-2 hover:bg-blue-100/50 rounded-xl transition-all duration-300 hover:scale-110 active:scale-95"
            >
              <ArrowLeft className="w-6 h-6 text-blue-600" />
            </button>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent mb-1">About {APP_CONFIG.name}</h1>
              <p className="text-blue-600/70 text-sm font-light tracking-wide">{APP_CONFIG.fullName} for Modern Teams</p>
            </div>
          </div>
        </div>

        {/* Project Description */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-8 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">What is {APP_CONFIG.name}?</h2>
          <div className="space-y-4 text-gray-700 leading-relaxed">
            <p className="text-lg">
              <span className="font-bold text-blue-600">{APP_CONFIG.name} ({APP_CONFIG.fullName})</span> is a cutting-edge context management platform designed to revolutionize how teams share, retrieve, and collaborate on knowledge.
            </p>
            <p>
              In today&apos;s fast-paced development environment, teams struggle with scattered documentation, lost context, and inefficient knowledge sharing. {APP_CONFIG.name} solves this by providing a centralized, intelligent platform where your team&apos;s collective knowledge is always accessible, searchable, and up-to-date.
            </p>
            <p>
              Built with modern technologies including <span className="font-semibold">Next.js</span>, <span className="font-semibold">FastAPI</span>, <span className="font-semibold">MongoDB</span>, and <span className="font-semibold">AI-powered semantic search</span>, {APP_CONFIG.name} combines the power of traditional databases with advanced retrieval systems to provide context-aware, intelligent responses to your team&apos;s queries.
            </p>
            <p className="text-lg font-semibold text-blue-600">
              Whether you&apos;re building software, managing projects, or collaborating across teams, {APP_CONFIG.name} ensures that critical information is never more than a search away.
            </p>
          </div>
        </div>

        {/* Key Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {featuresWithIcons.map((feature, index) => (
            <div
              key={index}
              className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-2 hover:scale-[1.02] group"
            >
              <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-all duration-300`}>
                <feature.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-gray-600 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Tech Stack */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-8 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Tech Stack</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {TECH_STACK.map((tech, index) => (
              <div
                key={index}
                className={`bg-gradient-to-br ${tech.color} text-white p-4 rounded-xl text-center font-bold shadow-lg hover:scale-105 transition-all duration-300`}
              >
                {tech.name}
              </div>
            ))}
          </div>
        </div>

        {/* Team Section */}
        <div className="backdrop-blur-xl bg-white/70 rounded-2xl shadow-lg p-8 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300">
          <div className="flex items-center gap-3 mb-6">
            <Users className="w-8 h-8 text-blue-600" />
            <h2 className="text-3xl font-bold text-gray-900">Meet the Team</h2>
          </div>
          <p className="text-gray-600 mb-8">
            {APP_CONFIG.name} is brought to you by a team of passionate developers and designers committed to revolutionizing team collaboration.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {TEAM_MEMBERS.map((member, index) => (
              <div
                key={index}
                className="backdrop-blur-xl bg-white/80 rounded-2xl shadow-lg p-6 border border-white/60 hover:shadow-[0_20px_50px_-15px_rgba(59,130,246,0.4)] transition-all duration-300 hover:-translate-y-2 hover:scale-[1.05] group text-center"
              >
                <div className={`w-20 h-20 bg-gradient-to-br ${member.color} rounded-full flex items-center justify-center mx-auto mb-4 shadow-xl group-hover:scale-110 transition-all duration-300`}>
                  <span className="text-3xl font-bold text-white">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{member.name}</h3>
                
                {/* LinkedIn URL - appears on hover */}
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <a
                    href={member.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    <Linkedin className="w-4 h-4" />
                    LinkedIn Profile
                  </a>
                </div>
              </div>
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}

