import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Activity, CreditCard, Key, Users, Settings, Bell, Database, Clock } from 'lucide-react';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const usageData = [
    { month: 'Jan', requests: 45000, cost: 150 },
    { month: 'Feb', requests: 52000, cost: 180 },
    { month: 'Mar', requests: 61000, cost: 210 },
    { month: 'Apr', requests: 85000, cost: 280 },
  ];

  return (
    <div className="p-6 space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="bg-white">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center">
              <Activity className="w-4 h-4 mr-2 text-blue-500" />
              API Requests
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">85,000</div>
            <p className="text-xs text-gray-500">+12.5% from last month</p>
          </CardContent>
        </Card>
        
        {/* Additional cards and content */}
      </div>
    </div>
  );