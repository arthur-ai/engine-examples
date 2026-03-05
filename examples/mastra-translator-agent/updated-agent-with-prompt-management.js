import { Agent } from "@mastra/core/agent";
import { arthurClient } from "./lib/arthur.js";
import { resolveModel } from "./lib/model-provider.js";

const prompt = await arthurClient.getPromptByTag("translator-prompt", "production");
console.log(`Loaded prompt "${prompt.name}" v${prompt.version} (model: ${prompt.model_name}, tags: ${prompt.tags.join(", ")})`);

// Mastra requires the system message via `instructions` — split it out from the rest
const systemMessage = prompt.messages.find((m) => m.role === "system");

export const translatorAgent = new Agent({
  name: "translator-agent",
  instructions: systemMessage?.content ?? "",
  model: resolveModel(prompt.model_provider, prompt.model_name),
});