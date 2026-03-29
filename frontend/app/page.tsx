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
    message: "Vyberte ZIP archiv s vašimi daňovými dokumenty.",
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
      setStatus({
        type: "idle",
        message: `Připraveno k nahrání: ${file.name}`,
      });
    } else {
      setStatus({
        type: "idle",
        message: "Vyberte ZIP archiv s vašimi daňovými dokumenty.",
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
      setStatus({
        type: "error",
        message: "Nejprve vyberte ZIP soubor.",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    setStatus({
      type: "loading",
      message: "Nahrávám a počítám daň...",
    });

    try {
      const response = await fetch(calculateTaxUrl, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = "Nahrání se nepodařilo. Zkuste to prosím znovu.";
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
      setStatus({ type: "success", message: "Výpočet daně dokončen." });
      router.push("/result");
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Nastala neočekávaná chyba.";
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
              <h1 className="h5 mb-1">Nahrajte daňové dokumenty</h1>
              <div className="text-muted small">
                Bezpečný příjem ZIP souboru pro vaše daňové podklady
              </div>
            </div>
            <div className="d-flex gap-2">
              <span className="badge text-bg-primary">Pouze ZIP</span>
              <span className="badge text-bg-secondary">FastAPI</span>
            </div>
          </div>
          <div className="card-body p-4 p-md-5">
            <p className="text-muted mb-4">
              Nahrajte ZIP archiv, který obsahuje vaše daňové dokumenty.
              Zpracujeme je a spočítáme váš daňový výsledek.
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
                  Přetáhněte ZIP soubor sem nebo klikněte pro výběr.
                </div>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={status.type === "loading"}
              >
                {status.type === "loading" ? "Nahrávám..." : "Odeslat"}
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
