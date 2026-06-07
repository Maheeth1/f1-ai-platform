import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Activity, LayoutDashboard, Map, Settings, History, Users } from "lucide-react";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "F1 AI Race Intelligence",
  description: "Advanced Formula 1 analytics, telemetry, and race prediction platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${outfit.variable} antialiased min-h-screen flex flex-col`}>
        <nav className="glass sticky top-0 z-50 px-6 py-4 flex items-center justify-between border-b border-white/5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-f1-red flex items-center justify-center text-white font-bold italic">F1</div>
            <span className="font-bold text-xl tracking-tight">AI Intelligence</span>
          </div>
          
          <div className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Activity size={16} /> Home
            </Link>
            <Link href="/dashboard" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <LayoutDashboard size={16} /> Analytics
            </Link>
            <Link href="/track" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Map size={16} /> Track Maps
            </Link>
            <Link href="/comparison" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Users size={16} /> Drivers
            </Link>
            <Link href="/simulation" className="text-sm font-medium text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <Settings size={16} /> Simulator
            </Link>
            <Link href="/analyst" className="text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2">
              <Activity size={16} /> AI Analyst
            </Link>
          </div>
          
          <div>
            <button className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded text-sm font-medium transition-colors border border-white/10">
              Sign In
            </button>
          </div>
        </nav>
        
        <main className="flex-1 flex flex-col">
          {children}
        </main>
      </body>
    </html>
  );
}
