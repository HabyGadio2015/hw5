# HW 5 — AI Prompts Log

Word-for-word log of every prompt Haby typed, grouped by problem.

## Setup (before Problem 1)

1. Lets work in the HW 5 folder
2. We are doing this step by step one problem at a time. I will tell you what we need to do. For each problem I need you to prompt me with asking me the problem number and title. prompt me when we move onto to the next one. If I move us on before saying the number and title, bring me back.  And before we move onto to the next problem, I need you to ask me for feedback called "Feedback from Haby:" put that at the end of the problem. Do not let me move on without completing the feedback.
3. Here's the scenario we are working with. Campus Customs Multi-Agent Operations is the agentic team that runs the shop. Open tickets land on a board - customer orders, rent, unpaid bills, discount requetss, whatever the shop has to handle. You will build 3 pieces that tallk to each other: an MCP server, a FastAPI backend with a multi-agent team, and a React dashboard so a human can watch the agents at work and approve requests. Your agent team has FULL CONNECTIVITY any agent may delegate tasks to any other agent for help. In this assignment I need you to build these agents (1) BOSS - reads each ticket, decides who should work on it, and makes final calls (2) INVENTORY - checks stock by SKU and size, spots shortfalls, and figures out which vendor can restock. (3) ACCOUNTING - watches cash and invoices, check margins, and prepares payments or purchase orders for human approval (4) FACILITIES - handles the shop space side (leases, rent, etc) (5) CUSTOMER SERVICE - drafts messages for customers.
4. I need you to refer to data in the zip into the HW 5 folder I just put in there. Unzip it so you have data/campus_customs.db That file is the original shop database. Tables include desk, tickets, inventory, pricing, vendors, leases, cash_accounts, payments and invoices. Your tools will update the database as tickets get resolved. Make a copy of the database file called data/campus_customs_new.db and point your MCP server and backend at that working copy. Keep campus_customs.db untouched so you can reset when you want to restart resolving tickets
5. This is just background info, we haven't started Prob 1 yet
6. Here are the rules of this shop that MUST be followed. The field desk.date_today is "today' for the shop. Use this data to determine what is overdue. Vendor lead times come from the vendors table. A vendor will not ship new product while they still have an open unpaid invoice. Human approval is REQUIRED for any payments. Points WILL BE DEDUCTED IF THIS IS NOT FOLLOWED. If payment is made, make sure to update the relevant table. If there is not enough cash, the pay tool must refuse - no negative balances allowed. Cash only goes out in this homework. We did not model revenue, so no money comes in. Before a full run to resolve the tickets, make sure to reset the database to the original values. DO NOT EMAIL CUSTOMERS OR CALL ANY VENDORS. Drafts stay on the board. Use my PORTKEY_API_KEY for AL calls. For this assignment, use ONLY gpt-6-luna through Portkey for every agent. Muti-agent agent chats will burn my tokens fast. POINTS WILLE BE DEDUCTED IF ANY OTHER MODEL SHOWS UP IN MY CODE. BEFORE YOU START ANYTHING, I NEED YOU TO CONFIRM THAT YOU ARE USING THAT MODEL. In the end, we will be putting this in a public GitHub repo (that'll be the last problem).
7. (The agent asked which model name to use, because AGENTS.md listed an older model than the one in Haby's message. Haby confirmed via selection: "gpt-6-luna")
8. Yes update it all to gpt-6-luna

## Problem 1: Vibe Coder Prompts

1. Problem 1: Vibe Coder Prompts           Create AI_prompts.md at the start of the assignment and keep updating it as we go. The file is the log of what we did.

Feedback from Haby: No additional comments or edits were necessary in this first step.

## Problem 2: Study the Campus Customs Database

1. Problem 2: Study the Campus Customs Database.         Open data/campus_customs.db and look through every table and its fields. Copy the original file to data/campus_customs_new.db  -late problems update that working copy.
2. Prob 2 not finished. Study the 3 open tickets so you see how they link to other tables. Start output/harness.md For each table, list the fields and one short line on why that table matters for the agents. You will keep growing this harness file in later problems.
3. Remember what I said in the beginning, we are working on this step by step, stop jumping ahead

Feedback from Haby: The agent tried to circumvent my original instructions by referring back to previous homeworks. Again, it was necessary for me to remind it that we are working on this assignment step-by-step one problem at a time.

## Problem 3: Build the MCP Server

1. Problem 3: Build the MCP Server.            Write an MCP server in mcp_server/ using FastMCP. It will talk to data/campus_customs_new.db You do NOT need to connect or run it in this problem. Please do not.  Every agent in this HW uses the tools in this MCP server. You will add more tools to it later, for now write 3 tools you know you will need for the tickets in the database. Keep the names CLEAR. NEVER EVER EVER INVENT DATA. Only use info in the database.
2. which do you suggest
3. Ok go
4. In output/harness.md List each of your 3 MCP tools. For every tool include - which table it reads, which ticket it helps unlock (101, 102 or 103) and 1 sentence ONLY on why that tool is the right one for that ticket. Vague lines like "reads inventory" socre low - tie the tool to the ticket. Also add a short mcp_server/README.md file that explains what the MCP server is for, which database file it uses, and the 3 tools it has.

Feedback from Haby: Claude did well here in identifying a problem (which FASTMCP package to use) and instead of assuming - which is seemed like it was inclined to do because it referenced the work we did in the Lecture 9 folder - it asked for permission. As the human-in-the-loop, I need to be able to verify and have autonomy over the choices that need to be made throughout the assignment. I appreciated being asked permission. Keep up the good work.

## Problem 4: Add the MCP Server to Vibe Coder and Test Each Tool

1. Problem 4: Add the MCP Server to Vibe Coder and Test Each Tool

In my vibe coder, add your MCP server to THIS PROJECT so the vibe coder can call the tools. Save the connection JSON text in .mcp.json at the project root (or however you as the vibe coder saves local MCP server lists.
2. Give me the list of my 3 MCP tools. 1, 2, 3 no editorializing.
3. Give me a one liner of what each one does
4. one liner of how each of these are related or can help
5. i meant a liner of what they can do in combo
6. Great! With the vibe coder connected, test EACH of my 3 MCP tools. Save the evidence in output/mcp_smoke.json. For every tool include (1) the prompt you asked the vibe coder. Include what I asked. (2) The Tool Name (3) The Tool Output (must match values in data/campus_customs_new.db)
7. show we what you wrote for the last prompt. put it here
8. No I mean show me what you did to answer this prompt. put it here
9. Did you include what I asked? Remember the previous one-liner requests. Did you include those in the .json
10. Fix the capitalization and punctuation. Include your answers, and add them to the .json
11. show me

Feedback from Haby: My agent either did not understand the instructions or interpreted them differently. I knew it hadn't followed the prompt because the summary did not include any of the questions I gave it. I had to specifically ask it to include those requests within the .json

## Problem 5: Build the Agent Team and Grow the MCP Tools

1. Problem 5: Build the Agent Team and Grow the MCP Tools.  Build the agentic team for Campus Customs using PydanticAI: BOSS, INVENTORY, ACCOUNTING, FACILITIES, and CUSTOMER SERVICE. Include prompts, models, and agent loops so they can delegate work to each other with full connectivity. Put the agent prompts in backend/prompts/ ONE FILE PER AGENT. Put data types in backend/models.py and the agent files under backend/ (your layout can vary as long as the FIVE ROLES ARE CLEAR). Use my PORTKEY_API_KEY and ONLY gpt-6-luna for every agent.
2. 1. No additional instructions 2. If that is best, go ahead, if there's a better way, do it that way
3. Yes run it
4. Give me suggestions for shop rules an agent should follow
5. Now give me suggestions for tools you'd need to work on open tickets
6. Great! Now. Here are the rules I want you to follow. Make sure you have this listed for my grader to clearly see. Additionally, I want all these tool suggestions to also be listed for my grader.

1. The goal is to make a profit. P=R-C. Ensure that every sale has a profit and that no discount is given such that there is no profit.

2. Double check that payments are made ONCE. Do not double pay and flag any mistakes or concerns.

3. BOSS always has the last say.

4. A Human (meaning me) MUST approve before anything is paid.

5. Do not send any emails to customers and/or vendors.

6. Open tickets land on a board - customer orders, rent, unpaid bills, discount requests, whatever the shop has to handle.

7. DO NOT mark anything as resolved, if it is only partially resolved. Say Not Resolved. Add a "Partial Fulfillment" Note to explain the details in a one-liner.

8. NO INVENTIONS - of dates, amounts, requests, tools, etc etc. If something is not found, say so. If something is wrong, say so. If something is not there, say so.
7. Make sure the tools listed that you need for the MCP server work so you can open tickets. Shop facts come from the MCP server over data/campus_customs_new.db - do NOT INVENT a second shop-tools layer that bypasses MCP. Wire the agents so they append to output/audit_trail.json as they run: for each agent-loop step, record enough to audit later. Append to this file - do not wipe it each run. In output/harness.md list each agent and each MCP tool (incl ones you add in this prob) along w which table the tool uses. Also add a short safety section: the guardrails a real business would want when agents touch real customers and real money, plus limits that keep token use in check. Update mcp_server/README.md so the tool list matches what you have now.
8. I have a quick question: I ONLY want you to use gpt6 as I mentioned. I am working in Sonnet 5, correct? If I bump it up to Opus 5.5, are you still going to be operating in gpt6? Remember, my professor will mark me down if I use anything besides 6, so I DO NOT WANT THAT
9. Ok great. I am ready to move on

Feedback from Haby: I took the initiative of asking my agent to do a preliminary test in order to see its process and address any bugs early on. I like that it is being cost-efficient and raising the flag of the runs costing a high value. I believe it did so because I made a quick mention of it in the beginning. I also wanted to be crystal clear on gpt6 luna versus using the stronger models on Claude Code and it clarified that those are completely separate.

## Problem 6: Plan the 3 Tickets

1. Problem 6: Plan the 3 Tickets

Before you wire the backend, I want you to write down what you expect the team to do on each open ticket. Build output/desk_tickets.html - a page you can double-click with one tab per ticket (101, 102, and 103). Also add empty Cash and Reflection tabs for later problems (leave them blank or with a short "coming later" note for now). On each ticket tab, fill an Expected section only (leave room for an Actual section you will after you run the agents).
2. Give me suggestions for who the boss should call first (give me 3 suggestions and a 1 liner ONLY and why)

Agent delegations you expect

Which MCP tools you expect to run

. Do not do anything yet
3. Here's what I you to write for me for each ticket's Expected section (make sure my grader is able to see it):
(1) Who the Boss Should Call First
The BOSS should call INVENTORY first. This allows the BOSS to have a full scope of what products are available. It also gives the BOSS a full scope of the product specifications (SKU, SIZE and QUANTITY).
(2) Agent Delegations

* 101: BOSS → INVENTORY → ACCOUNTING
* 102: BOSS → FACILITIES → ACCOUNTING.
* 103: BOSS → INVENTORY → ACCOUNTING → CUSTOMER SERVICE

(3) MCP Tools To run

* `get_ticket` — all 3
* `check_inventory` — 101, 103
* `list_vendors` + `check_vendor_invoice_status` — 101, 103 (same vendor, Bulldog Print Co)
* `get_invoice` — 101
* `get_cash_balance` — 101, 102
* `get_pricing` — 103
* `get_lease` + `get_shop_today` — 102
* `save_draft` — 101, 103 (customer-facing drafts)
* `record_payment` — not expected to actually fire on any ticket yet, since no human approval has been given — ACCOUNTING should only recommend
* `update_ticket_status` — not expected yet either, since nothing should close out as resolved
4. Last thing on Prob 6: Plans that send every specialist on every ticket score low. You will compare this plan to what actually happens when your agents resolve the 3 tickets.

Feedback from Haby: I liked that my agent suggested separated delegations by number 101 vs. 102 vs. 103. I asked for 3 suggestions for BOSS calls and it advised picking between Inventory, Facilities and Accounting. I picked Inventory because I felt it was important for the boss to have a clear understanding of what we have and do not have. I did consider going to Accounting first because it would also give some information on inventory on top of invoices, but I worried the Boss would not have the full scope needed to make an informed decision.

## Problem 7: Backend Routes

1. Problem 7: Backend Routes.                        My react frontend dashboard (the next prob) needs a backend it can call. In backend/main.py use FastAPI and add routes that do the following things (1) Return the 3 tickets and whether each is open (2) Take a ticket ID and run my agent team on that ticket (3) Return recent agent events - what each agent said and which tools they used - so the board can refresh (4) Approve a payment or purchase after a human clicks approve (agents only prepare the pay) - this route is what actually changes cash) (5) Return the current checking balance from cash_accounts (6) Reset the database to the original values when you want to try a fresh run
2. We are not done yet hold on
3. From the backend/ folder, start the server with uvicorn main:app --reload --port 8000 (This turns on my backend at http://localhost:8000 so the frontend dashboard can call those routes. In output/harness.md list each route in one line (what URL and what it does)
4. Run a double check that all instructions have been followed

Feedback from Haby: I asked my agent to do a double check of its work because so far it has done a smooth job and I became worried that it was making mistakes or inventing. I was right. After doing the double check, the agent found mistakes and made those corrections.

## Problem 8: Agent Dashboard

1. Problem 8: Agent Dashboard 
Build the frontend dashboard in frontend/ with React + Vite + TypeScript. The page should call the routes you built in Prob 7. At minimum the board should do the following (1) List ALL 3 tickets (2) Let me pick one ticket ONLY and start the agent team on it (3) Show each agent and what they are saying and doing while the ticket runs (4) Mark a ticket resolved when the run finishes (5) Show a short summary of what each agent did on that ticket (5) Let human approve a pay or purchase when asked (6) Show the checking balance (it should drop after an approved pay). 
Make sure the dashboard looks good. Be creative with the layout and feel - this is a real desk people want to sit at, so MAKE IT BEAUTIFUL, ANIMATED WITH MOVEMENT AND ANIMATED WITH DESIGN CHARACTERS.
2. Lets wait a bit. Ask me again later.
3. Tell the frontend to talk to your backend at http://localhost:8000 On the backend allow the Vite page origin (usually http://localhost:5173 ) so the browser is allowed to call those routes. Start the board with npm run dev (This opens the React desk in my browser so you can pick tickets and watch agents. Write output/design.md with what you chose for the dashboard look (layout, how agents read differently, how resolved tickets and cash show up) and why - including the creative choices that make it feel special and something humans would actually enjoy using.

Feedback from Haby: This was the longest run thus far because the agent had to go through "scaffolding." It then wrote the whole dashboard . I also like that it created a specific "Human Panel" that is used for that human approval touch.

## Problem 9: Resolve The Tickets

1. Problem 9: Resolve The Tickets. Before testing the agents on a full run over the 3 tickets, RESET the working database data/campus_customs_new.db again so you can start clean. Note the start checking balance. Then run ALL 3 TICKETS on board (101, 102, 103) until each is resolved. Open output/desk_tickets.html from Prob 6. On each ticket tab, fill the ACTUAL section from this run: which agents worked, what they delegated, and which tools they used. Keep my Expected section so you can compare the two.
2. On the Cash tab of the same output/desk_tickets.html    Itemize the money: (1) Start checking balance after the reset (2) For EACH ticket: how cash changed when that ticket resolved, and why (which pay/purchase, dollar amount) (3) Ending checking balance - it must match cash_accounts in the working database. Note: Wrong cash math loses points even if the board shows every ticket resolved. Also save output/resolved_tickets.json for each ticket: ID, final status, short outcome, what each agent contributed, and any human approvals. output/resolved_board.html a page you can double click with a screenshot of your React board for each resolved ticket (101, 102, AND 103). Appeal real runs to output/audit_trail.json Finish output/harness.md so it covers tables, MCP tools, the 5 agents, API routes, the dashboard and safety rules
3. for qu 1 what is the optimal number? how many total are there
4. No "best guesses" run everything. for qu 2 - yes that working is good. Go ahead and run it
5. Approved
6. Can you do 2 without inventing anything - YES or NO only
7. Go ahead
8. Leave it as-is, move to 103
9. Wow how many minutes did that take?

Feedback from Haby: The agent was taking too long to process 102. At the 18 minute mark, I told it to leave it as is with the intention of bringing in a stronger model to take it to the finish line.

## Problem 10: Reflection

*(Note: Haby first gave this prompt during Problem 9, before the live runs. The agent held off because no real results existed yet, and filled the tab once Problem 9's runs were done. Haby later confirmed this work belongs under Problem 10.)*

1. Open output/desk_tickets.html and fill the Reflection tab. Answer these questions and be VERY THOROUGH: (1) How would you evaluate the performance of agents on each ticket and why? (2) For each ticket, how did Actual compare to Expected plan you wrote earlier? (3) What would have been simpler as one agent with tools - and WHY? (4) Describe 3 NEW problems CAMPUS CUSTOMS might face that this agent team could solve with the tools you built (5) Describe 3 NEW problems Campus Customs might face that this agent team could NOT solve with the tools you built and explain the tools and agents you would need to solve them.       For each answer, tie every answer to THIS app and the 3 tickets you ran. Use the ticket tabs and Cash tab on the same page as your evidence. REMEMBER GENERIC ESSAYS WITHOUT CAMPUS CUSTOMS DETAILS WILL SCORE LOW. I WANT A 100/100 this is very important to me, please no mistakes and no inventions
2. Yes. Do not take long please
3. I need only a yes or no answer: I am about to crank this last bit to Opus 5.5 - please verify that you will continue to stay in gpt6.
4. (Haby switched the Claude Code session model to Opus 5.5 with /model.) Great. Hello Opus 5.5 agent. I want you to act as the SUPERIOR agent that will check the previous agent's work with a fine tooth comb. I have high doubts about the previous agent's work because it was a lower model and made mistakes. I want you to go prompt by prompt, sentence by sentence and make sure that the previous agent did everything correctly, that there are no inventions and there are no mistakes. I want you to run the full check top to bottom 3 times. Let me know its mistakes and make those corrections. When you are finished, I want you to verify with me that everything has been followed down to the tiniest details and that my assignment willl receive a 100/100, anything less is unacceptable. Try not to spend more than $4.
5. Yes annotate, dont rewrite - unless it is incorrect. If it is incorrect fix it. I do not want wrong answers to show up anywhere in my results or my read receipts

Feedback from Haby: My agent was having a lot of trouble with 102. It marked it Not Resolved as I requested in the beginning. It then tried to offer me a solution by suggesting it could create a small read tool called "check_payment_history(kind, ref_id)" so that ACCOUNTING could verify whether or not rent was paid. I explicitly asked it if it was capable of doing so without breaking my golden rule of "no inventions" and it affirmed positively so I gave it the greenlight. Unfortunately however, even with this second tool, it was unable to. The entire process took almost 20 minutes. Eventually I gave it a hard stop because it was going in circles. I re-affirmed that we are still is gpt6, and then cranked up the model to Opus 5.5 (still with gpt6) and did a full re-run and check. The result: my Opus 5.5 agent said "I found several real errors in the previous agent's" work and proceeded to make those corrections.

## Problem 11: Submit to GitHub

1. Problem 11: Submit to GitHub

Push my code to a public GitHub repository so graders can clone it. Also put it in output/github_url.txt      DO NOT push my real .env to the GitHub repo. DO include both database files under data/ (the original and my working copy) so graders can run my app easily. 

Here is the expected layout. Please show me below how you will have it written so I can approve:

hw5/
├── AI_prompts.md
├── requirements.txt
├── .env.example
├── .gitignore
├── .mcp.json

├── README.md

├── data/
│   ├── campus_customs.db
│   ├── campus_customs_new.db

├── mcp_server/
│   ├── server.py
│   ├── README.md

├── frontend/

├── backend/
│   ├── main.py
│   ├── models.py

│   └── prompts/
│   │   ├── boss.md
│   │   ├── inventory.md

│   │   ├── accounting.md
│   │   ├── facilities.md

│   │   └── customer_service.md

└── output/
│       ├── harness.md
│       ├── mcp_smoke.json
│       ├── desk_tickets.html
│       ├── design.md
│       ├── resolved_tickets.json
│       ├── resolved_board.html
│       ├── audit_trail.json
│       └── github_url.txt


README should explain the following: copy original DB to the working copy when you need a clean run, start MCP server, start FastAPI backend, start the React board, reset the DB before a full 3 Ticket run.
2. Sorry I didnt clarify. Problem 10: Reflection. I already gave the prompt, so put all that work and the feedback under that problem (Open output/desk_tickets.html and fill the Reflection tab. Answer these questions and be VERY THOROUGH: (1) How would you evaluate the performance of agents on each ticket and why? (2) For each ticket, how did Actual compare to Expected plan you wrote earlier? (3) What would have been simpler as one agent with tools - and WHY? (4) Describe 3 NEW problems CAMPUS CUSTOMS might face that this agent team could solve with the tools you built (5) Describe 3 NEW problems Campus Customs might face that this agent team could NOT solve with the tools you built and explain the tools and agents you would need to solve them.       For each answer, tie every answer to THIS app and the 3 tickets you ran. Use the ticket tabs and Cash tab on the same page as your evidence. REMEMBER GENERIC ESSAYS WITHOUT CAMPUS CUSTOMS DETAILS WILL SCORE LOW. I WANT A 100/100 this is very important to me, please no mistakes and no inventions)
3. you didnt follow my layout for the tress
4. 1. A, 2. OK 3. like HW4 hide 4.public 5.why didn't you remind me? give me a quick one-liner of what went wrong
5. Is that where I had said leave it as is?
6. Yes or no only
7. Before that, one more thing, hold on
8. You are a new and the most superior agent called "The Professor." The previous agent's claim that it cannot guarantee a 100/100 does not suffice. I want you to comb through this entire chat from the first word in the first prompt all the way to the last word in my last prompt and make sure BOTH agents did it correctly. If there are any mistakes or inventions, fix it. $4 max spend. GO!
9. Do one last run through
10. No, Prob 6 heading is - Problem 6: Plan the 3 Tickets
11. Yes change it. Give me the probs and titles here. only that no editorializing
12. Keep my wording.
13. Let's wrap this up nicely
14. give me the website link here
15. Is the cards in team supposed to be double clickable?
16. Did the assignment not ask for clickablity for those
17. Yes do that please
18. Replace: Show all with "Hide" 
Delete: Pick a ticket and start the team to watch them work.
19. Nevermind about that last requst
20. Replace "Show All" with "Click the Yellow Button Above to See Agents at Work and Status Below"
21. is the website link in my https://github.com/HabyGadio2015/hw5 link and if so where
22. and its public yes or no only
23. Thank you
24. Make sure that's fixed. Do what's needed. Make the updates on my github so it is all correct for my professor
25. Make sure you run 103 yourself, because I don't trust the first agent's work
26. Ok
27. Thank you

Feedback from Haby: My Opus 5.5 agent said it cannot guarantee a 100/100. From my experience working with agents, when pitted against each other, they perform even better than expected. For this reason, I am going to create on last agent called "The Professor" who will do the final check of the previous 2 agents. Though Opus has done a great job of catching *many* mistakes of my 1st agent, I still doubt its complete accurateness, so this last check will catch any lingering bugs. 
