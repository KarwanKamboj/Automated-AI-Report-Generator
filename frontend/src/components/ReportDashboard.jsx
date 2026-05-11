"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileType,
  AlertCircle,
  Loader2,
  Download,
  BarChart3,
  BrainCircuit,
} from "lucide-react";
import axios from "axios";

export default function ReportDashboard() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [apiKey, setApiKey] = useState("");

  const fileInputRef = useRef(null);
  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_BASE_URL ||
    "https://automated-ai-report-generator.onrender.com";

  // =========================
  // FILE HANDLING
  // =========================

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setError(null);

    const validTypes = [
      "text/csv",
      "application/vnd.ms-excel",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ];

    const isValid =
      validTypes.includes(selectedFile.type) ||
      /\.(csv|xls|xlsx)$/i.test(selectedFile.name);

    if (!isValid) {
      setError("Please upload a valid CSV or Excel file.");
      return;
    }

    setFile(selectedFile);
  };

  // =========================
  // API CALL
  // =========================

  const handleGenerateReport = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setReportData(null);

    const formData = new FormData();
    formData.append("file", file);

    if (apiKey) {
      formData.append("api_key", apiKey);
    }

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/generate-report`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        },
      );

      setReportData(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Error generating report. Check backend and API key.",
      );
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // DOWNLOAD PDF
  // =========================

  const handleDownloadPDF = () => {
    if (!reportData?.pdf_base64) return;

    const linkSource = `data:application/pdf;base64,${reportData.pdf_base64}`;

    const downloadLink = document.createElement("a");

    const fileName = `Analysis_Report_${
      file?.name?.split(".")[0] || "report"
    }.pdf`;

    downloadLink.href = linkSource;
    downloadLink.download = fileName;

    downloadLink.click();
  };

  // =========================
  // MARKDOWN RENDER
  // =========================

  const renderMarkdown = (text = "") => {
    let html = text
      .replace(/^### (.*$)/gim, "<h3>$1</h3>")
      .replace(/^## (.*$)/gim, "<h2>$1</h2>")
      .replace(/^# (.*$)/gim, "<h1>$1</h1>")
      .replace(/^\* (.*$)/gim, "<ul><li>$1</li></ul>")
      .replace(/^- (.*$)/gim, "<ul><li>$1</li></ul>")
      .replace(/\*\*(.*?)\*\*/gim, "<b>$1</b>")
      .replace(/\n/gim, "<br />");

    html = html.replace(/<\/ul>\s*<ul>/gim, "");

    return { __html: html };
  };

  {
    /* =========================
         SUMMARY CARDS
   ========================= */
  }
  const summaryCards = reportData
    ? [
        { label: "Rows", value: reportData.summary?.num_rows ?? 0 },
        { label: "Columns", value: reportData.summary?.num_cols ?? 0 },
        {
          label: "Missing Values",
          value: reportData.summary?.total_missing_values ?? 0,
        },
        {
          label: "Duplicate Rows",
          value: reportData.summary?.duplicate_rows ?? 0,
        },
      ]
    : [];

  {
    /*=========================*/
  }
  {
    /* NORMALIZE CHART*/
  }
  {
    /* =========================*/
  }
  const normalizeChart = (key, value) => {
    if (typeof value === "string") {
      return {
        title: key.replace(/_/g, " "),
        image: value,
        caption: "",
      };
    }

    return {
      title: value?.title || key.replace(/_/g, " "),
      image: value?.image || "",
      caption: value?.caption || "",
    };
  };

  return (
    <div className="w-full space-y-8">
      {/* ========================= */}
      {/* UPLOAD SECTION */}
      {/* ========================= */}

      {!reportData && (
        <div className="max-w-2xl mx-auto">
          <div
            className={`glass rounded-3xl p-10 text-center cursor-pointer transition-all duration-300 border-2 border-dashed ${
              isDragging
                ? "border-emerald-500 bg-emerald-500/5 scale-[1.02]"
                : "border-gray-700 hover:border-emerald-400/50 hover:bg-white/[0.02]"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={(e) => {
              const tag = e.target.tagName;

              if (tag !== "INPUT" && tag !== "BUTTON") {
                fileInputRef.current?.click();
              }
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={handleFileChange}
              accept=".csv,.xls,.xlsx"
            />

            <div className="w-20 h-20 mx-auto bg-gray-800 rounded-full flex items-center justify-center mb-6 shadow-inner">
              <UploadCloud
                className={`w-10 h-10 ${
                  isDragging ? "text-emerald-400" : "text-gray-400"
                }`}
              />
            </div>

            <h3 className="text-2xl font-semibold mb-2 text-white">
              {file ? file.name : "Drag & Drop your dataset"}
            </h3>

            <p className="text-gray-400 mb-6">
              {file
                ? `Ready to analyze ${(file.size / 1024).toFixed(2)} KB`
                : "Supports CSV, XLS, XLSX up to 50MB"}
            </p>

            {file && !loading && (
              <div className="space-y-4 max-w-sm mx-auto pt-4">
                <input
                  type="password"
                  placeholder="Optional: Enter Gemini API Key"
                  value={apiKey}
                  onChange={(e) => {
                    e.stopPropagation();
                    setApiKey(e.target.value);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  className="w-full bg-gray-900/50 border border-gray-700 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-center placeholder-gray-500"
                />

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleGenerateReport();
                  }}
                  className="w-full bg-emerald-500 hover:bg-emerald-400 text-black font-bold py-3 px-8 rounded-xl transition-all flex items-center justify-center gap-2"
                >
                  <BrainCircuit className="w-5 h-5" />
                  Generate AI Report
                </button>
              </div>
            )}
          </div>

          {/* ERROR */}

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-3 text-red-400">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}

          {/* LOADING */}

          {loading && (
            <div className="mt-8 text-center space-y-4">
              <Loader2 className="w-10 h-10 animate-spin text-emerald-500 mx-auto" />
              <p className="text-gray-400 animate-pulse">
                Analyzing data and generating insights...
              </p>
            </div>
          )}
        </div>
      )}

      {/* ========================= */}
      {/* DASHBOARD SECTION */}
      {/* ========================= */}

      {reportData && (
        <div className="space-y-8">
          {/* HEADER */}

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 glass p-6 rounded-2xl">
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2 text-white">
                <FileType className="w-6 h-6 text-emerald-400" />
                {reportData.filename}
              </h2>

              <p className="text-gray-400 mt-1">
                {reportData.summary?.num_rows} rows •{" "}
                {reportData.summary?.num_cols} columns
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setReportData(null)}
                className="px-6 py-2 rounded-full border border-gray-600 text-white hover:bg-gray-800 transition-colors"
              >
                Upload New
              </button>

              <button
                onClick={handleDownloadPDF}
                className="bg-emerald-500 hover:bg-emerald-400 text-black font-bold py-2 px-6 rounded-full transition-all flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download PDF
              </button>
            </div>
          </div>

          {/* CONTENT */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* LEFT */}

            <div className="lg:col-span-2 glass rounded-3xl p-8 relative overflow-hidden">
              <div className="flex items-center gap-3 mb-6 border-b border-gray-800 pb-4">
                <div className="p-2 bg-emerald-500/20 rounded-lg">
                  <BrainCircuit className="w-6 h-6 text-emerald-400" />
                </div>

                <h3 className="text-xl font-bold text-white">
                  Executive Summary
                </h3>
              </div>

              <div
                className="markdown-body text-gray-300"
                dangerouslySetInnerHTML={renderMarkdown(
                  reportData.ai_insights || "",
                )}
              />
            </div>

            {/* RIGHT */}

            <div className="space-y-6">
              {/* SNAPSHOT */}

              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-5">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                  </div>

                  <h3 className="text-lg font-bold text-white">
                    Report Snapshot
                  </h3>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {summaryCards.map((item) => (
                    <div
                      key={item.label}
                      className="bg-gray-950/50 border border-gray-800 rounded-lg p-4"
                    >
                      <p className="text-2xl font-bold text-white">
                        {item.value}
                      </p>

                      <p className="text-xs text-gray-400 mt-1">{item.label}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* CHARTS */}

              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-blue-500/20 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                  </div>

                  <h3 className="text-lg font-bold text-white">
                    Data Visualizations
                  </h3>
                </div>

                <div className="space-y-5">
                  {Object.entries(reportData.charts || {}).map(
                    ([key, value]) => {
                      const chart = normalizeChart(key, value);

                      if (!chart.image) return null;

                      return (
                        <div
                          key={key}
                          className="bg-gray-950/50 rounded-lg overflow-hidden border border-gray-800"
                        >
                          <div className="p-4 border-b border-gray-800">
                            <h4 className="text-sm font-semibold text-white capitalize">
                              {chart.title}
                            </h4>

                            {chart.caption && (
                              <p className="text-xs text-gray-400 mt-1">
                                {chart.caption}
                              </p>
                            )}
                          </div>

                          <div className="bg-white p-2">
                            <img
                              src={`data:image/png;base64,${chart.image}`}
                              alt={chart.title}
                              className="w-full h-auto object-contain"
                            />
                          </div>
                        </div>
                      );
                    },
                  )}

                  {Object.keys(reportData.charts || {}).length === 0 && (
                    <p className="text-gray-500 text-center py-8">
                      No charts available.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
