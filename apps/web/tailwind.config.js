/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Amazon storefront palette
        amzn: {
          squid: "#131921", // top nav bar
          navy: "#232F3E", // secondary nav / dark panels
          yellow: "#FFD814", // primary CTA
          yellowHover: "#F7CA00",
          orange: "#FF9900", // smile / accents
          orangeBtn: "#FFA41C",
          search: "#FEBD69",
          bg: "#EAEDED", // page background
          price: "#B12704", // prices
          link: "#007185", // links
          border: "#D5D9D9",
          band: "#F0F2F2", // order-card header band
        },
        // trust + alert reserved for meaning (verification / fraud)
        trust: { DEFAULT: "#0e9f6e", dark: "#057a55", soft: "#def7ec" },
        alert: { DEFAULT: "#e02424", soft: "#fde8e8" },
        ink: "#131921",
        slate850: "#172033",
      },
      fontFamily: {
        // Amazon ships "Amazon Ember"; Arial is its real-world fallback
        sans: ["'Amazon Ember'", "Arial", "Inter", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "monospace"],
      },
      keyframes: {
        sheen: {
          "0%": { transform: "translateX(-120%)" },
          "100%": { transform: "translateX(220%)" },
        },
        pulsering: {
          "0%": { transform: "scale(0.8)", opacity: "0.7" },
          "100%": { transform: "scale(2.4)", opacity: "0" },
        },
      },
      animation: {
        sheen: "sheen 1.8s ease-in-out",
        pulsering: "pulsering 2s ease-out infinite",
      },
    },
  },
  plugins: [],
};
