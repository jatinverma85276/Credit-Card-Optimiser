# 💳 Credit Card Optimiser Agent

An intelligent LangGraph-based agent that helps users optimize their credit card usage by providing personalized recommendations based on spending patterns and available card rewards.

## 🚀 Features

- **Smart Credit Card Management**: Add and manage your credit cards with detailed information
- **Intelligent Expense Analysis**: Parse and analyze your expenses to find optimal card usage
- **Reward Optimization**: Get personalized recommendations on which credit cards to use for maximum rewards
- **Persistent Memory**: Built-in conversation memory using SQLite checkpoints
- **Interactive CLI Interface**: Easy-to-use command-line interface for real-time interaction

## 🏗️ Architecture

This project uses **LangGraph** to build a stateful, multi-agent system with the following components:

### Core Graph Structure

- **Router Node**: Routes conversations between finance and general topics
- **Finance Router**: Handles finance-specific routing (card management vs expense analysis)
- **Card Parser**: Extracts credit card details from user input
- **Add Card Node**: Stores credit card information in the database
- **Transaction Parser**: Analyzes expense transactions
- **Reward Calculator**: Computes potential rewards across different cards
- **Decision Engine**: Makes intelligent recommendations
- **LLM Recommendation**: Provides human-readable advice

### Data Flow

```
User Input → Router → Finance Router → [Card Management | Expense Analysis] → Recommendation
```

## 🛠️ Tech Stack

- **LangGraph**: Stateful graph-based agent framework
- **LangChain**: LLM integration and orchestration
- **OpenAI GPT-4o-mini**: Language model for intelligent responses
- **SQLite**: Database for persistent storage (cards and checkpoints)
- **Pydantic**: Data validation and serialization
- **Python**: Core programming language

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Langgraph
```

### 2. Set Up Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application

```bash
python main.py
```

## 💡 Usage Examples

### Adding a Credit Card

```
You: /add_card
Agent: Please paste the credit card details in the following format:
- Card Name:
- Bank:
- Reward Type:
- Annual Fee:
- Cashback Rate:
- Points Rate:
- Miles Rate:
- Categories:
```

### Expense Analysis

```
You: I spent $150 on groceries at Whole Foods yesterday
Agent: Let me analyze this expense and find the best card for you...
[Analyzes your available cards and provides recommendation]
```

### General Conversation

```
You: What's the weather like today?
Agent: I'm here to help with credit card optimization and financial advice. For weather information, you might want to check a weather app or website.
```

## 📁 Project Structure

```
Langgraph/
├── app/
│   ├── db/                 # Database models and repositories
│   ├── graph/              # LangGraph nodes and state management
│   │   ├── graph.py        # Main graph construction
│   │   ├── nodes.py        # Individual node implementations
│   │   └── state.py        # Graph state definitions
│   ├── schemas/            # Pydantic data models
│   ├── tools/              # Utility tools
│   └── utils/              # Helper utilities
├── main.py                 # CLI application entry point
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── cards.db               # SQLite database for cards
└── checkpoints.db         # SQLite database for conversation memory
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Database Setup

The application automatically creates SQLite databases on first run:

- `cards.db`: Stores credit card information
- `checkpoints.db`: Stores conversation history and state

## 🎯 Key Commands

### CLI Commands

- `/add_card`: Add a new credit card to your portfolio
- Natural language expense descriptions for analysis
- General conversation for financial advice

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run tests (if available)
python -m pytest
```

## 🧠 How It Works

1. **Input Processing**: User input is routed based on content analysis
2. **State Management**: LangGraph maintains conversation state across interactions
3. **Intelligent Routing**: Smart routing determines the appropriate processing path
4. **Data Analysis**: Expenses are analyzed against available credit cards
5. **Recommendation Engine**: Provides optimized suggestions based on reward structures
6. **Memory Persistence**: All interactions are stored for context retention

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Notes

### Adding New Nodes

1. Create node function in `app/graph/nodes.py`
2. Add node to graph in `app/graph/graph.py`
3. Update routing logic as needed
4. Test the integration

### Database Schema

Credit cards are stored with the following key fields:

- Card name and issuing bank
- Reward structure (cashback, points, miles)
- Annual fees and rates
- Spending categories

### Memory Management

The system uses LangGraph's checkpoint system to maintain conversation context across sessions, enabling personalized and context-aware interactions.

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**: Ensure your OpenAI API key is correctly set in `.env`
2. **Database Lock**: Restart the application if database locks occur
3. **Memory Issues**: Clear `checkpoints.db` if conversation memory becomes corrupted

### Debug Mode

Add print statements in node functions to trace execution flow and debug routing decisions.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions, issues, or feature requests:

- Create an issue in the repository
- Check existing documentation
- Review the code comments for implementation details

---

**Built with ❤️ using LangGraph and OpenAI**
