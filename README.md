# Business question: What are the primary drivers of customer renewals for RoadGuard Car Insurance?

A small Streamlit app will collects, labels, and analyzes **why returning
customers chose to renew** with a car insurance company. Each feedback comment
is classified into one of four business features — **price**, **coverage**,
**quality of service**, or **other** — and the owner gets a live dashboard that
answers a single question:

The app is a prototype for **customer-retention analytics**. It replaces the
"we think they came back for the price" gut feeling with a labelled,
quantifiable, and reviewable data trail.

---

## Business context

Returning customers are the cheapest revenue a car insurer has. Renewal costs a
fraction of acquisition. Once the company be aware of that, it can allocate resource to maintain or improve some area of this business like: Price, Coverage, Quality of serviceor other.


This app captures that "why" at the point of renewal, in the customer's own
words, and turns it into four measurable buckets the business can act on:

| Labels | Definition | What it tells the business |
| :--- | :--- | :--- |
| **Price** | Feedback related to cost, perceived value, and how pricing compares to competitors. | We are winning on premium. Upside: cross-sell. Risk: price war. |
| **Coverage** | Feedback highlighting product variety, uniqueness, or design as a key competitive advantage. | Our product design is the differentiator. Keep investing in it. |
| **Quality of service** | Feedback on overall customer experience, including support agents, claims, and app usability. | Claims, agents, or app experience are working. Protect it. |
| **Other** | Vague, off-topic, or unclassifiable feedback that requires manual human review. | Not yet classifiable, so it worth a human read. |

The dashboard's **"Read carefully"** list surfaces two kinds of risk:

1. Comments the classifier could not place (labelled `other`), and
2. Returning customers who rated the service **2 stars or fewer** — they
   renewed, but they are unhappy and are a churn risk at the next renewal.

---

## Features

- **Customer-facing tab** — one short text box, a star rating, and a
  "Send" button. The comment is sent to an LLM, which returns a single
  feature label. The result is saved to `feedback.csv`.
- **Owner-facing tab** — KPIs, three charts, and a prioritised reading list.
  - Total reasons, **Top reason (with % share)**, average stars, count of
    reasons to read carefully.
  - Reasons by feature (bar chart).
  - Average stars by feature (bar chart).
  - Reasons by feature and star rating (stacked bar chart).
  - **"Read carefully"** table: unclassified reasons and low-rated renewals.
  - Full feedback table, CSV download, and a reminder that Streamlit Cloud
    does not persist the CSV across restarts.
- **Labels are computed by an LLM** (Groq's `openai/gpt-oss-20b` by default),
  following this instruction:

  > *"Label the comment with exactly one of: price, coverage, quality of
  > service, or other. If more than one feature of the service is mentioned,
  > label by the first mentioned."*

- **Robust to model drift** — a small alias map (`cost → price`,
  `service → quality of service`, `cover → coverage`, …) ensures common
  near-misses don't fall into `other`.

---

## How it works

a) GO to the app
https://hszuauz4cunk8cqdbwjkws.streamlit.app/

b) introduce Some example of customer feedback in the tab "Returning customer: share your reason":

The price was a great deal

WHen I needed the agent came to help me out so fast!

The premium covered 24/7 mechanical assistance, it was awesome! 

your premium was the cheapest I found this year 

When I call , the agents are so kind

Your app was to easy to work with

You are the best
