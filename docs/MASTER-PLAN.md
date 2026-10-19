# Master plan: one standard stack across all five apps

Started 2026-10-19. This is the single plan for the Options modernization, the backend split, the shared app-shell, and the other three apps.
It replaces the scattered plans (`options/docs/frontend-modernization/PLAN.md`, `options/docs/phase4/PLAN.md`, the notes in memory); those stay as detail.
**This page is the one to read, and the one to update.**

**Legend**  🟩 done and verified · 🟨 in progress · ⬜ not started · 🟧 deviates from the plan (always explained in section 8) · 🟥 blocked

**Last updated:** 2026-10-19. Owner decisions are recorded in section 5; changes to the plan are logged in section 8.

---

## 0. Status at a glance

| Step | What | Status |
|---|---|---|
| 0 | Ship what is already finished | 🟩 done 2026-10-19 (one optional item left; the digest still has to be read on Monday 2026-10-26) |
| 1 | Refresh app-shell (foundation) | 🟩 done 2026-10-19: published backend 0.9.0 and frontend 0.10.0 |
| 2 | Roll the standard to Kitchen, then Fitness, then Peptides | 🟨 Kitchen 🟩 and Fitness 🟩 deployed 2026-10-19; Peptides next |
| 3 | Options platform alignment (Node 24, target versions) | ⬜ |
| 4 | Finish the Options backend split (slices 9m1 to 9m4) | ⬜ |
| 5 | TypeScript and Tailwind in Options, as files are touched (ongoing) | ⬜ |
| 6 | Adopt the shared shell in Options, in stages (last; go/no-go at the start of this step) | ⬜ |
| Backlog | Security review, branding, AI cost, billing and others (section 4) | ⬜ |

Already finished and deployed (do not redo) 🟩: Options frontend Stages 0 to 4 (Playwright safety net, Vite 8 + React 19, Tailwind 4 installed, TypeScript 6 + Vitest, `App.jsx` split from 5,474 to 2,299 lines, router with URLs), the planner capital fix (panel and page share one calculation), the digest history table and viewer, Dependabot PRs merged (CI actions and backend packages incl. Anthropic SDK 0.134), the weekly-digest diagnosis, Phase 4 slices 1 to 9l4, Options moved off the old landing page.

---

## 1. Where we are, in plain words

- **Options is modern and in production.** React 19, Vite 8, Tailwind 4, TypeScript 6 tooling, React Router 7, tests. Every screen has its own URL. All of it is deployed (2026-10-19).
- **Two things in Options are half done:** the backend split (`server.js` is 899 lines; four small slices left) and TypeScript/Tailwind *in the code* (tools installed; code mostly plain JavaScript with inline styles).
- **app-shell is not current.** Its lockfiles are behind its own version ranges, it runs on different Node versions from the apps, and it has not adopted several newer major versions.
- **The other three apps are not on one standard either:** different Node versions, test setups, automatic dependency updates, and amounts of TypeScript.
- **The shared-shell trial for Options worked** (header, menus, Community fit). It is parked on branch `stage5-trial` (folder `options-stage5`), uncommitted. Per the owner, the shell adoption now comes last (Step 6).
- **Some finished work is not live yet** (Step 0).

The reason it felt unfinished: the next layer kept starting before the last one closed. The fix is a fixed order, a "done when" line for each step, and this one status page.

---

## 2. The standard we are aiming for (the "target stack")

Every app, plus app-shell, ends up on this. "Latest" means the newest release of the current major unless section 5 says otherwise.

