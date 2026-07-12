# P1Y validation report

## Result

- P1Y: **PASS**
- P2-Lite: **PARTIAL**
- Engine: Unreal Engine 5.2.1
- Save/reopen: passed
- New load, asset or Blueprint compile errors: 0

## Scene and NPC evidence

The run fixed exposure, reduced Bloom, restrained the main/sky/accent lighting hierarchy, and used neutral grey materials with limited cool-blue and amber accents. Three complete Manny/Quinn humanoids were present with animation classes and feet within 2 cm of the navigation surface by bounds checks.

## P2-Lite evidence

RecastNavMesh runtime generation changed from static to dynamic and persisted after reopen. A 65-second PIE test recorded movement and idle samples for all three NPCs. Maximum displacement was 416.9, 361.8 and 306.8 cm; sampled maximum speed was 165 cm/s for each NPC.

The movement sequence was issued by a repeatable Python PIE harness. The Behavior Tree and Blackboard assets exist, but the random-patrol graph is not wired. P2-Lite therefore remains partial.

## Publication boundary

The public package omits the real project path, user/machine identifiers, process IDs, raw logs, caches, screenshots from the private working project, and the locally installed Manny/Quinn assets.
