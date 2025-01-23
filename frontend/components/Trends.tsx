'use client'; // Client-side for Chart.js
import { useState, useEffect } from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import type { ChartData } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

interface SentimentCounts {
    POSITIVE: number;
    NEGATIVE: number;
    NEUTRAL: number;
}

interface TrendsData {
    trends: string;
    sentiment_counts: SentimentCounts;
}

// ...existing code...
export default function Trends() {
    const [data, setData] = useState<ChartData<'pie', number[], string> | null>(null);
    const [trends, setTrends] = useState<string>(''); // Add this line

    useEffect(() => {
        fetch('http://localhost:8000/trends', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ niche: 'fitness' }),
        })
            .then((res) => res.json() as Promise<TrendsData>)
            .then((data) => {
                setData({
                    labels: ['Positive', 'Negative', 'Neutral'],
                    datasets: [
                        {
                            data: [
                                data.sentiment_counts.POSITIVE,
                                data.sentiment_counts.NEGATIVE,
                                data.sentiment_counts.NEUTRAL,
                            ],
                            backgroundColor: ['#4CAF50', '#F44336', '#9E9E9E'],
                            borderColor: ['#FFFFFF', '#FFFFFF', '#FFFFFF'],
                            borderWidth: 1,
                        },
                    ],
                });
                setTrends(data.trends); // Store trends string
            })
            .catch((error) => console.error('Error fetching trends:', error));
    }, []);

    if (!data) return <div className="p-4">Loading...</div>;

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Trends for Fitness</h2>
            <div className="w-full max-w-md">
                <Pie data={data} />
            </div>
            <p className="mt-4 text-gray-700">{trends}</p> {/* Use trends here */}
        </div>
    );
}
// ...existing code...