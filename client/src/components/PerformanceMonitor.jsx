import React, { useEffect, useState, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export default function PerformanceMonitor() {
    const [metrics, setMetrics] = useState([]);
    const ws = useRef(null);

    useEffect(() => {
        ws.current = new WebSocket('ws://localhost:8000/ws/metrics');
        
        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setMetrics(prev => [...prev, { ...data, timestamp: new Date() }]
                .slice(-30));
        };

        return () => ws.current.close();
    }, []);

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-4">Real-time Performance Metrics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-2">CPU Usage</h3>
                    <LineChart width={400} height={200} data={metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="cpu" stroke="#8884d8" />
                    </LineChart>
                </div>

                <div className="bg-white p-4 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-2">Memory Usage</h3>
                    <LineChart width={400} height={200} data={metrics}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="memory" stroke="#82ca9d" />
                    </LineChart>
                </div>
            </div>
        </div>
    );
}