'use client';
import { useState, useEffect } from 'react';

interface IdeasData {
    ideas: string;
}

export default function Ideas() {
    const [ideas, setIdeas] = useState<string[]>([]);

    useEffect(() => {
        fetch('http://localhost:8000/ideas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ niche: 'fitness' }),
        })
            .then((res) => res.json() as Promise<IdeasData>)
            .then((data) => {
                const ideaList = data.ideas.split('\n').filter((line: string) => line.trim());
                setIdeas(ideaList);
            })
            .catch((error) => console.error('Error fetching ideas:', error));
    }, []);

    if (!ideas.length) return <div className="p-4">Loading...</div>;

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Content Ideas</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {ideas.map((idea, index) => (
                    <div key={index} className="p-4 bg-gray-100 rounded-lg shadow">
                        <p className="text-gray-800">{idea}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}