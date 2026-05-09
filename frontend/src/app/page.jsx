import ReportDashboard from "@/components/ReportDashboard";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-neutral-950 to-neutral-900 text-white selection:bg-emerald-500/30 overflow-x-hidden">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay pointer-events-none"></div>
      
      {/* Decorative background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-emerald-600/10 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none"></div>

      <div className="container mx-auto px-4 py-12 relative z-10 min-h-screen flex flex-col items-center">
        <header className="mb-12 text-center w-full max-w-4xl mx-auto">
          <div className="inline-flex items-center justify-center p-2 bg-emerald-500/10 rounded-2xl mb-4 border border-emerald-500/20 neon-glow">
            <span className="text-emerald-400 font-semibold text-sm tracking-wider uppercase">Nexus Analytics</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight mb-6 text-transparent bg-clip-text bg-gradient-to-r from-white via-gray-200 to-gray-400">
            Automated AI Report Generator
          </h1>
          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
            Upload your CSV or Excel data. Our AI agent instantly analyzes it, generates visualizations, and extracts key insights into a beautiful PDF report.
          </p>
        </header>

        <div className="flex-1 w-full max-w-6xl mx-auto">
          <ReportDashboard />
        </div>
      </div>
    </main>
  );
}
