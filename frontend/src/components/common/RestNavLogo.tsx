interface RestNavLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  withText?: boolean;
  className?: string;
}

export function RestNavLogo({ size = 'md', withText = false, className = '' }: RestNavLogoProps) {
  const sizeMap = {
    sm: 'w-10 h-10',
    md: 'w-[54px] h-[54px]',
    lg: 'w-20 h-20',
    xl: 'w-28 h-28',
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className={`relative flex shrink-0 items-center justify-center ${sizeMap[size]} rounded-2xl bg-white shadow-[0_6px_24px_rgba(15,44,89,0.28)] border-2 border-indigo-400/40 dark:border-sky-400/40 p-0.5 overflow-hidden transition-transform duration-300 hover:scale-105`}
      >
        <img
          src="/logo.png"
          alt="RestNav Logo"
          className="w-full h-full object-contain scale-120 drop-shadow-sm"
        />
      </div>

      {withText && (
        <div className="flex flex-col">
          <span className="text-xl font-black tracking-tight text-[#0F2C59] dark:text-sky-300 font-display">
            RestNav
          </span>
          <span className="text-xs font-semibold text-muted-soft tracking-wide">
            Peradeniya University
          </span>
        </div>
      )}
    </div>
  );
}
