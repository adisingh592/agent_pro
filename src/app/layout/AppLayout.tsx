import React from "react";
import { Sidebar } from "./Sidebar";
import { TitleBar } from "./TitleBar";
import { NavPage } from "../../types/agent";

interface AppLayoutProps {
  currentPage: NavPage;
  onNavigate: (page: NavPage) => void;
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({
  currentPage,
  onNavigate,
  children,
}) => {
  return (
    <div className="h-screen w-screen flex flex-col bg-bg-main overflow-hidden text-text-primary">
      {/* Desktop App Window TitleBar */}
      <TitleBar currentPage={currentPage} onNavigate={onNavigate} />

      {/* Application Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <Sidebar currentPage={currentPage} onNavigate={onNavigate} />

        {/* Dynamic Page Viewport */}
        <main className="flex-1 bg-bg-main flex flex-col overflow-hidden relative">
          {children}
        </main>
      </div>
    </div>
  );
};
