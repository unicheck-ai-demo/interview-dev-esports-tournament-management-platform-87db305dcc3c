# Interview Tasks

## Task 1: Participant Registration Capacity Enforcement

Users are able to register for a tournament even after it has reached its maximum capacity. This causes tournaments to exceed their configured participant limits and can lead to scheduling and resource issues.

The system should prevent any further player registrations once the maximum number of participants has been reached for a tournament.

## Task 2: Global Capacity Enforcement for Players and Teams

Tournaments can become overbooked because individual player and team registrations are counted separately against the maximum participants limit. This allows a tournament to accept more participants than intended, leading to logistical challenges and potential resource overuse.

The system should enforce the maximum number of participants limit across both individual player and team registrations so that once the limit is reached, no further registrations of either type can be accepted.

## Task 3: Star Performers Endpoint

Organizers want a way to quickly see the top performers in any tournament. The platform should provide a new API endpoint that, given a specific tournament, returns two lists: the top three players and the top three teams ranked by their current scores. If the tournament cannot be found, the system should return an appropriate error response.
