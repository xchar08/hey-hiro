import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({ baseDirectory: __dirname });

export default [
  // Extend Next.js’s recommended rules for Core Web Vitals and TypeScript
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Allow unescaped characters in JSX (e.g. apostrophes)
      "react/no-unescaped-entities": "off",
    },
  },
];
