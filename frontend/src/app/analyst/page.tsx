"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, Send, Sparkles, User, FileText, Activity } from "lucide-react";

export default function AIAnalyst() {
  const [messages, setMessages] = useState([
    { role: "ai", content: "Hello! I am your AI Race Analyst. Ask me about telemetry, tire degradation, or race strategies for any driver or session." }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [story, setStory] = useState<string | null>(null);
  const [isGeneratingStory, setIsGeneratingStory] = useState(false);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input;
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await fetch("http://localhost:8000/analyst/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, context_race: "Monaco 2025", context_driver: "Max Verstappen" })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: "ai", content: data.reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "ai", content: "Sorry, I am currently offline or cannot connect to the backend." }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleGenerateStory = async () => {
    setIsGeneratingStory(true);
    try {
      const res = await fetch("http://localhost:8000/analyst/story?race_name=Monaco 2025", { method: "POST" });
      const data = await res.json();
      setStory(data.story);
    } catch (error) {
      setStory("Failed to generate race story. Ensure the backend is running.");
    } finally {
      setIsGeneratingStory(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 p-6 md:p-10 max-w-[1200px] mx-auto w-full h-[calc(100vh-80px)]">
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Sparkles className="text-blue-400" /> AI Race Analyst
          </h1>
          <p className="text-gray-400">Natural language insights powered by Gemini.</p>
        </div>
        <button 
          onClick={handleGenerateStory}
          disabled={isGeneratingStory}
          className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 text-sm border border-white/10 disabled:opacity-50"
        >
          {isGeneratingStory ? <Activity className="animate-pulse" size={16} /> : <FileText size={16} />}
          {isGeneratingStory ? "Generating..." : "Generate Race Story"}
        </button>
      </div>

      {story && (
        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 glass-panel p-6 rounded-xl border-l-4 border-blue-500"
        >
          <h3 className="font-bold mb-2 flex items-center gap-2"><FileText size={16}/> Auto-Generated Race Summary</h3>
          <p className="text-gray-300 leading-relaxed text-sm">{story}</p>
          <button onClick={() => setStory(null)} className="text-xs text-blue-400 mt-4 hover:underline">Dismiss</button>
        </motion.div>
      )}

      <div className="glass-panel flex-1 rounded-2xl flex flex-col overflow-hidden border border-white/10">
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${msg.role === "user" ? "bg-f1-red" : "bg-blue-600"}`}>
                  {msg.role === "user" ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div className={`p-4 rounded-2xl max-w-[80%] ${msg.role === "user" ? "bg-f1-red/20 border border-f1-red/30 rounded-tr-none" : "bg-white/5 border border-white/10 rounded-tl-none"}`}>
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                </div>
              </motion.div>
            ))}
            
            {isTyping && (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4"
              >
                <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center shrink-0">
                  <Bot size={20} />
                </div>
                <div className="p-4 rounded-2xl bg-white/5 border border-white/10 rounded-tl-none flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce"></span>
                  <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-75"></span>
                  <span className="w-2 h-2 rounded-full bg-gray-500 animate-bounce delay-150"></span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Input Area */}
        <div className="p-4 bg-black/40 border-t border-white/5">
          <form onSubmit={handleSendMessage} className="relative">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about Verstappen's tire wear in Sector 2..."
              className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-4 pr-14 outline-none focus:border-blue-500 transition-colors"
            />
            <button 
              type="submit"
              disabled={!input.trim() || isTyping}
              className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-blue-600 hover:bg-blue-500 rounded-lg flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Send size={18} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
