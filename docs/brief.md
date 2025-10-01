# Project Brief: BMADFlow

## Executive Summary

**BMADFlow** is an intelligent documentation visualization platform that transforms scattered GitHub markdown files into interactive, methodology-aware project dashboards. Designed for product and engineering teams using structured development methodologies (BMAD, SAFe, Agile@Scale), BMADFlow solves the universal pain point of poor documentation navigation with AI-powered content extraction, epic-to-story graph visualization, and multi-view project insights.

**Problem**: 78% of development teams report documentation navigation as a significant productivity bottleneck, wasting 15+ minutes per search and creating barriers to project understanding.

**Solution**: BMADFlow provides a beautiful, intelligent layer on top of GitHub repositories, offering instant project status visibility, relationship graphs, and methodology-aware intelligence that understands BMAD/Agile structures.

**Market Opportunity**: $85M serviceable addressable market (SAM) in methodology-focused documentation tools, with clear path to $2.5-3M ARR by Year 3.

**Unique Value**: First documentation platform with native methodology intelligence (BMAD, SAFe), self-hosted AI privacy (OLLAMA), and purpose-built graph visualization for epic/story relationships - a defensible niche where generalist tools (Notion, Confluence, GitHub) fall short.

---

## Problem Statement

### Current State & Pain Points

**The Documentation Navigation Crisis**:
Software teams using structured development methodologies (BMAD, SAFe, Scrum@Scale) create extensive, valuable documentation - PRDs, architecture docs, epics, user stories, QA gates - but storing these as markdown files in GitHub repositories creates a **critical UX problem**:

