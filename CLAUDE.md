# CLAUDE.md

# AI Job Market Intelligence & Personal Job Assistant

## 1. Project Overview

This project is a personal job-market intelligence and job-search assistant focused primarily on the Austrian technology job market.

The goal is to build a realistic Python + AI + Data Science application that can:

1. Collect job postings from multiple data sources.
2. Clean, normalize and store job-market data.
3. Analyze the Austrian technology job market.
4. Extract skills and other useful information from job descriptions using NLP.
5. Use machine learning for selected analytical tasks.
6. Allow the user to upload and analyze their CV.
7. Match the user's profile/CV against available jobs.
8. Perform semantic search over job postings using embeddings.
9. Use a vector database for retrieval.
10. Use an LLM to explain matches, skill gaps and recommendations.
11. Provide an Angular dashboard through a FastAPI backend.
12. Automate the data-processing workflow as a real data pipeline.

The project is primarily a personal tool for the developer's own job search and learning.

The project should be technically serious, but it must remain manageable for approximately 3–5 weeks of focused development.

---

# 2. Primary Market

## Core market

Austria.

The main locations of interest include:

- Vienna
- Graz
- Linz
- Salzburg
- Innsbruck
- other Austrian cities when data is available

## Optional markets

Serbia and Bosnia and Herzegovina may be added if reliable and legally usable data sources are found.

They are NOT required for the first version.

Do not design the architecture around Serbia/Bosnia unless useful data sources actually exist.

---

# 3. Job Categories

The system should focus on technology jobs relevant to the developer.

## Include

- Java Developer
- Java Software Engineer
- Java Backend Developer
- Java Full Stack Developer
- Software Engineer
- Backend Developer
- Full Stack Developer
- Python Developer
- Python Software Engineer
- Data Engineer
- Data Scientist
- AI Engineer
- DevOps Engineer
- QA Automation / Test Automation where useful

Java jobs should be treated as a broad category rather than only "Java Backend".

Python jobs should also be treated broadly.

## Explicitly exclude

- ML Engineer
- Machine Learning Engineer

Do not create ML Engineer as a target career category.

---

# 4. Main Product Features

## 4.1 Job Collection

The system should support multiple data sources.

Potential sources:

- Apify actors/scrapers where permitted
- Public APIs
- Public datasets
- CSV/JSON imports

The ingestion system must be source-independent.

Do NOT tightly couple the application to one scraper.

Use an abstraction similar to:

