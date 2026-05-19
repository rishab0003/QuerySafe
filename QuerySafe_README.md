# QuerySafe 🔒

> **Your Database Speaks Human — Securely**

An AI-powered, read-only natural language database assistant built for enterprise non-technical teams. Ask your company database questions in plain English. Get instant, secure, encrypted answers — no SQL knowledge required.

---

## What is QuerySafe?

QuerySafe lets employees from HR, Finance, Sales, and Support query company databases using plain English — without writing a single line of SQL. The AI converts natural language into safe, read-only database queries, enforces role-based access, and never modifies your data.

**Example queries:**
- *"Show all customers who signed up last week"*
- *"What are the top-selling products this month?"*
- *"Get all invoices above ₹50,000 for the Finance team"*
- *"How many support tickets are unresolved?"*

---

## Core Features

| Feature | Description |
|---|---|
| Natural language queries | Ask questions in plain English — no SQL needed |
| Read-only enforcement | AI can only SELECT. INSERT, UPDATE, DELETE are blocked at 2 levels |
| End-to-end encryption | Database credentials encrypted with AES-256. Never stored in plaintext |
| Two-factor authentication | Email OTP + authenticator app (TOTP) + Google SSO |
| Role-based access control | HR sees HR data. Sales sees Sales data. No cross-department leakage |
| Zero chat retention | Session history auto-deleted. Optional zero-retention mode |
| SQL safety engine | Every generated SQL is validated before execution |
| AI explainability | See what SQL was generated, which tables were used, and confidence score |
| Auto dashboard generation | Type "Create monthly sales dashboard" — charts appear instantly |
| Multi-database support | PostgreSQL, MySQL, MongoDB, SQL Server, Snowflake, BigQuery |

---

## Team Structure

This project is divided across **5 people**, each owning a complete vertical.

---

### Person 1 — AI & LLM Engineer
**Module:** `/backend/ai/`
**Role:** Brain of QuerySafe

**Responsibilities:**
- LangChain / LangGraph orchestration pipeline
- Natural language → SQL generation (GPT-4 / Claude)
- Schema-aware prompting with ChromaDB vector store
- Intent detection (query / explain / dashboard)
- AI explainability panel (confidence score, reasoning chain)
- Redis session memory (last 5 messages per session)
- Auto dashboard chart config generation

**Tech Stack:**
- Python, FastAPI
- LangChain, LangGraph
- OpenAI API / Anthropic Claude API
- ChromaDB (vector store)
- Sentence Transformers (embeddings)
- Redis (session memory)

**API Endpoints:**
```
POST  /ai/query        → accepts user_prompt, schema_context, role, session_id
POST  /ai/explain      → returns reasoning behind SQL generation
POST  /ai/dashboard    → generates chart config from natural language
```

---

### Person 2 — Security & Auth Engineer
**Module:** `/backend/auth/` + `/backend/security/`
**Role:** Shield of QuerySafe

**Responsibilities:**
- JWT authentication (access + refresh tokens)
- Two-factor authentication (TOTP via pyotp, QR code setup)
- SQL Safety Engine — validates every generated SQL before execution
- RBAC system — role-based table and column access per department
- AES-256 credential encryption
- Prompt injection detection
- Audit logging (every query logged with user, timestamp, result)
- Rate limiting and query timeout enforcement

**Tech Stack:**
- Python, FastAPI
- JWT (python-jose)
- pyotp (TOTP/2FA)
- sqlparse (SQL AST validation)
- cryptography (AES-256)
- bcrypt (password hashing)
- Redis (token blacklist)
- SQLAlchemy

**API Endpoints:**
```
POST  /auth/register       → create account
POST  /auth/login          → returns JWT + triggers 2FA
POST  /auth/verify-2fa     → validate TOTP code
POST  /auth/setup-2fa      → generate QR code
POST  /auth/refresh        → refresh access token
POST  /auth/logout         → blacklist token

POST  /security/validate-sql  → {sql} → {is_safe, reason, blocked_keywords}
```

**SQL Safety Rules:**
- Blocks: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `EXEC`, `TRUNCATE`, `GRANT`, `REVOKE`
- Max 500 rows per query
- Max 10 second query timeout
- Full-table scan detection
- Prompt injection pattern matching

---

### Person 3 — Database & API Engineer
**Module:** `/backend/database/`
**Role:** Connector of QuerySafe

**Responsibilities:**
- Multi-database adapter system (PostgreSQL, MySQL, MongoDB, Snowflake, BigQuery)
- Database connection management with encryption
- Schema extraction and indexing pipeline
- Read-only transaction enforcement at driver level
- Connection pooling with Redis
- Internal QuerySafe metadata database schema and migrations
- RBAC row-level restriction injection

