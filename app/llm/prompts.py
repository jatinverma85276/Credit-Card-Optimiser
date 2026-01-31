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

# Prompt for formatting recommendations
FORMAT_RECOMMENDATION_PROMPT = """
You are a helpful assistant that formats credit card recommendations in a clear and friendly way.

Given the following recommendation details:
- Card: {card}
- Expected Return: {expected_return}%
- Reason: {reason}
- Purchase Details: {expense_details}

Format this into a clear, conversational response that explains the recommendation to the user.
Include the card name, expected return percentage, and the reason for the recommendation.

Example output:
"Based on your purchase at [Merchant] for ₹[Amount], I recommend using your [Card Name] card. You can expect a return of [X]% because [reason]."

Guidelines:
- Keep it concise (1-2 sentences)
- Include the merchant and amount if available
- Make it sound natural and conversational
- Don't include any special formatting or markdown
- Don't include the word 'Recommendation:' or similar prefixes

Format the response to be friendly and easy to understand.
"""