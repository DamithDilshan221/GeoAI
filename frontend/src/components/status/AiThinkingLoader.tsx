export function AiThinkingLoader({ message = 'Thinking' }: { message?: string }) {
  const cleanMessage = message.replace(/\.+$/, '') || 'Thinking';
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-6 text-center animate-fade-in select-none">
      {/* Ambient background glow */}
      <div className="relative flex items-center justify-center">
        <div className="absolute w-48 h-48 rounded-full bg-blue-500/20 blur-3xl animate-pulse pointer-events-none" />
        <div className="absolute w-32 h-32 rounded-full bg-cyan-400/20 blur-2xl animate-pulse delay-300 pointer-events-none" />

        {/* AI Sparkle + Thinking container */}
        <div className="relative z-10 flex items-center gap-4.5 px-6 py-4 rounded-3xl glass-panel border border-white/20 shadow-[0_12px_40px_rgba(37,99,235,0.25)]">
          {/* AI Sparkles Multi-Star Badge */}
          <div className="relative shrink-0 w-16 h-16 flex items-center justify-center animate-bounce-subtle">
            <svg
              viewBox="0 0 70 70"
              className="w-full h-full drop-shadow-[0_0_16px_rgba(6,182,212,0.6)]"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="aiSparkleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#1E40AF" />
                  <stop offset="45%" stopColor="#2563EB" />
                  <stop offset="85%" stopColor="#06B6D4" />
                  <stop offset="100%" stopColor="#38BDF8" />
                </linearGradient>
                <linearGradient id="aiAccentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3B82F6" />
                  <stop offset="100%" stopColor="#06B6D4" />
                </linearGradient>
              </defs>

              {/* Top-Left Small Star */}
              <path
                d="M 14,8 C 14.8,11.5 15.5,13.2 19,14 C 15.5,14.8 14.8,16.5 14,20 C 13.2,16.5 12.5,14.8 9,14 C 12.5,13.2 13.2,11.5 14,8 Z"
                fill="url(#aiAccentGrad)"
                className="animate-pulse"
              />

              {/* Top-Right Medium Star */}
              <path
                d="M 52,6 C 53.2,11 54.5,13.8 60,15 C 54.5,16.2 53.2,19 52,24 C 50.8,19 49.5,16.2 44,15 C 49.5,13.8 50.8,11 52,6 Z"
                fill="url(#aiAccentGrad)"
                className="animate-pulse delay-150"
              />

              {/* Center Main Sparkle Star */}
              <path
                d="M 35,4 C 37,20.5 40.5,28.5 61,31 C 40.5,33.5 37,41.5 35,58 C 33,41.5 29.5,33.5 9,31 C 29.5,28.5 33,20.5 35,4 Z"
                fill="url(#aiSparkleGrad)"
                stroke="rgba(255,255,255,0.4)"
                strokeWidth="0.8"
              />

              {/* Clean 'AI' Text Inscription */}
              <text
                x="35"
                y="33.5"
                fill="#FFFFFF"
                fontFamily="'Inter', system-ui, -apple-system, sans-serif"
                fontWeight="900"
                fontSize="12.5"
                textAnchor="middle"
                dominantBaseline="middle"
                letterSpacing="-0.5px"
                className="drop-shadow-[0_1px_2px_rgba(0,0,0,0.5)]"
              >
                AI
              </text>
            </svg>
          </div>

          {/* Glowing Animated Thinking Text */}
          <div className="flex items-baseline">
            <span className="text-[26px] font-black tracking-tight bg-gradient-to-r from-blue-600 via-sky-500 to-indigo-600 dark:from-sky-400 dark:via-blue-400 dark:to-indigo-300 bg-clip-text text-transparent drop-shadow-[0_0_12px_rgba(56,189,248,0.4)]">
              {cleanMessage}
            </span>
            {/* 3 Staggered Blinking Dots */}
            <span className="inline-flex items-center gap-1 ml-1 text-[26px] font-black leading-none bg-gradient-to-r from-sky-500 to-indigo-500 dark:from-sky-400 dark:to-indigo-300 bg-clip-text text-transparent select-none">
              <span className="inline-block animate-dot-1">.</span>
              <span className="inline-block animate-dot-2">.</span>
              <span className="inline-block animate-dot-3">.</span>
            </span>
          </div>
        </div>
      </div>

      {/* Subtext info */}
      <p className="text-[13px] font-bold text-muted-soft mt-5 tracking-wide animate-pulse">
        Analyzing proximity, cleanliness & crowd status
      </p>
    </div>
  );
}
