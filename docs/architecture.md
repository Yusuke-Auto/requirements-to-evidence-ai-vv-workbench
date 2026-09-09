# Minimal Architecture

## Runtime path

1. Perception Adapter
2. Risk Assessor
3. AEB Supervisor
4. Brake Interface

## V&V support path

5. Evidence Logger
6. Review Agent Interface

## Context entities

- Vehicle
- Feature
- Requirement
- Component
- Scenario
- TestCase
- Evidence
- Finding
- HumanReview

## Core relations

- Feature `hasRequirement` Requirement
- Requirement `allocatedTo` Component
- Requirement `verifiedBy` TestCase
- TestCase `uses` Scenario
- TestCase `produces` Evidence
- Finding `references` Requirement/TestCase/Evidence
- Finding `reviewedBy` HumanReview
