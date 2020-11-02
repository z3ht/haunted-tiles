# Haunted Tiles

![galaxy-brain](https://www.dailydot.com/wp-content/uploads/db4/41/6e8734dfe00c1b1d-768x384.jpg)

Tyler Technologies Coding Competition Fall 2020

### Structure:
The Haunted Tiles API executes on port `8421`. Ensure no other processes are using this port on the host machine.

`web` contains frontend code (executed by the client)

`api` contains api code (executed by the server)  
- All API endpoints should be located in `api/haunted_tiles.py` and point to relevant logic
(for an example, see endpoint `/`)
- Please abide by the [microservices](https://microservices.io/patterns/microservices.html) design patterns
- `GET` requests should **never** change state

`build.py` builds and runs the codebase (the server runs this automatically)

`setup.sh` automatically sets up a development environment  
- Environment variables are added to .env
<br />

## Environment Variables
Add these env variables so everything can be run

`HAUNTED_TILES_TARGET` → Haunted Tiles server target (testing: `localhost` or production: `haunted-tiles.xyz`)

[//]: # (TODO: remove secret key when repo goes public)
`HAUNTED_TILES_API_TOKEN` → Haunted Tiles secret key (set to: `ep1c-Passw0rD`)

<br />


## Competition Info

Tyler has built a web based game from scratch called Haunted Tiles and they are excited to host a competition for 
students across the nation to compete in.

### Register
Register here (https://haunted-tiles.tylerdev.io/register) by November 5th 11:59pm MST

Coding will open on November 6th at 5:00pm MST

At that time you will be able to clone from a repository or download a zip to begin development

### Prepare
There is specific software you'll need to download in order to participate

latest stable version of node (LTS) here -> https://nodejs.org/en/

### Submit
Code should be provided through a public hosted link to a single raw javascript file (preferably on Github), or directly
into the submission form as a string

We will pull your code at the start of each match. If you used a hosted link and if you’re brave enough :) you 
technically can push changes throughout the competition

There will be more directions on submission when coding opens. Know that if your code fails to run it is an 
automatic forfeit

Submission will be due by November 13th at 5:00pm MST

### Watch
The competition begins Friday November 13th at 6:00pm MST

It will be live streamed at https://www.twitch.tv/tylertechnologies/

### Tournament Format

#### Stage 1: Inner School Competition
During this stage teams will be compete against other teams from their same school

Seeding will be based upon registration order. For example the first team to register will play the last team to 
register

#### Stage 2: The Grand Finale
The winner from each inner school competition will then compete against each other in the grand finale. Only the first 
place AI from each school makes it to this stage

### Questions? 
Email `hauntedtiles@tylertech.com`