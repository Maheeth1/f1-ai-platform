"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Activity, BrainCircuit, LineChart, Cpu, Trophy, Zap } from "lucide-react";

export default function Home() {
  const features = [
    {
      title: "Real-time Telemetry",
      description: "Dive deep into throttle, braking, and speed traces across every corner.",
      icon: <Activity className="text-f1-red" size={24} />,
    },
    {
      title: "Predictive Analytics",
      description: "Machine learning models forecasting lap times, tire degradation, and race outcomes.",
      icon: <BrainCircuit className="text-f1-red" size={24} />,
    },
    {
      title: "Interactive Track Maps",
      description: "Visualize drivers on physical track coordinates with speed and sector heatmaps.",
      icon: <LineChart className="text-f1-red" size={24} />,
    },
    {
      title: "Strategy Simulator",
      description: "Run Monte Carlo simulations to find the optimal pit window and tire sequence.",
      icon: <Cpu className="text-f1-red" size={24} />,
    },
    {
      title: "Driver Comparison",
      description: "Overlay delta times and sector performances to see exactly where time was won or lost.",
      icon: <Trophy className="text-f1-red" size={24} />,
    },
    {
      title: "AI Race Analyst",
      description: "Ask natural language questions about race events and get instant, data-backed insights.",
      icon: <Zap className="text-f1-red" size={24} />,
    },
  ];

  return (
    <div className="flex flex-col flex-1">
      {/* Hero Section */}
      <section className="relative flex-1 flex items-center justify-center min-h-[80vh] overflow-hidden px-6">
        {/* Background Gradients */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-f1-red/10 rounded-full blur-[120px]" />
          <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-500/5 rounded-full blur-[100px]" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6">
              AI-Powered <br className="hidden md:block" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-f1-red to-red-400">
                Formula 1
              </span>{" "}
              Race Intelligence
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="text-lg md:text-xl text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed"
          >
            A professional-grade analytics dashboard combining historical telemetry, machine learning predictions, and AI-generated insights for the ultimate motorsport engineering experience.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Link
              href="/dashboard"
              className="bg-f1-red hover:bg-f1-red-hover text-white px-8 py-4 rounded-full font-bold text-lg transition-all hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(225,6,0,0.4)] flex items-center gap-2"
            >
              Enter Dashboard <Activity size={20} />
            </Link>
            <button className="glass hover:bg-white/10 px-8 py-4 rounded-full font-bold text-lg transition-all text-white">
              View Documentation
            </button>
          </motion.div>
        </div>
      </section>

      {/* Feature Showcase */}
      <section className="py-24 px-6 border-t border-white/5 relative z-10 bg-black/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Engineering-Grade Capabilities</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Explore data like a real trackside engineer with our comprehensive suite of intelligence modules.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: idx * 0.1 }}
                className="glass-panel p-8 rounded-2xl group hover:border-f1-red/30 transition-colors"
              >
                <div className="w-12 h-12 rounded-xl bg-f1-red/10 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Live Stats Ticker placeholder */}
      <div className="w-full bg-f1-red text-white py-3 overflow-hidden whitespace-nowrap border-y border-white/10 flex items-center">
        <div className="animate-marquee flex gap-12 text-sm font-bold tracking-widest uppercase">
          <span>Verstappen Wins Monaco</span>
          <span>•</span>
          <span>Leclerc Secures Pole</span>
          <span>•</span>
          <span>McLaren Updates Aero Package</span>
          <span>•</span>
          <span>Predictive Model Accuracy: 94.2%</span>
          <span>•</span>
          <span>Verstappen Wins Monaco</span>
          <span>•</span>
          <span>Leclerc Secures Pole</span>
        </div>
      </div>
    </div>
  );
}
