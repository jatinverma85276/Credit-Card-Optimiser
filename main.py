from langchain_core.messages import HumanMessage
from app.graph.graph import build_graph

graph = build_graph()

result = graph.invoke({
    "messages": [
        HumanMessage(content="""/add_card   American Express SmartEarn™ Credit Card
Rs. 500 cashback as a Welcome Gift in form of statement credit on eligible spends1 of Rs. 10,000 in the first 90 days of Cardmembership

American Express is accepting applications for select Cards. Explore your options and apply today.

Compare Card
Card Type
Credit Card
Annual fee
Annual Fee of Rs. 495 plus applicable taxes
Reward Earn Rate
Earn Accelerated Membership Rewards® points2 when you spend on Amazon, Flipkart, Uber, BookMyShow, Zomato, EaseMyTrip and many more.
Fee Waiver
Get a renewal fee waiver on eligible spends3 of Rs.40,000 and above in the previous year of Cardmembership
Key Benefits
Accelerated Earn Rate
Earn Accelerated Membership Rewards® points2 when you spend on Amazon, Flipkart, Uber, BookMyShow, Zomato, EaseMyTrip and many more.
Welcome Bonus
Rs. 500 cashback as a Welcome Gift on eligible spends1 of Rs. 10,000 in the first 90 days of Cardmembership
GIFT VOUCHERS
Earn vouchers worth ₹500 upon reaching the spend milestones of ₹1.20 lacs, ₹1.80 lacs, and ₹2.40 lacs respectively in a Cardmembership year.
Renewal Fee Waiver
Get a renewal fee waiver on eligible spends3 of Rs.40,000 and above in the previous year of Cardmembership
AMERICAN EXPRESS EMI
Convert purchases into EMI at the point of sale with an interest rate as low as 14% p.a.
Rewards Programme
10X Membership Rewards®
Transact on Zomato, Ajio, Nykaa, BookMyShow, Uber and many more and get 10X rewards for every Rs. 50 spent
5X Membership Rewards®
Transact on Amazon and get 5X rewards for every Rs. 50 spent
Earn 1 Membership Rewards Point for every Rs. 50 spent except for spends on Fuel, Insurance, Utilites, Cash Transactions and EMI conversion at Point of Sale4.
Did you know you can earn up to 1,250 Membership Rewards points on the SmartEarn Credit Card every month by spending only INR 7,500?
So now, spend more and enjoy accelerated benefits with your American Express SmartEarn Credit Card:
On Spending INR 2500 in a month on our 10X Partner (Zomato), you will earn 500 Membership Rewards points
On Spending INR 2500 in a month on our 10X Partner (BookMyShow, Flipkart, Uber and other partners), you will earn 500 Membership Rewards points
On Spending INR 2500 in a month on our 5X Partner (Amazon), you will earn 250 Membership Rewards points
Offers and Privileges
Enjoy convenience, exclusive benefits, assistance at any hour and much more. Your American Express SmartEarnTM Credit Card brings a host of special privileges, only for you.
Enjoy freedom and convenience
Enjoy the flexibility and convenience to pay your Credit Card bill, fully or partially. You can also convert your spends into easy monthly instalments with the American Express EMI
Fuel Convenience Fee Waiver at HPCL
Services on your Card
24X7 Card Related Assistance
Dispute Resolution
Zero Lost Card Liability5
Emergency Card Replacement
Contactless Payment
Your American Express Card may be enabled for contactless payments. To see if your Card is contactless, look for the contactless symbol network on the front and back of your Card.
Eligibility
To save time before you apply for your Card, it’s best to make sure you can say yes to the following:
I/We confirm that I / supplementary card applicant/s is a Resident Indian as defined under the Income Tax Act of India and hereby declare that I/We will notify American Express Banking Corp. if there is a change in the residential status.
I understand American Express Cards are currently issued to residents of Delhi/NCR, Mumbai, Bangalore, Chennai, Pune, Hyderabad, Jaipur, Indore, Coimbatore, Chandigarh, Ahmedabad, Surat, Vadodra, Lucknow, Ludhiana, Nagpur, Nasik, Trivandrum and Mysuru subject to condition.
I am Employed and have a Personal Annual Income of INR 4.5 lakhs and above or Self Employed with a Personal Annual Income of INR 6 lakhs and above.
I have an Indian or multinational bank’s savings or current account in India
I have a current / permanent residential address in India
I am over 18 years of age
I have a good credit history and no payment defaults
If self-employed: My company has been trading for more than 12 months
Most Important Terms & Conditions

American Express SmartEarn™ Credit Card
Get cashback of Rs. 500 as a Welcome Gift on spending Rs. 10,0001 in the first 90 days of Cardmembership
Footnotes
1.Eligible spends do not include cash advances, express cash transactions, drafts made from the Account, balance transfers and fees. Statement Credit will be given within 10 working days of completion of eligible spends.
Welcome Gift is available only in the 1st year on payment of the annual fee and on spending INR 10,000 within 90 days of Cardmembership.

2. For example, for a spend of Rs. 50 on an eligible merchant the Cardmember will get 10 Membership Rewards® points (if merchant is under 10X category) and 5 Membership Rewards® points (if merchant is under 5X category). Under 10X category, 10X Membership Rewards® points will be capped at 500 Points per month per Card Account jointly for Flipkart, Uber, BookMyShow and other merchants put together. 10X Membership Rewards® points will be capped at 500 Points per month per Card Account jointly for EaseMyTrip and Zomato. Under 5X category, 5X Membership Rewards® points will be capped at 250 Points per month per Card Account for Amazon put together. Please note that eligible merchant partners may change from time to time. To view the complete list of merchant partners, please visit amex.co/seccrewards. 10X category means Cardmember earns 9 Membership Rewards® points on every Rs. 50 spent at participating merchant(s) over and above the regular Membership Rewards® points earn rate applicable on the Card Account. For example, an eligible spend of Rs. 250 will get the Cardmember 5 regular Membership Rewards® points and 45 additional Membership Rewards® points. 5X category means Cardmember earns 4 Membership Rewards® points on every Rs. 50 spent at participating merchant(s) over and above the regular Membership Rewards® points earn rate applicable on the Card Account. For example, an eligible spend of Rs. 250 will get the Cardmember 5 regular Membership Rewards® points and 20 additional Membership Rewards® points.

3. Eligible spends do not include cash advances, express cash transactions, drafts made from the account, balance transfers and fees.

4. You will not earn Membership Rewards® points on your American Express Card for all your spending on fuel, insurance and utility (electricity, water and gas bills) payments. Fuel includes petrol, diesel, CNG from Oil Marketing Companies (OMCs). Utility services includes providers of household/domestic electricity, gas and water. These providers can be government departments and agencies including local, state, municipal organizations, public housing societies and apartment associations. Telecommunications includes providers of landline phones, mobile phones, internet services, cable and other pay TV services, and calling cards.
Effective February 1, 2020, you would not earn Membership Rewards® points on any EMI option selected from a merchant’s website e.g. online shopping with Amazon or Flipkart etc. and on any EMI option selected at Merchant’s terminal e.g. a Chip and PIN transaction at Croma retail store etc. At the same time, you would continue to earn Membership Rewards® points on all EMI transactions through American Express® SafeKey and on all EMI conversions done post purchase.

5. Cardmember liability is nil if American Express receives the report within 3 working days of the fraud. If the fraud is reported beyond 3 working days then the maximum liability of the customer will be limited to Rs. 1,000. For further details, please refer MITC.""")
    ],
    "route": "general"  # default value
})

print(result["messages"][-1].content)