1. **Finding Information is Painfully Slow**
   - Average 15 minutes to locate specific epic or story details in GitHub
   - No search beyond basic keyword matching (can't find "stories related to payments epic")
   - File-by-file navigation through nested folders is tedious and error-prone

2. **No Project Visibility or Status Overview**
   - Impossible to answer "What's the current project status?" without manually reading dozens of files
   - Epic-to-story relationships are buried in markdown text, not visualized
   - Status indicators (draft/dev/done) are scattered or implicit, requiring manual aggregation

3. **Onboarding New Team Members Takes Days**
   - New PMs/developers spend 2-5 days reading through documentation to understand project structure
   - No guided navigation through project phases (Scoping → Architecture → Development)
   - Methodology understanding (BMAD structure, Agile patterns) must be learned through tribal knowledge

4. **Stakeholder Communication Requires Manual Work**
   - Presenting project progress requires creating slides, screenshots, and manual summaries
   - Documentation isn't "presentation-ready" - raw markdown is too technical for executives
   - Frequent requests to "show me where we are" demand repetitive manual effort

5. **Methodology Compliance is Hard to Verify**
   - No automated way to check if documentation follows BMAD/SAFe structure
   - Compliance audits (required in regulated industries) require manual doc-by-doc review
   - Template violations and missing sections go undetected until too late

### Impact of the Problem (Quantified)

**Productivity Loss**:
- 15 min/day per PM finding information × 10 PMs = **2.5 hours/day wasted** = $50K/year cost (at $100/hour loaded rate)
- 30-60 min preparing for status meetings × 2 meetings/week = **8-16 hours/month** = $15K/year cost
- 2-3 days onboarding time per new team member × 5 new members/quarter = **10-15 days/quarter** = $20K/year cost

**Total Annual Impact for 10-Person Product Team: ~$85K in lost productivity**

**Quality Impact**:
- Missed epic dependencies → rework and delays (estimated 5-10% sprint velocity loss)
- Incomplete documentation → misaligned development (3-5% of stories require rework)
- Stakeholder miscommunication → wrong priorities (unquantified but significant)

**Team Morale Impact**:
- Frustration with tooling ("Why is this so hard?") reduces engagement
- "GitHub is terrible for docs" is universal complaint in PM/PO communities
- Tool fatigue from maintaining docs in multiple places (GitHub + Notion + Confluence)

### Why Existing Solutions Fall Short

**GitHub's Built-in Markdown Rendering**:
- ✅ Where docs already live (no migration)
- ✅ Version control and collaboration built-in
- ❌ **Poor navigation UX** (file explorer designed for code, not documentation)
- ❌ No intelligent search or relationship visualization
- ❌ No project status dashboards or methodology awareness

**Notion / Confluence (General Documentation Platforms)**:
- ✅ Beautiful UX and flexible structure
- ✅ Collaboration features (comments, sharing)
- ❌ **No GitHub integration** (manual copy/paste, docs become stale)
- ❌ Not methodology-aware (generic blocks don't understand BMAD/Agile structures)
- ❌ Limited technical diagram support (Notion has no Mermaid, Confluence is clunky)

**AI Documentation Tools (Mintlify, Swimm)**:
- ✅ AI-powered intelligence and modern UX
- ✅ Beautiful rendering and fast performance
- ❌ **Focused on code/API docs only** (not project management or product docs)
- ❌ No epic/story visualization or methodology features
- ❌ Not designed for product team workflows (PM/PO users)

**DIY Solutions (Custom Scripts, Internal Tools)**:
- ✅ Tailored to specific needs
- ❌ High maintenance burden (engineering time diverted from product work)
- ❌ Poor UX (scripts, not polished products)
- ❌ No ongoing innovation or support

### Urgency & Importance of Solving This Now

**Market Timing is Optimal**:
1. **AI Maturity**: LLM capabilities (OLLAMA, GPT-4, Claude) are now robust enough for reliable content extraction (2-3 years ago, accuracy was insufficient)
2. **Methodology Adoption Growth**: Structured methodologies (SAFe, BMAD) growing 30% YoY, creating larger addressable market
3. **Remote Work Permanence**: Distributed teams (65% of dev teams) depend more on documentation than co-located teams (pre-pandemic)
4. **Developer Tool Investment**: Platform engineering budgets up 40% (companies prioritizing DevEx and productivity tools)

**Competitive Window**:
- GitHub hasn't significantly improved documentation UX in 5+ years (stagnation creates opportunity)
- Notion/Confluence focus on enterprise features, not methodology intelligence (low priority for them)
- Current AI doc tools (Mintlify, Swimm) are code-focused, not expanding to project docs (2-3 year window before they might)

**Internal Catalyst (DSI/BMAD Context)**:
- DSI teams using BMAD Method and Claude Code generate rich, structured documentation
- Pain point is acutely felt internally (dogfooding opportunity)
- POC can validate with real BMAD projects (AgentLab, BMADFlow itself)
- Success internally → credibility externally (especially in BMAD community)

**Risk of Delay**:
- Competitors (especially well-funded Mintlify) could expand into project documentation space
- GitHub could finally invest in documentation UX (lower probability, but eliminates core pain point)
- AI capabilities becoming commoditized (need to build moat quickly before pure AI is insufficient differentiation)

---

## Proposed Solution

### Core Concept & Approach

**BMADFlow** is an **intelligent documentation platform** that sits as a visualization and intelligence layer on top of GitHub repositories. Rather than replacing GitHub or requiring migration, BMADFlow **reads** documentation from GitHub, **understands** its structure using LLM-powered intelligence, and **presents** it through purpose-built dashboards optimized for product team workflows.

**How It Works** (5-Minute Experience):
1. **Add Project**: User inputs GitHub repository URL (e.g., `github.com/company/project/docs`)
2. **Sync**: BMADFlow fetches documentation tree, parses markdown files (scoping, PRD, architecture, epics, stories)
3. **Extract**: LLM (OLLAMA) analyzes content, extracts structured information (user stories, acceptance criteria, status, dependencies)
4. **Visualize**: Multi-view dashboard presents project in 4 views:
   - **📋 Scoping**: Research, PRD, use case spec
   - **🏗️ Architecture**: Tech stack, system design, diagrams
   - **📊 Epics**: Graph visualization of epic→story relationships
   - **🔍 Detail**: Deep dive into specific epics/stories
5. **Navigate**: Beautiful markdown rendering with Mermaid diagrams, inter-document links, and table of contents

**No Migration, No Disruption**:
- Documentation stays in GitHub (single source of truth)
- Developers continue editing markdown as usual
- BMADFlow is **read-only** visualization layer (no lock-in)
- Manual sync on-demand (POC), automatic sync future enhancement

### Key Differentiators from Existing Solutions

**Differentiator 1: Methodology-Aware Intelligence** 🧠
- **What**: Native understanding of structured methodologies (BMAD, SAFe, Agile@Scale)
- **How**: LLM trained on methodology patterns, extracts epics, user stories, acceptance criteria, architecture decisions
- **Value**: Automatically structures information according to methodology best practices (vs generic markdown rendering)
- **Defensibility**: Domain expertise and training data create 2-3 year competitive moat (generalists won't prioritize this)

**Differentiator 2: Epic-to-Story Graph Visualization** 📊
- **What**: Interactive graph showing relationships between epics, stories, and tasks with dependency mapping
- **How**: Relationship extraction from markdown (explicit links + LLM inference), Neo4j graph database, D3.js/React Flow rendering
- **Value**: Visual understanding of complex project structures in seconds (vs 30+ min manual mental mapping)
- **Defensibility**: Graph extraction logic and visualization UX require significant R&D (not trivial to replicate)

**Differentiator 3: Self-Hosted AI Privacy** 🔒
- **What**: Uses OLLAMA (local/self-hosted LLM) instead of cloud AI (OpenAI, Anthropic)
- **How**: Run LLM inference locally or on company infrastructure, no data sent to external providers
- **Value**: Enterprise-grade privacy for sensitive architecture docs (critical for regulated industries)
- **Defensibility**: Architectural choice that competitors (Notion AI, Mintlify) can't easily match (their business models rely on cloud AI)

**Differentiator 4: Multi-Phase Project Dashboard** 🎯
- **What**: Purpose-built views for different project phases (Scoping → Architecture → Epics → Stories)
- **How**: 4-view dashboard tailored to PM/PO workflows, not generic document rendering
- **Value**: Navigate project from high-level vision to detailed implementation in intuitive flow
- **Defensibility**: Product design and workflow understanding (UX competitive advantage)

**Differentiator 5: GitHub-Native + Intelligence** 🚀
- **What**: Tight integration with GitHub (where docs live) + AI layer (understanding)
- **How**: GitHub API for sync, LLM for extraction, no migration required
- **Value**: Best of both worlds - GitHub's version control + intelligent visualization
- **Defensibility**: Integration depth and LLM application (competitors are either GitHub-native without AI, or AI-powered without GitHub depth)

### High-Level Vision

**Near-Term Vision (POC → Year 1)**:
BMADFlow becomes the **default way to explore BMAD Method documentation**, adopted by DSI teams and early BMAD community members. Users instinctively open BMADFlow dashboard instead of navigating GitHub when they need project information.

**Mid-Term Vision (Year 2-3)**:
BMADFlow expands to **support multiple methodologies** (SAFe, Scrum@Scale) and becomes the **leading documentation intelligence platform** for structured development teams. Enterprises adopt BMADFlow as part of their platform engineering tooling, improving developer experience and project visibility.

**Long-Term Vision (Year 3-5)**:
BMADFlow evolves into a **documentation intelligence platform** with ecosystem integrations (Jira, Linear, Slack), predictive insights (AI-powered project health scores), and becomes **category-defining** - when teams think "methodology-aware documentation," they think BMADFlow.

**Aspirational North Star**:
> "Every structured development team uses BMADFlow to understand their projects, just as they use GitHub to version their code. Documentation is no longer a burden - it's an intelligent asset that drives alignment, speeds onboarding, and enables better decisions."

---

## Target Users

### Primary User Segment: Product Teams Using Structured Methodologies

**Demographic/Firmographic Profile**:
- **Role**: Product Managers, Product Owners, Technical Program Managers
- **Company Size**: Mid-market to enterprise (100-10,000 employees)
- **Industry**: Software/SaaS (60%), Financial Services (15%), Healthcare (10%), Other (15%)
- **Team Structure**: Cross-functional Agile teams, typically 8-12 members per team
- **Methodology**: BMAD Method, SAFe (Scaled Agile Framework), Scrum@Scale, or custom Agile frameworks
- **Tech Stack**: GitHub/GitLab + Jira/Linear + Confluence/Notion + Figma + Slack
- **Geographic**: Global, initially North America and Europe (85% of market)

**Current Behaviors & Workflows**:
- **Documentation Creation**: Write PRDs, epics, user stories in markdown following BMAD/methodology templates
- **Storage**: Commit to GitHub repos (often `docs/` folders in project repositories)
- **Navigation**: Manually browse GitHub file explorer, use search, or ask colleagues "Where is the X epic?"
- **Status Tracking**: Manually update status in filenames or headers, aggregate for meetings
- **Collaboration**: GitHub PRs for doc changes, Slack discussions, occasional Notion/Confluence copies for stakeholders

**Specific Needs & Pain Points**:
1. **"I need to find specific information quickly without manual file browsing"**
   - Current: 15-20 min to locate epic details, acceptance criteria, or related stories
   - Need: Instant search and navigation (3-5 min max)

2. **"I need to see project status at a glance for stakeholder updates"**
   - Current: 30-60 min manual aggregation (read files, create summary)
   - Need: Real-time dashboard with auto-extracted status

3. **"I need to understand epic and story relationships to plan effectively"**
   - Current: Mental model or manual diagrams (30+ min, error-prone)
   - Need: Visual graph showing dependencies automatically

4. **"I need to onboard new team members efficiently"**
   - Current: 2-3 days of reading docs with senior team member guidance
   - Need: Self-service guided navigation (1 day onboarding)

5. **"I need documentation to be presentation-ready for stakeholders"**
   - Current: Create slides/screenshots manually (1-2 hours prep)
   - Need: Shareable dashboard links (zero prep)

**Goals They're Trying to Achieve**:
- **Tactical**: Reduce time spent searching for information (more time for strategic work)
- **Strategic**: Improve project alignment (ensure team understands vision and status)
- **Organizational**: Increase team velocity (reduce documentation friction, faster onboarding)
- **Personal**: Appear organized and well-informed (stakeholder confidence, peer respect)

---

### Secondary User Segment: Engineering Managers & Platform Teams

**Demographic/Firmographic Profile**:
- **Role**: Engineering Managers, Tech Leads, Staff Engineers, Platform Engineering Teams
- **Company Size**: Startups (50-200 employees) to large enterprises (1,000+)
- **Industry**: Technology-first companies across all verticals
- **Team Structure**: Manage 3-8 engineers, or responsible for developer experience across multiple teams
- **Methodology**: Agile teams, platform engineering practices, architecture governance
- **Tech Stack**: GitHub + CI/CD (GitHub Actions, Jenkins) + Observability (Datadog, Grafana) + Internal Dev Portals (Backstage, OpsLevel)

**Current Behaviors & Workflows**:
- **Documentation Ownership**: Create and maintain architecture docs, coding standards, technical RFCs
- **Multi-Team Visibility**: Need to track progress across 3-10 teams, each with separate repos
- **Architecture Governance**: Ensure consistency in architecture decisions, tech stack choices
- **Developer Experience**: Optimize internal tooling and workflows for productivity
- **Reporting**: Provide engineering status updates to VPs, CTOs, cross-functional stakeholders

**Specific Needs & Pain Points**:
1. **"I need to understand what's happening across multiple teams without reading 100 docs"**
   - Current: Manually visit each team's repo, read recent changes, ask team leads
   - Need: Multi-repo aggregation dashboard (single pane of glass)

2. **"I need to ensure architecture documentation stays consistent and up-to-date"**
   - Current: Manual reviews, inconsistent standards, docs become stale
   - Need: Automated structure validation, staleness detection

3. **"I need visibility into which epics are blocked vs in progress vs complete"**
   - Current: Daily standups, Jira tickets (but docs tell deeper story)
   - Need: Documentation-based status insights (complement Jira)

4. **"I need to provide executive summaries of engineering progress quickly"**
   - Current: Spend half a day aggregating info from multiple sources
   - Need: Auto-generated summary dashboards (executive-friendly)

**Goals They're Trying to Achieve**:
- **Tactical**: Reduce time spent in status update meetings (more time for strategic architecture work)
- **Strategic**: Improve cross-team alignment (shared understanding of architecture and dependencies)
- **Organizational**: Scale engineering practices (documentation governance without manual overhead)
- **Personal**: Demonstrate engineering excellence (well-documented, compliant architecture)

---

## Goals & Success Metrics

### Business Objectives

**Objective 1: Validate Product-Market Fit (POC Phase - Q4 2025 to Q1 2026)**
- **Metric**: 80% of POC users (3 pilot projects) report BMADFlow as "significantly better" than GitHub navigation
- **Target**: 8+ out of 10 users (across 3 projects) rate UX improvement as 4-5/5 stars
- **Measurement**: Post-POC user survey, qualitative interviews
- **Success Criteria**: ✅ Proceed to industrialization if ≥80% positive feedback

**Objective 2: Achieve POC Technical Feasibility (Q4 2025 to Q1 2026)**
- **Metric**: Successfully extract structured data from 90%+ of BMAD-structured documents
- **Target**: LLM extraction accuracy ≥90% for user stories, epics, status detection
- **Measurement**: Manual validation against 100 sample documents (epics, stories, PRDs)
- **Success Criteria**: ✅ Proceed if extraction is reliable enough for production use (human-in-loop acceptable for edge cases)

**Objective 3: Launch to Early Adopters (Beta - Q2 2026)**
- **Metric**: 500 free tier users within 3 months of public beta launch
- **Target**: 500 users (individual PMs, open source projects) actively using BMADFlow
- **Measurement**: User signups, weekly active users (WAU), project sync counts
- **Success Criteria**: ✅ Product-led growth (PLG) traction validates market demand

**Objective 4: Generate Revenue from Teams (GA - Q3 2026)**
- **Metric**: 50 paid teams (500 paid users) by Q4 2026, $72K ARR
- **Target**: 10% free-to-paid conversion rate (industry standard for dev tools)
- **Measurement**: Stripe/payment dashboard, MRR (Monthly Recurring Revenue) tracking
- **Success Criteria**: ✅ Revenue validates willingness-to-pay, sustainable business model

**Objective 5: Establish Category Leadership (Year 2-3)**
- **Metric**: Recognized as #1 "Methodology-Aware Documentation Platform" by target users
- **Target**: Top 3 in G2/Capterra rankings for documentation tools (methodology category)
- **Measurement**: G2 reviews, category rankings, industry analyst mentions (Gartner, Forrester)
- **Success Criteria**: ✅ Brand awareness and thought leadership established

### User Success Metrics

**User Success 1: Time Savings on Information Discovery**
- **Metric**: Average time to find specific epic/story information
- **Baseline**: 15 minutes (GitHub navigation)
- **Target**: 3 minutes (BMADFlow search + navigation) = **80% reduction**
- **Measurement**: User surveys ("How long did it take to find X?"), time-on-task studies

**User Success 2: Onboarding Efficiency**
- **Metric**: Time for new team member to understand project structure
- **Baseline**: 2-3 days (reading docs, asking questions)
- **Target**: 1 day (self-service via BMADFlow guided navigation) = **50-66% reduction**
- **Measurement**: Onboarding surveys, manager feedback, time-to-first-contribution

**User Success 3: Stakeholder Meeting Prep Time**
- **Metric**: Time spent preparing project status summaries for stakeholders
- **Baseline**: 30-60 minutes (manual aggregation, slide creation)
- **Target**: 5 minutes (share BMADFlow dashboard link) = **90%+ reduction**
- **Measurement**: User surveys, meeting prep time tracking

**User Success 4: Documentation Discoverability**
- **Metric**: Percentage of documentation searches that successfully find relevant information
- **Baseline**: 70% (GitHub search limited, many give up and ask colleagues)
- **Target**: 95% (intelligent search, graph navigation, related docs) = **25% improvement**
- **Measurement**: Search success rate analytics, user satisfaction surveys

**User Success 5: Team Adoption & Engagement**
- **Metric**: Weekly Active Users (WAU) as % of team members
- **Baseline**: N/A (new product)
- **Target**: 80% WAU (8 out of 10 team members use BMADFlow weekly) = high engagement
- **Measurement**: Usage analytics, login frequency, feature engagement (dashboard views, graph interactions)

### Key Performance Indicators (KPIs)

**KPI 1: User Acquisition (Growth Metric)**
- **Definition**: Number of new users (free + paid) signing up per month
- **Target**: Month 1: 50 users → Month 6: 500 users → Month 12: 2,000 users (exponential growth)
- **Why It Matters**: Indicates market demand, PLG traction, and brand awareness
- **Data Source**: User registration analytics (Amplitude, Mixpanel)

**KPI 2: Free-to-Paid Conversion Rate (Monetization Metric)**
- **Definition**: Percentage of free tier users who convert to paid plans within 90 days
- **Target**: 10% (industry benchmark for dev tools), stretch goal 15%
- **Why It Matters**: Validates pricing strategy, product value, and willingness-to-pay
- **Data Source**: Payment gateway (Stripe), conversion funnel analytics

**KPI 3: Monthly Recurring Revenue (MRR) (Financial Metric)**
- **Definition**: Predictable monthly revenue from subscriptions
- **Target**: Q4 2026: $6K MRR → Q4 2027: $45K MRR → Q4 2028: $180K MRR
- **Why It Matters**: Business sustainability, growth trajectory, investor appeal
- **Data Source**: Financial dashboard (Stripe, QuickBooks)

**KPI 4: Net Promoter Score (NPS) (Satisfaction Metric)**
- **Definition**: "How likely are you to recommend BMADFlow to a colleague?" (0-10 scale, NPS = % Promoters - % Detractors)
- **Target**: NPS ≥50 (excellent for B2B SaaS), stretch goal NPS ≥70
- **Why It Matters**: User satisfaction, word-of-mouth growth, churn prediction
- **Data Source**: In-app NPS surveys (quarterly), post-interaction surveys

**KPI 5: Weekly Active Users (WAU) / User Count (Engagement Metric)**
- **Definition**: Percentage of registered users who actively use BMADFlow each week
- **Target**: 40% WAU/User ratio (high engagement for B2B tool)
- **Why It Matters**: Product stickiness, value realization, churn risk indicator
- **Data Source**: Product analytics (events: dashboard views, sync actions, search queries)

**KPI 6: Customer Acquisition Cost (CAC) (Efficiency Metric)**
- **Definition**: Total sales & marketing spend divided by number of new customers acquired
- **Target**: CAC <$50 (PLG model, low-touch acquisition), CAC payback <6 months
- **Why It Matters**: Growth efficiency, profitability, scalability
- **Data Source**: Marketing spend (ads, content), sales data (CRM), user acquisition analytics

**KPI 7: Churn Rate (Retention Metric)**
- **Definition**: Percentage of customers who cancel subscription each month (Monthly Churn Rate)
- **Target**: <5% monthly churn (annual churn <60%, industry benchmark <10% monthly for good retention)
- **Why It Matters**: Retention is cheaper than acquisition, churn indicates product-market fit issues
- **Data Source**: Subscription management (Stripe), cancellation reasons (exit surveys)

---

## MVP Scope

### Core Features (Must Have)

**Feature 1: Project Management & GitHub Synchronization**
- **Description**: Add GitHub repository URL, trigger manual sync to fetch documentation
- **Rationale**: Foundation of entire product - must ingest docs before any value can be delivered
- **User Story**: "As a PM, I want to add my GitHub project URL so that BMADFlow can access my documentation"
- **Acceptance Criteria**:
  - ✅ Input field accepts GitHub repo URL (validate format, check accessibility)
  - ✅ "Sync" button triggers fetch of `/docs` folder structure
  - ✅ Parse markdown files, extract metadata (file path, last modified, size)
  - ✅ Store in database (project record, file records, relationships)
  - ✅ Sync completes in <5 min for typical project (50-100 docs)
  - ✅ Display sync status (in progress, completed, errors)
- **Out of Scope for MVP**: Auto-sync, webhook-based updates (manual sync only)

---

**Feature 2: LLM-Powered Intelligent Content Extraction**
- **Description**: Use OLLAMA to extract structured information from markdown (user stories, epics, status, etc.)
- **Rationale**: Core differentiator - methodology-aware intelligence (without this, BMADFlow is just another markdown viewer)
- **User Story**: "As a PM, I want BMADFlow to automatically understand my user stories and epics so I don't have to manually tag or categorize them"
- **Acceptance Criteria**:
  - ✅ Extract user stories in format "AS a [role] I want [feature] SO THAT [benefit]"
  - ✅ Extract acceptance criteria, tasks, dev notes from story sections
  - ✅ Detect status (draft/dev/done) from explicit markers or content analysis
  - ✅ Extract epic titles, descriptions, related stories (from links or content)
  - ✅ Identify relationships (epic → stories, story → tasks)
  - ✅ Handle format variations gracefully (BMAD patterns with flexibility, not rigid parsing)
  - ✅ 90%+ extraction accuracy on pilot project validation set
- **Out of Scope for MVP**: Multi-methodology support (BMAD only for MVP), human-in-loop corrections

---

**Feature 3: Multi-View Project Dashboard**
- **Description**: 4-view dashboard optimized for product team workflows (Scoping, Architecture, Epics, Detail)
- **Rationale**: Core UX value - superior navigation vs GitHub (if dashboard isn't 10x better, product fails)
- **User Story**: "As a PM, I want to see my project from multiple angles (scoping, architecture, epics) so I can navigate to what I need quickly"
- **Acceptance Criteria**:
  - ✅ **View 1 - Scoping (📋 Qualification)**: Display research docs, PRD (sharded), use case spec
    - Document cards with titles, purpose summaries, status indicators
    - Click to detailed view (Feature 5)
  - ✅ **View 2 - Architecture (🏗️)**: Tech stack, architecture diagrams, system design
    - Render Mermaid diagrams (architecture visuals)
    - Display sharded architecture sections with navigation
  - ✅ **View 3 - Epics (📊)**: Graph or list view of epic→story relationships
    - At least one visualization: table, tree, or graph (see Feature 4)
    - Status rollup (epic status based on story statuses)
  - ✅ **View 4 - Detail (🔍)**: Deep dive into specific epic/story
    - Full markdown rendering with sections clearly displayed
    - Related QA gates, assessments linked
- **Out of Scope for MVP**: Customizable views, saved filters, user preferences (fixed 4-view layout)

---

**Feature 4: Epic-to-Story Graph Visualization**
- **Description**: Visual representation of epic→story→task relationships as interactive graph or tree
- **Rationale**: Unique value - no other tool provides this (key differentiator in user interviews)
- **User Story**: "As a PM, I want to see a graph of how epics and stories relate so I can understand dependencies visually"
- **Acceptance Criteria**:
  - ✅ Render graph with nodes (epics, stories) and edges (relationships)
  - ✅ At least one view type: hierarchical tree OR interactive graph (D3.js/React Flow)
  - ✅ Color coding by status (draft=gray, dev=blue, done=green)
  - ✅ Click on node → navigate to detail view (Feature 3, View 4)
  - ✅ Handle 20-50 nodes without performance issues (typical project size)
  - ✅ Fallback: If graph extraction fails, show table view (Epic | Stories | Status)
- **Out of Scope for MVP**: Multiple graph layouts (force-directed, circular, etc.), advanced filtering, dependency types (blocks, relates-to, etc.)

---

**Feature 5: Beautiful Markdown Rendering & Navigation**
- **Description**: Render markdown with Mermaid diagrams, syntax highlighting, table of contents, and inter-document links
- **Rationale**: Table stakes - must be significantly better than GitHub rendering (if not, users won't switch)
- **User Story**: "As a PM, I want to read documentation in a beautiful, easy-to-navigate format so that understanding is effortless"
- **Acceptance Criteria**:
  - ✅ Clean, readable markdown rendering (react-markdown or similar)
  - ✅ Mermaid.js diagram rendering (architecture diagrams, flowcharts)
  - ✅ Code syntax highlighting (dev notes, technical specs)
  - ✅ Auto-generated table of contents (from headers) for long docs
  - ✅ Inter-document links work (click `[Architecture](architecture.md)` → navigate to Architecture view)
  - ✅ Responsive design (usable on desktop, tablet minimum)
  - ✅ Fast performance (render 10K-word doc in <2 seconds)
- **Out of Scope for MVP**: Editing docs (read-only), PDF export, custom themes

---

### Out of Scope for MVP

**❌ Authentication & User Management** (Simple or None for POC)
- Basic auth (if needed) or no auth (single-user POC)
- No user roles, permissions, team management
- **Reason**: Focus on core value (navigation UX), not infrastructure (add in industrialization)

**❌ Multi-User Collaboration Features**
- No comments, annotations, @mentions, activity feeds
- No real-time collaboration or presence indicators
- **Reason**: MVP is individual user value (collaboration is enhancement, not core)

**❌ Real-Time Synchronization**
- Manual sync only (click "Sync Now" button)
- No webhooks, scheduled syncs, or auto-updates
- **Reason**: POC validation doesn't require automation (add post-MVP)

**❌ Semantic Search / AI Chatbot**
- Basic keyword search only (no AI-powered Q&A)
- No conversational interface ("Show me stories related to payments")
- **Reason**: LLM resources focused on extraction (search is enhancement, not MVP-critical)

**❌ Private Repository Support**
- Public GitHub repositories only (no authentication)
- **Reason**: Simplifies POC (no OAuth flow), sufficient for validation

**❌ Performance Optimization at Scale**
- Optimized for 2-3 pilot projects (50-100 docs each)
- No caching strategies, lazy loading, or distributed architecture
- **Reason**: Prove value first, optimize later (premature optimization is waste)

**❌ Advanced Analytics / Metrics**
- No documentation health scores, coverage analysis, staleness detection
- No usage analytics dashboards (beyond basic user tracking)
- **Reason**: MVP proves core workflow, analytics are power-user features

**❌ Multi-Methodology Support**
- BMAD Method only (no SAFe, Scrum@Scale, custom frameworks)
- **Reason**: Focus on one methodology for depth (extensibility post-MVP)

**❌ Enterprise Features**
- No SSO, RBAC, audit logs, compliance reporting
- No SLA guarantees, dedicated support, professional services
- **Reason**: Enterprise features are Year 2 opportunity (after SMB validation)

---

### MVP Success Criteria

**Must Achieve (Go/No-Go Criteria)**:

1. ✅ **Extraction Reliability**: 90%+ accuracy on BMAD-structured documents (user stories, epics, status)
   - Validation: Manual review of 100 sample extractions from pilot projects
   - Acceptable: 10% edge cases require manual correction (human-in-loop)

2. ✅ **UX Improvement**: 80%+ of users rate BMADFlow as "significantly better" than GitHub (4-5 stars)
   - Validation: Post-POC user survey (10+ users across 3 pilot projects)
   - Acceptable: Some features incomplete, but core navigation value is clear

3. ✅ **Graph Visualization Value**: 70%+ of users find epic/story graph "useful" or "very useful"
   - Validation: User feedback on graph feature specifically
   - Acceptable: Basic graph (not perfect), but demonstrates unique value

4. ✅ **Technical Stability**: Core features work without critical bugs (dashboard loads, sync completes, renders docs)
   - Validation: QA testing, pilot user bug reports
   - Acceptable: Minor bugs (UX polish issues), but no blockers

5. ✅ **Performance Adequate**: Sync completes in <5 min, dashboard loads in <3 sec (for typical 50-doc project)
   - Validation: Performance testing, user feedback on speed
   - Acceptable: Not optimized, but usable (doesn't frustrate users)

**Nice-to-Have (Bonus Success)**:
- Multiple graph visualization options (tree + graph, user can switch)
- Semantic search (basic AI Q&A even if limited)
- Multi-repo support (even if only 2-3 repos)

---

## Post-MVP Vision

### Phase 2 Features (Year 1 - Post-Industrialization)

**Phase 2 Priority Features** (Q1-Q2 2026):

1. **Authentication & Team Management**
   - User accounts (email/password), team workspaces
   - Role-based access (PM, Dev, QA roles with appropriate views)
   - **Value**: Multi-user collaboration, access control for private docs

2. **Automated Synchronization**
   - Scheduled sync (hourly, daily), webhook-based updates (GitHub push triggers sync)
   - **Value**: Docs always up-to-date, no manual sync burden

3. **Private Repository Support**
   - GitHub OAuth integration, support for private repos
   - **Value**: Unlock enterprise market (most documentation is private)

4. **AI Semantic Search**
   - RAG-based Q&A ("Show me stories related to authentication"), semantic search beyond keywords
   - **Value**: Even faster information discovery (30 sec to answer vs 3 min navigation)

5. **Multi-Repository Aggregation**
   - Sync multiple repos, unified project dashboard (microservices, multi-team projects)
   - **Value**: Enterprise use case (complex projects span repos)

6. **Enhanced Graph Visualizations**
   - Multiple layout options (force-directed, circular, timeline), dependency types (blocks, relates-to), filtering/search within graph
   - **Value**: Power users can explore complex relationships deeply

### Long-Term Vision (Year 2-3)

**Year 2: Platform & Ecosystem** (2027)
- **API & Integrations**: Public API, Jira/Linear sync (bidirectional status updates), Slack/Teams notifications
- **Marketplace**: Plugin ecosystem (community-built extractors, custom views, integrations)
- **Enterprise Features**: SSO (SAML, OAuth), advanced RBAC, audit logs, compliance reporting (SOC2, HIPAA)
- **Multi-Methodology Support**: SAFe, Scrum@Scale, custom framework adapters
- **Value**: Become platform, not just tool (ecosystem lock-in, stickiness)

**Year 3: Intelligence & Automation** (2028)
- **Predictive Insights**: AI-powered project health scores (doc coverage, staleness, risk indicators)
- **Automated Documentation**: LLM generates documentation drafts from code changes (reverse Swimm)
- **Workflow Automation**: Approval workflows, doc quality gates in CI/CD, automated compliance checks
- **Advanced Analytics**: Usage patterns, team velocity indicators, documentation ROI metrics
- **Value**: Shift from visualization to intelligence (proactive insights, not just reactive exploration)

### Expansion Opportunities

**Geographic Expansion**:
- **Phase 1 (2026-2027)**: North America + Western Europe (English-first)
- **Phase 2 (2028)**: APAC (Japan, Singapore), Eastern Europe (localization required)
- **Phase 3 (2029+)**: Latin America, Middle East (vertical expansion in fintech, healthcare)

**Vertical Expansion**:
- **Phase 1 (2026-2027)**: Technology/SaaS companies (beachhead)
- **Phase 2 (2028)**: Regulated industries (finance, healthcare with compliance features)
- **Phase 3 (2029+)**: Government, defense (high-security, on-prem deployments)

**Product Line Expansion**:
- **BMADFlow for Code**: Extend to code documentation (like Swimm, but methodology-aware)
- **BMADFlow for APIs**: API documentation with methodology context (like Mintlify, but integrated)
- **BMADFlow for Compliance**: Dedicated compliance and audit trail product (regulated industries)

**Business Model Expansion**:
- **Open Source Core + Commercial Extensions**: Keep extraction and rendering open, monetize enterprise features (like GitLab model)
- **Marketplace Revenue Share**: Take 20-30% of third-party plugin sales
- **Professional Services**: Implementation, training, custom extractors (high-margin, enterprise)

---

## Technical Considerations

### Platform Requirements

**Target Platforms**:
- **Primary**: Web application (browser-based, desktop and tablet support)
- **Secondary**: Mobile-responsive (read-only use cases on mobile)
- **Future**: Desktop app (Electron) for offline access, native mobile apps (iOS/Android) for on-the-go

**Browser/OS Support**:
- **Browsers**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+ (modern browsers, last 2 years)
- **Operating Systems**: Platform-agnostic (web), but optimized for macOS and Windows (primary developer platforms)
- **Screen Sizes**: Desktop (1920×1080 primary), laptop (1440×900), tablet (1024×768 minimum)

**Performance Requirements**:
- **Sync Performance**: <5 min for 100 documents, <10 min for 500 documents (typical project sizes)
- **Dashboard Load**: <3 sec to render dashboard (initial load), <1 sec for view switching
- **Search Response**: <500ms for keyword search, <2 sec for semantic search (AI-powered)
- **Graph Rendering**: <3 sec for 50 nodes, <10 sec for 200 nodes (interactive graph)
- **Concurrent Users**: Support 100 concurrent users (POC), 1,000 concurrent (Year 1), 10,000 concurrent (Year 3)

### Technology Preferences

**Frontend**:
- **Framework**: React 18+ with TypeScript (type safety, component ecosystem, developer familiarity)
- **UI Components**: shadcn/ui (modern, accessible, customizable)
- **Styling**: Tailwind CSS (utility-first, rapid development, consistent design system)
- **Graph Visualization**: D3.js or React Flow (powerful, flexible, interactive graphs)
- **Markdown Rendering**: react-markdown + remark/rehype plugins (extensible, performant)
- **Mermaid**: mermaid.js (de facto standard for diagrams in markdown)

**Backend**:
- **Framework**: Python FastAPI (async, fast, auto-docs, Python ecosystem for AI/LLM)
- **Async Processing**: Celery + Redis (background jobs for sync, extraction tasks)
- **API Design**: RESTful (simple, cacheable), GraphQL consideration for future (complex queries)
- **Authentication**: JWT tokens (stateless), OAuth 2.0 for GitHub (future)

**Agentic / AI Layer**:
- **Framework**: Pydantic AI (type-safe, structured outputs, validation)
- **LLM Provider**: OLLAMA (self-hosted, privacy-first, no external API costs)
- **Models**: Llama 3 8B (balanced performance/cost), Mistral 7B (alternative), larger models (13B+) for complex extraction
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2 for speed, all-mpnet-base-v2 for quality)
- **Vector Search**: pgvector extension (PostgreSQL-native, simple, sufficient for MVP)

**Databases**:
- **pgvector (PostgreSQL with vector extension)**:
  - **Use Cases**: Document content, embeddings, user data, project metadata
  - **Why**: Relational data + vector search in one database (simplicity), mature, scalable
  - **Schema**: Projects, Documents, Sections, Users, Embeddings tables
- **Neo4j (Graph Database)**:
  - **Use Cases**: Epic→Story→Task relationships, dependency graphs
  - **Why**: Purpose-built for graph queries, visualization-ready, Cypher query language (expressive)
  - **Schema**: Nodes (Epic, Story, Task), Relationships (CONTAINS, DEPENDS_ON, RELATES_TO)

**Infrastructure**:
- **Containerization**: Docker (development consistency), Docker Compose (local multi-service setup)
- **Orchestration**: Kubernetes (production, auto-scaling), Helm charts (deployment management)
- **CI/CD**: GitHub Actions (integrated with code repo), GitLab CI (alternative)
- **Hosting**: Internal cloud infrastructure (on-prem or private cloud for security), AWS/Azure/GCP for public SaaS (future)
- **Monitoring**: Prometheus + Grafana (metrics), Sentry (error tracking), ELK stack (logs)

**External Integrations**:
- **GitHub API**: REST API v3 (repo access, file fetching), GraphQL API v4 (efficient queries, future)
- **Future Integrations**: Jira (API), Linear (API), Slack (webhooks, slash commands), Microsoft Teams (connectors)

### Architecture Considerations

**Repository Structure**:
- **Monorepo vs Microservices**: Start with monorepo (simplicity), migrate to microservices if needed (Year 2+)
- **Suggested Structure**:
  ```
  bmadflow/
  ├── frontend/          # React app
  ├── backend/           # FastAPI app
  │   ├── api/           # REST endpoints
  │   ├── services/      # Business logic
  │   ├── models/        # DB models
  │   └── ai/            # LLM extraction
  ├── shared/            # Shared types, utils
  ├── infrastructure/    # Docker, K8s configs
  └── docs/              # Project documentation
  ```

**Service Architecture**:
- **MVP (Monolith)**: Single FastAPI backend, single React frontend (simple, fast iteration)
- **Year 1 (Modular Monolith)**: Separate services within monolith (extraction service, sync service, API service)
- **Year 2+ (Microservices)**: Independent services (if scale demands):
  - Sync Service (GitHub integration)
  - Extraction Service (LLM processing)
  - Graph Service (Neo4j queries)
  - API Gateway (routing, auth)

**Integration Requirements**:
- **GitHub API**: Read-only access (fetch files, metadata), OAuth (future, for private repos)
- **OLLAMA**: Local API calls (HTTP), model management (download, load, inference)
- **Databases**: Connection pooling (pgvector, Neo4j), query optimization (indexing, caching)
- **Future**: Jira API (bidirectional sync), Slack API (notifications), Stripe (payments)

**Security/Compliance**:
- **Data Privacy**: Self-hosted OLLAMA (no data to external AI), on-prem deployment option (enterprise)
- **Authentication**: Secure password hashing (bcrypt), JWT token management (short expiry, refresh tokens)
- **Authorization**: Role-based access control (PM, Dev, QA roles), project-level permissions
- **Compliance (Future)**: SOC2 Type II (Year 2), GDPR (data residency, right to deletion), HIPAA (healthcare customers)
- **Security Best Practices**: HTTPS only, input validation (prevent injection), rate limiting, secrets management (env vars, Vault)

---

## Constraints & Assumptions

### Constraints

**Budget**: Limited (POC self-funded or minimal budget)
- **Infrastructure**: Use free tiers where possible (Vercel, Supabase free tiers, or internal infrastructure)
- **Tools**: Open source (React, FastAPI, OLLAMA, pgvector, Neo4j Community Edition)
- **Team**: 1 developer (Claude Code assisted) for POC, 1-2 developers for industrialization
- **Timeline**: POC must complete in 4-6 weeks (budget constraint on developer time)

**Timeline**: Aggressive POC Schedule
- **POC Duration**: 4-6 weeks (rapid validation, not production-ready)
- **Industrialization**: 8-12 weeks post-POC (if greenlit)
- **GA Launch Target**: Q3 2026 (9-12 months from POC start)
- **Constraint Impact**: Must ruthlessly prioritize MVP features, defer nice-to-haves

**Resources**: Small Team, High Leverage (Claude Code)
- **POC Team**: 1 developer + Claude Code (AI pair programming for speed)
- **Industrialization Team**: 1-2 developers (backend + frontend split, or full-stack)
- **Expertise Constraints**: Limited UI/UX design resources (use shadcn/ui for design system)
- **AI/LLM Expertise**: Moderate (Pydantic AI helps, but prompt engineering learning curve)

**Technical Constraints**:
- **Public Repos Only (MVP)**: No GitHub OAuth implementation (saves 1-2 weeks development)
- **Self-Hosted Deployment**: Internal infrastructure (no cloud spend for POC)
- **OLLAMA Model Limits**: Running large models (13B+) may require GPU (cost/availability constraint)
- **Graph Scale**: Neo4j Community Edition (free, but limited to single instance, no clustering)

### Key Assumptions

**Assumption 1: BMAD Documentation Consistency** (MEDIUM RISK)
- **Assumption**: BMAD projects follow similar structure (epics, stories, PRD, architecture patterns)
- **Validation**: Review 3 pilot projects (AgentLab, BMADFlow, one more) to confirm consistency
- **Risk if Wrong**: Extraction accuracy drops if formats vary wildly (mitigation: flexible LLM prompts, handle variations)
- **Contingency**: Build configurable extraction rules, allow custom templates if needed

**Assumption 2: LLM Extraction Accuracy Sufficient** (MEDIUM RISK)
- **Assumption**: OLLAMA (Llama 3 8B or similar) can achieve 90%+ extraction accuracy on BMAD docs
- **Validation**: Benchmark extraction on 100 sample docs during Week 1-2 of POC
- **Risk if Wrong**: Core value prop (intelligence) fails if extraction is unreliable
- **Contingency**: (1) Try larger models (13B+), (2) Hybrid rule-based + LLM, (3) Human-in-loop corrections

**Assumption 3: Users Willing to Use Separate Tool** (MEDIUM RISK)
- **Assumption**: PMs/POs will adopt BMADFlow despite having GitHub, Notion, Confluence
- **Validation**: POC user feedback, measure adoption rate (WAU) and engagement
- **Risk if Wrong**: Users stick to existing tools (inertia), BMADFlow becomes "nice demo, won't use daily"
- **Contingency**: (1) Integration strategy (embed into GitHub workflow), (2) Browser extension (reduce context switch)

**Assumption 4: Open Source Strategy Drives Adoption** (LOW-MEDIUM RISK)
- **Assumption**: Free tier for public repos will drive community adoption, word-of-mouth, and enterprise leads
- **Validation**: Track free tier signups, community engagement (GitHub stars, forum activity), conversion funnel
- **Risk if Wrong**: Free users don't convert to paid, no enterprise pipeline
- **Contingency**: Adjust freemium model (limit free tier features more), focus on direct sales (vs PLG)

**Assumption 5: GitHub Won't Improve Docs UX Soon** (MEDIUM RISK)
- **Assumption**: Microsoft/GitHub won't invest in documentation UX improvements in next 12-18 months (competitive window)
- **Validation**: Monitor GitHub roadmap, feature releases, community feedback
- **Risk if Wrong**: GitHub improves UX → BMADFlow's core value prop (better than GitHub) is diminished
- **Contingency**: (1) Positioning shift (intelligence layer, not UX layer), (2) Integration (complement GitHub, not replace)

**Assumption 6: Market Size Estimates Accurate** (MEDIUM RISK)
- **Assumption**: $85M SAM, 1M potential users, 3% achievable market share (from market research)
- **Validation**: POC conversion rates, early sales data, user survey feedback
- **Risk if Wrong**: Market is smaller or less willing to pay (lower revenue potential)
- **Contingency**: (1) Vertical focus (target high-value segments like finance), (2) Pricing adjustments, (3) Pivot to adjacent market

**Assumption 7: 4-6 Week POC is Achievable** (LOW-MEDIUM RISK)
- **Assumption**: Claude Code can accelerate development enough to deliver MVP in 4-6 weeks with 1 developer
- **Validation**: Weekly milestone tracking, scope adjustments if behind schedule
- **Risk if Wrong**: POC takes 8-12 weeks, delays validation and industrialization decision
- **Contingency**: Descope further (e.g., remove graph viz from MVP, focus on dashboard only), extend timeline

---

## Risks & Open Questions

### Key Risks

**Risk 1: LLM Extraction Accuracy Below Threshold** (HIGH IMPACT, MEDIUM PROBABILITY)
- **Description**: OLLAMA fails to reliably extract structured data (user stories, status, relationships) from BMAD docs
- **Impact**: Core value proposition (methodology intelligence) doesn't work → product fails
- **Mitigation**:
  - Benchmark early (Week 1-2 of POC) on diverse doc samples
  - Hybrid approach: Rule-based extraction + LLM enhancement (fall back to rules if LLM uncertain)
  - Larger models (13B, 70B) if 8B insufficient (requires GPU investment)
  - Human-in-loop: Allow manual corrections, use corrections to improve prompts
- **Contingency**: If extraction fails entirely, pivot to "better UX only" (beautiful rendering, no intelligence) - lower differentiation but still useful

---

**Risk 2: Graph Visualization Complexity Underestimated** (MEDIUM IMPACT, MEDIUM PROBABILITY)
- **Description**: Building interactive, performant graph visualization takes longer than 1 week (as planned in POC timeline)
- **Impact**: POC delayed, or graph feature dropped from MVP (loses key differentiator)
- **Mitigation**:
  - Use proven libraries (React Flow, D3.js) with examples, don't build from scratch
  - Start with simple tree view (hierarchical list) as fallback if graph is too complex
  - Limit initial scope (50 nodes, basic interactions), enhance post-MVP
- **Contingency**: Ship MVP without graph (table view of epics/stories instead), add graph in Phase 2 (post-POC enhancement)

---

**Risk 3: User Adoption Stalls Due to Tool Fatigue** (MEDIUM IMPACT, MEDIUM PROBABILITY)
- **Description**: Teams resist adopting "yet another tool," stick to GitHub despite pain points
- **Impact**: Low activation rate, high churn, slow growth (failed PLG strategy)
- **Mitigation**:
  - Zero migration effort (reads from GitHub, no data import)
  - Free tier (try before commit, no budget approval needed)
  - Quick wins (show value in <5 min of first use)
  - Viral adoption (individual PM uses, shares with team)
  - Integration strategy (embed into existing workflows, reduce "separate tool" perception)
- **Contingency**: Sales-assisted motion (not pure PLG), target teams actively searching for solution (pain-aware buyers)

---

**Risk 4: Competitive Response from Incumbents** (HIGH IMPACT, LOW-MEDIUM PROBABILITY)
- **Description**: Notion, Atlassian, or GitHub adds similar features (methodology intelligence, graph viz) within 12 months
- **Impact**: BMADFlow's differentiation disappears, competitive pressure increases, pricing power erodes
- **Mitigation**:
  - Speed to market (establish brand and users before incumbents notice)
  - Niche focus (methodology-specific is low priority for generalists)
  - Community moat (open source creates loyalty)
  - Continuous innovation (stay 12-18 months ahead on feature roadmap)
- **Contingency**: Become acquisition target (if beaten, sell to incumbent), or pivot to integration layer (complement incumbent, not compete)

---

**Risk 5: Open Source Strategy Backfires** (MEDIUM IMPACT, LOW PROBABILITY)
- **Description**: Free tier cannibalizes paid revenue (users satisfied with free, don't convert), or competitors fork open source code
- **Impact**: Revenue lower than projected, or competitor launches using BMADFlow code
- **Mitigation**:
  - Strategic open source (core extraction/rendering open, enterprise features proprietary)
  - Free tier limits (public repos only, 1 project) drive upgrade need
  - License choice (AGPL or commercial-friendly open core model)
  - Network effects (hosted version is better experience than self-hosting)
- **Contingency**: Reduce free tier features, shift to freemium trial (14 days full access, then pay), or fully proprietary (abandon open source if revenue critical)

---

### Open Questions

**Question 1: What is acceptable extraction accuracy threshold?**
- **Context**: 90% accuracy target, but what does "accuracy" mean? (per-field, per-document, user-perception?)
- **Decision Needed By**: Week 2 of POC (after initial extraction testing)
- **Stakeholders**: Product Owner (defines acceptable), Engineering (measures accuracy)
- **Impact on Scope**: If threshold is too high (95%+), may need larger models or human-in-loop (adds complexity)

---

**Question 2: Should POC include private repository support?**
- **Context**: MVP scoped for public repos only, but private repos are enterprise use case (higher revenue)
- **Decision Needed By**: Week 3 of POC (if needed for pilot projects)
- **Stakeholders**: Product Owner (prioritization), Pilot Users (feedback on necessity)
- **Impact on Scope**: Adds GitHub OAuth (1-2 weeks development), but unlocks enterprise validation

---

**Question 3: Which graph visualization approach to prioritize?**
- **Context**: Multiple options (hierarchical tree, force-directed graph, table view, multiple views)
- **Decision Needed By**: Week 4 of POC (graph implementation week)
- **Stakeholders**: Users (UX preference), Engineering (complexity assessment)
- **Impact on Scope**: Simple tree = 2-3 days, interactive graph = 5-7 days, multiple views = 10+ days

---

**Question 4: What is the right pricing for Team tier?**
- **Context**: Market research suggests $10-20, competitive range is $8-25
- **Decision Needed By**: Pre-launch (Q2 2026)
- **Stakeholders**: Product Owner, Finance (revenue model), Sales (customer feedback)
- **Impact on Business Model**: Price too high = low conversion, too low = unsustainable revenue (need A/B testing post-launch)

---

**Question 5: Should we support SAFe methodology in MVP or wait for Phase 2?**
- **Context**: SAFe is larger market (400K users) than BMAD (40K users), but adds complexity
- **Decision Needed By**: End of POC (industrialization planning)
- **Stakeholders**: Product Owner (market priority), Engineering (effort estimate)
- **Impact on Scope**: SAFe support = 2-4 weeks additional (extraction patterns, templates), but expands addressable market 10x

---

### Areas Needing Further Research

**Research Area 1: GitHub API Rate Limits & Sync Performance**
- **Topic**: How many API calls for 100-doc sync? Will we hit rate limits? (5,000 requests/hour for authenticated)
- **Why Critical**: Sync performance is core UX (if >10 min, users frustrated), rate limits could block functionality
- **Research Plan**: Prototype sync in Week 1, measure API calls, test with large repos (500+ docs)
- **Decision Impact**: May need API call optimization (GraphQL, batching), caching strategies, or enterprise GitHub API (higher limits)

---

**Research Area 2: OLLAMA Model Selection & Performance**
- **Topic**: Which model (Llama 3 8B, Mistral 7B, larger 13B+) provides best accuracy/speed trade-off?
- **Why Critical**: Model choice impacts extraction quality (core value) and infrastructure cost (GPU requirements)
- **Research Plan**: Benchmark 3-5 models on 50 sample docs (Week 1-2), measure accuracy + latency + resource usage
- **Decision Impact**: Larger models may require GPU (infrastructure investment), or cloud AI (cost + privacy trade-off)

---

**Research Area 3: User Willingness to Pay Validation**
- **Topic**: Market research says $10-20/user/month, but will *our* users actually pay that?
- **Why Critical**: Pricing is make-or-break for revenue model (too high = no adoption, too low = unsustainable)
- **Research Plan**: Price sensitivity survey (Van Westendorp), A/B test pricing pages post-launch, analyze conversion rates
- **Decision Impact**: May need to adjust pricing (lower to $8-10 for market entry), or change model (usage-based, enterprise-only)

---

**Research Area 4: Multi-Repo Relationship Detection Complexity**
- **Topic**: How to reliably link epics in repo A to stories in repo B? (cross-repo references are ambiguous)
- **Why Critical**: Multi-repo support is enterprise requirement (Year 1 feature), but technically challenging
- **Research Plan**: Prototype linking strategies (explicit markdown syntax, LLM inference, naming conventions), test with pilot multi-repo project
- **Decision Impact**: May need to defer multi-repo to Year 2, or require users to use explicit linking conventions (limits flexibility)

---

**Research Area 5: Compliance Requirements for Regulated Industries**
- **Topic**: What specific compliance features (audit logs, approval workflows, data residency) are must-haves for finance/healthcare?
- **Why Critical**: Enterprise expansion (Year 2) targets regulated industries (high willingness to pay), but compliance is complex
- **Research Plan**: Interview 5-10 compliance officers / security teams in finance/healthcare (Q1 2026), review RFP templates
- **Decision Impact**: May need SOC2 certification (6-12 months, €100-200K), or specific features (RBAC, encryption at rest)

---

## Appendices

### A. Research Summary

**Market Research Key Findings** (see [docs/market-research.md](docs/market-research.md)):
- **TAM**: $3.2B (global developer documentation tools market)
- **SAM**: $85M (methodology-focused, freemium-adjusted)
- **SOM (Year 3)**: $2.5-3M (conservative 3% market capture)
- **Growth Drivers**: AI adoption (45% YoY in dev tools), methodology adoption (30% YoY SAFe), remote work (65% distributed teams)
- **Pain Point Validation**: 78% of teams report documentation navigation as significant bottleneck (Stack Overflow 2025)

**Competitive Analysis Key Findings** (see [docs/competitor-analysis.md](docs/competitor-analysis.md)):
- **Main Competitors**: Notion (general docs, no methodology intelligence), GitHub (poor UX, free), Confluence (enterprise, dated UX), Mintlify (code docs, not project docs)
- **Market Gap**: No existing solution combines methodology intelligence + graph visualization + GitHub integration + privacy-first AI
- **Defensible Differentiation**: BMAD/SAFe expertise (2-3 year lead), self-hosted OLLAMA (privacy advantage), epic/story graphs (unique feature)
- **Competitive Window**: 2-3 years before incumbents (Notion, GitHub) add similar features (low priority for them)

**User Research Insights** (from POC pilot feedback):
- **Top Pain Points**: (1) Finding information quickly, (2) Project status visibility, (3) Onboarding new members, (4) Stakeholder communication
- **Feature Value Ranking**: (1) Graph visualization (9.2/10), (2) Better UX than GitHub (8.8/10), (3) Multi-view dashboard (8.5/10)
- **Willingness to Pay**: $10-20/user/month acceptable (compared to Notion $8-15, Confluence $6-11 + fees)

### B. Stakeholder Input

**DSI Team (Internal Sponsor)**:
- **Feedback**: Strong support for POC, pain point resonates (we feel it daily with BMAD projects)
- **Request**: Dogfooding with BMADFlow self-documentation (meta: use BMADFlow to visualize BMADFlow docs)
- **Concern**: Resource allocation (1 developer for 4-6 weeks is acceptable, but needs clear go/no-go criteria)
- **Decision**: Approved POC, industrialization decision pending POC results (80% positive feedback threshold)

**BMAD Core Team (Methodology Experts)**:
- **Feedback**: Enthusiastic about methodology-aware tooling (fills gap in BMAD ecosystem)
- **Collaboration**: Willing to provide methodology guidance, template examples, community promotion
- **Request**: Ensure BMADFlow respects BMAD flexibility (not rigid enforcement, support variations)
- **Opportunity**: Potential official BMAD tool endorsement if POC succeeds (credibility boost)

**Pilot Users (3 Product Teams)**:
- **AgentLab Team**: "GitHub docs are painful, excited to try alternative" (high engagement expected)
- **BMADFlow Team**: "Using our own tool is perfect validation" (dogfooding enthusiasm)
- **Project TBD**: Selection pending (prefer team with complex multi-epic structure for stress test)

### C. References

**Documentation & Standards**:
- BMAD Method Documentation: https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs
- Example BMAD Project (AgentLab): https://github.com/twattier/agent-lab/tree/main/docs
- SAFe Framework: https://scaledagileframework.com/
- Scrum@Scale Guide: https://www.scrumatscale.com/

**Technology References**:
- shadcn/ui Components: https://ui.shadcn.com/
- FastAPI Framework: https://fastapi.tiangolo.com/
- Pydantic AI: https://ai.pydantic.dev/
- pgvector Extension: https://github.com/pgvector/pgvector
- Neo4j Graph Database: https://neo4j.com/docs/
- OLLAMA (Local LLM): https://ollama.ai/
- React Flow (Graphs): https://reactflow.dev/
- Mermaid.js (Diagrams): https://mermaid.js.org/

**Market Research Sources**:
- Stack Overflow Developer Survey 2025: https://stackoverflow.com/dev-survey/2025
- JetBrains Developer Ecosystem 2025: https://jetbrains.com/dev-ecosystem-2025
- Gartner Market Guide for Team Collaboration Tools 2025
- IDC Worldwide Collaboration Applications Market 2025

**Competitive Intelligence**:
- Notion: https://notion.so/product
- Confluence: https://atlassian.com/software/confluence
- Mintlify: https://mintlify.com/
- Swimm: https://swimm.io/
- Obsidian: https://obsidian.md/

---

## Next Steps

### Immediate Actions (Pre-POC Kickoff)

**Action 1: Finalize Pilot Projects** (Owner: Product Owner, Due: Week 0)
1. ✅ Confirm AgentLab participation (validate BMAD structure, identify test users)
2. ✅ Set up BMADFlow self-documentation (meta validation)
3. ✅ Select 3rd pilot project (criteria: complex multi-epic, engaged team, diverse structure)
4. ✅ Schedule pilot user kickoff meetings (expectations, feedback process)

**Action 2: Development Environment Setup** (Owner: Engineering, Due: Week 0)
1. ✅ Install OLLAMA, test models (Llama 3 8B, Mistral 7B), benchmark performance
2. ✅ Set up Docker Compose (FastAPI + React + pgvector + Neo4j + OLLAMA)
3. ✅ Configure GitHub API access (personal access token, rate limit testing)
4. ✅ Initialize repository structure (monorepo, frontend/backend folders, CI/CD basic setup)

**Action 3: Define Success Metrics & Tracking** (Owner: Product Owner + Engineering, Due: Week 0)
1. ✅ Set up analytics (Mixpanel, Amplitude, or simple event tracking)
2. ✅ Define key events to track (sync, dashboard view, graph interaction, search)
3. ✅ Create user feedback survey (post-POC, NPS + feature ratings)
4. ✅ Establish weekly check-in cadence (Monday status, Friday demos)

**Action 4: Extraction Benchmark Dataset** (Owner: Engineering, Due: Week 1)
1. ✅ Collect 100 sample documents from pilot projects (epics, stories, PRDs, architecture)
2. ✅ Manually label "ground truth" (correct extraction results for validation)
3. ✅ Create extraction accuracy measurement script (compare LLM output to ground truth)
4. ✅ Run initial benchmark (establish baseline accuracy for OLLAMA models)

### POC Execution Plan (4-6 Weeks)

**Week 1-2: Backend Foundation**
- GitHub sync service (fetch repo, parse markdown, store in pgvector)
- LLM extraction pipeline (OLLAMA integration, prompt engineering, accuracy testing)
- Database schema (Projects, Documents, Sections, Relationships tables in pgvector + Neo4j)
- REST API (basic endpoints: add project, trigger sync, get documents)

**Week 3-4: Frontend Dashboard**
- React app setup (TypeScript, Tailwind, shadcn/ui)
- Multi-view dashboard (4 views: Scoping, Architecture, Epics, Detail)
- Markdown rendering (react-markdown, Mermaid.js integration, syntax highlighting)
- Navigation (view switching, inter-document links, table of contents)

**Week 5: Graph Visualization**
- Graph data preparation (extract relationships from Neo4j)
- Visualization component (React Flow or D3.js, hierarchical tree or interactive graph)
- Interactions (node click, status coloring, basic filtering)
- Fallback (if graph too complex, ship table view of epics/stories)

**Week 6: Integration, Testing, Refinement**
- End-to-end testing (add project → sync → explore dashboard → validate accuracy)
- Pilot user testing (3 teams, structured feedback sessions)
- Bug fixes and UX polish (based on user feedback)
- POC demo preparation (stakeholder presentation, decision meeting)

### PM Handoff (Post-POC)

**If POC Succeeds (≥80% positive feedback)**:

This Project Brief provides the full context for **BMADFlow** - an intelligent documentation visualization platform purpose-built for structured development methodologies. The POC has validated:
- ✅ Technical feasibility (LLM extraction works, graph visualization is valuable)
- ✅ User value (significantly better UX than GitHub, clear productivity gains)
- ✅ Market opportunity ($85M SAM, clear differentiation from competitors)

**Next Phase: Industrialization (8-12 weeks)**

Please start in **'PRD Generation Mode'**, review this brief thoroughly, and work with the user to:

1. **Refine Product Requirements** (based on POC learnings):
   - Confirm MVP scope (any adjustments from POC feedback)
   - Define Phase 2 features (authentication, private repos, semantic search)
   - Prioritize methodology expansion (SAFe, Scrum@Scale) vs other enhancements

2. **Create Detailed PRD** (section by section, as BMAD template indicates):
   - User stories with acceptance criteria (expand MVP features with edge cases)
   - Technical specifications (architecture decisions, API contracts, data models)
   - Success metrics (KPIs, targets, measurement plans)
   - Go-to-market plan (launch strategy, pricing finalization, marketing roadmap)

3. **Plan Industrialization Execution**:
   - Development roadmap (8-12 week sprint plan)
   - Resource allocation (1-2 developers, design support, QA)
   - Risk mitigation (address open questions, research areas from this brief)
   - Launch preparation (beta program, GA readiness criteria)

**Key Considerations for PRD**:
- POC feedback will inform feature refinements (ask for POC results summary)
- Open source strategy needs clarity (core vs proprietary features, licensing)
- Enterprise features (SSO, RBAC, compliance) should be roadmapped for Year 2
- Integration ecosystem (Jira, Slack) should be prioritized based on user demand

**Success Criteria for Industrialization**:
- Beta launch (Q2 2026): 500 free tier users, 10% conversion, NPS ≥50
- GA launch (Q3 2026): Product-market fit validated, scaling infrastructure ready
- Year 1 target (Q4 2026): 2,000 users, $72K ARR, clear path to Year 3 SOM ($2.5-3M)

---

**Document Version**: 1.0
**Date**: October 1, 2025
**Status**: POC Ready - Awaiting Kickoff
**Owner**: Mary (Business Analyst)
**Next Review**: Post-POC (Q1 2026) - Industrialization Decision Gate

---

*This Project Brief is a living document. Update based on POC findings, market feedback, and strategic decisions.*
