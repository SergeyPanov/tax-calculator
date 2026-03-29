import "bootstrap/dist/css/bootstrap.min.css";
import "./globals.css";

import type { ReactNode } from "react";

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body
        style={{
          fontFamily:
            "system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
        }}
      >
        {children}
      </body>
    </html>
  );
}
