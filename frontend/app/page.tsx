"use client";

import { useMemo, useRef, useState } from "react";
import type { ChangeEvent, DragEvent } from "react";

type TaxResult = {
  overpayment_or_underpayment?: number | string;
};

const currencyFormatter = new Intl.NumberFormat("cs-CZ", {
  style: "currency",
  currency: "CZK",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [taxResult, setTaxResult] = useState<TaxResult | null>(null);

  const isZipFile = (file: File) => {
    const name = file.name.toLowerCase();
    return (
      name.endsWith(".zip") ||
      file.type === "application/zip" ||
      file.type === "application/x-zip-compressed"
    );
  };

  const handleFileSelect = (file: File | null) => {
    if (file && !isZipFile(file)) {
      setSelectedFile(null);
      setErrorMessage("Nahrajte prosím ZIP soubor s PDF dokumenty.");
      setSuccessMessage(null);
      setTaxResult(null);
      return;
    }

    setSelectedFile(file);
    setErrorMessage(null);
    setSuccessMessage(null);
    setTaxResult(null);
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    handleFileSelect(file);
  };

  const handleDrop = (event: DragEvent<HTMLLabelElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0] ?? null;
    handleFileSelect(file);
  };

  const handleCalculate = async () => {
    if (!selectedFile) {
      setErrorMessage("Nejprve vyberte ZIP soubor s PDF dokumenty.");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("/calculate-tax", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        const message =
          payload?.detail ??
          "Nepodařilo se spočítat daně. Zkuste to znovu.";
        throw new Error(message);
      }

      const data = (await response.json()) as TaxResult;
      setTaxResult(data);
      setSuccessMessage("Výpočet je hotový. Výsledek je připraven k revizi.");
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Došlo k neočekávané chybě.";
      setErrorMessage(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formattedResult = useMemo(() => {
    if (!taxResult?.overpayment_or_underpayment) {
      return null;
    }
    const value = Number(taxResult.overpayment_or_underpayment);
    if (Number.isNaN(value)) {
      return null;
    }
    return value;
  }, [taxResult]);

  const estimateLabel =
    formattedResult === null
      ? "Odhadovaný přeplatek"
      : formattedResult < 0
        ? "Odhadovaný přeplatek"
        : formattedResult > 0
          ? "Odhadovaný nedoplatek"
          : "Výsledek vyrovnán";

  const estimateValue =
    formattedResult === null
      ? "0,00 Kč"
      : currencyFormatter.format(Math.abs(formattedResult));

  return (
    <div className="min-h-screen bg-background text-on-background">
      <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-6 py-3 bg-slate-50 border-b-0">
        <div className="flex items-center gap-8">
          <span className="text-xl font-bold text-primary tracking-tighter font-headline">
            Daně Architect
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button
            className="p-2 text-primary"
            type="button"
            aria-label="Nápověda"
          >
            <span className="material-symbols-outlined">help_outline</span>
          </button>
        </div>
      </header>

      <main className="pt-20 min-h-screen px-6 pb-20 flex justify-center">
        <div className="max-w-6xl w-full space-y-10">
          <header className="pt-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="text-4xl font-extrabold font-headline text-primary tracking-tight mb-2">
                Vítejte, pane architekte
              </h1>
              <p className="text-on-surface-variant max-w-xl leading-relaxed">
                Vaše daňové přiznání za rok 2023 je připraveno k vyplnění.
                Nahrajte dokumenty a nechte systém provést profesionální
                kalkulaci.
              </p>
            </div>
            <div className="bg-surface-container-lowest p-6 rounded-xl shadow-sm border border-outline-variant/10 flex items-center gap-6">
              <div className="text-right">
                <span className="block text-xs uppercase font-bold text-on-surface-variant tracking-widest mb-1">
                  {estimateLabel}
                </span>
                <span className="block text-3xl font-black text-primary font-headline">
                  {estimateValue}
                </span>
              </div>
              <div className="h-12 w-[1px] bg-surface-variant"></div>
              <div className="flex flex-col items-center justify-center">
                <span className="material-symbols-outlined text-primary text-3xl">
                  account_balance_wallet
                </span>
              </div>
            </div>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <section className="lg:col-span-8 bg-surface-container-lowest rounded-xl p-8 border border-outline-variant/10 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between mb-8 flex-wrap gap-3">
                <h3 className="text-xl font-bold font-headline text-primary">
                  Nahrát dokumenty
                </h3>
                <span className="text-xs font-semibold text-primary/60 bg-primary-fixed/30 px-3 py-1 rounded-full">
                  ZIP s PDF (Max 50 MB)
                </span>
              </div>

              <label
                htmlFor="tax-documents"
                onDragOver={(event) => {
                  event.preventDefault();
                  setIsDragging(true);
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`group relative border-2 border-dashed rounded-xl p-12 md:p-16 transition-all bg-surface-container-low/50 flex flex-col items-center justify-center text-center cursor-pointer focus-within:ring-2 focus-within:ring-primary/40 ${
                  isDragging
                    ? "border-primary-container"
                    : "border-outline-variant hover:border-primary-container"
                }`}
              >
                <div className="w-20 h-20 rounded-full bg-primary-fixed flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <span
                    className="material-symbols-outlined text-primary text-4xl"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    upload_file
                  </span>
                </div>
                <h3 className="text-lg font-bold font-headline text-primary mb-2">
                  Přetáhněte ZIP soubor sem
                </h3>
                <p className="text-on-surface-variant mb-6 max-w-sm">
                  Nahrajte potvrzení o zdanitelných příjmech (POZP) ve formátu
                  ZIP s PDF soubory.
                </p>
                <span className="bg-primary text-on-primary px-8 py-3 rounded-full font-semibold hover:bg-primary-container transition-all flex items-center gap-2 shadow-lg">
                  <span className="material-symbols-outlined text-xl">add</span>
                  Vybrat soubor z počítače
                </span>
                <input
                  ref={fileInputRef}
                  id="tax-documents"
                  name="tax-documents"
                  type="file"
                  accept=".zip,application/zip,application/x-zip-compressed"
                  className="sr-only"
                  onChange={handleInputChange}
                />
                <div className="absolute inset-0 pointer-events-none opacity-5 group-hover:opacity-10 transition-opacity">
                  <div className="absolute top-4 left-4 w-24 h-32 border border-primary rounded-lg"></div>
                  <div className="absolute bottom-10 right-10 w-32 h-24 border border-primary rounded-lg rotate-12"></div>
                </div>
              </label>

              <div className="mt-6 text-sm text-on-surface-variant flex flex-wrap gap-3 items-center">
                <span className="font-semibold">Vybraný soubor:</span>
                <span>
                  {selectedFile ? selectedFile.name : "Zatím nebyl vybrán."}
                </span>
              </div>

              {(errorMessage || successMessage) && (
                <div
                  aria-live="polite"
                  className={`mt-4 text-sm font-medium ${
                    errorMessage ? "text-error" : "text-primary"
                  }`}
                >
                  {errorMessage ?? successMessage}
                </div>
              )}

              <div className="mt-8 flex justify-center">
                <button
                  className="group relative w-full md:w-auto bg-gradient-to-r from-primary to-primary-container text-on-primary px-12 py-5 rounded-full font-bold text-lg hover:shadow-2xl hover:-translate-y-1 transition-all flex items-center justify-center gap-4 disabled:opacity-60 disabled:hover:translate-y-0 disabled:hover:shadow-none"
                  type="button"
                  onClick={handleCalculate}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Počítám..." : "Vypočítat daně"}
                  <span className="material-symbols-outlined group-hover:translate-x-1 transition-transform">
                    analytics
                  </span>
                </button>
              </div>
            </section>

            <aside className="lg:col-span-4 space-y-8">
              <div className="bg-primary text-on-primary p-6 rounded-xl shadow-xl relative overflow-hidden">
                <div className="relative z-10">
                  <h3 className="text-sm font-bold uppercase tracking-widest opacity-80 mb-4">
                    Aktuální stav
                  </h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center border-b border-on-primary/10 pb-2">
                      <span className="text-xs opacity-70">
                        Identifikace poplatníka
                      </span>
                      <span
                        className="material-symbols-outlined text-sm text-green-400"
                        style={{ fontVariationSettings: '"FILL" 1' }}
                      >
                        check_circle
                      </span>
                    </div>
                    <div className="flex justify-between items-center border-b border-on-primary/10 pb-2">
                      <span className="text-xs opacity-70">
                        Příjmy (ze závislé činnosti)
                      </span>
                      <span className="text-xs font-bold text-primary-fixed">
                        Čeká na nahrání
                      </span>
                    </div>
                    <div className="flex justify-between items-center border-b border-on-primary/10 pb-2">
                      <span className="text-xs opacity-70">
                        Nezdanitelné části daně
                      </span>
                      <span className="text-xs font-bold text-primary-fixed">
                        0 položek
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-xs opacity-70">Slevy na dani</span>
                      <span className="text-xs font-bold text-primary-fixed">
                        1 aktivní
                      </span>
                    </div>
                  </div>
                </div>
                <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-on-primary/5 rounded-full blur-2xl"></div>
              </div>

              <div className="bg-surface-container rounded-xl p-6 border border-outline-variant/10">
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center shrink-0">
                    <span className="material-symbols-outlined text-primary">
                      auto_stories
                    </span>
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-primary">
                      Průvodce architekta
                    </h4>
                    <p className="text-xs text-on-surface-variant mt-1">
                      Náš inteligentní algoritmus prohledá vaše dokumenty a
                      automaticky vyhledá možné slevy.
                    </p>
                  </div>
                </div>
                <a
                  className="inline-flex items-center gap-2 text-xs font-bold text-primary hover:gap-3 transition-all"
                  href="#"
                >
                  Více o daňových slevách 2023
                  <span className="material-symbols-outlined text-sm">
                    arrow_forward
                  </span>
                </a>
              </div>

              <div className="bg-error-container/30 border border-error/10 p-6 rounded-xl flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-error-container flex items-center justify-center shrink-0">
                  <span
                    className="material-symbols-outlined text-error"
                    style={{ fontVariationSettings: '"FILL" 1' }}
                  >
                    timer
                  </span>
                </div>
                <div>
                  <span className="block text-xs font-bold text-error/60 uppercase">
                    Termín podání
                  </span>
                  <span className="block text-base font-black text-on-error-container font-headline">
                    2. dubna 2024
                  </span>
                </div>
              </div>
            </aside>
          </div>
        </div>
      </main>
    </div>
  );
}
