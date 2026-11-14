
"use client";

import { useEffect } from "react";

const sectionTitles: Record<string, string> = {
  features: "Knowly - Features",
  "how-it-works": "Knowly - How It Works",
  security: "Knowly - Security",
  pricing: "Knowly - Pricing",
  faq: "Knowly - FAQ",
};

export default function SectionTitleSync() {
  useEffect(() => {
    const updateTitle = (hash: string) => {
      const section = hash.replace(/^#/, "");

      document.title = sectionTitles[section] || "Knowly";
    };

    const handleClick = (event: MouseEvent) => {
      const target = event.target;

      if (!(target instanceof Element)) return;

      const link = target.closest("a");

      if (!link) return;

      const url = new URL(link.href, window.location.href);

      if (url.pathname === window.location.pathname) {
        updateTitle(url.hash);
      }
    };

    const handleNavigation = () => {
      updateTitle(window.location.hash);
    };

    document.addEventListener("click", handleClick, true);
    window.addEventListener("hashchange", handleNavigation);
    window.addEventListener("popstate", handleNavigation);

    handleNavigation();

    return () => {
      document.removeEventListener("click", handleClick, true);
      window.removeEventListener("hashchange", handleNavigation);
      window.removeEventListener("popstate", handleNavigation);
    };
  }, []);

  return null;
}
