# DevStart AI 🚀
### AI-Powered Developer Assistant

DevStart AI is a Chrome extension designed to help developers understand, analyze, and improve unfamiliar code repositories using Artificial Intelligence.

It assists developers with project onboarding, code analysis, identifying potential issues, and suggesting improvements through an AI-powered workflow.

---

## 📌 Features

- **Repository Understanding** – Helps developers understand unfamiliar repositories, project structures, and documentation.
- **Project Onboarding** – Provides guidance on project setup, dependencies, and getting started.
- **AI Code Analysis** – Analyzes source code to identify potential bugs, code smells, and areas for improvement.
- **Code Suggestions** – Generates explanations and proposed code improvements.
- **Pull Request Integration** – Allows users to review proposed changes and create GitHub Pull Requests after approval.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| HTML, CSS, JavaScript | Chrome Extension Frontend |
| Python | Backend Development |
| FastAPI | Backend API |
| Render | Backend hosting |
| Gemini API | AI-Powered Code Analysis |
| Semgrep | Static Code Analysis |
| GitHub API | Repository Access and Pull Requests |

---

## 📂 Project Structure

```text
devstart-ai/
├── .github/
│   └── workflows/          # GitHub Actions and CI/CD
│
├── extension/              # Chrome Extension
│   ├── manifest.json
│   ├── service-worker.js
│   ├── sidepanel/
│   │   ├── sidepanel.html
│   │   ├── sidepanel.css
│   │   └── sidepanel.js
│   └── assets/
│
├── backend/                # Python + FastAPI
│   ├── main.py
│   ├── requirements.txt
│   ├── routes/
│   ├── services/
│   └── config/
│
├── docs/                   # Project Documentation
├── tests/                  # Testing
│
├── .gitignore
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

---

## ⚙️ Getting Started

### Prerequisites

Before setting up DevStart AI, make sure you have:

- [Google Chrome](https://www.google.com/chrome/)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Python](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- A [Google AI Studio](https://aistudio.google.com/) API key
- A GitHub account

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd devstart-ai
```

### 2. Set Up the Chrome Extension

1. Open Google Chrome.
2. Navigate to `chrome://extensions/`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the project's `extension/` folder.

### 3. Set Up the Python Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn main:app --reload
```

The local API will be available at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 🔐 Environment Configuration

Store API keys and private credentials in environment variables.

Create a `.env` file inside the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_token
```

**Important:**
- Never commit `.env` files or private credentials.
- Never expose secret API keys in the Chrome extension's JavaScript files.
- Analysis results are kept in memory only and are not persisted by the backend.

---

## 🤝 Contributing

Contributions from team members and developers are welcome.

1. Fork or clone the repository.
2. Create a new branch for your changes.
3. Make and test your changes.
4. Commit and push your branch.
5. Submit a Pull Request for review.

Example:

```bash
git checkout -b feature/your-feature
git add .
git commit -m "Add: your feature description"
git push origin feature/your-feature
```

Please follow the project's coding conventions and contribution guidelines.

---

## 👥 Development Team

| Member | Responsibility |
|---|---|
| Nicko | Project Lead / Documentation |
| Wen | Frontend Developer / UI/UX Designer |
| Justine | Backend Developer / Firebase Engineer |
| Jiliane | Verification / DevOps Engineer |

---

## 🔒 Security

DevStart AI is designed to support developer productivity while keeping users in control of code changes.

- Users review proposed code changes before approval.
- Code modifications are not automatically merged.
- API credentials and sensitive information must be protected.
- Repository analysis should avoid exposing secrets or private credentials.

---

## 📄 License

This project is intended to be released under the [MIT License](https://opensource.org/license/mit/). See the `LICENSE` file for details.

---

**Built with ❤️ by the DevStart AI Team.**
