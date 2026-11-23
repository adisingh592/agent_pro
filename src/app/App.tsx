import React, { useState } from "react";
import { AppLayout } from "./layout/AppLayout";
import { NavPage } from "../types/agent";
import { OrbitHome } from "../components/orbit/OrbitHome";
import { ChatPage } from "../pages/ChatPage";
import { ComputerPage } from "../pages/ComputerPage";
import { ApplicationsPage } from "../pages/ApplicationsPage";
import { FilesPage } from "../pages/FilesPage";
import { TasksPage } from "../pages/TasksPage";
import { MemoryPage } from "../pages/MemoryPage";
import { ActivityPage } from "../pages/ActivityPage";
import { SettingsPage } from "../pages/SettingsPage";
import { IdePage } from "../pages/IdePage";
import { AutomationPage } from "../pages/AutomationPage";
import { SkillsPage } from "../pages/SkillsPage";
import { NineRoomsDeck } from "../components/rooms/NineRoomsDeck";

export default function App() {
  const [currentPage, setCurrentPage] = useState<NavPage>("orbit");
  const [selectedModel, setSelectedModel] = useState<string>("Qwen3 8B");
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

  const handleStartChatFromOrbit = (prompt: string) => {
    setPendingPrompt(prompt);
    setCurrentPage("chat");
  };

  // If on Orbit Home, render full-window spatial interface matching reference image (Image 1)
  if (currentPage === "orbit") {
    return (
      <OrbitHome
        onNavigate={setCurrentPage}
        onStartChat={handleStartChatFromOrbit}
        modelName={selectedModel}
        onModelSelect={setSelectedModel}
      />
    );
  }

  // If on Nine Rooms Deck, render spatial 9 rooms view matching reference image (Image 2)
  if (currentPage === "rooms") {
    return <NineRoomsDeck onNavigate={setCurrentPage} />;
  }

  const renderPage = () => {
    switch (currentPage) {
      case "chat":
        return <ChatPage onNavigate={setCurrentPage} />;
      case "ide":
        return <IdePage onNavigate={setCurrentPage} />;
      case "automation":
        return <AutomationPage onNavigate={setCurrentPage} />;
      case "skills":
        return <SkillsPage onNavigate={setCurrentPage} />;
      case "computer":
        return <ComputerPage />;
      case "applications":
        return <ApplicationsPage />;
      case "files":
        return <FilesPage />;
      case "tasks":
        return <TasksPage />;
      case "memory":
        return <MemoryPage />;
      case "activity":
      case "history":
        return <ActivityPage />;
      case "settings":
        return <SettingsPage />;
      default:
        return (
          <OrbitHome
            onNavigate={setCurrentPage}
            onStartChat={handleStartChatFromOrbit}
            modelName={selectedModel}
            onModelSelect={setSelectedModel}
          />
        );
    }
  };

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage()}
    </AppLayout>
  );
}
