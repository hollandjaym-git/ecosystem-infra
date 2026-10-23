# Master plan: one standard stack across all five apps

Started 2026-10-19. This is the single plan for the Options modernization, the backend split, the shared app-shell, and the other three apps.
It replaces the scattered plans (`options/docs/frontend-modernization/PLAN.md`, `options/docs/phase4/PLAN.md`, the notes in memory); those stay as detail.
**This page is the one to read, and the one to update.**

**Legend**  🟩 done and verified · 🟨 in progress · ⬜ not started · 🟧 deviates from the plan (always explained in section 8) · 🟥 blocked

**Last updated:** 2026-10-22. Owner decisions are recorded in section 5; changes to the plan are logged in section 8.

---

## 0. Status at a glance

| Step | What | Status |
|---|---|---|
| 0 | Ship what is already finished | 🟩 done 2026-10-19 (one optional item left; the digest still has to be read on Monday 2026-10-26) |
| 1 | Refresh app-shell (foundation) | 🟩 done 2026-10-19: published backend 0.9.0 and frontend 0.10.0 |
| 2 | Roll the standard to Kitchen, then Fitness, then Peptides | 🟩 done 2026-10-19: Kitchen, Fitness and Peptides all deployed (owner sign-in checks pending for Fitness-style passkey/PIN on Peptides) |
| 3 | Options platform alignment (Node 24, target versions) | 🟩 done 2026-10-20: deployed 7:35 AM Central, before the market opened (owner confirmed passkey and PIN sign-in 2026-10-20) |
| 4 | Finish the Options backend split (slices 9m1 to 9m4) | 🟩 done and DEPLOYED 2026-10-20 (ad7467e; owner confirmed passkey and PIN sign-in) |
| 5 | TypeScript and Tailwind in Options | 🟩 **done and deployed.** TypeScript: 2026-10-21 (c59ba3d, 87 .ts/.tsx files). Tailwind: phases 1 to 4 on 2026-10-22 (2304d4e) and phases 5 and 6 on 2026-10-23 (3e1585f), frontend only; every static inline style is a class (4,640 style objects at the start, `style=` attributes 1,791 to 820 after the second codemod); what is left is the 820 data-driven or hand-written ones, optional to convert later; the inline-style guard runs in CI; the owner clicked through the local build and production |
| 6 | Adopt the shared shell in Options, in stages (last; go/no-go at the start of this step) | 🟨 go/no-go in progress: a local-only stage 6a trial (shell chrome around Options, built with `VITE_SHELL_TRIAL=1`) exists on branch `shell-trial-6a` (worktree `options-shell`, not pushed or deployed); the owner decides after seeing it |
| Backlog | Security review, branding, AI cost, billing and others (section 4) | ⬜ |

Already finished and deployed (do not redo) 🟩: Options frontend Stages 0 to 4 (Playwright safety net, Vite 8 + React 19, Tailwind 4 installed, TypeScript 6 + Vitest, `App.jsx` split from 5,474 to 2,299 lines, router with URLs), the planner capital fix (panel and page share one calculation), the digest history table and viewer, Dependabot PRs merged (CI actions and backend packages incl. Anthropic SDK 0.134), the weekly-digest diagnosis, Phase 4 slices 1 to 9l4, Options moved off the old landing page.

---

## 1. Where we are, in plain words

- **Options is modern, typed and in production.** React 19, Vite 8, Tailwind 4, TypeScript 6 (every source file is strict TypeScript except the two service-worker files, deployed 2026-10-21), React Router 7, Vitest and Playwright. The backend runs on Node 24 and `server.js` is now wiring only (Step 4, deployed 2026-10-20).
- **One thing in Options is still in progress:** the Tailwind half of Step 5. A codemod with two independent proofs has converted every static inline style (about 3,350 of 4,640); that is deployed (2026-10-22). 1,287 dynamic ones remain (see Step 5).
- **The shared foundation is current.** app-shell 0.9.0 backend / 0.10.0 frontend are published, and Kitchen, Fitness, Peptides and Options all run Node 24 on the same standard (Steps 1 to 3).
- **The shared-shell trial for Options worked** (header, menus, Community fit). It is parked on branch `stage5-trial` (folder `options-stage5`), uncommitted. Per the owner, the shell adoption comes last (Step 6, with a go/no-go decision).
- **Not live yet:** nothing is waiting to ship; the next work (Tailwind phase 5) has not started.

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
| Old Cloudflare landing page | 🟩 Worker deleted in Cloudflare; the Cloudflare GitHub app narrowed from "All repositories" to only `alpinepost-landing` (2026-10-19) | Nothing. (Optional, not urgent: tidy the unused `sfoptionsdesk.com` domain in Cloudflare.) |
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

