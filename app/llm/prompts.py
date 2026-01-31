from langchain_core.prompts import ChatPromptTemplate

PARSE_EXPENSE_PROMPT = ChatPromptTemplate.from_template("""
Extract structured expense info from the message.

Message:
"{message}"

Return ONLY valid JSON in the following format:
{{
  "amount": number,
  "merchant": string,
  "category": string
}}
""")


CARD_INGEST_PROMPT = ChatPromptTemplate.from_template("""
You are an expert at extracting structured credit card information from unstructured text.
Extract ONLY valid JSON in the following format:

{{
  "card_name": string,
  "card_type": "credit" | "debit",
  "annual_fee": number,
  "annual_fee_tax_applicable": boolean,
  "welcome_bonus": {{
      "type": string,
      "amount": number,
      "condition": string
  }},
  "fee_waiver": {{
      "type": string,
      "condition": string
  }},
  "cashback_rules": [
    {{
      "category": string,
      "percentage": number,
      "monthly_cap": number | null
    }}
  ],
  "reward_rules": [
    {{
      "category": string,
      "points_per_unit": number,
      "unit_amount": number,
      "monthly_cap": number | null
    }}
  ],
  "special_vouchers": [
    {{
      "amount": number,
      "milestones": [number],
      "frequency": string
    }}
  ],
  "emi_options": {{
      "available": boolean,
      "interest_rate": number
  }},
  "exclusions": [string],
  "eligibility": {{
      "residency": string,
      "income": {{
          "salaried": number,
          "self_employed": number
      }},
      "age": number,
      "bank_account": boolean,
      "credit_history": string,
      "company_trade_duration": number
  }},
  "other_benefits": [string]
}}

Card description:
"{description}"
""")