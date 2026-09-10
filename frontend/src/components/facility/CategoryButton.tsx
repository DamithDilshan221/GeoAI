
interface CategoryButtonProps {
  label: string;
  code: string;
  onClick: (audience?: 'VISITOR' | 'STAFF' | null) => void;
}

const getCategoryStyles = (code: string) => {
  const c = code.toLowerCase();
  if (c.includes('men') && !c.includes('women')) {
    return {
      colorClass: 'text-cat-men',
      bgClass: 'bg-[rgba(47,111,237,0.10)]',
      icon: (
        <svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="3"/><path d="M12 9c-3 0-5 2-5 5v7h3v-6h4v6h3v-7c0-3-2-5-5-5z"/></svg>
      )
    };
  }
  if (c.includes('women') || c.includes('female')) {
    return {
      colorClass: 'text-cat-women',
      bgClass: 'bg-[rgba(255,95,160,0.14)]',
      icon: (
        <svg width="30" height="30" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="4.5" r="3"/><path d="M12 8c-1 0-1.8.6-2.1 1.6L8 15h2l.4 6h3.2l.4-6h2l-1.9-5.4C13.8 8.6 13 8 12 8z"/></svg>
      )
    };
  }
  if (c.includes('unisex') || c.includes('neutral')) {
    return {
      colorClass: 'text-amber-dark',
      bgClass: 'bg-[rgba(231,174,78,0.16)]',
      icon: (
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="9"/><path d="M9 8v8M15 8v8M9 12h6"/></svg>
      )
    };
  }
  if (c.includes('access') || c.includes('wheelchair')) {
    return {
      colorClass: 'text-indigo',
      bgClass: 'bg-[rgba(110,127,209,0.14)]',
      icon: (
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="4.2" r="1.7"/><path d="M11 8.5v4.5l-3.5 5.5"/><path d="M11 10h5l-1.2 3"/><circle cx="15" cy="17.5" r="3.3"/></svg>
      )
    };
  }
  
  return {
    colorClass: 'text-teal-dark',
    bgClass: 'bg-[rgba(63,203,190,0.16)]',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
    )
  };
};

export function CategoryButton({ label, code, onClick }: CategoryButtonProps) {
  const styles = getCategoryStyles(code);
  const isGendered = code.toLowerCase().includes('men') || code.toLowerCase().includes('women') || code.toLowerCase().includes('female');

  return (
    <div
      onClick={() => onClick()}
      className="flex flex-col bg-paper text-ink rounded-lg p-[18px] mb-3.5 shadow-card cursor-pointer transition-transform active:scale-[0.985]"
    >
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 ${styles.bgClass} ${styles.colorClass}`}>
          {styles.icon}
        </div>
        <div className="flex-1 min-w-0">
          <h2 className="m-0 mb-2 text-[18.5px] font-bold">{label}</h2>
          <p className="text-[12px] text-muted-soft font-medium m-0 mt-0.5">Explore {label.toLowerCase()}</p>
        </div>
      </div>
      
      {isGendered && (
        <div className="mt-4 flex gap-2">
          <button 
            onClick={(e) => { e.stopPropagation(); onClick('VISITOR'); }}
            className="flex-1 py-2 px-3 rounded-xl bg-pill-bg text-ink border border-pill-border text-sm font-semibold hover:bg-pill-border/50"
          >
            Visitor
          </button>
          <button 
            onClick={(e) => { e.stopPropagation(); onClick('STAFF'); }}
            className="flex-1 py-2 px-3 rounded-xl bg-pill-bg text-ink border border-pill-border text-sm font-semibold hover:bg-pill-border/50"
          >
            Staff
          </button>
        </div>
      )}
    </div>
  );
}