| Thing | Target | Today | Notes |
|---|---|---|---|
| Node (build + run) | **24** (`node:24-alpine`) | Options **20**; Kitchen, Fitness 22; app-shell 22 front / 24 back; Peptides 24 | Node 20 reached end of life in April 2026: Options is the urgent one. |
| React, React DOM | ^19.3 | 19.3 Options; 19.2 others | Safe patch bump. |
| Vite | ^8.3 | 8.3 Options; 8.2 others | |
| Tailwind | ^4.3 | same everywhere | Already aligned. |
| TypeScript | ~6.0 | same everywhere | TypeScript 7: wait (section 5). |
| Vitest | ^5 | Options 5; app-shell, Peptides 4.1; Kitchen, Fitness none | Adopt (section 5). |
| React Router | ^7.18 | 7.18.4 Options; 7.18.2 others | |
| vite-plugin-pwa | ^1.3 | 1.3 | Version 2: wait (section 5). |
| Express | ^5.3 | 5.3 Options; 5.1 others | |
| pg | ^8.23 | 8.23 Options; 8.12 to 8.16 others | |
| express-rate-limit | ^8.7 | 8.7 Options; 7.x others | Adopt (section 5). |
| Anthropic SDK | latest 0.13x | 0.134 Options; 0.120 to 0.122 others | Keep within a few releases. |
| `@simplewebauthn` | 14 | 13 in app-shell | Adopt carefully with a passkey sign-in test per app. |
| bcryptjs / dotenv / `@types/node` | 3 / 18 / **24** (matches Node 24, not 26) | 2 / 16 / 24 in app-shell before Step 1 | bcryptjs and dotenv adopted in app-shell 2026-10-19. |
| Postgres | 16 | 16 everywhere | Fine until 2028. |
| Dependabot | on, weekly, grouped | Options only | Add to the other four repos. |
| CI | build + tests on every push | Options, app-shell, Kitchen, Fitness; Peptides: no workflow folder found in my copy (the digest says green: check) | |
| Shared packages | current `app-shell-frontend` and `app-shell-backend` | Kitchen, Fitness, Peptides use both; Options uses the backend one only | Options' frontend adoption is Step 6. |

---

## 3. The order of work (do them in this order; finish each before the next)

Rule: **a step is done only when it is deployed (or merged), verified, and marked 🟩 here.** No new step starts while the previous one is half open, except items in Step 0 that are waiting on the owner.

### Step 0: ship what is already finished  🟩

Small, no new code. Deploys after market close (section 5).

| Item | State | What is left |
|---|---|---|
| ecosystem-infra: Fitness CSP enforced | 🟩 pushed | 🟩 Caddyfile backed up, validated, copied, Caddy reloaded; Fitness serves the enforced policy and its sign-in page loads with no policy errors. All four sites answer 200. |
| ecosystem-infra: digest probe fix | 🟩 pushed | 🟩 Config copied (backup kept); the dry-run now shows "Options public site" green. |
| Peptides: Flask 3.1.3 and uuid override | 🟩 pushed | 🟩 `deploy.sh` run: only the two bridges were recreated (Flask 3.1.3 confirmed inside both); Peptides backend and frontend untouched; site 200. |
| ecosystem-infra: this plan | 🟩 committed and pushed | Nothing. |
| Old Cloudflare landing page | disconnected in Cloudflare | Optional: remove `options` from the Cloudflare app in GitHub settings. |
| Options | everything pushed and deployed | Nothing. |

Done when: the next weekly security digest shows Options and Fitness green and Peptides with 0 alerts. (Checked early with a dry run: Options public site green. Still to read on 2026-10-26: Peptides alert count, and 2 failed admin sign-ins on Options flagged in the dry run, for the owner to glance at.)

### Step 1: app-shell refresh (the foundation)  🟩 done 2026-10-19

app-shell is its own repo; changing it touches no live app until an app bumps the package, so this is safe during trading hours.

1. Bring every dependency to the target table; refresh both lockfiles.
2. Apply the major versions agreed in section 5, one at a time, tests green after each.
3. Node 24 in its Dockerfiles; add Dependabot; keep CI green.
4. Publish new `app-shell-backend` and `app-shell-frontend` versions and write the changelog line each app needs.

Done when: app-shell builds and passes on the target table, new versions are published, and the changelog says exactly what an app must change.

**Result:** merged as app-shell PR 1 (GitHub checks green on Node 24 with Postgres) and published: `@hollandjaym-git/app-shell-backend` **0.9.0**, `@hollandjaym-git/app-shell-frontend` **0.10.0**. Routine bumps plus Vitest 5, express-rate-limit 8, bcryptjs 3 (checked: it verifies hashes written by version 2), dotenv 18, `@simplewebauthn` 14 (one type renamed; the real WebAuthn integration tests pass). 136 tests, both reference builds and both Docker images pass on Node 24. Dependabot added. `CHANGELOG.md` in the app-shell repo lists exactly what each app must do (section "What an app does to take these"). Deliberate gaps: `@types/node` stays on 24 (see section 8), TypeScript 7 and vite-plugin-pwa 2 wait (section 5).

### Step 2: roll the standard to the three apps, one at a time  🟨

Order: Kitchen (the reference app), then Fitness, then Peptides. For each: bump to the target table and the new shell versions, Node 24, add Dependabot, add Vitest if missing, run the app's tests, deploy on a quiet day, check the digest.

