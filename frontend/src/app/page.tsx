import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import Features from "@/components/landing/Features";
import HowItWorks from "@/components/landing/HowItWorks";
import Security from "@/components/landing/Security";
import Pricing from "@/components/landing/Pricing";
import FAQ from "@/components/landing/FAQ";
import FinalCTA from "@/components/landing/FinalCTA";
import Footer from "@/components/landing/Footer";
import SectionTitleSync from "@/components/landing/SectionTitleSync";

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Navbar />
      <SectionTitleSync />
      
      <Hero />
      <Features />
      <HowItWorks />
      <Security />
      <Pricing />
      <FAQ />
      <FinalCTA />
      <Footer />
    </main>
  );
}