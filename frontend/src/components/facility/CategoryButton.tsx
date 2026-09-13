
interface CategoryButtonProps {
  label: string;
  code: string;
  onClick: (audience?: 'VISITOR' | 'STAFF' | null) => void;
}

const getCategoryStyles = (code: string) => {
  const c = code.toLowerCase();
  if ((c.includes('men') || c.includes('male')) && !c.includes('women') && !c.includes('female')) {
    return {
      cardClass: 'card-mens',
      iconBoxClass: 'icon-box-mens',
      subtitle: "Explore men's washrooms near you",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="4.5" r="2.5" />
          <path d="M12 8c-2.5 0-4 1.5-4 3.5v6.5h2.5v4.5h3v-4.5h2.5v-6.5c0-2-1.5-3.5-4-3.5z" />
        </svg>
      )
    };
  }
  if (c.includes('women') || c.includes('female')) {
    return {
      cardClass: 'card-womens',
      iconBoxClass: 'icon-box-womens',
      subtitle: "Explore women's washrooms near you",
      icon: (
        <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
          <circle cx="12" cy="4.5" r="2.5" />
          <path d="M12 8c-1.2 0-2 .6-2.3 1.6L8 15h2l.4 6h3.2l.4-6h2l-1.7-5.4C14 8.6 13.2 8 12 8z" />
        </svg>
      )
    };
  }
  
  return {
    cardClass: 'card-nearby',
    iconBoxClass: 'icon-box-nearby',
    subtitle: "Explore facilities near you",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none" />
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
      </svg>
    )
  };
};         

export function CategoryButton({ label, code, onClick }: CategoryButtonProps) {
  const styles = getCategoryStyles(code);
 
  return (
    <div
      onClick={() => onClick()}
      className={`flex items-center gap-4 text-ink rounded-2xl p-4 mb-3.5 shadow-card cursor-pointer transition-all duration-200 hover:scale-[1.01] active:scale-[0.985] group relative overflow-hidden backdrop-blur-xl ${styles.cardClass}`}
    >
      <div className={`w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 shadow-inner group-hover:scale-105 transition-transform ${styles.iconBoxClass}`}>
        {styles.icon}
      </div>
      <div className="flex-1 min-w-0">
        <h2 className="m-0 mb-1 text-[18px] font-extrabold tracking-tight text-ink">{label}</h2>
        <p className="text-[12.5px] text-muted font-medium m-0">{styles.subtitle}</p>
      </div>
      <div className="text-muted-soft group-hover:text-ink group-hover:translate-x-1 transition-all">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>
    </div>
  );
}