**Tech Stack:**
- Python, FastAPI
- SQLAlchemy, psycopg2, pymysql, pymongo
- Redis (connection pool)
- PostgreSQL (QuerySafe metadata DB)

**API Endpoints:**
```
POST    /database/connect              → encrypt credentials, test connection, return connection_id
GET     /database/schema/{id}         → extract tables, columns, types, relationships
POST    /database/execute             → run validated read-only SQL, return rows + metadata
DELETE  /database/disconnect/{id}     → remove active connection
```

**Database Adapters:**
```
/backend/database/adapters/
├── base.py        → abstract interface
├── postgres.py    → PostgreSQL adapter
├── mysql.py       → MySQL adapter
└── mongodb.py     → MongoDB adapter (SQL → aggregation translation)
```

---

### Person 4 — Frontend Engineer
**Module:** `/frontend/`
**Role:** Face of QuerySafe

**Responsibilities:**
- Landing page with animated AI pipeline visualization
- Auth flow (login, register, 2FA setup)
- Main dashboard with ChatGPT-style chat interface
- SQL generation panel with explainability drawer
- Department switcher (HR / Finance / Sales / Support)
- Attack simulation demo (DROP table → blocked)
- Auto dashboard generator with Recharts
- Dark mode, responsive design, smooth animations

**Tech Stack:**
- Next.js 14 (App Router)
- TailwindCSS
- Shadcn UI
- Framer Motion (animations)
- Recharts (dashboard charts)
- React Query + Axios
- Zustand (state management)

**Pages:**
```
/                    → Landing page (hero, demo, features)
/auth/login          → Email + password + 2FA
/auth/register       → Sign up with department selection
/auth/setup-2fa      → QR code for authenticator app
/dashboard           → Main chat interface + DB connector
/dashboard/charts    → Auto-generated dashboards
```

---

### Person 5 — DevOps & Infra Engineer
**Module:** Root config, Docker, CI/CD
**Role:** Foundation of QuerySafe

**Responsibilities:**
- Docker + Docker Compose setup for all 5 services
- Nginx reverse proxy configuration
- GitHub Actions CI/CD pipeline
- PostgreSQL migration scripts
- Environment variable management
- README and API documentation
- Security headers and VPC isolation config

**Tech Stack:**
- Docker, Docker Compose
- Nginx
- GitHub Actions
- PostgreSQL (migrations)
- Redis

**Services in Docker Compose:**
```
backend   → FastAPI app          (port 8000)
frontend  → Next.js app          (port 3000)
postgres  → Metadata database    (port 5432)
redis     → Session + cache      (port 6379)
chroma    → Vector store         (port 8001)
nginx     → Reverse proxy        (port 80)
```

---

## Project Folder Structure

```
querysafe/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── auth/
│   │   ├── routes.py
│   │   ├── jwt.py
│   │   ├── totp.py
│   │   └── models.py
│   ├── ai/
│   │   ├── routes.py
│   │   ├── pipeline.py
│   │   ├── embeddings.py
│   │   ├── memory.py
│   │   └── dashboard.py
│   ├── database/
│   │   ├── routes.py
│   │   ├── pool.py
│   │   ├── schema_indexer.py
│   │   └── adapters/
│   │       ├── base.py
│   │       ├── postgres.py
│   │       ├── mysql.py
│   │       └── mongodb.py
│   ├── security/
│   │   ├── sql_validator.py
│   │   ├── rbac.py
│   │   ├── encryption.py
│   │   └── audit.py
│   └── vector/
│       └── schema_store/
├── frontend/
│   ├── app/
│   │   ├── page.tsx              (landing)
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── setup-2fa/page.tsx
│   │   └── dashboard/
│   │       ├── page.tsx          (chat)
│   │       └── charts/page.tsx
│   ├── components/
│   ├── lib/
│   └── package.json
├── migrations/
│   └── 001_init.sql
├── nginx/
│   └── nginx.conf
├── docker-compose.yml
├── .github/
│   └── workflows/ci.yml
└── README.md
```

---

## Getting Started

### Prerequisites
- Docker & Docker Compose installed
- Git
- OpenAI API key or Anthropic API key

### 1. Clone the repository

```bash
git clone https://github.com/your-org/querysafe.git
cd querysafe
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

```env
# Database
DATABASE_URL=postgresql://postgres:password@postgres:5432/querysafe

# Redis
REDIS_URL=redis://:password@redis:6379

# AI
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Security
JWT_SECRET=your-super-secret-jwt-key-here
ENCRYPTION_KEY=your-32-byte-aes-encryption-key