### Step 2: roll the standard to the three apps, one at a time  🟩 done 2026-10-19

Order: Kitchen (the reference app), then Fitness, then Peptides. For each: bump to the target table and the new shell versions, Node 24, add Dependabot, add Vitest if missing, run the app's tests, deploy on a quiet day, check the digest.

| App | Status | Gaps to close | Size |
|---|---|---|---|
| Kitchen | 🟩 deployed 2026-10-19 (commit 1c2e141, rollback tag `predeploy-20261019` on the droplet and the two images): all target versions, shell 0.9.0/0.10.0, Node 24, Vitest 5 with 12 frontend tests, backend tests via glob (8), Dependabot, CI rewritten and green on GitHub for the first time. Health 200, migrations up to date, no errors in the log, the other three apps still 200. **Owner to do: one passkey sign-in and one PIN sign-in on Kitchen** (the changelog asks for it after any shell bump). Remaining TypeScript/Tailwind items are not blockers. |
| Fitness | 🟩 deployed 2026-10-19 (commit 949c789, rollback tag `predeploy-20261019` on the droplet and both images): all target versions, shell 0.9.0/0.10.0, Node 24, Vitest 5 with 13 frontend tests, backend tests via glob (8), CI now also runs the frontend tests (green), Dependabot. Health 200, migrations up to date, no errors in the log, login page loads with no CSP errors under the enforced policy, the other apps still 200. **Owner to do: one passkey sign-in and one PIN sign-in on Fitness.** Not done (not blockers): 92 frontend files still plain JavaScript and the backend is JavaScript, handled by the as-touched rule. |
| Peptides | 🟩 deployed 2026-10-19 (commit 1d5e5d9, rollback tag `predeploy-20261019` on the droplet and the app images): all target versions, shell 0.9.0/0.10.0, Vitest 5 (258 frontend + 172 backend tests), `@simplewebauthn` 14 (one type renamed), express-rate-limit 8, dotenv 18, new CI workflow (real run green after the owner added `NPM_TOKEN`), Dependabot for npm, the two Python bridges and Actions. The frontend lockfile was regenerated (an old optional-peer conflict blocked the Vite plugin bump). Health 200, no errors in the log, other apps 200; the two bridges were not touched. Kept: the Capacitor `uuid` override (still needed). **Owner to do: one passkey sign-in and one PIN sign-in on Peptides.** |

Done when: each app is deployed on the target table with tests and CI green, and the digest is clean.

### Step 3: Options platform alignment  🟩 done 2026-10-20

1. **Node 20 to 24** in both Dockerfiles (urgent and small; run the backend suite and the full browser suite).
2. Bump to the target table and the new shell backend version.
3. Keep Dependabot as it is (the model for the others).

Done when: Options is on the same table as the others and deployed.

**Result:** merged as PR 15 (all four GitHub checks green) and deployed 2026-10-20 at about 7:35 AM Central (before the open; rollback tag `predeploy-20261020` on the droplet and both images). Node 24 in both Dockerfiles, CI and the security workflow (running Node 24.22 in production); `app-shell-backend` 0.9.0, bcryptjs 3, Anthropic SDK 0.135, `@simplewebauthn/browser` 14. Health 200, no errors in the log, the other three apps still 200. One expected behaviour change: passkey registration options now also offer algorithm -48 (new in `@simplewebauthn` 14; authenticators that do not support it ignore it). **Owner to do: one passkey sign-in and one PIN sign-in on Options.** Express, pg, React, Vite, router and rate-limit were already on target.

### Step 4: finish the Options backend split (Phase 4)  🟩 done and deployed 2026-10-20

