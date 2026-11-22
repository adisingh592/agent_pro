import React, { useState } from "react";
import {
  Folder,
  FileCode,
  FileText,
  File,
  Search,
  ChevronRight,
  ArrowUpDown,
  MoreVertical,
  Copy,
  Info
} from "lucide-react";
import { mockFiles } from "../lib/mockData";
import { FileItem } from "../types/agent";

export const FilesPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [files, setFiles] = useState<FileItem[]>(mockFiles);
  const [currentPath, setCurrentPath] = useState("h:\\pro agent");

  const filteredFiles = files.filter((f) =>
    f.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getFileIcon = (file: FileItem) => {
    if (file.isDirectory) return <Folder className="w-4 h-4 text-accent fill-accent/20" />;
    if (file.extension === "py") return <FileCode className="w-4 h-4 text-accent" />;
    if (file.extension === "md") return <FileText className="w-4 h-4 text-text-secondary" />;
    return <File className="w-4 h-4 text-text-muted" />;
  };

  const formatSize = (bytes?: number) => {
    if (bytes === undefined) return "--";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border-subtle shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-text-primary tracking-tight flex items-center gap-2">
            <Folder className="w-5 h-5 text-accent" />
            File Intelligence & Workspace
          </h1>
          <p className="text-xs text-text-muted mt-0.5">
            Safe file navigation, metadata inspection, and verified organization under boundary guards.
          </p>
        </div>
      </div>

      {/* Path Breadcrumbs & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
        <div className="flex items-center gap-1.5 text-xs text-text-secondary bg-bg-secondary px-3 py-1.5 rounded-md border border-border-subtle font-mono w-full sm:w-auto">
          <span>h:</span>
          <ChevronRight className="w-3 h-3 text-text-muted" />
          <span>pro agent</span>
          <ChevronRight className="w-3 h-3 text-text-muted" />
          <span className="text-text-primary font-semibold">workspace</span>
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="w-full h-8 bg-bg-secondary border border-border-subtle rounded-md pl-8 pr-3 text-xs text-text-primary placeholder:text-text-muted focus:border-accent/60 outline-none"
          />
        </div>
      </div>

      {/* File List Table */}
      <div className="flex-1 bg-bg-secondary border border-border-subtle rounded-lg overflow-hidden flex flex-col">
        {/* Table Header */}
        <div className="grid grid-cols-12 px-4 py-2 bg-bg-elevated border-b border-border-subtle text-[11px] font-medium text-text-muted select-none">
          <div className="col-span-6 flex items-center gap-1">
            <span>Name</span>
            <ArrowUpDown className="w-3 h-3" />
          </div>
          <div className="col-span-2">Type</div>
          <div className="col-span-2">Size</div>
          <div className="col-span-2 text-right">Modified</div>
        </div>

        {/* Table Rows */}
        <div className="flex-1 overflow-y-auto divide-y divide-border-subtle/50">
          {filteredFiles.map((file) => (
            <div
              key={file.id}
              className="grid grid-cols-12 px-4 py-2.5 text-xs hover:bg-bg-hover transition-colors items-center group cursor-pointer"
            >
              <div className="col-span-6 flex items-center gap-2.5 truncate font-medium text-text-primary group-hover:text-accent transition-colors">
                {getFileIcon(file)}
                <span className="truncate">{file.name}</span>
              </div>
              <div className="col-span-2 text-text-muted text-[11px]">
                {file.isDirectory ? "Folder" : file.extension?.toUpperCase() || "File"}
              </div>
              <div className="col-span-2 text-text-secondary font-mono text-[11px]">
                {formatSize(file.sizeBytes)}
              </div>
              <div className="col-span-2 text-right text-text-muted text-[11px]">
                {file.modifiedAt}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