```text
data_sources/
    base.py
    adzuna.py
    karriere_at.py
    csv_loader.py

Additional sources should be easy to add later.

5. Data Pipeline

The project must contain a real data pipeline.

The conceptual pipeline is:

Data Sources
     ↓
Collection
     ↓
Raw Data
     ↓
Validation
     ↓
Cleaning
     ↓
Deduplication
     ↓
Normalization
     ↓
PostgreSQL
     ↓
NLP processing
     ↓
Embeddings
     ↓
ChromaDB
     ↓
Analytics / Search / AI

The pipeline should be reproducible.

A developer should be able to run something like:

python -m pipeline.run

and process collected data.

The pipeline should eventually support scheduled execution.

6. Raw vs Processed Data

Do not destroy raw data.

Maintain a distinction between:

raw job data

and

normalized/processed job data

This makes it possible to:

rerun preprocessing
improve NLP extraction
change normalization rules
debug bad records
reproduce results
7. Data Cleaning

The pipeline should handle:

missing values
inconsistent locations
inconsistent salary formats
duplicate job postings
HTML inside descriptions
whitespace/noise
inconsistent company names
inconsistent employment types
inconsistent experience descriptions

Example:

Wien
Vienna
Wien, Österreich
Vienna, Austria

should be normalized where appropriate.

Salary examples:

€55.000 - €70.000
55000-70000 EUR
ab €60.000

should be converted into structured fields where possible:

salary_min
salary_max
currency
salary_period

Do not invent salary information when it is not present.

8. Database

Use PostgreSQL as the primary relational database.

Suggested entities:

Job
Company
Location
Skill
JobSkill
JobSnapshot
CandidateProfile
CandidateSkill

The exact schema may evolve.

Use:

SQLAlchemy
Alembic

Avoid excessively complicated database relationships.

Indexes should be added for fields frequently used for:

filtering
searching
sorting
deduplication
9. NLP

NLP is a major part of the project.

Use NLP to turn unstructured job descriptions into useful structured information.

Possible extraction:

skills
programming languages
frameworks
databases
cloud technologies
tools
years of experience
education requirements
languages
employment type
seniority
location

Potential technologies:

spaCy
regex
sentence-transformers
Hugging Face Transformers where useful

Start simple.

Do NOT immediately use an LLM for every extraction task.

Use deterministic methods/NER/rules where they are sufficient.

10. Skill Taxonomy

Create a normalized skill vocabulary.

Examples:

Postgres
PostgreSQL
PostgreSQL Database

should map to:

PostgreSQL

Similarly:

JS
Javascript
JavaScript

should map to:

JavaScript

The system should distinguish related but different technologies.

For example:

Java != JavaScript

This is extremely important.

The taxonomy should eventually support categories such as:

Programming Language
Framework
Database
Cloud
DevOps
Messaging
Testing
AI/ML
Frontend
Backend
Other
11. Data Science

The project must include real exploratory data analysis.

Use:

Pandas
NumPy
Matplotlib
Seaborn
Jupyter

Questions the system should be able to answer:

Market demand
Which skills are most requested?
Which Java technologies are most common?
Which Python technologies are most common?
How does demand differ between Vienna and other cities?
Which companies post the most relevant jobs?
How does demand change over time?
Salary
Salary distribution
Salary by experience
Salary by location
Salary by technology
Salary by job category
Job characteristics
Junior vs Mid vs Senior
Remote vs hybrid vs onsite
Full-time vs part-time
Required languages
Required experience

Visualizations should be useful, not decorative.

12. Machine Learning

Machine learning should be present, but it is NOT the main purpose of the project.

Do not add ML just to claim "machine learning".

Possible ML features:

Salary prediction

Predict salary/range using features such as:

experience
location
job category
skills
remote status
industry

Potential models:

Linear Regression
Random Forest
Gradient Boosting
XGBoost

Compare models using appropriate metrics.

Document:

train/test split
preprocessing
feature engineering
evaluation metrics
limitations

Do not claim salary predictions are authoritative.

They are estimates based on available data.

Optional second ML task

Job seniority classification:

Junior
Mid
Senior

Only implement this if it adds genuine value.

13. CV Analysis

The user should be able to upload a CV in PDF format.

The system should extract:

skills
programming languages
frameworks
databases
cloud technologies
experience
education
languages
relevant projects

The result should be converted into a structured candidate profile.

Example:

{
    "skills": [
        "Java",
        "Spring Boot",
        "PostgreSQL",
        "Docker"
    ],
    "languages": [
        "German",
        "English"
    ],
    "experience_years": 2
}

Do not permanently store the CV unless explicitly needed.

14. Job Matching

The system should calculate how well the user's profile matches a job.

Matching should combine multiple signals.

Possible components:

Skill overlap
+
Experience compatibility
+
Location
+
Job category
+
Semantic similarity

Example:

Java Backend Developer
Match: 87%

Strong matches:
✓ Java
✓ Spring Boot
✓ PostgreSQL
✓ Docker

Missing/common skills:
✗ AWS
✗ Kubernetes
✗ Kafka

Do not pretend the score is objectively "87% qualified".

Label it as:

Match Score

and explain how it was calculated.

15. Embeddings and Semantic Search

Use embeddings to represent job descriptions and candidate profiles.

Preferred initial stack:

sentence-transformers
+
ChromaDB

ChromaDB is intentionally selected because the developer already has experience with it.

Do NOT replace ChromaDB with Qdrant merely for the sake of using another technology.

Potential embedding model:

paraphrase-multilingual-MiniLM-L12-v2

or another suitable multilingual model.

The system should support queries such as:

"Find Java jobs in Vienna that are similar to my experience."

Semantic retrieval should find jobs even when exact keywords do not match.

16. RAG

Implement a RAG component over the collected job data.

Example query:

What skills are most commonly requested
for Java developers in Vienna?

The system should:

User question
    ↓
Embedding
    ↓
ChromaDB retrieval
    ↓
Relevant jobs
    ↓
LLM
    ↓
Grounded answer

The LLM should use retrieved job data rather than inventing market statistics.

Whenever possible, the answer should reference the underlying jobs/data.

17. AI Features

The LLM may be used for:

job description summarization
skill extraction when traditional NLP is insufficient
CV analysis assistance
match explanation
skill-gap analysis
job-market Q&A
personalized learning recommendations
semantic job search assistance
RAG-based market analysis

Example:

Why am I a weak match for this job?

The AI should answer using:

user's profile
job requirements
retrieved data

Do NOT build a generic chatbot unrelated to the job-market system.

18. Explicitly Excluded AI Feature

Do NOT implement:

Cover letter generation
Cover letter optimization

The project should focus on:

finding
understanding
comparing
and analyzing
jobs

rather than generating application documents.

19. Backend

Use:

Python
FastAPI
Pydantic
SQLAlchemy
Alembic

FastAPI should expose APIs for:

jobs
search
filtering
analytics
candidate profile
CV analysis
matching
semantic search
RAG queries

Keep API boundaries clean.

20. Frontend

Use:

Angular

The frontend should provide:

Dashboard

Show:

number of jobs
jobs by city
jobs by category
most demanded skills
salary statistics
trends
Job Search

Filters:

city
job category
Java/Python/etc.
experience
salary
remote/hybrid
date
Job Details

Show:

title
company
location
salary
description
extracted skills
match score
Candidate Profile

Show:

extracted CV skills
experience
languages
skill gaps
AI Assistant

Allow questions about:

jobs
skills
market trends
user's profile
21. Docker

Use Docker for the infrastructure.

Initial services:

PostgreSQL
ChromaDB
FastAPI
Angular

Potential later services:

Redis
Airflow
MLflow

Do not add all of them immediately.

22. Airflow / Scheduling

Airflow is optional for the first version.

First build the pipeline as ordinary Python modules.

After the pipeline works, Airflow may be introduced to orchestrate:

collect jobs
     ↓
clean
     ↓
deduplicate
     ↓
store
     ↓
NLP
     ↓
embeddings
     ↓
update ChromaDB

Example schedule:

daily

Do not introduce Airflow before there is a working pipeline to orchestrate.

23. Redis

Redis is optional.

Potential future use:

caching expensive queries
caching analytics
rate limiting
temporary job-processing state

Do not add Redis unless a concrete problem requires it.

24. Kafka

Kafka is NOT part of the initial implementation.

Do not introduce Kafka just because it is commonly requested in job descriptions.

It may be explored later if the data ingestion architecture genuinely benefits from event-driven processing.

If introduced, it should have a clear purpose such as:

JobCollected
     ↓
Kafka
     ↓
NLP processor
     ↓
Embedding processor
     ↓
Analytics
25. MLflow

MLflow is optional.

It may be introduced if multiple ML experiments/models need to be tracked.

Do not add MLflow merely to increase the technology list.

26. Architecture Philosophy

Prefer:

Modular monolith

over microservices.

The system should have logical modules such as:

ingestion
pipeline
jobs
analytics
nlp
ml
embeddings
candidate
matching
rag
api

Do NOT create:

10 microservices

for a personal 3–5 week project.

27. Code Quality

Use:

type hints
Pydantic models
clear naming
small functions
dependency injection where appropriate
logging
error handling
configuration via environment variables
.env for local secrets
no hardcoded API keys

Use a modern Python project structure.

Prefer:

pyproject.toml

over a collection of ad-hoc configuration files.

28. Testing

Use:

pytest

Tests should cover important logic.

Especially:

data normalization
salary parsing
deduplication
skill extraction
matching score
API endpoints
database integration
pipeline steps

Do not attempt 100% coverage.

Focus on meaningful tests.

29. Development Phases
Phase 1 — Foundation

Build:

Python project
PostgreSQL
basic schema
one data source
job ingestion
raw data storage

Goal:

Can collect and store jobs.
Phase 2 — Data Pipeline

Add:

validation
cleaning
normalization
deduplication
structured salary parsing
location normalization

Goal:

Raw jobs → clean database
Phase 3 — Data Science

Add:

Jupyter notebooks
EDA
skill statistics
location statistics
salary analysis
demand trends

Goal:

Understand the Austrian tech job market.
Phase 4 — NLP

Add:

skill extraction
skill normalization
seniority extraction
experience extraction
language extraction

Goal:

Turn job descriptions into structured data.
Phase 5 — CV + Matching

Add:

PDF CV extraction
candidate profile
skill matching
match scoring
skill-gap analysis

Goal:

Understand which jobs fit the user.
Phase 6 — Embeddings + RAG

Add:

sentence-transformers
ChromaDB
semantic job search
RAG
LLM explanations

Goal:

Search and reason over the collected job market.
Phase 7 — Machine Learning

Add:

salary prediction
model evaluation
optional seniority classification

Goal:

Demonstrate real ML workflow.
Phase 8 — FastAPI + Angular

Build:

REST API
dashboard
job search
job details
candidate profile
matching
AI assistant

Goal:

Usable personal application.
Phase 9 — Docker + Polish

Add:

Docker Compose
tests
logging
documentation
clean README
architecture diagram

Optional:

Airflow
Redis
MLflow

Only if time permits.

30. Technology Priority
Must have
Python
Pandas
NumPy
Scikit-learn
FastAPI
PostgreSQL
SQLAlchemy
Pydantic
spaCy / NLP
sentence-transformers
ChromaDB
LLM API
Angular
Docker
pytest
Nice to have
Airflow
Redis
MLflow
XGBoost
Hugging Face
Explicitly NOT required
Kafka
Kubernetes
Microservices
Cloud infrastructure
Complex distributed systems

These may be explored only if there is a genuine technical reason.

31. Important Rule: Do Not Overengineer

The primary goal is learning and building a useful personal tool.

Never introduce a technology solely because it looks good on a CV.

Before adding a technology, ask:

What problem does it solve?
Do we currently have that problem?
Is the added complexity justified?
Will this help the learning goals of the project?

If the answer is no, do not add it.

32. Important Rule: Build Incrementally

Do not generate the entire project at once.

Work in small milestones.

For each milestone:

Explain the purpose.
Explain the architecture.
Implement the smallest useful version.
Run/test it.
Verify it works.
Only then move to the next step.

The developer wants to understand the technologies, not blindly copy generated code.

33. Learning Philosophy

When implementing a new technology, explain:

What is it?
Why are we using it?
What problem does it solve here?
What alternatives exist?
Why did we choose this one?

For example, before implementing ChromaDB:

Explain:

Why PostgreSQL alone is not ideal for semantic search.
What embeddings are.
What a vector database does.
Why ChromaDB is sufficient for this project.

Do not assume the developer already understands every technology.

34. Definition of Done

The project is considered successful when the user can:

Collect Austrian tech jobs.
Store them in PostgreSQL.
Run a reproducible data pipeline.
Analyze the market with Python/Data Science.
Extract normalized skills with NLP.
Upload a CV.
Generate a candidate profile.
Find suitable jobs.
See skill gaps.
Search jobs semantically.
Ask RAG/LLM questions about the market.
See useful analytics in Angular.
Run the system using Docker.
Understand every major technology used in the project.

The final system should be a genuinely useful personal job-search tool while also demonstrating practical Python, Data Science, NLP, ML, AI, data engineering and software engineering skills.


**Ovo bih ja smatrao našim “constitutionom” projekta.** 😄

I najbitnije: **nemojmo odmah krenuti da kodiramo 15 stvari.** Prvi milestone bih postavio kao samo:

```text
Apify/API
   ↓
Python ingestion
   ↓
raw JSON
   ↓
PostgreSQL