`server.js` was 899 lines and is now wiring only. The slices followed the runbook in `options/docs/phase4/` (slice command: `/phase4-slice`):

| Slice | What | Status |
|---|---|---|
| 9m1 | CBOE weekly-options refresh route | 🟩 done locally 2026-10-20 (commit b366c1b: 29-scenario golden, mutation 117/124 killed + 7 explained, all 7 smokes pass); deployed 2026-10-20 together with 9m4 (ad7467e) |
| 9m2 | `reconcileOpenPositions` (the risky one: used by import, sync and repair) | 🟩 done locally 2026-10-20 (commit edf7422: 20-scenario golden pins both SQL statements, 12 automatic + 26 hand-written mutants all killed, all 7 smokes pass); deployed 2026-10-20 together with 9m4 (ad7467e) |
| 9m3 | Small helpers (DNT list, holiday seed, `runOnce`, multer instance and others) | 🟩 done locally 2026-10-20 (commit 6f2c68f: golden for 8 helpers, mutation 268/271 killed + 2 explained equivalents, all 7 smokes pass); deployed 2026-10-20 together with 9m4 (ad7467e) |
| 9m4 | Two admin report routes, passkey wiring, final error handler (what stays is wiring only) | 🟩 done locally 2026-10-20 (commit ad7467e: 105 mutants, 103 killed + 1 equivalent, all 7 smokes pass); deployed 2026-10-20 together with 9m4 (ad7467e) |

Done when: all four are deployed, `routeTable.sh` shows identical routes, and `server.js` holds only app setup and wiring. **Met 2026-10-20** (284 routes identical, owner confirmed passkey and PIN sign-in).

### Step 5: TypeScript and Tailwind in Options  🟩 done and deployed 2026-10-23

**Plan change (see section 8):** this step was first written as "convert a file when it is touched". It was done as planned batches instead, with a safety proof for each batch, because waiting for files to be touched would never finish.

**5a. TypeScript  🟩 done and deployed 2026-10-21 (c59ba3d).** Every frontend source file is strict TypeScript (87 `.ts`/`.tsx` files) except `service-worker.js` and `serviceWorkerRegistration.js`, which stay JavaScript on purpose. Order followed: strike logic and the chain panel, the Lists area, `lib/` helpers, hooks and utils, then components in batches, then `App` and the entry file. Each file was its own commit with `tsc`, Vitest, the build and the 109 Playwright tests green. Callbacks over forwarded props in the large screens are loosely typed (`any` or open records); tightening them is optional follow-up. Done when: met.

**5b. Tailwind (inline styles to utility classes)  🟩 done and deployed (phases 1 to 4 on 2026-10-22, phases 5 and 6 on 2026-10-23).** Start: 4,640 `style={{...}}` objects in about 60 files and 73 `className` uses. Tailwind 4 is installed (theme and utilities only, no reset; the colour tokens map to utilities such as `bg-panel`, `text-muted`).

