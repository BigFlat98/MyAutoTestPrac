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
    - Focus states use a Gold ring.

### 4. Component Standards

#### Glass Button (Ghost Style)
Used for secondary actions or overlay buttons (e.g., Edit/Cancel in chat).

```css
.glass-btn {
    border: 1px solid #ffffff;
    background-color: rgba(255, 255, 255, 0.3);
    backdrop-filter: blur(2px);
    transition: all 0.3s ease;
}

.glass-btn:hover {
    background-color: rgba(255, 255, 255, 0.5);
    /* Subtle Premium Gold Glow */
    box-shadow: 0 0 15px rgba(218, 165, 32, 0.25);
}
```
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
- `src/api/index.js`: **Centralized API Client**. Uses Axios with a configured `baseURL` for easy environment switching (Local vs Production with Nginx).
- `postcss.config.js`: Configured for `@tailwindcss/postcss`.

## 🌐 API Configuration

API requests are managed centrally via `src/api/index.js`.
- **Development**: Defaults to `http://127.0.0.1:8000`.
- **Production (Nginx)**: Set `VITE_API_BASE_URL` in `.env` or use relative paths (e.g., `/api`) to allow Nginx to handle port forwarding/proxying.

To configure the API URL:
1. Create a `.env` file in the `Front` directory.
2. Add `VITE_API_BASE_URL=your_api_url`.


## 🚀 Running the Project

```bash
npm install
npm run dev
```
