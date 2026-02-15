# OneLake PDF Viewer

A production-ready full-stack application for browsing and viewing PDF reports stored in **Microsoft Fabric OneLake** (Lakehouse Files folder).

| Layer    | Stack                                            |
| -------- | ------------------------------------------------ |
| Frontend | React 18 · Vite 6 · Axios                       |
| Backend  | FastAPI · Uvicorn · Azure Identity & ADLS Gen2   |
| Auth     | Azure AD Service Principal (+ placeholder API key middleware) |
| Infra    | Docker · Docker Compose                          |

---

## 📁 Folder Structure

```
onelake-pdf-viewer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry-point, CORS, health-check
│   │   ├── config.py          # pydantic-settings configuration
│   │   ├── auth.py            # Placeholder auth middleware (API key)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── files.py       # GET /files  &  GET /files/{filename}
│   │   └── services/
│   │       ├── __init__.py
│   │       └── onelake.py     # Azure OneLake client + filename validation
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .dockerignore
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx            # Root component – orchestrates state
│       ├── api.js             # Axios instance with interceptors
│       ├── index.css          # Global styles (dark theme, glassmorphism)
│       └── components/
│           ├── FileList.jsx   # Sidebar file list with skeletons & error
│           └── PdfViewer.jsx  # PDF display / loading / error / empty
├── docker-compose.yml
└── README.md                  ← you are here
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** & npm
- An **Azure AD Service Principal** with access to your Fabric Lakehouse
- PDF files stored in `<LakehouseName>.Lakehouse/Files/reports/` inside your Fabric workspace

### 1. Clone & configure

```bash
git clone <repo-url>
cd onelake-pdf-viewer

# Backend
cp backend/.env.example backend/.env
# → Edit backend/.env with your Azure credentials

# Frontend (optional – defaults work for dev)
cp frontend/.env.example frontend/.env
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API docs are now available at **http://localhost:8000/docs**.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

> The Vite dev server proxies `/api/*` → `http://localhost:8000`, so CORS is handled automatically during development.

---

## 🐳 Docker Compose

```bash
# Make sure backend/.env exists with your credentials, then:
docker compose up --build
```

- Backend: **http://localhost:8000**
- Frontend: **http://localhost:5173**

---

## 🔐 Authentication & Security

### Service Principal (Backend → OneLake)

The backend authenticates to OneLake using `ClientSecretCredential` from `azure-identity`:

| Variable         | Description                              |
| ---------------- | ---------------------------------------- |
| `TENANT_ID`      | Azure AD tenant ID                       |
| `CLIENT_ID`      | Service Principal (app registration) ID  |
| `CLIENT_SECRET`  | Service Principal secret                 |
| `WORKSPACE_NAME` | Microsoft Fabric workspace name          |
| `LAKEHOUSE_NAME` | Lakehouse name (without `.Lakehouse`)    |

### Placeholder API-Key Middleware (Frontend → Backend)

A simple `X-API-Key` header check is included as a **placeholder**. In production, replace `app/auth.py` with proper Azure AD JWT validation using libraries like `python-jose` or `msal`.

### Security Features

- **Path-traversal prevention** – filenames are validated with a strict regex (no `..`, `/`, `\`)
- **CORS scoping** – only listed origins are allowed
- **No public blob URLs** – PDFs are streamed through the backend, never exposed directly
- **Content-Disposition: inline** – PDFs render in-browser, not downloaded

---

## 🔑 Azure Role Permissions Required

The Service Principal needs the following roles on the **Fabric Workspace** or **Lakehouse**:

| Role / Permission                    | Scope              | Purpose                        |
| ------------------------------------ | ------------------ | ------------------------------ |
| **Storage Blob Data Reader**         | Lakehouse / Workspace | Read PDF files from OneLake   |
| **Workspace Viewer** (Fabric)        | Workspace          | List files in the Lakehouse    |

### How to assign

1. Go to **Azure Portal → Microsoft Entra ID → App Registrations** → select your app.
2. Go to **Fabric Portal → Workspace → Manage Access** → add the Service Principal with **Viewer** role.
3. Optionally, in **Azure Portal → Storage account → Access Control (IAM)**, assign **Storage Blob Data Reader** to the Service Principal (if using direct ADLS Gen2 access).

> **Note:** OneLake uses Fabric workspace roles for authorization. Ensure the Service Principal is added as a member/viewer of the workspace.

---

## 📡 API Endpoints

| Method | Path               | Auth       | Description                       |
| ------ | ------------------ | ---------- | --------------------------------- |
| `GET`  | `/health`          | None       | Liveness probe                    |
| `GET`  | `/files`           | `X-API-Key`| List PDF filenames                |
| `GET`  | `/files/{filename}`| `X-API-Key`| Stream a PDF as `application/pdf` |

### Example

```bash
# List files
curl -H "X-API-Key: changeme-in-production" http://localhost:8000/files

# Download a PDF
curl -H "X-API-Key: changeme-in-production" \
     -o report.pdf \
     http://localhost:8000/files/quarterly-report.pdf
```

---

## 🏗️ Production Checklist

- [ ] Replace placeholder API-key auth with Azure AD JWT validation
- [ ] Build the React frontend (`npm run build`) and serve via nginx or a CDN
- [ ] Set strong, unique `API_KEY` / JWT secrets
- [ ] Enable HTTPS (TLS termination via reverse proxy or cloud load balancer)
- [ ] Restrict `CORS_ORIGINS` to your production domain
- [ ] Add rate limiting (e.g. via nginx or a middleware like `slowapi`)
- [ ] Set up monitoring & alerting (Application Insights, Prometheus, etc.)
- [ ] Use Azure Key Vault for secrets instead of `.env` files
- [ ] Add unit & integration tests

---

## 📄 License

MIT – see [LICENSE](./LICENSE) for details.
