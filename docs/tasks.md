# Interview Tasks

## Task 1: Participant Registration Capacity Enforcement

Users are able to register for a tournament even after it has reached its maximum capacity. This causes tournaments to exceed their configured participant limits and can lead to scheduling and resource issues.

The system should prevent any further player registrations once the maximum number of participants has been reached for a tournament.

## Task 2: Global Capacity Enforcement for Players and Teams

Tournaments can become overbooked because individual player and team registrations are counted separately against the maximum participants limit. This allows a tournament to accept more participants than intended, leading to logistical challenges and potential resource overuse.

The system should enforce the maximum number of participants limit across both individual player and team registrations so that once the limit is reached, no further registrations of either type can be accepted.