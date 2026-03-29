"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";

type Status =
  | { type: "idle"; message: string }
  | { type: "loading"; message: string }
  | { type: "success"; message: string }
  | { type: "error"; message: string };

export default function Page() {
  const router = useRouter();
  const backendUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";
  const calculateTaxUrl = `${backendUrl}/calculate-tax`;
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState<Status>({
    type: "idle",
    message: "Select a ZIP archive with your tax documents.",
  });

  const statusClass = useMemo(() => {
    switch (status.type) {
      case "success":
        return "alert alert-success";
      case "error":
        return "alert alert-danger";
      case "loading":
        return "alert alert-info";
      default:
        return "alert alert-secondary";
    }
  }, [status.type]);

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    if (file) {
      setStatus({ type: "idle", message: `Ready to upload: ${file.name}` });
    } else {
      setStatus({
        type: "idle",
        message: "Select a ZIP archive with your tax documents.",
      });
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0] ?? null;
    handleFileChange(file);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedFile) {
      setStatus({ type: "error", message: "Please choose a ZIP file first." });
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setStatus({ type: "loading", message: "Uploading and calculating tax..." });

    try {
      const response = await fetch(calculateTaxUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = "Upload failed. Please try again.";
        try {
          const payload = (await response.json()) as { detail?: string };
          if (payload?.detail) {
            errorMessage = payload.detail;
          }
        } catch {
          // Keep default error message when the response is not JSON.
        }
        throw new Error(errorMessage);
      }

      const payload = (await response.json()) as unknown;
      try {
        sessionStorage.setItem("taxResult", JSON.stringify(payload));
      } catch {
        // Ignore sessionStorage failures (private mode, quota, etc.).
      }
      setStatus({ type: "success", message: "Tax calculation completed." });
      router.push("/result");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Unexpected error occurred.";
      setStatus({ type: "error", message });
    }
  };

  return (
    <main
      className="min-vh-100 d-flex align-items-center justify-content-center bg-body-tertiary"
    >
      <div className="container" style={{ maxWidth: "560px" }}>
        <div className="card shadow-lg border-0">
          <div className="card-header bg-white border-0 py-3 px-4 d-flex align-items-center justify-content-between">
            <div>
              <h1 className="h5 mb-1">Upload tax documents</h1>
              <div className="text-muted small">
                Secure ZIP intake for your tax materials
              </div>
            </div>
            <div className="d-flex gap-2">
              <span className="badge text-bg-primary">ZIP only</span>
              <span className="badge text-bg-secondary">FastAPI</span>
            </div>
          </div>
          <div className="card-body p-4 p-md-5">
            <p className="text-muted mb-4">
              Upload a ZIP archive that contains your tax documents. We will
              extract and calculate your tax result.
            </p>

            <form onSubmit={handleSubmit} className="d-grid gap-3">
              <div
                className={`border rounded-3 p-4 text-center bg-white ${
                  isDragging ? "border-primary shadow-sm" : "border-secondary"
                }`}
                onDragOver={(event) => {
                  event.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
              >
                <input
                  id="zipUpload"
                  className="form-control form-control-lg"
                  type="file"
                  accept=".zip"
                  onChange={(event) =>
                    handleFileChange(event.target.files?.[0] ?? null)
                  }
                />
                <div className="small text-muted mt-2">
                  Drag and drop your ZIP file here or click to browse.
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={status.type === "loading"}
              >
                {status.type === "loading" ? "Uploading..." : "Submit"}
              </button>
            </form>

            <div className={`${statusClass} mt-4 mb-0`} role="status">
              {status.message}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
