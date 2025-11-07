# 📜 Doc-Chat

Chat with your documents using natural language


## Setup

### 1. Clone the Repository

```bash
git clone git@github.com:yildiz-fatih/doc-chat.git
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a file named `.env` in the project root and fill in your credentials:

```
OPENAI_API_KEY=your-api-key-here
```

### 4. Run the App

```bash
python main.py
```

## How to Use

### Example Session

```
> /add my_resume.pdf
✅ Added successfully: my_resume.pdf

> What programming languages do I know?
🤖 Doc-Chat: Based on your resume, you know Python, Go and Java...

📚 Sources:
  [1] my_resume.pdf (Chunk 2)

> /list
📜 Your Documents:
- my_resume.pdf

> /exit
👋 Thanks for using Doc-Chat!
```
