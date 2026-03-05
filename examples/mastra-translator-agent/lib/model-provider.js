import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";
import { google } from "@ai-sdk/google";

const providers = {
  openai: (modelName) => openai(modelName),
  anthropic: (modelName) => anthropic(modelName),
  gemini: (modelName) => google(modelName),
};

/**
 * Resolves an Arthur model provider string and model name to an AI SDK model instance.
 * Supports "openai", "anthropic", and "gemini" — matching the providers configured
 * in Arthur Engine.
 */
export function resolveModel(modelProvider, modelName) {
  const provider = providers[modelProvider];

  if (!provider) {
    throw new Error(
      `Unsupported model provider "${modelProvider}". Supported: ${Object.keys(providers).join(", ")}`
    );
  }

  return provider(modelName);
}