# Vector Store
CHROMA_URL=http://chroma:8001

# Frontend
NEXT_PUBLIC_API_URL=http://localhost/api
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

### 4. Access the app

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost/api |
| API Docs (Swagger) | http://localhost/api/docs |
| ChromaDB | http://localhost:8001 |

---

## 3-Day Build Plan

### Day 1 — Foundation
| Person | Task |
|---|---|
| P5 | Set up Docker Compose, folder structure, Nginx, run all services locally |
| P2 | Build auth endpoints, JWT, 2FA, SQL safety engine |
| P3 | Build database adapters (PostgreSQL + MySQL), connection manager |
| P4 | Landing page, auth UI (login, register, 2FA) |
| P1 | ChromaDB setup, LangChain pipeline skeleton, embeddings |

### Day 2 — Core Build
| Person | Task |
|---|---|
| P1 | Complete AI query pipeline, Redis memory, confidence scoring |
| P2 | RBAC system, credential encryption, audit logging |
| P3 | Schema indexer, MongoDB adapter, read-only transaction enforcement |
| P4 | Dashboard chat interface, SQL panel, explainability drawer |
| P5 | GitHub Actions CI, migration scripts, integration testing |

### Day 3 — Integration & Polish
| Person | Task |
|---|---|
| All | Connect frontend (P4) to backend APIs (P1 + P3) |
| P1 + P2 | Wire SQL validator into AI pipeline |
| P4 | Dashboard chart generator, dark mode polish, mobile responsive |
| P5 | End-to-end testing, README, final Docker build |

---

## Security Architecture

```
User Request
     ↓
[2FA + JWT Auth]           ← Person 2
     ↓
[RBAC Permission Check]    ← Person 2
     ↓
[AI Pipeline]              ← Person 1
     ↓
[SQL Safety Engine]        ← Person 2 (validates generated SQL)
     ↓
[Read-Only DB Driver]      ← Person 3 (enforced at connection level)
     ↓
[Audit Log]                ← Person 2
     ↓
Response to User
```

Security is enforced at **three independent layers**:
1. Prompt level — system prompt instructs LLM to generate SELECT only
2. SQL validator — sqlparse AST inspection rejects any non-SELECT statement
3. Database driver — connection opened in read-only transaction mode

---

## API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | /auth/register | Create account |
| POST | /auth/login | Login + trigger 2FA |
| POST | /auth/verify-2fa | Validate TOTP code |
| POST | /auth/setup-2fa | Get QR code |
| POST | /auth/refresh | Refresh JWT |
| POST | /auth/logout | Logout + blacklist token |

### Database
| Method | Endpoint | Description |
|---|---|---|
| POST | /database/connect | Connect a database |
| GET | /database/schema/{id} | Get schema metadata |
| POST | /database/execute | Run read-only query |
| DELETE | /database/disconnect/{id} | Remove connection |

### AI
| Method | Endpoint | Description |
|---|---|---|
| POST | /ai/query | Natural language → SQL → result |
| POST | /ai/explain | Explain why SQL was generated |
| POST | /ai/dashboard | Generate chart config |

### Security
| Method | Endpoint | Description |
|---|---|---|
| POST | /security/validate-sql | Validate SQL safety |

---

## Role-Based Access

| Role | Access |
|---|---|
| Admin | All tables, all departments |
| HR | employees, departments, payroll |
| Finance | invoices, expenses, budgets, transactions |
| Sales | customers, orders, products, leads |
| Support | tickets, users (read), responses |

---

## Supported Databases

- PostgreSQL
- MySQL
- MongoDB
- Microsoft SQL Server
- Snowflake
- Google BigQuery

---

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TailwindCSS, Shadcn UI, Framer Motion |
| Backend | Python, FastAPI |
| AI | GPT-4 / Claude, LangChain, LangGraph |
| Vector DB | ChromaDB, Sentence Transformers |
| Cache / Memory | Redis |
| Metadata DB | PostgreSQL |
| Auth | JWT, pyotp, bcrypt |
| Encryption | AES-256 (cryptography library) |
| SQL Safety | sqlparse |
| Deployment | Docker, Docker Compose, Nginx |
| CI/CD | GitHub Actions |

---

## Contributing

1. Each person works on their own module branch
2. Branch naming: `feature/p1-ai-pipeline`, `feature/p2-security`, etc.
3. Open a pull request to `main` — another team member reviews
4. P5 handles merges and deployment

---

## License

MIT License — QuerySafe Team 2026

---

*Built in 3 days. Secured by design. Powered by AI.*
