\# AI Career Assistant



\# DOMAIN MODEL



\*\*Status:\*\* Draft



\*\*Version:\*\* 1.0



\---



\# Purpose



The Domain Model defines the core business entities of AI Career Assistant and the relationships between them.



This document serves as the blueprint for:



\* Database schema

\* SQLAlchemy models

\* Repository layer

\* Service layer

\* REST APIs

\* AI Engine



The goal is to model the real-world hiring process rather than individual job boards.



\---



\# Design Principles



\* Model real-world business entities.

\* Separate business concepts from implementation details.

\* Avoid duplicate information.

\* Keep relationships simple and scalable.

\* Every entity should have one primary responsibility.



\---



\# Core Entities



\## User



Represents the owner of AI Career Assistant.



Responsibilities:



\* Personal profile

\* Career preferences

\* Resume management

\* Skills

\* Experience

\* Certifications

\* Job preferences



Relationships:



\* Owns many Resumes

\* Owns many Applications

\* Owns many Skills



\---



\## Resume



Represents a version of a user's resume.



Examples:



\* Application Support Resume

\* Product Support Resume

\* DevOps Resume



Relationships:



\* Belongs to one User

\* Can be used in many Applications



\---



\## Company



Represents an employer.



Examples:



\* Blue Yonder

\* Microsoft

\* Google

\* Amazon

\* Atlassian



Relationships:



\* Has many Jobs

\* Has many Recruiters

\* Has many Employees



\---



\## Job



Represents the \*\*canonical job opportunity\*\*.



A Job exists independently of where it was found.



Examples:



\* Application Support Engineer

\* Product Support Engineer

\* Software Engineer



Stores:



\* Job ID

\* Title

\* Department

\* Location

\* Employment Type

\* Remote Status

\* Skills Required



Relationships:



\* Belongs to one Company

\* Has many JobPostings

\* Has many Applications



\---



\## JobPosting



Represents a single advertisement for a Job.



The same Job can appear on multiple platforms.



Examples:



\* LinkedIn Posting

\* Indeed Posting

\* Microsoft Careers Posting



Stores:



\* Posting URL

\* Source

\* Date Found

\* Last Scraped

\* Salary

\* Job Description

\* Posting Status



Relationships:



\* Belongs to one Job

\* Belongs to one Source



\---



\## Source



Represents a platform where JobPostings are discovered.



Examples:



\* LinkedIn

\* Indeed

\* Wellfound

\* RemoteOK

\* Greenhouse

\* Lever

\* Microsoft Careers

\* Google Careers



Stores:



\* Name

\* Type

\* Base URL

\* Scraper Name

\* Enabled

\* Last Scrape Time

\* Status



Relationships:



\* Has many JobPostings



\---



\## Application



Represents a job application submitted by the user.



Tracks the application lifecycle.



Statuses:



\* Saved

\* Applied

\* Interview Scheduled

\* Assessment

\* Rejected

\* Offer Received

\* Accepted



Relationships:



\* Belongs to one User

\* Belongs to one Job

\* Uses one Resume

\* Can have many Interviews



\---



\## Recruiter



Represents a recruiter working for a Company.



Stores:



\* Name

\* LinkedIn

\* Email

\* Position



Relationships:



\* Belongs to one Company



\---



\## Employee



Represents a company employee who may provide a referral.



Stores:



\* Name

\* Position

\* LinkedIn

\* Department



Relationships:



\* Belongs to one Company

\* Can create many Referrals



\---



\## Referral



Represents a referral request.



Stores:



\* Request Date

\* Status

\* Notes

\* Response Date



Relationships:



\* Belongs to one Employee

\* Belongs to one Application



\---



\## Skill



Represents a professional skill.



Examples:



\* SQL

\* Python

\* Linux

\* Azure

\* Shell Scripting

\* Oracle

\* ServiceNow



Relationships:



\* Belongs to one User



\---



\## Interview



Represents an interview process.



Stores:



\* Round

\* Date

\* Interviewer

\* Feedback

\* Result



Relationships:



\* Belongs to one Application



\---



\# Entity Relationships



User



\* Owns many Resumes

\* Owns many Skills

\* Owns many Applications



Resume



\* Belongs to one User

\* Used by many Applications



Company



\* Has many Jobs

\* Has many Recruiters

\* Has many Employees



Job



\* Belongs to one Company

\* Has many JobPostings

\* Has many Applications



JobPosting



\* Belongs to one Job

\* Belongs to one Source



Source



\* Has many JobPostings



Application



\* Belongs to one User

\* Belongs to one Job

\* Uses one Resume

\* Has many Interviews



Employee



\* Belongs to one Company

\* Has many Referrals



Recruiter



\* Belongs to one Company



Referral



\* Belongs to one Employee

\* Belongs to one Application



Interview



\* Belongs to one Application



\---



\# Career Ecosystem



```text

User

│

├── Resume

├── Skill

├── Application

│

▼

Company

│

├── Job

│      │

│      ├── JobPosting

│      │         │

│      │         └── Source

│      │

│      └── Application

│

├── Recruiter

└── Employee

&#x20;      │

&#x20;      └── Referral

```



\---



\# Future Entities (Not in Scope Yet)



The following entities are intentionally deferred until later milestones:



\* Contact

\* Hiring Manager

\* Assessment

\* Offer

\* Salary Benchmark

\* Certification

\* Portfolio

\* Networking Event

\* Learning Path



\---



\# Architecture Notes



The system is designed around \*\*Jobs\*\*, not \*\*Job Boards\*\*.



A single Job may appear on multiple platforms.



Each platform creates a separate JobPosting while referencing the same canonical Job.



This approach enables:



\* Duplicate detection

\* Multiple application options

\* Official careers prioritization

\* Better referral workflows

\* Cleaner analytics



\---



\# Future AI Capabilities



This model supports future AI features such as:



\* Intelligent job matching

\* Resume tailoring

\* ATS optimization

\* Referral recommendations

\* Recruiter discovery

\* Duplicate job detection

\* Company intelligence

\* Career analytics



