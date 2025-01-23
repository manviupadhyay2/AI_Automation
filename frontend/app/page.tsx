import Trends from '@/components/Trends';
import Ideas from '@/components/Ideas';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white p-4 text-center">
        <h1 className="text-3xl font-bold">Social Trend Analyzer</h1>
      </header>
      <main className="p-4">
        <Trends />
        <Ideas />
      </main>
    </div>
  );
}