| App | Status | Gaps to close | Size |
|---|---|---|---|
| Kitchen | 🟩 deployed 2026-10-19 (commit 1c2e141, rollback tag `predeploy-20261019` on the droplet and the two images): all target versions, shell 0.9.0/0.10.0, Node 24, Vitest 5 with 12 frontend tests, backend tests via glob (8), Dependabot, CI rewritten and green on GitHub for the first time. Health 200, migrations up to date, no errors in the log, the other three apps still 200. **Owner to do: one passkey sign-in and one PIN sign-in on Kitchen** (the changelog asks for it after any shell bump). Remaining TypeScript/Tailwind items are not blockers. |
| Fitness | 🟩 deployed 2026-10-19 (commit 949c789, rollback tag `predeploy-20261019` on the droplet and both images): all target versions, shell 0.9.0/0.10.0, Node 24, Vitest 5 with 13 frontend tests, backend tests via glob (8), CI now also runs the frontend tests (green), Dependabot. Health 200, migrations up to date, no errors in the log, login page loads with no CSP errors under the enforced policy, the other apps still 200. **Owner to do: one passkey sign-in and one PIN sign-in on Fitness.** Not done (not blockers): 92 frontend files still plain JavaScript and the backend is JavaScript, handled by the as-touched rule. |
| Peptides | ⬜ | Already fully TypeScript and on Node 24; align versions; add a CI workflow if missing; Dependabot; drop the Capacitor `uuid` override once the CLI updates | Small |

Done when: each app is deployed on the target table with tests and CI green, and the digest is clean.

### Step 3: Options platform alignment  ⬜

1. **Node 20 to 24** in both Dockerfiles (urgent and small; run the backend suite and the full browser suite).
2. Bump to the target table and the new shell backend version.
3. Keep Dependabot as it is (the model for the others).

Done when: Options is on the same table as the others and deployed.

### Step 4: finish the Options backend split (Phase 4)  ⬜

`server.js` is 899 lines. Remaining slices follow the runbook in `options/docs/phase4/` (slice command: `/phase4-slice`):

| Slice | What | Status |
|---|---|---|
| 9m1 | CBOE weekly-options refresh route | ⬜ |
| 9m2 | `reconcileOpenPositions` (the risky one: used by import, sync and repair) | ⬜ |
| 9m3 | Small helpers (DNT list, holiday seed, `runOnce`, multer instance and others) | ⬜ |
| 9m4 | Two admin report routes, passkey wiring, final error handler (what stays is wiring only) | ⬜ |

Done when: all four are deployed, `routeTable.sh` shows identical routes, and `server.js` holds only app setup and wiring.

### Step 5: TypeScript and Tailwind in Options, as files are touched  ⬜ (ongoing)

Today 10 of 93 frontend files (about 1,400 of 33,500 lines) are TypeScript, with about 4,500 inline styles and no Tailwind classes. No big-bang. Rules: a file touched for any reason is converted to TypeScript and its styles move to Tailwind as part of that change; new files are TypeScript from the start; convert leaf files first (dialogs, drag-and-drop, passkeys, then leaf components), big components last.

Done when: nothing is "in progress"; what remains is a tracked list that shrinks as files are touched.

### Step 6: adopt the shared shell in Options, in stages (last)  ⬜

Owner decision 2026-10-19: adopt in stages, but **only after the underpinnings (Steps 0 to 4) are done**, and the owner is not yet sure about adopting at all. So Step 6 begins with a go/no-go, using `options/docs/frontend-modernization/STAGE5-DECISION.md` (on the trial branch) and the real state of the shell after Step 1.

- **If go:** stage 6a shell chrome (header, menus, drawer, dialogs); stage 6b Community. Keep User Management, Profile and sign-in as Options' own until each is checked. First, close the gaps the trial found: `/auth/me` answers `{ user }` as well as the bare user (compat), forum routes aliased as `/community/*`, `/me/prefs` route, a login-page branding slot in the shell, and a way for shell pages to point at an existing backend. A one-time sign-out for everyone happens when the token key changes; choose a quiet day.
- **If no-go:** close the branch, record it here, and Options keeps its own UI.

Done when: the go/no-go is recorded here, and either the staged adoption is deployed or the branch is closed.

---

## 4. Standing backlog (not tech stack; do not let it interrupt Steps 0 to 6)

