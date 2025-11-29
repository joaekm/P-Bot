// --- ADDA DESIGN SYSTEM TOKENS ---
// Central source of truth for all visual styles.

export const tokens = {
  colors: {
    brand: {
      primary: '#D32F00', // Orange/Röd - Huvudfärg för Header och CTA
      secondary: '#005B59', // Petrol/Deep Teal - Footer, rubriker, ikoner
      bgHero: '#FFF0ED', // Ljus Rosa - Hero-ytor
      light: '#B9EAE9',
      accent: '#D32F00',
      lightTint: '#E0F5F4', // Ice Teal - Bakgrundscirklar för ikoner
    },
    neutral: {
      text: '#2B2825', // Mörkgrå/Svart
      bg: '#FBF4EA', // Warm Beige
      surface: '#FFFFFF',
      border: '#D4D3CD', // Hårdkodad, inte från JSON
      grey: '#333333',
      lightGrey: '#706F6B',
    },
    accent: {
      darkRed: '#9E2300', // 25% mörkare än #D32F00
      darkPetrol: '#004443', // 25% mörkare än #005B59
    },
    ui: {
      iconBg: '#E0F5F4', // Ice Teal - Bakgrundscirklar för ikoner
      iconColor: '#005B59', // Petrol - Ikonfärg
      cardBgYellow: '#FFFAD0', // Gul - Produktkort kategori
      cardBgBlue: '#E6F3F9', // Blå - Produktkort kategori
      cardBgGreen: '#E8F5E9', // Grön - Produktkort kategori
      cardBgPink: '#FCE4EC', // Rosa - Produktkort kategori
      cardBgOrange: '#FFF0ED', // Orange - Produktkort kategori (samma som bgHero)
    },
    status: {
      info: '#2196F3', // Blue
      infoBg: '#E3F2FD',
      infoDark: '#1565C0',
      success: '#4CAF50', // Green
      successBg: '#E8F5E9',
      successDark: '#2E7D32',
      warning: '#FF9800', // Orange
      warningBg: '#FFF3E0',
      warningDark: '#E65100',
      error: '#F44336', // Red
      errorBg: '#FFEBEE',
      errorDark: '#C62828',
    }
  },
  typography: {
    fontFamily: '"Avenir Next", "Avenir", "Helvetica", sans-serif',
    weights: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    sizes: {
      xs: '12px',
      sm: '14px',
      base: '16px',
      lg: '20px',
      xl: '22px',
      '2xl': '24px',
      '3xl': '32px',
      '4xl': '34px',
      '5xl': '50px',
    },
    lineHeights: {
      tight: '1.1',
      normal: '1.2',
      relaxed: '1.6',
    }
  },
  spacing: {
    xs: '4px',
    sm: '6px',
    md: '8px',
    lg: '10px',
    xl: '12px',
    '2xl': '16px',
    '3xl': '20px',
    '4xl': '24px',
    '5xl': '32px',
    '6xl': '40px',
  },
  borderRadius: {
    none: '0px',
    sm: '4px',
    md: '8px',  // Standard card radius (updated from 6px)
    lg: '16px', // Large card radius
    pill: '9999px', // Fullt rundade knappar
    circle: '50px',
    full: '100px',
    iconCircle: '50%', // Ikon-cirklar
  },
  shadows: {
    card: 'rgba(0, 0, 0, 0.08) 0px 3px 10px 0px',
    subtle: 'rgba(0, 0, 0, 0.12) 0px 0px 3px 0px',
    inset: 'rgb(255, 252, 223) 0px 0px 0px 2px inset',
    button: '0 4px 12px rgba(211, 47, 0, 0.3)',
  },
  layout: {
    containerMaxWidth: '1200px',
    gridColumns: 12,
    gridGap: '24px',
    headerHeight: '142px',
    headerBg: '#D32F00', // Röd
    footerBg: '#004443', // Dark Petrol
    breakpoints: {
      mobile: '640px',
      tablet: '768px',
      desktop: '1024px',
    }
  }
};
