# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.models.expense import Expense
import json

llm = ChatOpenAI(model="gpt-4", temperature=0)


PROMPT = ChatPromptTemplate.from_template("""
Extract structured expense info from the message.

Message:
"{message}"

Return ONLY valid JSON:
{
  "amount": number,
  "merchant": string,
  "category": string
}
""")
