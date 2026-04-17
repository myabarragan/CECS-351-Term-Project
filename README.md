# CECS-351-Term-Project - AI Semantic Email Search
CECS 451 - SEC 01 | Professor Ju Cheol Moon | Group 20

Mia Carter, Belle Lopez, Cristina Le, Mya Barragan

**Overview**
Modern email systems rely on keyword-based search, but people don't remember emails by keywords. They remember context:

"The email my professor sent about extending the deadline last month."

"That message about switching our meeting time sometime in February."

AI Semantic Email Search bridges the gap between how humans remember information and how email systems retrieve it. Using transformer-based language models and vector similarity search, users can find emails using natural language descriptions instead of exact phrases or filters.

**The Problem**
As inboxes grow into the thousands, retrieving specific messages becomes increasingly inefficient. Traditional search fails when users can't recall exact wording of the email, forcing multiple attempts with filters and guesswork. This creates real friction for professionals, students, and anyone managing high-volume email.

Key pain points include:
- Time wasted scrolling and refining filters to locate a single message.
- Cognitive load and frustration when users know an email exists but can't surface it.
- Information overload for managers, recruiters, consultants, and students with large inboxes.

**Solution**
A semantic email search platform that lets users query their inbox using natural language. The system converts emails and user queries into high-dimensional embedding vectors, then retrieves the most semantically relevant results, leaving no exact phrasing required.

**AI & Technical Approach**

Email Ingestion - Connect to Gmail via Google Cloud API; extract subject, body, sender, and timestamp.

Preprocessing - Tokenize and normalize text; remove formatting and system-generated noise.

Embedding Generation - Convert each email into a vector using a transformer-based language model.

Vector Storage - Store embeddings in a vector database indexed for fast retrieval.

Query Processing - Embed the user's natural language query using the same model.

Similarity Search - Perform ANN (Approximate Nearest Neighbor) search to find closest email vectors.

Metadata Filtering - Use NER and rule-based parsing to extract temporal/relational cues (e.g., "last week," "from my manager") and refine results.

Ranked Results - Return top emails ranked by semantic similarity + metadata relevance.

**AI Technologies**

Transformer-based text embeddings - capture contextual meaning across email content.

Cosine similarity / vector search - match query embeddings to stored email embeddings.

ANN indexing - enables scalable, fast retrieval over large inboxes.

Named Entity Recognition (NER) - extracts time references, sender roles, and other contextual signals.

OpenAI API - powers the LLM layer for query understanding and the conversational chatbot interface.


**Features (MVP)**

Gmail API integration - authenticate and connect to a user's Gmail inbox via Google Cloud

Semantic search chatbot - conversational interface where users describe the email they're looking for

Email result cards - clean, scannable result view with key fields bolded for readability

Natural language query support - retrieve emails without remembering exact keywords

Figma prototype - full UI flow demonstrating login, chatbot interaction, and search results

**UI Design**

The interface is designed to be minimal, intuitive, and distraction-free across three core screens:

Login Screen - Centered layout with application name, tagline, and essential credential fields only.

AI Chatbot Interface - Conversational design with visually separated user and assistant messages. A clear input box and a highlighted "View Results" action button guide users through the flow naturally.

Search Results Page - Card-style layout separating each retrieved email in a consistent format. Key metadata (sender, subject, date) is bolded for quick scanning.

A single accent color is used throughout for interactive elements, keeping the interface neutral and focused while drawing attention to key actions.

**Dataset Strategy**

Enron Email Dataset - 500,000+ real business emails with sender, recipient, subject, and timestamp metadata.

Email Thread Sum Dataset - ~4,000 email threads (~21,000 emails) with similar metadata structure.

Personal exports (CSV) - Team member email exports providing a student-perspective dataset.

Preprocessing includes subject/body extraction, formatting removal, tokenization, and filtering of system-generated messages.

**Business Model**

Free - Limited semantic searches per month

Premium Subscription - Unlimited search + productivity integrations

Enterprise - Per-seat licensing for organizations

Target users: Professionals, students, recruiters, managers, and anyone managing a high-volume inbox.

**Industry Context**

Productivity Software / Enterprise SaaS - Email remains one of the most widely used communication tools globally. While platforms like Gmail and Microsoft Outlook have integrated AI (Microsoft Copilot, Gemini) for content generation and summarization, no major solution focuses on semantic retrieval across an entire inbox. This project targets that specific, underserved gap.

**Team Contribution**

Cristina Le - Gmail API, Google Cloud integration, OpenAI API connection

Mia Carter - UI/UX design

Mya Barragan - UI/UX design, UI documentation, Github README.md

Belle Lopez - 
