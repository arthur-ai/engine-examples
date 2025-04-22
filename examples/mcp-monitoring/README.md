# Prompt Validation using Open WebUI

## Video Demo

TODO: Insert Link to Demo Video

## Quickstart

1. Edit local.env file to add OpenAI configs
2. Run `SHIELD_VERSION=latest docker compose up`
3. Navigate to http://localhost:3000 and create a new admin account
4. Create a new Arthur Engine Filter Function
   1. Navigate to the Admin Panel - Functions (via profile icon in bottom left)
   2. Create a new function
   3. Copy the contents of filter.py into the filter and give it a name + description
   4. Save the filter
5. Run `python setup_engine.py` to set up the Task + Rules
   1. Copy the API Key + Task ID
6. Configure the filter
   1. Click the cog icon next to the filter
   2. Set the API Key and Task ID to what was output from the setup_engine.py output above
7. Turn the filter on and make it global
   1. Toggle the on/off switch to the left of the filter
   2. Click the ... and toggle the Global setting
8. Setup the MCP server for GSuite API
   1. Clone the gsuite-mcp server from Github (https://github.com/rishipradeep-think41/gsuite-mcp)
   2. Navigate to the directory you cloned the repo into and run `npm install`
   3. Read the README on how to grab and setup the GSuite credentials and follow those steps
   4. Run `npm run build`
   5. Start the MCP Server over HTTP so it can connect to Open WebUI with `uvc mcpo --port 8000 -- node ./build/index.js`
9. Configure Open WebUI to connect to the tools
   1. In Open WebUI, click the profile icon -> Settings and then select Tools
   2. Add a new tool and point the URL to http://localhost:8000
10. Start chatting
   1. Confirm that the tools are available (click the wrench icon below the prompt input)
   2. Ask questions about your inbox (eg: "Summarize my unread emails")

## Explanation

This example shows how to set up Open WebUI with an MCP Server that can interact with your GMail Inbox and Google Calendar.

By setting up the MCP server (https://github.com/rishipradeep-think41/gsuite-mcp) and configuring it to be available to
Open WebUI, LLMs can now work directly with the GSuite APIs and pull in content to generate messages.

More details can be found on our blog post here:
TODO: insert link



### Ways to extend this example

In setting up this project, it's been pretty cool to see how easy it was to get started, and how powerful this workflow could
be with some additional investments. Overall I could see something like this becoming part of my daily routine. That said, as-is,
it isn't quite as useful as I'd like. I've noticed a handful of problems that get in the way of my ability to completely rely on
this on a daily basis.

For example, things that I'd like to explore in the future are:

* Using a voice interface
    * I find that interacting with the LLM through a text interface is slower and more burdensome than just reading and interacting with the emails directly in my inbox.
    * I expect that, just like if I had an administrative assistant doing this, if I could interact with the system using my voice things would be much simpler.
* Integrating memory and preferences into the system
    * The system doesn't learn from my interactions. Unlike an administrative assistant, I cannot instruct the language model on what are the emails I'd consider requiring my immediate attention or action, nor can it learn to abstract and apply these instructions in a generic way for future emails.
    * I've read about how integrating with a preference or long-term memory store might help with this, so future work might include me playing around with some of these tools to see if I can get some of this.
* Keeping track of outstanding items / TODOs
    * While I aspire to get to inbox-zero, this isn't always feasible for me; I sometimes leave unread emails in my inbox as a cue that there's something I need to action at a later point when I have free time.
    * One thing that could be useful would be to integrate this with my preferred system for keeping track of action items so that I can keep track of things and hold true to inbox zero.
    * This could also help the "assistant" with keeping track of and reminding me of any actions that I need to prioritize.
* Integrating with an instant-messaging client (eg: Slack)
    * For some emails, it can be helpful to immediately resolve any outstanding questions or actions directly through a synchronous messaging channel (eg: slack).
* Adding calendar triage + workflows
    * A non-trivial amount of my email traffic are calendar invites - including both sending and receiving invitations to meetings.
    * I often have the most complicated schedule among people trying to schedule time with me, and so having an assistant that could help with booking time for everyone that I could also prompt on the priority (and therefore, could help with moving things around) would be helpful
* Improving the functionality with evals + monitoring
    * I plan on releasing a follow up to this post showing how to do this
    * Getting a workflow to work right some of the time is easy. Getting it to work right that’s good enough for daily use is quite hard.
    * Integrating with a third-party tool (like the Arthur Engine and Platform) will help with ensuring that my prompts always get me the desired and expected output, and that the system uses the right tools in the right way to generate the best expected output.

