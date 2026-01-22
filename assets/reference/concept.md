# Project Concept Template

A lightweight, [describe your application's category, e.g., productivity, social] app for [target audience] to [solve a specific problem]. The app allows users to [core action] with [key features]. This is designed as a [web app, mobile app, desktop app] for [number or type of users].

---

## Core Principles

- **Principle 1:** Explain the foundational idea behind your app. What is the most important concept a user should understand?
- **Principle 2:** Describe another core rule or philosophy. How does the app behave in a predictable way?
- **Principle 3:** Add any other guiding principles that define the user experience.

## Key Features

### Feature A: [Name of Feature]
- Describe the feature's purpose and how it works from a user's perspective
- Detail the specific actions a user can take related to this feature

### Feature B: [Name of Feature]
- Describe this second feature, its purpose, and its mechanics
- List the user interactions involved

---

## User Actions

- **[Action 1]:** Who can perform this action and under what conditions? (e.g., The creator of an item can edit its title)
- **[Action 2]:** What is another key interaction? What are its rules?
- **[Action 3]:** Detail any other significant user capabilities

---

## Data Synchronization Strategy

- **Source of Truth:** The [backend/client] is the single source of truth for all data. The UI updates based on responses from the authoritative source
- **Data Flow:** Describe how data gets from the server to the client. Is it through polling, a push-based service (like WebSockets), or simple request-response?
- **Conflict Resolution:** Explain how the system will handle potential conflicts. For example, if two users try to edit the same resource at once, how is that resolved? Often, the "source of truth" principle is sufficient, where the first-to-arrive action wins and the second is rejected

---

## Backend Schema

Define the required schema if your project needs a database.