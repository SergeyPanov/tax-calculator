"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type TaxResult = {
  total_employment_income?: number | string;
  partial_tax_base?: number | string;
  rounded_tax_base?: number | string;
  income_tax?: number | string;
  total_tax_credits?: number | string;
  tax_after_credits?: number | string;
  advances_withheld?: number | string;
  overpayment_or_underpayment?: number | string;
  total_tax?: number | string;
  tax_at_15_pct?: number | string;
  tax_at_23_pct?: number | string;
  aggregated_tax_base?: number | string;
  aggregated_advances_withheld?: number | string;
};

type FieldConfig = {
  label: string;
  key: keyof TaxResult;
  helper?: string;
};

const fields: FieldConfig[] = [
  {
    label: "Total employment income (DAP 31)",
    key: "total_employment_income",
  },
  {
    label: "Partial tax base (DAP 36)",
    key: "partial_tax_base",
  },
  {
    label: "Rounded tax base (DAP 56)",
    key: "rounded_tax_base",
  },
  {
    label: "Income tax (DAP 57)",
    key: "income_tax",
  },
  {
    label: "Tax credits total (DAP 70)",
    key: "total_tax_credits",
  },
  {
    label: "Tax after credits (DAP 71)",
    key: "tax_after_credits",
  },
  {
    label: "Advances withheld (DAP 84)",
    key: "advances_withheld",
  },
  {
    label: "Overpayment / underpayment",
    key: "overpayment_or_underpayment",
    helper: "Negative means refund due.",
  },
];

const detailFields: FieldConfig[] = [
  { label: "Aggregated tax base", key: "aggregated_tax_base" },
  {
    label: "Aggregated advances withheld",
    key: "aggregated_advances_withheld",
  },
  { label: "Tax at 15%", key: "tax_at_15_pct" },
  { label: "Tax at 23%", key: "tax_at_23_pct" },
  { label: "Total tax", key: "total_tax" },
];

const formatCurrency = (value: number | string | undefined): string => {
  if (value === null || value === undefined) {
    return "—";
  }

  const numeric =
    typeof value === "number"
      ? value
      : Number.isFinite(Number(value))
        ? Number(value)
        : null;

  if (numeric === null) {
    return String(value);
  }

  return new Intl.NumberFormat("cs-CZ", {
    style: "currency",
    currency: "CZK",
    maximumFractionDigits: 0,
  }).format(numeric);
};

export default function ResultPage() {
  const [result, setResult] = useState<TaxResult | null>(null);

  useEffect(() => {
    try {
      const stored = sessionStorage.getItem("taxResult");
      if (!stored) {
        setResult(null);
        return;
      }
      const parsed = JSON.parse(stored) as TaxResult;
      setResult(parsed);
    } catch {
      setResult(null);
    }
  }, []);

  const summaryRows = useMemo(
    () =>
      fields.map((field) => ({
        ...field,
        value: formatCurrency(result?.[field.key]),
      })),
    [result]
  );

  const detailRows = useMemo(
    () =>
      detailFields.map((field) => ({
        ...field,
        value: formatCurrency(result?.[field.key]),
      })),
    [result]
  );

  return (
    <main className="min-vh-100 d-flex align-items-center bg-body-tertiary py-5">
      <div className="container" style={{ maxWidth: "720px" }}>
        <div className="d-flex align-items-center justify-content-between mb-3">
          <div>
            <h1 className="h4 mb-1">Tax calculation result</h1>
            <div className="text-muted small">
              Review the key DAP lines before filing.
            </div>
          </div>
          <Link className="btn btn-outline-secondary btn-sm" href="/">
            Upload another ZIP
          </Link>
        </div>

        {!result ? (
          <div className="alert alert-warning" role="alert">
            <div className="fw-semibold mb-1">No result found</div>
            <div className="small text-muted">
              Upload documents again to calculate your tax result.
            </div>
            <Link className="btn btn-primary btn-sm mt-3" href="/">
              Go back to upload
            </Link>
          </div>
        ) : (
          <div className="card shadow-sm border-0">
            <div className="card-body p-4">
              <div className="mb-4">
                <h2 className="h6 text-uppercase text-muted mb-2">Key lines</h2>
                <div className="table-responsive">
                  <table className="table table-sm align-middle mb-0">
                    <tbody>
                      {summaryRows.map((row) => (
                        <tr key={row.key}>
                          <th scope="row" className="fw-normal">
                            <div>{row.label}</div>
                            {row.helper ? (
                              <div className="small text-muted">{row.helper}</div>
                            ) : null}
                          </th>
                          <td className="text-end fw-semibold">{row.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h2 className="h6 text-uppercase text-muted mb-2">Details</h2>
                <div className="table-responsive">
                  <table className="table table-sm align-middle mb-0">
                    <tbody>
                      {detailRows.map((row) => (
                        <tr key={row.key}>
                          <th scope="row" className="fw-normal">
                            {row.label}
                          </th>
                          <td className="text-end">{row.value}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
