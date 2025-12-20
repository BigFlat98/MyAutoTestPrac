# Frontend Documentation (Vue + Tailwind CSS)

## 🎨 Design System: "Modern Luxury"

This project follows a strict design theme characterized by **sharp edges, high contrast, and gold accents**.

### 1. Color Palette
| Name | Value | Usage |
|------|-------|-------|
| **Background** | `White (#ffffff)` | Global background |
| **Text/Border** | `Black (#000000)` | Primary text, Thin borders (1px) |
| **Luxury Gold** | `#996515` | **Brand Accent**, Active states, Borders |
| **Gold Hover** | `#b8860b` | Button hover states |
| **Gold Light** | `rgba(153, 101, 21, 0.02)` | Subtle backgrounds (Response area) |

> **Note**: These colors are defined in `src/style.css` using Tailwind v4 `@theme` variables.

### 2. Typography
- **Font**: Inter, system-ui, sans-serif
- **Style**: Clean, Modern, Monospace for data.
- **Rules**:
    - Headers are thin (`font-light`) and tight (`tracking-tight`).
    - Labels are uppercase with wide letter-spacing (`tracking-widest`).

### 3. UI Rules (Strict)
- **Square Edges**: `border-radius: 0` (or `rounded-none`) is mandatory for all interactive elements.
- **Thin Lines**: 1px borders for structure.
- **Alignment**: Inputs and Buttons must have identical height (`3.2rem` / `h-input`).
- **Interactions**:
    - Hovering usually triggers a color change to **Gold** + a slight lift (`-translate-y-0.5`).
    - Focus states use a Gold ring.

---

## 🛠 Tech Stack & Migration

### Migration History
1.  **Initial Setup**: Standard Vanilla CSS in `style.css`.
2.  **Tailwind Migration**:
    - Installed `tailwindcss`, `postcss`, `autoprefixer`.
    - Upgraded to **Tailwind CSS v4** (using `@tailwindcss/postcss`).
    - Replaced `tailwind.config.js` with CSS-first configuration in `style.css`.
    - Refactored `App.vue` to use utility classes (`flex`, `p-6`, etc.) instead of scoped CSS.

### Key Files
- `src/style.css`: Contains the **Tailwind v4 Setup** (`@import "tailwindcss"`) and Custom Theme variables (`@theme`).
- `src/App.vue`: Main UI component using Tailwind utility classes.
- `postcss.config.js`: Configured for `@tailwindcss/postcss`.

## 🚀 Running the Project

```bash
npm install
npm run dev
```
