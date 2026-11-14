
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  FileText,
  Menu,
  X,
  ChevronRight,
} from "lucide-react";

const navigation = [
  { name: "Features", href: "#features", id: "features" },
  { name: "How It Works", href: "#how-it-works", id: "how-it-works" },
  { name: "Security", href: "#security", id: "security" },
  { name: "Pricing", href: "#pricing", id: "pricing" },
  { name: "FAQ", href: "#faq", id: "faq" },
];

export default function Navbar() {
  const [activeSection, setActiveSection] = useState("");
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Detect the currently visible section
  useEffect(() => {
    const updateActiveSection = () => {
      if (window.scrollY < 150 && !window.location.hash) {
        setActiveSection("");
        return;
      }

      const activationPoint = 140;
      let currentSection = "";

      navigation.forEach((item) => {
        const section = document.getElementById(item.id);

        if (section) {
          const sectionTop = section.getBoundingClientRect().top;

          if (sectionTop <= activationPoint) {
            currentSection = item.id;
          }
        }
      });

      setActiveSection(currentSection);
    };

    updateActiveSection();

    window.addEventListener("scroll", updateActiveSection, {
      passive: true,
    });

    window.addEventListener("hashchange", updateActiveSection);

    return () => {
      window.removeEventListener("scroll", updateActiveSection);
      window.removeEventListener("hashchange", updateActiveSection);
    };
  }, []);

  // Close mobile menu
  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  // Navigate to homepage
  const handleLogoClick = () => {
    setActiveSection("");
    closeMobileMenu();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-100 bg-white/95 backdrop-blur-xl">
      <nav className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">
        {/* Knowly Logo */}
        <Link
          href="/"
          onClick={handleLogoClick}
          className="flex items-center gap-2.5"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-white shadow-sm">
            <FileText size={23} strokeWidth={2.2} />
          </div>

          <span className="text-2xl font-bold tracking-tight text-gray-900">
            Knowly<span className="text-primary">.</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-2 lg:flex">
          {navigation.map((item) => {
            const isActive = activeSection === item.id;

            return (
              <Link
                key={item.id}
                href={item.href}
                aria-current={isActive ? "location" : undefined}
                onClick={() => {
                  setActiveSection(item.id);
                }}
                className={`rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? "bg-purple-100 text-primary"
                    : "text-gray-600 hover:bg-purple-50 hover:text-primary"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </div>

        {/* Desktop Sign In and Get Started */}
        <div className="hidden items-center gap-5 lg:flex">
          <Link
            href="/login"
            className="text-sm font-semibold text-gray-700 transition-colors hover:text-primary"
          >
            Sign In
          </Link>

          <Link
            href="/get-started"
            className="rounded-full bg-primary px-6 py-3 text-sm font-semibold text-white shadow-md shadow-purple-200 transition-all hover:-translate-y-0.5 hover:bg-primary-dark hover:shadow-lg"
          >
            Get Started
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          type="button"
          aria-label={
            mobileMenuOpen
              ? "Close navigation menu"
              : "Open navigation menu"
          }
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-navigation"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-gray-200 text-gray-700 transition-colors hover:bg-purple-50 hover:text-primary lg:hidden"
        >
          {mobileMenuOpen ? (
            <X size={22} />
          ) : (
            <Menu size={22} />
          )}
        </button>
      </nav>

      {/* Mobile Navigation Panel */}
      {mobileMenuOpen && (
        <div
          id="mobile-navigation"
          className="border-t border-gray-100 bg-white px-6 py-5 shadow-lg lg:hidden"
        >
          <div className="space-y-2">
            {navigation.map((item) => {
              const isActive = activeSection === item.id;

              return (
                <Link
                  key={item.id}
                  href={item.href}
                  onClick={() => {
                    setActiveSection(item.id);
                    closeMobileMenu();
                  }}
                  className={`flex items-center justify-between rounded-xl px-4 py-3 text-sm font-semibold transition-colors ${
                    isActive
                      ? "bg-purple-100 text-primary"
                      : "text-gray-600 hover:bg-purple-50 hover:text-primary"
                  }`}
                >
                  {item.name}

                  <ChevronRight size={17} />
                </Link>
              );
            })}
          </div>

          {/* Mobile Authentication Buttons */}
          <div className="mt-5 flex gap-3 border-t border-gray-100 pt-5">
            <Link
              href="/login"
              onClick={closeMobileMenu}
              className="flex-1 rounded-xl border border-gray-200 py-3 text-center text-sm font-semibold text-gray-700 transition-colors hover:bg-gray-50"
            >
              Sign In
            </Link>

            <Link
              href="/get-started"
              onClick={closeMobileMenu}
              className="flex-1 rounded-xl bg-primary py-3 text-center text-sm font-semibold text-white transition-colors hover:bg-primary-dark"
            >
              Get Started
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