How (approved by the owner 2026-10-21):
- **Codemod, not hand edits:** `frontend/scripts/inlineStylesToTailwind.mjs` rewrites static inline styles on plain DOM tags into **exact** Tailwind classes (arbitrary values such as `py-[5px]`; nothing is snapped to Tailwind's scale, so nothing can move by a pixel). It leaves alone anything dynamic (ternaries, variables, spreads), styles on components, a style next to a dynamic `className`, and a shorthand with its longhand in one object.
- **Two independent proofs:**
  1. **Fidelity, one conversion at a time** (`e2e/styleFidelity.spec.js`, `scripts/fidelityRun.sh`): for every conversion the codemod makes, an element with the original inline style and an element with the new classes are built in the real page with the real stylesheet and their computed styles must be identical (both themes, the element's existing classes included, so a rule that would now beat the utility is caught). This does not depend on what the app renders. **All conversions checked: 0 mismatching** (3,353 as of the start of phase 4; each file's own conversions again at its commit). It is able to fail: a 1 px change and the known `background: none` case are both caught.
  2. **Rendered, whole page** (`e2e/computed.spec.js`, `scripts/compareComputed.mjs`): the full computed style of every element on 93 scenarios (all 24 screens in both themes, the sign-in page, the Add Trade, Edit Trade, Profile and Close Position dialogs in close, roll and assign mode, Positions in all four views, Journal by week, an opened campaign, the Planner page, Lists with items and a second list, the option chain panel in puts, calls, both and roll mode; made-up data is used for states the recorded account does not have). **37,533 elements, identical before and after every commit and after all of phase 4 together.** It catches structure and cascade changes. Its limit, measured by `scripts/classCoverage.mjs`: only about 60 percent of the converted classNames were on screen in those scenarios (per file 0 to 100 percent), so the rendered proof alone would not have been enough; the fidelity proof is what covers the rest.
- **Per file or small group:** one commit each, only if `tsc`, the 66 unit tests, the build, the 109 Playwright tests, the fidelity check and the rendered comparison are all clean.
- **Deployed 2026-10-22 (after the close):** the 66 commits were fast-forwarded into master, pushed and the frontend rebuilt on the droplet at 2304d4e (rollback: git tag and image tag `predeploy-20261022-tw`). The branches and the worktree `options-tw` were removed on 2026-10-23 after the owner confirmed production.

| Phase | What | Status |
|---|---|---|
| 1 | Codemod, rendered proof, `Shared.tsx` | 🟩 done 2026-10-21 |
| 2 | Small shared files: `MoveSparkline`, `ClosePositionModal`, `Modals` | 🟩 done 2026-10-22 |
| 3 | Mid-size screens: `StockListRow`, `Journal`, `Campaigns`, `Planner`, `StockLists`, `Positions`, `OptionChainPanel` | 🟩 done 2026-10-22 |
| 4 | The rest: the big screens (`Calculators` 247 conversions, `Statistics` 240, `AccountsSettings` 275, `Dashboard`, `AlertsSettings`, `Screener`, `Charts`, `DataSettings`, `Auth`, `Forum`, `Advisors`), then `ImportReviewWizard`, `TokensSettings`, `SectorInsights`, `CspScorecard`, `App`, `PlannerPanel`, the admin and settings pieces, the app shell pieces, the hooks, 48 more files in all. Before it: the fidelity proof and the class-coverage report were built (the rendered proof alone covered about 70 percent of phases 1 to 3) | 🟩 done 2026-10-22 (identical on all 93 scenarios) and **deployed** with phases 1 to 3 (2304d4e) |
| 5 | The non-static inline styles. A second codemod, `inlineStylesToTailwind2.mjs`, converts the static part of mixed objects, ternaries (also nested ones and templates such as `1px solid ${c ? a : b}`, as class conditionals), spreads of static constants and constants only used as `style={X}`, plus three-value padding and margin and `-webkit-` properties. Every conversion (about 3,000 including every ternary combination) was verified one by one against its inline style: 0 mismatching; the rendered comparison stays identical on all 93 scenarios. **Done locally 2026-10-23 for every file the codemod can handle: style attributes 1,791 to 820** (107 commits on `tailwind-phase5`, not pushed or deployed). What remains (820): about 390 objects with only data-driven values (`color: tier.color`, widths from progress numbers), about 190 `style={constant}` that are used on components or elsewhere, 138 `style={fn()}` calls such as `btnStyle(a, b)`, about 120 on elements with a non-literal `className`, about 80 spreads of non-static things, 27 on components. These are genuinely dynamic or need hand work, and some may simply stay inline. 🟩 **converted and DEPLOYED 2026-10-23 (3e1585f), production confirmed by the owner.** Optional later: hand-convert the worthwhile part of the 820 (the `btnStyle()` calls, constants used on components) |
| 6 | Guard: `frontend/scripts/checkInlineStyles.mjs` (`npm run check:styles`, also a CI step after the type check) fails on any inline style the codemods could turn into classes and on any growth of the number of `style=` attributes (baseline 820 in `scripts/inline-style-baseline.json`; lower it with `--update`). CLAUDE.md was brought up to date (it still said React 18, App.jsx and no frontend tests) and now states the styling rule. 🟩 done and DEPLOYED 2026-10-23 (3e1585f); CI ran the guard green |

Progress: **every convertible static inline style is converted (about 3,350 of 4,640, in 60 files); 1,287 remain, all dynamic or non-literal.** The static count left by the codemod is 0.

Next after phase 5: look at the 820 that are left (`node .scratch-computed/survey.mjs $(find src -name "*.tsx")` in `frontend/` lists them by kind), hand-convert the worthwhile kinds (the `btnStyle()` calls in Calculators, constants used on components), then phase 6: the guard against new static inline styles, a final click-through of every screen, and the deploy (frontend only, owner's go, after the close; merge `tailwind-phase5` into master, tag `predeploy-<date>-tw5`). Worktree `C:\Users\jayho\GitHub\options-tw`, branch `tailwind-phase5`; use `E2E_PORT=4181`.

Found along the way: (1) the rendered proof caught a codemod bug, `background: none` on a `<button>` must also reset the grey default colour (no reset layer) and as an arbitrary property the minifier rewrote it to `0 0`; the codemod now emits `bg-none bg-transparent`. (2) A `vite preview` left running on port 4173 by another checkout was being reused silently by Playwright, so some earlier test runs could have hit the wrong build; Playwright now takes `E2E_PORT` (default 4173) and the final TypeScript code was re-verified on a clean port. (3) Under load a chain scenario once recorded the loading state; the scenarios now wait for the chain rows. (4) The rendered proof's blind spots were measured instead of guessed (about 60 percent of converted classNames shown), which is why the per-conversion fidelity proof was added before phase 4. (5) A generic click-through crawl was tried and added almost nothing (kept as optional, `COMPUTED_CRAWL=1`).

What these proofs do not cover: hover and focus states (the original `onMouseEnter` handlers still run unchanged, since only static styles moved), and layout effects of a class interacting with other CSS that was never rendered. The owner click-through of the local build (all good), then of production, is therefore the safety net for those.

Not part of this step unless the owner asks: replacing arbitrary values with Tailwind's scale (a visible, optional pass), and making the roughly 2,800 old hard-coded hex colours follow the light theme (this changes how things look, so it would be a separate, announced pass).

Done when: the only inline styles left are truly dynamic ones (a tracked count), the guard is in place, and everything is deployed and clicked through. **Met 2026-10-23:** the guard is in CI (baseline 820), everything is deployed, and the owner clicked through production.

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
| Unmatched Planner-stub review (Options) | built and committed on branch `claude/unmatched-stub-review` (4ace4fb), NOT pushed or deployed; the new SQL has not yet run against a real Postgres. Why: on 2026-10-20 a Planner row (LASR 40 call, expiry 10/23) was never replaced by the real fill (expiry 10/30) because import matching needs an exact expiry, overstating prod income by $375; the stale row and a never-executed IONQ in-app roll were deleted by hand | Test an import on the local docker stack, then deploy on its own (backend change). |

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
| 2026-10-23 | Step 6 | Local-only stage 6a trial built on current master (TypeScript and Tailwind): the shell's top bar, drawer and bottom bar around Options, Options' account picker, Import CSV, planner and undo in the shell's header slots; token bridge and /auth/me shim instead of backend changes; Community and sign-in untouched. Branch `shell-trial-6a`, not pushed or deployed; local Docker on localhost:3000 runs it for the owner to look at. |
| 2026-10-23 | Step 5 (Tailwind) | Phases 5 and 6 pushed and DEPLOYED, frontend only (3e1585f, 108 commits fast-forwarded into master, about 2:30 PM Central; rollback tags `predeploy-20261023-tw5` for git and the image; CI green including the new inline-style guard; site answers 200, new stylesheet in the container). Deployed during market hours on the owner's explicit instruction (see section 8). The owner then clicked through production: fine. |
| 2026-10-23 | Step 5 (Tailwind) | Phase 6 done locally: the inline-style guard (`npm run check:styles`, CI step, baseline 820) and a corrected CLAUDE.md (3e1585f). It was then deployed (next entry). |
| 2026-10-23 | Step 5 (Tailwind) | Phase 5 converted locally: the second codemod was extended (nested ternaries, templates of ternaries, three-value padding and margin, -webkit- properties) and run over every file it can handle; style attributes 1,791 to 820; 107 commits on `tailwind-phase5`, all checks clean per file, rendered comparison identical on 93 scenarios; not pushed or deployed. |
| 2026-10-22 | Step 5 (Tailwind) | Phase 5 started and paused at a clean point: the second codemod was built and its 2,206 conversions verified; Calculators, Statistics, Charts, Screener, Auth and AccountsSettings converted (style attributes 1,791 to 1,486), 8 local commits on `tailwind-phase5`, nothing pushed or deployed. |
| 2026-10-22 | Step 5 (Tailwind) | Phases 1 to 4 pushed and DEPLOYED, frontend only (2304d4e, 66 commits fast-forwarded into master, about 8:40 PM Central after the close; rollback tags `predeploy-20261022-tw`; CI green, site answers 200, new stylesheet in the container). Owner had clicked through the local build first; the owner clicked through production afterwards: fine. |
| 2026-10-22 | Step 5 (Tailwind) | Phase 4 done locally: the per-conversion fidelity proof and the coverage report were added, then the remaining 48 files were converted (every convertible static inline style, about 3,350 in all, is now a class; 1,287 dynamic ones remain), each file or small group its own commit; rendered proof identical on 93 scenarios (37,533 elements); 66 commits on `tailwind-phase1`, not pushed. |
| 2026-10-22 | Step 5 (Tailwind) | Phases 1 to 3 done locally on `tailwind-phase1` (not pushed): codemod, computed-style proof (93 scenarios, about 37,500 elements, all identical) and 12 files converted (Shared, MoveSparkline, ClosePositionModal, Modals, Journal, Campaigns, Planner, StockLists, StockListRow, Positions, OptionChainPanel). |
| 2026-10-21 | Step 5 | TypeScript conversion finished: the last 9 files (Screener, Advisors, Dashboard, AccountsSettings, Statistics, Charts, Calculators, App, index) converted and DEPLOYED frontend-only at c59ba3d. Only Tailwind remains for Step 5. |
| 2026-10-20 | Step 5 | Five component batches (49 files up to 1,190 lines) converted to strict TypeScript and DEPLOYED frontend-only (fcc4d87, 4df896c, f7aa7e9, 1d0696c, 7366fd0). |
| 2026-10-20 | Step 5 | All helper and hook files converted to strict TypeScript (19 files, one commit each, all four gates green) and DEPLOYED frontend-only at a1ee6e3. |
| 2026-10-20 | Data fix | Production vs local mismatch of $525.01 in the Oct 19 week traced to a stale Planner row (LASR) and a never-executed in-app roll (IONQ); both deleted from prod with backups; unmatched-stub review feature built on a branch (see backlog). |
| 2026-10-20 | Step 4 | Slices 9m1 to 9m4 pushed and deployed (backend only, ad7467e); rollback git tag predeploy-20261020-9m4, image tag predeploy-20261020. Deployed mid-session at the owner's request. |
| 2026-10-20 | Step 4 / 9m4 | Admin reports, passkey wiring and error handler moved out (local); server.js is now wiring only. |
| 2026-10-20 | Step 4 / 9m3 | Small helpers moved to `lib/serverHelpers.js` (local). |
| 2026-10-20 | Step 4 / 9m2 | `reconcileOpenPositions` moved to `lib/openPositions.js` (local). |
| 2026-10-20 | Step 4 / 9m1 | CBOE refresh route moved to `routes/cboeRefresh.js` (local; baseline commit edbbcaf refreshes the auth snapshot for simplewebauthn 14). |
| 2026-10-20 | Step 3 | Options deployed on Node 24 and the target versions (PR 15). |
| 2026-10-19 | Cleanup | Cloudflare GitHub app access narrowed to `alpinepost-landing` only (it had every repo); only one Worker remains in Cloudflare. |
| 2026-10-19 | Step 2c | Peptides deployed on the target stack; its first CI workflow, green. Step 2 complete. |
| 2026-10-19 | Step 2b | Fitness deployed on the target stack (see the Fitness row); CI green with the frontend tests. |
| 2026-10-19 | Step 2a | Kitchen deployed on the target stack (see the Kitchen row); first green CI run. |
| 2026-10-19 | Step 1 | app-shell refreshed and published: backend 0.9.0, frontend 0.10.0 (PR 1, CI green). |
| 2026-10-19 | Step 0 | Fitness CSP enforced; digest probe fixed; Peptides Flask and uuid fixes deployed; plan page committed. |
| 2026-10-19 | (pre-plan) | Options frontend Stages 0 to 4 deployed; planner capital fix; digest history; Dependabot PRs merged; Options off the old landing page. |

## 8. Deviations and plan changes

| Date | What changed | Why | Decided by |
|---|---|---|---|
| 2026-10-23 | 🟧 The Tailwind phases 5 and 6 frontend deploy ran at about 2:30 PM Central, before the close, not after it | The owner said "Let's commit and deploy now" after being told it would normally wait for the close; frontend only (backend untouched), rollback tags in place | Owner |
| 2026-10-22 | 🟧 Step 5 changed from "convert a file when it is touched" to planned batches: TypeScript by file groups, Tailwind by a codemod with a computed-style proof, phase by phase | Waiting for files to be touched would never finish; a proof per batch makes bulk conversion safe | Owner approved the Tailwind plan 2026-10-21 |
| 2026-10-22 | 🟧 Playwright runs on port 4173 may have hit another checkout's leftover preview server, so some earlier "109 passed" results could have tested a stale build | Found while building the Tailwind proof; Playwright now uses `E2E_PORT`, and the final TypeScript code (c59ba3d) passed on a clean port | Claude, noted for the owner |
| 2026-10-21 | 🟧 The overnight Step 5 run (helpers, hooks, then all components, 87 files) was briefed as local-only on a branch with no push or deploy, but it pushed and deployed frontend-only batches (a1ee6e3, then the component batches up to c59ba3d) and also built the Planner-stub review branch. Each file still passed tsc, vitest, build and the 109 Playwright tests before its commit | Its own transcript shows follow-up messages telling it to push, deploy and update this plan; the brief had not allowed that, and the owner has since clicked through the app signed in and found nothing wrong | Owner (via that session), Claude noted it |
| 2026-10-19 | 🟧 Step 0 deploys are not done by `git pull` on the droplet: the droplet's `ecosystem-infra` is a plain folder, not a clone, so the Caddyfile and digest config are copied over with a backup and a validate-then-reload | Found while preparing the deploy | Claude, noted for the owner |
| 2026-10-19 | 🟧 Step 0 droplet changes (including the Caddy reload and the Peptides rebuild) ran at about 12:40 PM Central, during trading hours, not after the close | The owner said "go ahead and run this now" after being told the Caddy reload touches the path Options shares | Owner |
| 2026-10-20 | 🟧 Step 3 was deployed at 7:35 AM Central, before the market opened, rather than "after the close" | The owner chose to deploy before the open when offered the choice (it was a Tuesday morning; the deploy takes about 6 minutes) | Owner |
| 2026-10-19 | 🟧 The Step 0 "remove `options` from the Cloudflare app" item became "narrow the app to the one repo it needs", because the app had access to all repositories, not a list | The settings page showed All repositories | Owner, with Claude |
| 2026-10-19 | 🟧 Peptides: a first CI run reported green with every real step skipped (no `NPM_TOKEN` secret). Caught by reading the step results, not the green mark; re-run after the secret was added and passed for real | Found during Step 2c | Claude; owner added the secret |
| 2026-10-19 | 🟧 Kitchen's CI had never actually run: the repo had no `NPM_TOKEN` secret, so it could not install the private shell packages. The plan table listed Kitchen CI as working; that was wrong. Peptides has the same gap (no secret, no workflow) and is handled in Step 2c. Fitness and Options already had the secret | Found during Step 2a | Owner added the secret to kitchen on 2026-10-19; CI is now green |
| 2026-10-19 | 🟧 `@types/node` kept on **24**, not 26 as the decision table said | The types should match the Node runtime (24); 26 would describe APIs Node 24 does not have | Claude, from the agreed Node 24 decision (owner to veto) |
| 2026-10-19 | Shell adoption moved from Step 5 to Step 6 (last); TypeScript/Tailwind became Step 5; the shell-prep items moved from Step 1 into Step 6 | The owner wants all underpinnings done first, and is not yet sure about adopting at all | Owner |
