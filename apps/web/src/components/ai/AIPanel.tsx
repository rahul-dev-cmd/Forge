"use client";

import * as React from "react";
import { X, Sparkles, Send, Mic, Paperclip, FileCode, CheckCircle, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";
import { useWorkspaceStore } from "@/store/workspaceStore";

interface Message {
  id: string;
  sender: "user" | "bot";
  text: string;
  attachment?: {
    name: string;
    size: string;
    type: string;
  };
}

export function AIPanel() {
  const { aiPanelOpen, toggleAiPanel } = useWorkspaceStore();
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: "msg-1",
      sender: "bot",
      text: "Hey Rahul! Need answers or help with your repository? I've got you covered! Let's dive into making things happen.",
    },
    {
      id: "msg-2",
      sender: "user",
      text: "Explain the repository structure and primary entry point for routing.",
    },
    {
      id: "msg-3",
      sender: "bot",
      text: "The monorepo uses Turborepo. The core frontend app is located in `apps/web/`, which handles Next.js App routing. All landing logic redirects directly to the `/dashboard` workspace.",
      attachment: {
        name: "pnpm-workspace.yaml",
        size: "90 B",
        type: "YAML Contract",
      },
    },
  ]);
  const [inputText, setInputText] = React.useState("");
  const [isTyping, setIsTyping] = React.useState(false);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const suggestedPrompts = [
    "Verify auth complexity",
    "Review DB schemas",
    "List OAuth endpoints",
  ];

  // Scroll to bottom when messages load
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `msg-user-${Date.now()}`,
      sender: "user",
      text: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText("");
    setIsTyping(true);

    // Simulate AI response delay
    setTimeout(() => {
      let botText = "";
      let botAttach = undefined;

      if (text.toLowerCase().includes("auth")) {
        botText = "I examined `apps/web/src/middleware.ts`. Complex conditional scopes are nesting login logic. I recommend isolating routing rules into helper validation utilities.";
      } else if (text.toLowerCase().includes("schema") || text.toLowerCase().includes("db")) {
        botText = "Found `schema-db` connected. The primary schema layout utilizes PostgreSQL schemas. I index-analyzed tables and drafted queries for optimization.";
        botAttach = {
          name: "schema.prisma",
          size: "4.2 KB",
          type: "Database Model",
        };
      } else {
        botText = `Understood. I scanned the project workspace. Let me know if you would like me to draft structural templates or explore specific components for "${text}".`;
      }

      const botMsg: Message = {
        id: `msg-bot-${Date.now()}`,
        sender: "bot",
        text: botText,
        attachment: botAttach,
      };

      setMessages((prev) => [...prev, botMsg]);
      setIsTyping(false);
    }, 1200);
  };

  if (!aiPanelOpen) return null;

  return (
    <aside
      className={cn(
        "w-[360px] h-[calc(100vh-32px)] fixed right-4 top-4 bottom-4 bg-surface border border-border rounded-xl flex flex-col justify-between py-5 select-none z-30 shadow-xs transition-all duration-300 ease-in-out",
        // Responsive Coordinates
        "max-lg:fixed max-lg:right-4 max-lg:top-4 max-lg:bottom-4 max-lg:z-50 max-lg:shadow-xl max-lg:w-[320px] max-md:left-4 max-md:w-auto"
      )}
    >
      {/* Header */}
      <div className="px-4 pb-3 border-b border-border/60 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-blue-600/10 border border-blue-600/20 text-blue-600 flex items-center justify-center shadow-3xs">
            <Sparkles className="w-4 h-4 animate-pulse" />
          </div>
          <div className="flex flex-col text-left">
            <span className="text-xs font-bold text-foreground">AI Copilot</span>
            <span className="text-[9px] text-muted-foreground leading-none">Ready to assist</span>
          </div>
        </div>
        <button
          onClick={toggleAiPanel}
          className="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground cursor-pointer transition-colors"
          title="Close Copilot"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-grow overflow-y-auto px-4 py-4 flex flex-col gap-4">
        {messages.map((msg) => {
          const isBot = msg.sender === "bot";
          return (
            <div key={msg.id} className="flex flex-col gap-1.5">
              <div
                className={cn(
                  "p-3 text-xs leading-relaxed max-w-[85%] shadow-3xs border",
                  isBot
                    ? "self-start bg-muted/30 text-foreground rounded-2xl rounded-tl-none border-border/40"
                    : "self-end bg-blue-600 text-white rounded-2xl rounded-tr-none border-blue-700"
                )}
              >
                {msg.text}
              </div>

              {/* Message attachments rendering */}
              {isBot && msg.attachment && (
                <div className="p-2.5 rounded-lg border border-border bg-surface flex items-center justify-between gap-3 max-w-[85%] self-start shadow-3xs">
                  <div className="flex items-center gap-2 overflow-hidden">
                    <div className="w-7.5 h-7.5 rounded bg-success/15 border border-success/20 flex items-center justify-center text-success shrink-0">
                      <FileCode className="w-4 h-4" />
                    </div>
                    <div className="flex flex-col overflow-hidden text-left">
                      <span className="text-[9px] font-black text-foreground truncate leading-none">
                        {msg.attachment.name}
                      </span>
                      <span className="text-[8px] text-muted-foreground font-mono mt-0.5 leading-none">
                        {msg.attachment.size} • {msg.attachment.type}
                      </span>
                    </div>
                  </div>
                  <CheckCircle className="w-4 h-4 text-success shrink-0" />
                </div>
              )}
            </div>
          );
        })}

        {/* Loading/Typing visualizer */}
        {isTyping && (
          <div className="flex items-center gap-1.5 self-start p-3 bg-muted/30 border border-border/40 text-xs text-muted-foreground rounded-2xl rounded-tl-none max-w-[80%] shadow-3xs">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Scanning project workspace...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Footer Area: Suggested Prompts & Input */}
      <div className="px-4 pt-3 border-t border-border/60 flex flex-col gap-2">
        {/* Prompt Chips */}
        <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
          {suggestedPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSendMessage(prompt)}
              className="text-[9px] font-bold text-muted-foreground hover:text-foreground bg-muted/50 hover:bg-muted px-2 py-1 rounded-md border border-border/65 whitespace-nowrap cursor-pointer transition-all select-none"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input box */}
        <div className="relative flex items-center border border-border rounded-lg bg-muted/15 p-1 group shadow-3xs hover:border-border/80 transition-colors">
          <button className="p-2 rounded hover:bg-muted text-muted-foreground cursor-pointer shrink-0">
            <Paperclip className="w-4 h-4" />
          </button>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && inputText.trim()) {
                handleSendMessage(inputText);
              }
            }}
            placeholder="Ask Copilot something..."
            className="w-full h-8 bg-transparent border-none outline-none text-xs px-2 placeholder:text-muted-foreground shrink min-w-0"
          />
          <button className="p-2 rounded hover:bg-muted text-muted-foreground cursor-pointer shrink-0 max-sm:hidden">
            <Mic className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleSendMessage(inputText)}
            className="p-2 rounded bg-blue-600 hover:bg-blue-600/90 text-white cursor-pointer shadow-3xs shrink-0"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
export default AIPanel;
