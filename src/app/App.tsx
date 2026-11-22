import React, { useState } from "react";
import { AppLayout } from "./layout/AppLayout";
import { NavPage } from "../types/agent";
import { ChatPage } from "../pages/ChatPage";
import { ComputerPage } from "../pages/ComputerPage";
import { ApplicationsPage } from "../pages/ApplicationsPage";
import { FilesPage } from "../pages/FilesPage";
import { TasksPage } from "../pages/TasksPage";
import { MemoryPage } from "../pages/MemoryPage";
import { ActivityPage } from "../pages/ActivityPage";
import { SettingsPage } from "../pages/SettingsPage";

export default function App() {
  const [currentPage, setCurrentPage] = useState<NavPage>("chat");

  const renderPage = () => {
    switch (currentPage) {
      case "chat":
        return <ChatPage onNavigate={setCurrentPage} />;
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
        return <ActivityPage />;
      case "settings":
        return <SettingsPage />;
      default:
        return <ChatPage onNavigate={setCurrentPage} />;
    }
  };

  return (
    <AppLayout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage()}
    </AppLayout>
  );
}