| Item | State | When |
|---|---|---|
| Security rollout (passkey hint, user-only checks) | paused 2026-10-15 | After Step 2: it ships through the shell versions. |
| Full security review of Options (OAuth tokens, endpoint gating) | requested 2026-09-29, not started | After Step 4 (easier once the code is split). |
| Login page branding (Options, Peptides, Fitness like Kitchen) | not started | With Step 1 (a branding slot in the shell), then each app in Steps 2, 3 and 6. |
| AI cost follow-up (trim advisor tool results, caching) | waiting on a few days of usage logs | Any time; independent. |
| Billing (Stripe sandbox) | built, paused until the owner decides | Owner's call. |
| All-values view (401K plus trading accounts) | "for later" | After Step 4. |
| "Set Default" account review | undecided | When the owner wants. |
| SnapTrade "add brokerage" notes for users | documentation | Any time. |
| GKTW | parked | Skip in cross-app audits. |

---

## 5. Decisions (recorded 2026-10-19)

| # | Question | Decision |
|---|---|---|
| 1 | Shared shell in Options | **Adopt in stages, and last.** Do all the underpinnings first; go/no-go at the start of Step 6. |
| 2 | Major versions | Adopt: Vitest 5, express-rate-limit 8, `@simplewebauthn` 14 (with a passkey sign-in test per app), bcryptjs 3, dotenv 18, `@types/node` 26. **Wait:** TypeScript 7 (a few months), vite-plugin-pwa 2 (until the shell and Kitchen are on the new base). |
| 3 | Node | **24 everywhere.** |
| 4 | Deploy days | **After market close or weekends** (no production deploys during trading hours). |

---

## 6. Working rules so nothing is left half done

- One step open at a time. A step is done only when its "done when" line is true; then mark it 🟩 here with the date.
- Anything unfinished at the end of a session is written in section 8 or the step itself, with the exact next action.
- Anything that differs from this plan is marked 🟧 and explained in section 8 (what changed, why, who decided, date).
- While markets are open: work in branches or in the app-shell repo; deploy only on the agreed days.
- Update this page when a step finishes. The older plan files only hold detail.

---

## 7. Completion log (newest first)

| Date | Step | What was completed |
|---|---|---|
| 2026-10-19 | Step 2b | Fitness deployed on the target stack (see the Fitness row); CI green with the frontend tests. |
| 2026-10-19 | Step 2a | Kitchen deployed on the target stack (see the Kitchen row); first green CI run. |
| 2026-10-19 | Step 1 | app-shell refreshed and published: backend 0.9.0, frontend 0.10.0 (PR 1, CI green). |
| 2026-10-19 | Step 0 | Fitness CSP enforced; digest probe fixed; Peptides Flask and uuid fixes deployed; plan page committed. |
| 2026-10-19 | (pre-plan) | Options frontend Stages 0 to 4 deployed; planner capital fix; digest history; Dependabot PRs merged; Options off the old landing page. |

## 8. Deviations and plan changes

| Date | What changed | Why | Decided by |
|---|---|---|---|
| 2026-10-19 | 🟧 Step 0 deploys are not done by `git pull` on the droplet: the droplet's `ecosystem-infra` is a plain folder, not a clone, so the Caddyfile and digest config are copied over with a backup and a validate-then-reload | Found while preparing the deploy | Claude, noted for the owner |
| 2026-10-19 | 🟧 Step 0 droplet changes (including the Caddy reload and the Peptides rebuild) ran at about 12:40 PM Central, during trading hours, not after the close | The owner said "go ahead and run this now" after being told the Caddy reload touches the path Options shares | Owner |
| 2026-10-19 | 🟧 Kitchen's CI had never actually run: the repo had no `NPM_TOKEN` secret, so it could not install the private shell packages. The plan table listed Kitchen CI as working; that was wrong. Peptides has the same gap (no secret, no workflow) and is handled in Step 2c. Fitness and Options already had the secret | Found during Step 2a | Owner added the secret to kitchen on 2026-10-19; CI is now green |
| 2026-10-19 | 🟧 `@types/node` kept on **24**, not 26 as the decision table said | The types should match the Node runtime (24); 26 would describe APIs Node 24 does not have | Claude, from the agreed Node 24 decision (owner to veto) |
| 2026-10-19 | Shell adoption moved from Step 5 to Step 6 (last); TypeScript/Tailwind became Step 5; the shell-prep items moved from Step 1 into Step 6 | The owner wants all underpinnings done first, and is not yet sure about adopting at all | Owner |
