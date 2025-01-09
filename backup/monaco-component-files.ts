// src/components/ui/card.tsx
import * as React from "react"

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={className}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={className}
      {...props}
    />
  )
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={className}
      {...props}
    />
  )
)
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={className}
      {...props}
    />
  )
)
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }

// src/components/ui/dashboard.tsx
import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './card';
import { Trophy, Target, CheckCircle, XCircle } from 'lucide-react';

const TeamDashboard = () => {
  const [goals] = useState([
    { id: 1, title: 'Increase Sales by 20%', deadline: '2024-12-31', completed: false },
    { id: 2, title: 'Launch New Product Line', deadline: '2024-06-30', completed: true },
    { id: 3, title: 'Reduce Customer Churn', deadline: '2024-09-30', completed: false },
    { id: 4, title: 'Expand to New Market', deadline: '2024-08-15', completed: false },
  ]);

  const [rankings] = useState([
    { id: 1, team: 'Alpha Team', score: 95, trend: 'up' },
    { id: 2, team: 'Beta Team', score: 88, trend: 'down' },
    { id: 3, team: 'Gamma Team', score: 82, trend: 'up' },
    { id: 4, team: 'Delta Team', score: 78, trend: 'stable' },
  ]);

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#E4CEFD' }}>
      <div className="max-w-6xl mx-auto mb-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-xl overflow-hidden" style={{ backgroundColor: '#560FE4' }}>
            <div className="w-full h-full p-2 flex flex-col justify-center items-center">
              <div className="flex gap-1 mb-1">
                <div className="w-3 h-6 bg-white rounded-sm" />
                <div className="w-6 h-6 flex flex-wrap gap-0.5">
                  <div className="w-2.5 h-2.5 bg-white rounded-full" />
                  <div className="w-2.5 h-2.5 bg-white rounded-full" />
                  <div className="w-2.5 h-2.5 bg-white rounded-full" />
                  <div className="w-2.5 h-2.5 bg-white rounded-full" />
                </div>
              </div>
              <span className="text-white text-xs font-bold">MONACO</span>
            </div>
          </div>
          <h1 className="text-3xl font-bold" style={{ color: '#220484' }}>Team Performance Dashboard</h1>
        </div>
      </div>
      
      <div className="max-w-6xl mx-auto space-y-6">
        <Card className="border-2" style={{ borderColor: '#560FE4' }}>
          <CardHeader className="bg-white">
            <CardTitle className="flex items-center gap-2" style={{ color: '#560FE4' }}>
              <Trophy style={{ color: '#A46CF6' }} />
              Team Rankings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {rankings.map((rank, index) => (
                <div 
                  key={rank.id} 
                  className="flex items-center justify-between p-4 rounded-lg"
                  style={{ backgroundColor: '#F8F5FF' }}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-xl font-bold" style={{ color: '#420AC4' }}>#{index + 1}</span>
                    <span className="font-medium" style={{ color: '#3107A4' }}>{rank.team}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold" style={{ color: '#560FE4' }}>{rank.score}</span>
                    <span className={`text-sm ${
                      rank.trend === 'up' ? 'text-green-500' : 
                      rank.trend === 'down' ? 'text-red-500' : 
                      'text-gray-500'
                    }`}>
                      {rank.trend === 'up' ? '↑' : rank.trend === 'down' ? '↓' : '→'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="border-2" style={{ borderColor: '#560FE4' }}>
          <CardHeader className="bg-white">
            <CardTitle className="flex items-center gap-2" style={{ color: '#560FE4' }}>
              <Target style={{ color: '#A46CF6' }} />
              Team Goals
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              {goals.map((goal) => (
                <div 
                  key={goal.id} 
                  className="flex items-center justify-between p-4 rounded-lg"
                  style={{ backgroundColor: '#F8F5FF' }}
                >
                  <div className="flex items-center gap-4">
                    {goal.completed ? (
                      <CheckCircle style={{ color: '#A5E004' }} />
                    ) : (
                      <XCircle style={{ color: '#F23535' }} />
                    )}
                    <div>
                      <h3 className="font-medium" style={{ color: '#3107A4' }}>{goal.title}</h3>
                      <p className="text-sm" style={{ color: '#420AC4' }}>Due: {goal.deadline}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    goal.completed ? 'bg-[#F5FDCB] text-[#436B00]' : 'bg-[#E4CEFD] text-[#220484]'
                  }`}>
                    {goal.completed ? 'Completed' : 'In Progress'}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TeamDashboard;

// src/app/page.tsx
import TeamDashboard from '@/components/ui/dashboard';

export default function Home() {
  return <TeamDashboard />;
}

// src/app/layout.tsx
import '@/styles/globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Monaco Dashboard',
  description: 'Team Performance Dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

// src/styles/globals.css
@tailwind base;
@tailwind components;
@tailwind utilities;
