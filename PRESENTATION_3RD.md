# Presentation 3rd — AI-Powered Project-Based Learning Platform

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Problem Definition](#2-problem-definition)
3. [Literature Survey](#3-literature-survey)
4. [System Design](#4-system-design)
   - [Use Case Diagram](#41-use-case-diagram)
   - [ER Diagram](#42-er-diagram-database)
   - [Class Diagram](#43-class-diagram)
   - [DFD Diagram](#44-dfd-diagram-data-flow-diagram)
5. [Hardware & Software Requirements](#5-hardware--software-requirements)
6. [Project UI / Front Page](#6-project-ui--front-page)

---

## 1. Introduction

### 1.1 Project Title

**AI-Powered Project-Based Learning Platform (AI-Learn Hub)**

### 1.2 Project Overview

AI-Learn Hub is a comprehensive, intelligent learning platform that provides **personalized project recommendations**, **dynamic learning roadmaps**, and **curated resources** to learners — all powered by Artificial Intelligence. Instead of forcing learners to manually hunt across YouTube, GitHub, Reddit, Stack Overflow, and documentation sites to figure out what to build and how, this platform orchestrates everything into a **one-stop learning experience**.

The system leverages **multiple AI models** working in concert — Google Gemini 2.5 Flash for complex reasoning, Groq (Llama 8B) for fast lightweight tasks, and local sentence-transformers for semantic embeddings — to deliver a hybrid AI architecture that stays entirely within **free-tier API limits** while providing enterprise-grade intelligence.

### 1.3 Key Features

| Feature | Description |
|---------|-------------|
| **AI-Powered Onboarding** | An interactive chatbot conducts a 3–4 question conversational interview to understand the user's experience level, goals, domain interests, and time commitment. |
| **Personalized Project Recommendations** | Based on the user's profile, the AI generates tailored project ideas combining LLM creativity and real-world GitHub project scraping. |
| **Dynamic Learning Roadmaps** | For each selected project, the system generates a milestone-based roadmap with checkpoints, estimated durations, and linked resources. |
| **Adaptive Progress Tracking** | The roadmap adapts in real-time — if the user struggles with a particular skill, the AI detects it and adjusts milestones, adds reinforcement content, or extends timelines. |
| **Multi-Platform Resource Aggregation** | Resources are scraped in parallel from GitHub, YouTube, Reddit, Stack Overflow, and Google, then classified, tagged, and ranked by the AI. |
| **RAG-Based Intelligent Q&A** | Users can ask questions and get answers augmented by semantically relevant context retrieved from the platform's vector database (Retrieval Augmented Generation). |
| **Checkpoint Submissions & AI Feedback** | Users submit screenshots/demos at checkpoints; the LLM analyzes submissions and provides detailed feedback. |

### 1.4 Motivation

In the age of information overload, learners — especially beginners and intermediates — face a paradox: there are millions of tutorials, but no clear, personalized path to follow. This platform solves the **"what should I build?"** and **"how do I build it?"** questions by combining AI with structured project-based pedagogy.

### 1.5 Objectives

1. Design an AI-driven onboarding system that profiles learner capabilities in under 2 minutes.
2. Implement a hybrid LLM architecture (Gemini + Groq + local embeddings) optimized for free-tier API quotas.
3. Build a Retrieval Augmented Generation (RAG) pipeline using Qdrant vector database and sentence-transformers.
4. Develop a multi-source web scraper that aggregates resources from 5+ platforms in parallel.
5. Create an adaptive roadmap engine that evolves based on learner progress.
6. Deliver a responsive, modern frontend using React.js and Tailwind CSS.

---

## 2. Problem Definition

### 2.1 Problem Statement

Learners today face several critical challenges when trying to learn new technical skills through project-based learning:

1. **Fragmented Resources**: Learning materials are scattered across YouTube, GitHub, Reddit, Stack Overflow, Medium, and official documentation. There is no single platform that aggregates, classifies, and personalizes these resources for an individual learner.

2. **No Personalized Guidance**: Existing platforms like freeCodeCamp, Udemy, or Coursera offer fixed curricula. They do not adapt to a learner's specific experience level, goals, time commitment, or domain of interest in real time.

3. **"What to Build" Problem**: One of the biggest barriers for learners is deciding **what project to build**. Generic project lists (e.g., "Build a To-Do App") don't account for individual skills, interests, or career goals.

4. **No Adaptive Learning Path**: Once a learner starts a project, there is no system that monitors their progress, detects struggles, and dynamically adjusts the learning roadmap.

5. **Lack of Structured Feedback**: Learners working on projects solo receive no feedback on their work. They don't know if they're on the right track until they fail.

6. **API Cost Barriers**: Most AI-powered educational tools require expensive API subscriptions. There is a need for a system that delivers intelligent features while staying within free-tier limits.

### 2.2 Proposed Solution

We propose an **AI-Powered Project-Based Learning Platform** that:

- Uses a **conversational AI chatbot** for intelligent onboarding (Gemini 2.5 Flash).
- Generates **personalized project recommendations** using a hybrid of LLM generation + web scraping.
- Creates **dynamic, adaptive roadmaps** with milestones, checkpoints, and linked resources.
- Aggregates resources from **5+ platforms** (GitHub, YouTube, Reddit, Stack Overflow, Google) using parallel web scraping.
- Implements **RAG (Retrieval Augmented Generation)** with local embeddings and Qdrant vector DB for contextual intelligence.
- Provides **AI-driven progress analysis** and checkpoint feedback.
- Stays entirely within **free-tier API limits** through a smart hybrid architecture (Gemini for complex tasks, Groq for lightweight tasks, local embeddings for zero-cost vector operations).

### 2.3 Scope

| In Scope | Out of Scope |
|----------|-------------|
| AI onboarding chatbot | Real-time video/voice interaction |
| Personalized project generation | Peer-to-peer collaboration features |
| Dynamic roadmap creation | Gamification (badges, leaderboards) |
| Multi-platform resource aggregation | Mobile native application |
| Checkpoint-based progress tracking | Payment/monetization system |
| RAG-based Q&A | Integration with LMS platforms (Moodle, Canvas) |
| Adaptive roadmap modification | Offline mode |

---

## 3. Literature Survey

### 3.1 Existing Systems & Research

| Sr. No. | Paper/System Title | Authors/Organization | Year | Key Contributions | Limitations |
|---------|-------------------|---------------------|------|-------------------|-------------|
| 1 | **"Intelligent Tutoring Systems: A Comprehensive Historical Survey"** | Nwana, H.S. | 1990 | Introduced the concept of AI-powered tutoring systems that adapt to individual learner needs. Defined the core components: domain model, student model, and tutoring model. | Early ITS systems lacked NLP capabilities and could not handle open-ended responses. No project-based learning support. |
| 2 | **"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"** | Lewis et al. (Facebook AI) | 2020 | Introduced RAG — combining retrieval from a knowledge base with generative LLMs. Showed that RAG outperforms pure generative models on knowledge-intensive tasks. | Focused on Q&A benchmarks, not applied to educational platforms. Required expensive infrastructure for the retrieval component. |
| 3 | **"LangChain: Building Applications with LLMs"** | Harrison Chase | 2023 | Provided a framework for chaining LLM calls, managing memory, and building RAG pipelines. Enabled complex multi-step AI workflows. | Framework complexity; steep learning curve for beginners. No built-in educational domain support. |
| 4 | **"Project-Based Learning: A Review of the Literature"** | Kokotsaki, Menzies & Wiggins | 2016 | Comprehensive meta-analysis showing project-based learning (PBL) significantly improves critical thinking, problem-solving, and knowledge retention versus traditional instruction. | PBL requires structured guidance — without it, learners often feel lost. No technology solution proposed to automate the guidance. |
| 5 | **Coursera / Udemy / freeCodeCamp** | Various | 2012–Present | Massive open online course platforms with millions of users. Provide structured video-based courses with quizzes and certificates. | Fixed curriculum — no personalization. No project-based adaptive learning. No multi-source resource aggregation. |
| 6 | **GitHub Copilot / ChatGPT** | OpenAI / GitHub | 2021–Present | AI coding assistants that help with code generation, debugging, and explanation. | Not designed for structured learning paths. No progress tracking, no roadmap generation, no project recommendation. Reactive only (user must ask the right questions). |
| 7 | **"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks"** | Reimers & Gurevych | 2019 | Introduced efficient sentence embeddings using siamese/triplet networks on BERT. Made semantic similarity search practical and fast. | Requires integration with a vector database for production use. Not an educational system by itself. |
| 8 | **Qdrant Vector Database** | Qdrant Team | 2023 | High-performance vector similarity search engine with filtering, payload storage, and cloud/local deployment. Designed for production RAG. | No built-in educational features. Needs to be integrated with an application layer. |

### 3.2 Research Gap

| Aspect | Existing Solutions | Our Solution |
|--------|-------------------|--------------|
| **Personalization** | Fixed curricula (Coursera, Udemy) | AI-powered conversational onboarding → dynamic profile → personalized projects |
| **Resource Aggregation** | Single-platform (YouTube-only, GitHub-only) | Multi-platform parallel scraping (GitHub + YouTube + Reddit + SO + Google) with AI classification |
| **Adaptive Learning** | Static roadmaps | Dynamic roadmaps that adapt based on progress, pace, and detected struggles |
| **Cost** | Expensive API calls (GPT-4 = ~$30/M tokens) | Hybrid architecture: Gemini free tier + Groq free tier + local embeddings = $0 operational cost |
| **RAG Integration** | ChatGPT (no persistent knowledge base) | Qdrant vector DB + local sentence-transformers = persistent, growing knowledge base |
| **Feedback Loop** | No automated feedback on projects | AI-powered checkpoint analysis with detailed feedback and roadmap adaptation |

### 3.3 Technologies Reviewed

| Technology | Purpose | Why Chosen Over Alternatives |
|------------|---------|------------------------------|
| **Google Gemini 2.5 Flash** | Primary LLM for complex reasoning | Free tier (1500 req/day), better than GPT-3.5 for structured output, lower latency than GPT-4 |
| **Groq (Llama 8B)** | Secondary LLM for lightweight tasks | 10x faster inference than Gemini for classification/extraction, generous free tier |
| **sentence-transformers (all-MiniLM-L6-v2)** | Local text embeddings | Zero API cost, 80MB model, CPU-optimized, 384-dim vectors, ~10ms per embedding |
| **Qdrant** | Vector database for RAG | Better performance than ChromaDB, supports in-memory dev mode + cloud production, metadata filtering |
| **FastAPI** | Backend API framework | Async-native, auto-documentation (Swagger), Pydantic validation, fastest Python framework |
| **React.js + Tailwind CSS** | Frontend | Component-based architecture, huge ecosystem, Tailwind for rapid responsive design |
| **MongoDB** | Primary database | Flexible schema for evolving data models, native JSON support, free tier (Atlas) |
| **LangChain** | LLM orchestration | Chains, memory management, RAG pipelines, multi-agent coordination — all in one framework |

---

## 4. System Design

### 4.1 Use Case Diagram

The Use Case Diagram shows the interactions between the **User (Learner)** and the **System (AI-Learn Hub Platform)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AI-Learn Hub Platform                              │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  Register / Login    │     │  Complete AI Onboarding      │             │
│  └──────────────────────┘     │  (3-4 conversational Qs)     │             │
│                                └──────────────────────────────┘             │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  View Dashboard      │     │  View Recommended Projects   │             │
│  │  (Stats, Activity)   │     │  (AI-generated + Scraped)    │             │
│  └──────────────────────┘     └──────────────────────────────┘             │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  Generate Custom     │     │  View Project Roadmap        │             │
│  │  Project Ideas       │     │  (Milestones + Checkpoints)  │             │
│  └──────────────────────┘     └──────────────────────────────┘             │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  Submit Checkpoint   │     │  Get AI Feedback on          │             │
│  │  (Screenshot/Demo)   │     │  Checkpoint Submission       │             │
│  └──────────────────────┘     └──────────────────────────────┘             │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  Search Resources    │     │  View Progress & Analytics   │             │
│  │  (Multi-Platform)    │     │  (AI-Powered Analysis)       │             │
│  └──────────────────────┘     └──────────────────────────────┘             │
│                                                                             │
│  ┌──────────────────────┐     ┌──────────────────────────────┐             │
│  │  Ask AI Questions    │     │  Adapt Roadmap               │             │
│  │  (RAG-based Q&A)     │     │  (Auto-adjust on struggle)   │             │
│  └──────────────────────┘     └──────────────────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                        ▲
                        │  interacts
                        │
                   ┌─────────┐
                   │  User   │
                   │(Learner)│
                   └─────────┘
```

**Detailed Use Cases:**

| Use Case ID | Use Case Name | Actor | Description | Pre-Condition | Post-Condition |
|-------------|--------------|-------|-------------|---------------|----------------|
| UC-01 | Register/Login | User | User creates an account or logs in using email and password. JWT tokens are issued. | None | User is authenticated, token stored in client. |
| UC-02 | Complete Onboarding | User | AI chatbot asks 3–4 adaptive questions to profile the user's experience level, interests, goals, and time commitment. | User is logged in; onboarding not yet completed. | User profile is saved to MongoDB; `onboarding_completed = true`. |
| UC-03 | View Dashboard | User | User sees aggregated stats (projects in progress, milestones completed, streak days) and recent activity. | User is logged in and onboarding is complete. | Dashboard data loaded from DB. |
| UC-04 | View Recommended Projects | User | AI generates 5 personalized project ideas based on user profile using Gemini + RAG + scraper. | Onboarding complete. | Projects displayed; stored in MongoDB. |
| UC-05 | Generate Custom Project | User | User enters a custom prompt (e.g., "Build a chatbot") and the AI generates a detailed project plan. | User is logged in. | Custom project created and saved. |
| UC-06 | View Project Roadmap | User | For a selected project, the AI generates a milestone-based roadmap with checkpoints and linked resources. | Project selected/started. | Roadmap stored in MongoDB; displayed to user. |
| UC-07 | Submit Checkpoint | User | User uploads a screenshot or demo URL at a roadmap checkpoint. | Milestone is in-progress, checkpoint is pending. | Checkpoint status changed to "submitted". |
| UC-08 | Get AI Feedback | System/User | LLM analyzes the checkpoint submission and provides detailed feedback. | Checkpoint submitted. | Feedback text stored; checkpoint approved or marked needs-revision. |
| UC-09 | Search Resources | User | User searches for learning resources; system scrapes GitHub, YouTube, Reddit, SO, Google in parallel. | User is logged in. | Resources displayed, classified, and stored in Qdrant. |
| UC-10 | View Progress | User | User views progress analytics — completion %, pace assessment, skills acquired, struggles detected. | At least 1 milestone started. | Progress data displayed. |
| UC-11 | Ask AI Question (RAG Q&A) | User | User asks a question; system retrieves relevant context from Qdrant and generates an answer via Gemini. | User is logged in. | Answer displayed with cited sources. |
| UC-12 | Adapt Roadmap | System | When the system detects the user is struggling (3+ failed checkpoints, slow pace), it automatically adjusts the roadmap. | Progress data indicates struggle. | Roadmap updated with reinforcement milestones. |

---

### 4.2 ER Diagram (Database)

The platform uses **MongoDB** (NoSQL) as the primary database and **Qdrant** as the vector database. Below is the Entity-Relationship diagram showing the MongoDB collections and their relationships.

```
┌─────────────────────────────────┐
│             USERS               │
├─────────────────────────────────┤
│ _id          : ObjectId (PK)   │
│ email        : String (Unique) │
│ full_name    : String          │
│ hashed_password : String       │
│ created_at   : DateTime        │
│ onboarding_completed : Boolean │
└──────────────┬──────────────────┘
               │ 1
               │
               │ has one
               ▼
┌─────────────────────────────────┐
│        ONBOARDING_DATA          │
├─────────────────────────────────┤
│ _id          : ObjectId (PK)   │
│ user_id      : String (FK)     │──────── References USERS._id
│ responses    : Array[Object]   │
│   └─ question : String         │
│   └─ answer   : String         │
│ experience_level : String      │
│ primary_goal : String          │
│ interests    : Array[String]   │
│ completed_at : DateTime        │
└─────────────────────────────────┘
               │
               │
┌──────────────┴──────────────────┐
│ 1                               │
│ has many                        │
▼                                 │
┌─────────────────────────────────┐
│           PROJECTS              │
├─────────────────────────────────┤
│ _id          : ObjectId (PK)   │
│ user_id      : String (FK)     │──────── References USERS._id
│ title        : String          │
│ description  : String          │
│ difficulty   : Enum            │
│   (beginner/intermediate/      │
│    advanced)                    │
│ domain       : String          │
│ duration_weeks : Integer       │
│ tech_stack   : Array[String]   │
│ resources    : Array[Object]   │
│ roadmap      : Array[String]   │
│ checkpoints  : Array[Object]   │
│   └─ id : Integer              │
│   └─ title : String            │
│   └─ description : String      │
│   └─ completed : Boolean       │
│   └─ screenshot_url : String   │
│   └─ user_notes : String       │
│   └─ completed_at : DateTime   │
│ status       : Enum            │
│   (not_started/in_progress/    │
│    completed/paused)           │
│ progress     : Integer (0-100) │
│ created_at   : DateTime        │
│ updated_at   : DateTime        │
│ started_at   : DateTime        │
│ completed_at : DateTime        │
└──────────────┬──────────────────┘
               │ 1
               │
               │ has one
               ▼
┌─────────────────────────────────┐
│           ROADMAPS              │
├─────────────────────────────────┤
│ _id          : ObjectId (PK)   │
│ user_id      : String (FK)     │──────── References USERS._id
│ project_id   : String (FK)     │──────── References PROJECTS._id
│ title        : String          │
│ description  : String          │
│ total_duration_weeks : Float   │
│ current_milestone_id : String  │
│ progress_percentage : Float    │
│ is_adaptive  : Boolean         │
│ adaptations  : Array[Object]   │
│ created_at   : DateTime        │
│ updated_at   : DateTime        │
│ last_activity_at : DateTime    │
│                                 │
│ milestones   : Array[Object]   │◄──── Embedded Documents
│   └─ id : String               │
│   └─ title : String            │
│   └─ description : String      │
│   └─ duration_weeks : Float    │
│   └─ prerequisites : [String]  │
│   └─ skills_to_learn : [String]│
│   └─ resources : [String]      │
│   └─ checkpoints : [String]    │
│   └─ status : Enum             │
│   └─ started_at : DateTime     │
│   └─ completed_at : DateTime   │
│   └─ order : Integer           │
└─────────────────────────────────┘
               │
               │ contains many
               ▼
┌─────────────────────────────────┐
│         CHECKPOINTS             │
│      (Embedded in Roadmap)      │
├─────────────────────────────────┤
│ id           : String          │
│ milestone_id : String (FK)     │──────── References Milestone.id
│ title        : String          │
│ description  : String          │
│ deliverable  : String          │
│ example_url  : String          │
│ status       : Enum            │
│   (pending/submitted/approved/ │
│    needs_revision)             │
│ submitted_at : DateTime        │
│ submission_url : String        │
│ submission_notes : String      │
│ feedback     : String          │
│ approved_at  : DateTime        │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│       PROGRESS_ENTRIES          │
├─────────────────────────────────┤
│ _id          : ObjectId (PK)   │
│ user_id      : String (FK)     │──────── References USERS._id
│ roadmap_id   : String (FK)     │──────── References ROADMAPS._id
│ milestone_id : String          │
│ checkpoint_id: String          │
│ action       : String          │
│ metadata     : Object          │
│ timestamp    : DateTime        │
└─────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│       RESOURCES (Qdrant Vector DB)              │
├─────────────────────────────────────────────────┤
│ id             : UUID (PK)                      │
│ vector         : Float[384]   ◄── Embedding     │
│ payload:                                        │
│   └─ title           : String                   │
│   └─ description     : String                   │
│   └─ url             : String                   │
│   └─ platform        : Enum                     │
│     (github/youtube/reddit/stackoverflow/       │
│      documentation/medium/arxiv/other)          │
│   └─ tags            : Array[String]            │
│   └─ relevance_score : Float                    │
│   └─ skills          : Array[String]            │
│   └─ difficulty      : String                   │
│   └─ resource_type   : String                   │
└─────────────────────────────────────────────────┘
```

**Relationships Summary:**

| Relationship | Type | Description |
|-------------|------|-------------|
| User → Onboarding Data | 1 : 1 | Each user has exactly one onboarding profile. |
| User → Projects | 1 : N | A user can have many projects. |
| Project → Roadmap | 1 : 1 | Each project has one learning roadmap. |
| Roadmap → Milestones | 1 : N | A roadmap has multiple milestones (embedded). |
| Milestone → Checkpoints | 1 : N | Each milestone has multiple checkpoints (embedded). |
| User → Progress Entries | 1 : N | Each user has many timestamped progress entries. |
| Resources (Qdrant) | Standalone | Stored as vectors with metadata payloads for semantic search. |

---

### 4.3 Class Diagram

The class diagram shows the core **models** and **services** in the backend application.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              MODELS LAYER                               │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
│     UserBase         │   │    ProjectBase       │   │  ResourceBase    │
├──────────────────────┤   ├──────────────────────┤   ├──────────────────┤
│ - email: str         │   │ - title: str         │   │ - title: str     │
│ - full_name: str     │   │ - description: str   │   │ - description:str│
├──────────────────────┤   │ - difficulty: Enum   │   │ - url: str       │
│                      │   │ - domain: str        │   │ - platform: Enum │
└──────┬──────┬────────┘   │ - duration_weeks: int│   │ - tags: [str]    │
       │      │            │ - tech_stack: [str]  │   │ - relevance: flt │
       │      │            │ - resources: [Dict]  │   ├──────────────────┤
       ▼      ▼            │ - roadmap: [str]     │   │                  │
┌──────────┐┌─────────┐   │ - checkpoints: [Obj] │   └────────┬─────────┘
│UserCreate││UserInDB  │   ├──────────────────────┤            │
├──────────┤├─────────┤   │                      │            ▼
│-password ││-id: str  │   └──────┬───────────────┘   ┌──────────────────┐
│  : str   ││-hashed_  │          │                   │   Resource       │
└──────────┘│ password │          ▼                   ├──────────────────┤
            │-created_ │   ┌──────────────────────┐   │ - id: str        │
            │  at: dt  │   │     Project           │   │ - user_id: str   │
            │-onboard_ │   ├──────────────────────┤   │ - created_at: dt │
            │ completed│   │ - id: str             │   │ - saved: bool    │
            └─────────┘   │ - user_id: str        │   └──────────────────┘
                           │ - status: Enum        │
┌──────────────────────┐   │ - progress: int       │   ┌──────────────────┐
│   OnboardingData     │   │ - created_at: dt      │   │  ResourceQuery   │
├──────────────────────┤   │ - updated_at: dt      │   ├──────────────────┤
│ - user_id: str       │   │ - started_at: dt      │   │ - query: str     │
│ - responses: [Obj]   │   │ - completed_at: dt    │   │ - platforms: []  │
│ - experience_level   │   └──────────────────────┘   │ - limit: int     │
│ - primary_goal: str  │                               └──────────────────┘
│ - interests: [str]   │
│ - completed_at: dt   │
└──────────────────────┘

┌──────────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
│      Roadmap         │   │     Milestone        │   │   Checkpoint     │
├──────────────────────┤   ├──────────────────────┤   ├──────────────────┤
│ - id: str            │   │ - id: str            │   │ - id: str        │
│ - user_id: str       │   │ - title: str         │   │ - milestone_id   │
│ - project_id: str    │   │ - description: str   │   │ - title: str     │
│ - title: str         │   │ - duration_weeks: flt│   │ - description    │
│ - milestones: [Obj]  │   │ - prerequisites: []  │   │ - deliverable    │
│ - total_duration: flt│   │ - skills_to_learn: []│   │ - status: Enum   │
│ - current_milestone  │   │ - resources: [str]   │   │ - submitted_at   │
│ - progress_%: flt    │   │ - checkpoints: [str] │   │ - submission_url │
│ - is_adaptive: bool  │   │ - status: Enum       │   │ - feedback: str  │
│ - adaptations: [Dict]│   │ - started_at: dt     │   │ - approved_at    │
│ - created_at: dt     │   │ - completed_at: dt   │   └──────────────────┘
│ - updated_at: dt     │   │ - order: int         │
└──────────────────────┘   └──────────────────────┘

┌──────────────────────┐   ┌──────────────────────┐
│   UserProgress       │   │  ProgressAnalysis    │
├──────────────────────┤   ├──────────────────────┤
│ - user_id: str       │   │ - user_id: str       │
│ - roadmap_id: str    │   │ - roadmap_id: str    │
│ - milestones_done: i │   │ - performance: str   │
│ - milestones_total: i│   │ - pace_assessment    │
│ - checkpoints_done: i│   │ - recommendations: []│
│ - current_milestone  │   │ - struggling_areas:[]│
│ - time_spent_hrs: flt│   │ - adjustments: Dict  │
│ - average_pace: str  │   │ - next_steps: [str]  │
│ - skills_acquired: []│   │ - analyzed_at: dt    │
│ - struggles: [str]   │   └──────────────────────┘
│ - strengths: [str]   │
│ - streak_days: int   │
└──────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                             SERVICES LAYER                              │
└─────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────┐
│     LearningOrchestrator       │   ◄── Central Service (Singleton)
├────────────────────────────────┤
│ - llm_service: LLMService     │
│ - groq_service: GroqService   │
│ - qdrant_service: QdrantSvc   │
│ - user_memories: Dict          │
├────────────────────────────────┤
│ + process_onboarding_message() │───► Uses Gemini (complex conversation)
│ + generate_personalized_       │───► Uses Groq + RAG + Gemini
│     projects()                 │
│ + generate_dynamic_roadmap()   │───► Uses Groq + RAG + Gemini
│ + adapt_roadmap()              │───► Uses Groq + Gemini
│ + aggregate_resources()        │───► Uses Groq + Scraper + Gemini + Qdrant
│ + answer_question()            │───► Uses RAG + Gemini
│ + route_task()                 │───► Smart LLM routing logic
└──────────┬─────────────────────┘
           │ uses
           ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   LLMService     │  │   GroqService    │  │  QdrantService   │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ - llm: Gemini    │  │ - client: Groq   │  │ - client: Qdrant │
├──────────────────┤  ├──────────────────┤  ├──────────────────┤
│ +generate_       │  │ +classify_       │  │ +search()        │
│  onboarding()    │  │  resource_type() │  │ +add_documents() │
│ +generate_       │  │ +extract_skills()│  │ +batch_upsert()  │
│  projects()      │  │ +assess_         │  │ +get_similar()   │
│ +generate_       │  │  difficulty()    │  └──────────────────┘
│  roadmap()       │  │ +generate_search │
│ +rank_resources()│  │  _query()        │  ┌──────────────────┐
│ +analyze_        │  │ +parse_project_  │  │ ScraperService   │
│  checkpoint()    │  │  requirements()  │  ├──────────────────┤
│ +suggest_        │  └──────────────────┘  │ - client: httpx  │
│  adjustments()   │                        ├──────────────────┤
│ +generate_       │  ┌──────────────────┐  │ +search_github() │
│  response_rag()  │  │ EmbeddingService │  │ +search_youtube()│
└──────────────────┘  ├──────────────────┤  │ +search_reddit() │
                      │ - model: MiniLM  │  │ +search_google() │
                      ├──────────────────┤  │ +search_stack    │
                      │ +encode_single() │  │  overflow()      │
                      │ +encode_batch()  │  │ +scrape_all_     │
                      │ +get_embedding() │  │  sources()       │
                      └──────────────────┘  └──────────────────┘
```

**Key Design Patterns Used:**

| Pattern | Where Used | Purpose |
|---------|-----------|---------|
| **Singleton** | `LLMService`, `GroqService`, `QdrantService`, `Orchestrator` | Ensure single instance of expensive resources (LLM connections, DB clients). |
| **Strategy** | `route_task()` in Orchestrator | Dynamically choose which LLM to use based on task type and complexity. |
| **Facade** | `LearningOrchestrator` | Provides a simplified interface for complex AI workflows involving multiple services. |
| **Repository** | `UserRepository`, `ProjectRepository`, `RoadmapRepository`, `ProgressRepository` | Abstracts database operations from business logic. |
| **Chain of Responsibility** | RAG Pipeline | Query → Embedding → Vector Search → Context Assembly → LLM Generation. |

---

### 4.4 DFD Diagram (Data Flow Diagram)

#### Level 0 DFD — Context Diagram

This shows the system as a single process with external entities.

```
┌──────────┐                                              ┌──────────────┐
│          │   Registration, Login, Chat Messages,        │              │
│          │   Project Selections, Checkpoint Uploads,    │   External   │
│   User   │──────────────────────────────────────────────│   APIs       │
│ (Learner)│   Resource Queries                           │  (GitHub,    │
│          │◄──────────────────────────────────────────────│  YouTube,    │
│          │   Dashboard, Projects, Roadmaps,             │  Reddit,     │
└──────────┘   Resources, Feedback, Progress              │  SO, Google) │
      │                                                   └──────┬───────┘
      │              ┌──────────────────────┐                    │
      │              │                      │                    │
      └─────────────►│   AI-Learn Hub       │◄───────────────────┘
                     │   Platform           │  Scraped Resources,
      ◄──────────────│   (System)           │  API Responses
                     │                      │
                     └──────────┬───────────┘
                                │
                     ┌──────────▼───────────┐
                     │   MongoDB + Qdrant   │
                     │   (Data Stores)      │
                     └──────────────────────┘
```

#### Level 1 DFD — Main Processes

This decomposes the system into its main functional processes.

```
                        ┌──────────┐
                        │   User   │
                        └────┬─────┘
                             │
            ┌────────────────┼───────────────────────────────────┐
            │                │                                   │
            ▼                ▼                                   ▼
  ┌─────────────────┐ ┌──────────────────┐            ┌─────────────────┐
  │  P1: Auth &     │ │  P2: Onboarding  │            │  P6: Resource   │
  │  Registration   │ │  Processing      │            │  Aggregation    │
  │                 │ │                  │            │                 │
  │ Input: email,   │ │ Input: user      │            │ Input: search   │
  │  password       │ │  messages        │            │  query          │
  │ Output: JWT     │ │ Output: profile, │            │ Output: ranked  │
  │  token          │ │  next question   │            │  resources      │
  └────────┬────────┘ └────────┬─────────┘            └────────┬────────┘
           │                   │                               │
           ▼                   ▼                               │
  ┌─────────────────┐ ┌──────────────────┐                     │
  │   D1: Users     │ │ D2: Onboarding   │                     │
  │   (MongoDB)     │ │  Data (MongoDB)  │                     │
  └─────────────────┘ └──────────────────┘                     │
                                                               │
            ┌──────────────────────────────────────────────────┘
            │
            ▼
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  P3: Project     │   │  P4: Roadmap     │   │  P5: Progress    │
  │  Generation      │   │  Generation &    │   │  Tracking &      │
  │                  │   │  Adaptation      │   │  Analysis        │
  │ Input: user      │   │                  │   │                  │
  │  profile         │   │ Input: project,  │   │ Input: checkpoint│
  │ Output: project  │   │  user profile    │   │  submission      │
  │  recommendations │   │ Output: roadmap  │   │ Output: feedback,│
  │                  │   │  with milestones │   │  analysis        │
  └────────┬─────────┘   └────────┬─────────┘   └────────┬─────────┘
           │                      │                       │
           ▼                      ▼                       ▼
  ┌─────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │  D3: Projects   │   │  D4: Roadmaps    │   │  D5: Progress    │
  │  (MongoDB)      │   │  (MongoDB)       │   │  Entries (DB)    │
  └─────────────────┘   └──────────────────┘   └──────────────────┘

                     ┌──────────────────┐
                     │  D6: Resources   │
                     │  (Qdrant Vector  │
                     │   Database)      │
                     └──────────────────┘
```

#### Level 2 DFD — Project Generation Process (P3 Expanded)

This shows the detailed data flow within the Project Generation process, demonstrating the hybrid AI approach.

```
                     ┌───────────────────┐
                     │   User Profile    │
                     │  (from D2)        │
                     └────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  P3.1: Extract Key  │
                   │  Skills & Interests │◄──── Uses Groq (Llama 8B)
                   │  (Classification)   │      (fast, lightweight)
                   └────────┬────────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
   │ P3.2: Search │ │ P3.3: Generate│ │ P3.4: Scrape │
   │ Qdrant for   │ │ Custom Ideas │ │ Real GitHub  │
   │ Similar      │ │ with LLM     │ │ Projects     │
   │ Projects     │ │              │ │              │
   │ (RAG)        │ │ Uses Gemini  │ │ Uses Scraper │
   └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
          │                │                │
          │     Uses local │                │
          │     embeddings │                │
          │                │                │
          └────────┬───────┴────────┬───────┘
                   │                │
                   ▼                │
        ┌──────────────────┐       │
        │  P3.5: Combine,  │◄──────┘
        │  Deduplicate &   │
        │  Rank Results    │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────┐
        │  D3: Projects    │
        │  (Save to DB)    │
        └──────────────────┘
```

---

## 5. Hardware & Software Requirements

### 5.1 Hardware Requirements

#### Development Environment

| Component | Minimum Requirement | Recommended |
|-----------|-------------------|-------------|
| **Processor** | Intel Core i3 / AMD Ryzen 3 (Dual-core, 2.0 GHz) | Intel Core i5 / AMD Ryzen 5 (Quad-core, 3.0+ GHz) |
| **RAM** | 4 GB | 8 GB or more |
| **Storage** | 10 GB free disk space (for dependencies, models, and databases) | 20 GB SSD |
| **GPU** | Not required (CPU-optimized embeddings) | Optional: NVIDIA GPU with CUDA for faster embeddings |
| **Network** | Broadband internet (for API calls and web scraping) | Stable broadband (10+ Mbps) |
| **Display** | 1280 × 720 resolution | 1920 × 1080 resolution |

#### Production / Deployment Environment

| Component | Specification |
|-----------|--------------|
| **Server** | Linux-based VPS (Ubuntu 22.04 LTS) or Docker container |
| **CPU** | 2+ vCPUs |
| **RAM** | 4 GB minimum (8 GB recommended for ML model loading) |
| **Storage** | 20 GB SSD minimum |
| **Network** | Public IP with HTTPS support |
| **Database Server** | MongoDB Atlas (free tier: 512 MB) or self-hosted |
| **Vector DB** | Qdrant Cloud (free tier: 1 GB) or Docker container |

### 5.2 Software Requirements

#### Operating System

| OS | Version | Status |
|----|---------|--------|
| **Ubuntu Linux** | 20.04 LTS / 22.04 LTS | Primary development OS |
| **macOS** | 12 (Monterey) or later | Fully supported |
| **Windows** | 10/11 (with WSL2) | Supported via WSL |

#### Backend Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.12.2 | Backend programming language |
| **pyenv** | Latest | Python version management |
| **pip** | Latest | Python package manager |
| **FastAPI** | 0.109.0 | High-performance async web framework |
| **Uvicorn** | 0.27.0 | ASGI server for FastAPI |
| **Pydantic** | 2.5.3 | Data validation and serialization |
| **Motor** | 3.3.2 | Async MongoDB driver for Python |
| **PyMongo** | 4.6.1 | MongoDB Python driver |
| **LangChain** | 0.1.4 | LLM orchestration, RAG pipelines, memory |
| **langchain-google-genai** | 0.0.6 | LangChain integration for Gemini |
| **langchain-groq** | 0.0.1 | LangChain integration for Groq |
| **google-generativeai** | 0.3.2 | Google Gemini API client |
| **groq** | 0.4.2 | Groq API client (Llama models) |
| **sentence-transformers** | 2.3.1 | Local text embeddings (all-MiniLM-L6-v2) |
| **PyTorch** | ≥ 2.2.0 | ML framework for sentence-transformers |
| **qdrant-client** | 1.7.0 | Qdrant vector database client |
| **httpx** | 0.26.0 | Async HTTP client for web scraping |
| **BeautifulSoup4** | 4.12.3 | HTML parsing for web scraping |
| **python-jose** | 3.3.0 | JWT token handling for authentication |
| **passlib** | 1.7.4 | Password hashing (bcrypt) |
| **Redis** | 5.0.1 | Response caching (Python client) |
| **scikit-learn** | 1.4.0 | ML utilities (similarity metrics, etc.) |

#### Frontend Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Node.js** | 20.x LTS | JavaScript runtime |
| **nvm** | Latest | Node.js version management |
| **npm** | Latest | Package manager |
| **React.js** | 18.2.0 | Frontend UI framework |
| **React Router DOM** | 6.21.1 | Client-side routing |
| **Vite** | 5.0.11 | Build tool and dev server |
| **Tailwind CSS** | 4.2.0 | Utility-first CSS framework |
| **Axios** | 1.6.5 | HTTP client for API calls |
| **Lucide React** | 0.307.0 | Icon library |
| **date-fns** | 3.2.0 | Date utility library |
| **clsx** | 2.1.0 | Conditional CSS class utility |

#### Database Software

| Software | Version | Purpose |
|----------|---------|---------|
| **MongoDB** | 7.x | Primary NoSQL database for users, projects, roadmaps, progress |
| **Qdrant** | Latest | Vector database for semantic search and RAG |

#### External APIs (Free Tier)

| API | Provider | Free Tier Limits | Purpose |
|-----|----------|-----------------|---------|
| **Gemini 2.5 Flash API** | Google | 1,500 requests/day, 1M tokens/day | Primary LLM for complex AI tasks |
| **Groq API** | Groq | Generous free tier | Secondary LLM for lightweight classification/extraction |
| **GitHub REST API** | GitHub | 60 req/hr (unauthenticated), 5000 req/hr (authenticated) | Repository scraping |
| **YouTube Data API v3** | Google | 10,000 units/day | Video resource scraping |
| **Stack Exchange API** | Stack Exchange | 300 req/day (unauthenticated), 10,000 req/day (authenticated) | Q&A resource scraping |
| **Reddit JSON API** | Reddit | Rate-limited | Discussion scraping |

#### Development Tools

| Tool | Purpose |
|------|---------|
| **VS Code** | Primary code editor / IDE |
| **Git** | Version control |
| **Postman / Swagger UI** | API testing (FastAPI auto-generates Swagger at `/docs`) |
| **MongoDB Compass** | Database GUI for MongoDB |
| **Docker** (optional) | Containerization for deployment |

---

## 6. Project UI / Front Page

### 6.1 Application Routes

| Route | Page | Description |
|-------|------|-------------|
| `/onboarding` | Onboarding Page | AI chatbot interview — no sidebar/header layout |
| `/dashboard` | Dashboard Page | Main landing page with stats, recent activity |
| `/projects` | Projects Page | View recommended projects, generate custom ones |
| `/resources` | Resources Page | Search and browse multi-platform resources |
| `/roadmaps` | Roadmaps Page | View learning roadmaps (coming soon) |
| `/chatbot` | AI Chatbot Page | RAG-based Q&A assistant (coming soon) |
| `/settings` | Settings Page | User preferences (coming soon) |

### 6.2 UI Component Architecture

The frontend is built using a **modular, component-based architecture** with React.js and Tailwind CSS. Every reusable UI element is encapsulated in its own component folder.

```
frontend/src/
├── components/              ◄── Global Reusable Components
│   ├── Badge/               — Status badges (difficulty, platform tags)
│   ├── Button/              — Primary, secondary, outline buttons
│   ├── Card/                — Content cards (project cards, resource cards)
│   ├── Header/              — Top navigation bar with menu toggle
│   ├── Input/               — Text inputs, search bars
│   ├── Modal/               — Overlay dialogs (confirmations, details)
│   ├── ProgressBar/         — Visual progress indicators
│   ├── Sidebar/             — Left navigation sidebar with route links
│   └── Spinner/             — Loading state indicators
│
├── pages/                   ◄── Page-Level Components
│   ├── Onboarding/          — AI chatbot onboarding interface
│   │   └── components/      — Chat bubbles, question cards, progress steps
│   ├── Dashboard/           
│   │   └── components/      
│   │       ├── DashboardStats.jsx   — Stat cards (projects, milestones, streak)
│   │       └── RecentActivity.jsx   — Activity feed timeline
│   ├── Projects/            
│   │   └── components/      — Project cards, filters, generate button
│   └── Resources/           
│       └── components/      — Resource cards, platform filters, search
│
├── services/                ◄── API Service Layer
│   ├── api.js               — Axios instance with base URL config
│   ├── onboarding.js        — Onboarding API calls
│   ├── projects.js          — Projects API calls
│   ├── resources.js         — Resources API calls
│   └── users.js             — User/auth API calls
│
├── styles/
│   └── global.css           — Global Tailwind CSS imports
│
└── utils/
    └── helpers.js           — Utility functions (formatDate, etc.)
```

### 6.3 Page Descriptions & UI Layout

#### Page 1: Onboarding Page (`/onboarding`)

```
┌──────────────────────────────────────────────────────────────┐
│                    AI-Learn Hub                               │
│                                                              │
│           ┌────────────────────────────────────┐             │
│           │      Welcome to AI-Learn Hub!      │             │
│           │                                    │             │
│           │  ┌──────────────────────────────┐  │             │
│           │  │  🤖 AI: Hi! I'm your         │  │             │
│           │  │  learning assistant. Let me   │  │             │
│           │  │  ask a few questions to       │  │             │
│           │  │  personalize your experience. │  │             │
│           │  │                               │  │             │
│           │  │  What's your experience       │  │             │
│           │  │  level in programming?        │  │             │
│           │  └──────────────────────────────┘  │             │
│           │                                    │             │
│           │  ┌──────────────────────────────┐  │             │
│           │  │  👤 User: I'm intermediate.  │  │             │
│           │  │  I know Python and some JS.  │  │             │
│           │  └──────────────────────────────┘  │             │
│           │                                    │             │
│           │  ┌──────────────────────────────┐  │             │
│           │  │  🤖 AI: Great! What's your   │  │             │
│           │  │  main goal? Building a        │  │             │
│           │  │  portfolio, career switch,    │  │             │
│           │  │  or exploring new tech?       │  │             │
│           │  └──────────────────────────────┘  │             │
│           │                                    │             │
│           │  ┌─────────────────────┐ [Send]   │             │
│           │  │ Type your message...│           │             │
│           │  └─────────────────────┘           │             │
│           │                                    │             │
│           │  Progress: ████████░░░░ Step 2/4   │             │
│           └────────────────────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

**Key Elements:**
- Full-screen layout (no sidebar) for focused onboarding experience
- Chat-style interface with AI and user message bubbles
- Progress indicator showing 4-step completion
- Auto-detection of profile completion triggers redirect to Dashboard

---

#### Page 2: Dashboard Page (`/dashboard`)

```
┌──────────┬───────────────────────────────────────────────────┐
│          │  ┌─────────────────────────────────────────────┐  │
│  SIDEBAR │  │  Header: AI-Learn Hub         [User Avatar] │  │
│          │  └─────────────────────────────────────────────┘  │
│ ┌──────┐ │                                                   │
│ │ 🏠   │ │  Welcome back, Devanshu! 👋                      │
│ │Dash- │ │                                                   │
│ │board │ │  ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│ ├──────┤ │  │  Projects  │ │ Milestones │ │   Streak   │   │
│ │ 📦   │ │  │  In Prog.  │ │ Completed  │ │   Days     │   │
│ │Proj- │ │  │     3      │ │    12      │ │    7 🔥    │   │
│ │ects  │ │  └────────────┘ └────────────┘ └────────────┘   │
│ ├──────┤ │                                                   │
│ │ 📚   │ │  ┌─────────────────────────────────────────────┐ │
│ │Resou-│ │  │           Recent Activity                   │ │
│ │rces  │ │  │                                             │ │
│ ├──────┤ │  │  ● Completed checkpoint "Setup React"       │ │
│ │ 🗺️   │ │  │    2 hours ago                              │ │
│ │Road- │ │  │                                             │ │
│ │maps  │ │  │  ● Started milestone "Authentication"       │ │
│ ├──────┤ │  │    Yesterday                                │ │
│ │ 🤖   │ │  │                                             │ │
│ │Chat  │ │  │  ● Generated project "E-Commerce App"       │ │
│ │bot   │ │  │    2 days ago                               │ │
│ ├──────┤ │  │                                             │ │
│ │ ⚙️   │ │  └─────────────────────────────────────────────┘ │
│ │Sett- │ │                                                   │
│ │ings  │ │                                                   │
│ └──────┘ │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

**Key Elements:**
- Persistent sidebar with navigation links (Dashboard, Projects, Resources, Roadmaps, Chatbot, Settings)
- Top header bar with menu toggle (hamburger icon for mobile) and user avatar
- Stat cards row: Projects in Progress, Milestones Completed, Streak Days
- Recent Activity feed showing timestamped learning events

---

#### Page 3: Projects Page (`/projects`)

```
┌──────────┬───────────────────────────────────────────────────┐
│          │  ┌─────────────────────────────────────────────┐  │
│  SIDEBAR │  │  Header: Projects              [User Avatar]│  │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                   │
│          │  Recommended Projects     [+ Generate New]        │
│          │                                                   │
│          │  ┌─────────────────────┐ ┌─────────────────────┐ │
│          │  │  🛒 E-Commerce      │ │  💬 Real-Time Chat  │ │
│          │  │     Platform        │ │     Application     │ │
│          │  │                     │ │                     │ │
│          │  │  Build a full-stack │ │  Build a WebSocket  │ │
│          │  │  e-commerce app     │ │  chat app with      │ │
│          │  │  with React &       │ │  rooms, typing      │ │
│          │  │  FastAPI...         │ │  indicators...      │ │
│          │  │                     │ │                     │ │
│          │  │  [Intermediate]     │ │  [Intermediate]     │ │
│          │  │  ⏱ 4 weeks          │ │  ⏱ 3 weeks          │ │
│          │  │  React, FastAPI,    │ │  React, Socket.io,  │ │
│          │  │  PostgreSQL         │ │  Node.js            │ │
│          │  │                     │ │                     │ │
│          │  │  [View Roadmap]     │ │  [View Roadmap]     │ │
│          │  │  [Start Project]    │ │  [Start Project]    │ │
│          │  └─────────────────────┘ └─────────────────────┘ │
│          │                                                   │
│          │  ┌─────────────────────┐ ┌─────────────────────┐ │
│          │  │  🤖 AI Chatbot      │ │  📊 Data Dashboard  │ │
│          │  │     Builder         │ │     with Analytics  │ │
│          │  │  ...                │ │  ...                │ │
│          │  └─────────────────────┘ └─────────────────────┘ │
│          │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

**Key Elements:**
- Grid of project recommendation cards generated by AI
- Each card shows: title, description, difficulty badge, duration, tech stack tags
- "View Roadmap" button to see/generate the milestone-based roadmap
- "Start Project" button to begin tracking progress
- "+ Generate New" button to enter a custom prompt for project generation

---

#### Page 4: Resources Page (`/resources`)

```
┌──────────┬───────────────────────────────────────────────────┐
│          │  ┌─────────────────────────────────────────────┐  │
│  SIDEBAR │  │  Header: Resources             [User Avatar]│  │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                   │
│          │  ┌─────────────────────────────────────────────┐ │
│          │  │  🔍 Search: [React authentication tutorial] │ │
│          │  │                                    [Search] │ │
│          │  └─────────────────────────────────────────────┘ │
│          │                                                   │
│          │  Platforms: [All] [GitHub] [YouTube] [Reddit]    │
│          │             [Stack Overflow] [Google]             │
│          │                                                   │
│          │  ┌─────────────────────────────────────────────┐ │
│          │  │  📺 YouTube                                 │ │
│          │  │  "React Auth Tutorial - JWT & Protected     │ │
│          │  │   Routes" by WebDev Pro                     │ │
│          │  │  ⭐ Relevance: 95%  |  Beginner-friendly   │ │
│          │  │  Tags: React, JWT, Authentication           │ │
│          │  │  [Open] [Save]                              │ │
│          │  └─────────────────────────────────────────────┘ │
│          │                                                   │
│          │  ┌─────────────────────────────────────────────┐ │
│          │  │  🐙 GitHub                                  │ │
│          │  │  "react-auth-kit" - ⭐ 2.3k stars           │ │
│          │  │  Complete auth solution for React apps      │ │
│          │  │  Tags: React, Authentication, Library       │ │
│          │  │  [Open] [Save]                              │ │
│          │  └─────────────────────────────────────────────┘ │
│          │                                                   │
│          │  ┌─────────────────────────────────────────────┐ │
│          │  │  💬 Stack Overflow                          │ │
│          │  │  "How to implement JWT authentication in    │ │
│          │  │   React with refresh tokens?"               │ │
│          │  │  ✅ 47 upvotes  |  Intermediate             │ │
│          │  │  [Open] [Save]                              │ │
│          │  └─────────────────────────────────────────────┘ │
│          │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

**Key Elements:**
- Search bar at top with multi-platform resource search
- Platform filter tabs (All, GitHub, YouTube, Reddit, Stack Overflow, Google)
- Resource cards with platform icon, title, relevance score, difficulty, tags
- "Open" (external link) and "Save" (bookmark) actions per resource
- Results are AI-classified and ranked by relevance to user profile

---

### 6.4 Responsive Design

The application follows a **mobile-first responsive design** approach:

| Breakpoint | Layout |
|------------|--------|
| **Mobile** (< 768px) | Sidebar hidden (hamburger menu toggle), single-column card layout |
| **Tablet** (768px – 1024px) | Sidebar collapsible, 2-column grid for cards |
| **Desktop** (> 1024px) | Sidebar always visible (256px width), 2–3 column grid for cards |

### 6.5 Design System

| Element | Specification |
|---------|--------------|
| **Primary Color** | Blue (#3B82F6) — Buttons, active sidebar, links |
| **Secondary Color** | Gray (#6B7280) — Inactive text, borders |
| **Success** | Green (#10B981) — Completed states, approved checkpoints |
| **Warning** | Amber (#F59E0B) — In-progress indicators |
| **Error** | Red (#EF4444) — Failed states, errors |
| **Background** | Light gray (#F9FAFB) — Page background |
| **Font** | System font stack (Inter / default sans-serif) |
| **Border Radius** | 8px (cards), 6px (buttons), 9999px (badges) |
| **Shadow** | `0 1px 3px rgba(0,0,0,0.1)` for cards |

---

## Summary

This document covers all aspects of the **AI-Powered Project-Based Learning Platform (AI-Learn Hub)** for the 3rd presentation:

1. **Introduction** — Defined the project, its features, motivation, and objectives.
2. **Problem Definition** — Identified 6 key problems in current learning ecosystems and proposed a comprehensive AI-driven solution.
3. **Literature Survey** — Reviewed 8 existing systems/papers, identified research gaps, and justified technology choices.
4. **System Design** — Provided detailed Use Case, ER, Class, and DFD diagrams with explanations.
5. **Hardware & Software Requirements** — Listed complete development and production requirements, every backend/frontend dependency, and external API specifications.
6. **Project UI** — Documented all 4 main pages with ASCII wireframes, component architecture, responsive design strategy, and design system specifications.

---
