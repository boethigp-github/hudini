import {v4 as uuidv4} from 'uuid';

export const UserContext = {
  Message: class {
    constructor(content, refusal = null, role) {
      this.content = content;
      this.refusal = refusal;
      this.role = role;
    }

    debug() {
      return `Message(content: ${this.content}, refusal: ${this.refusal}, role: ${this.role})`;
    }
  },

  Choice: class {
    constructor(finish_reason = null, index, logprobs = null, message) {
      this.finish_reason = finish_reason;
      this.index = index;
      this.logprobs = logprobs;
      this.message = message;
    }

    debug() {
      return `Choice(finish_reason: ${this.finish_reason}, index: ${this.index}, logprobs: ${this.logprobs}, message: ${this.message.debug()})`;
    }
  },

  Usage: class {
    constructor(completion_tokens, prompt_tokens, total_tokens) {
      this.completion_tokens = completion_tokens;
      this.prompt_tokens = prompt_tokens;
      this.total_tokens = total_tokens;
    }

    debug() {
      return `Usage(completion_tokens: ${this.completion_tokens}, prompt_tokens: ${this.prompt_tokens}, total_tokens: ${this.total_tokens})`;
    }
  },

  Completion: class {
    constructor(id, choices, created, model, object, system_fingerprint = null, usage) {
      this.id = id;
      this.choices = choices;
      this.created = created;
      this.model = model;
      this.object = object;
      this.system_fingerprint = system_fingerprint;
      this.usage = usage;
    }

    debug() {
      const choicesDebug = this.choices.map(choice => choice.debug()).join(", ");
      return `Completion(id: ${this.id}, choices: [${choicesDebug}], created: ${this.created}, model: ${this.model}, object: ${this.object}, system_fingerprint: ${this.system_fingerprint}, usage: ${this.usage.debug()})`;
    }
  },

  ContextDataItem: class {
    constructor(prompt_uuid, user = null, status = null, model = null, completion = null) {
      this.prompt_uuid = prompt_uuid;
      this.user = user;
      this.status = status;
      this.model = model;
      this.completion = completion;
    }

    debug() {
      return `ContextDataItem(prompt_uuid: ${this.prompt_uuid}, user: ${this.user}, status: ${this.status}, model: ${this.model}, completion: ${this.completion ? this.completion.debug() : null})`;
    }
  },


  UserContextPrompt: class {
    /**
     * Creates UserContextPrompt
     * @param uuid uuid
     * @param user uuid
     * @param prompt string
     * @param status string
     * @param created timestamp
     * @param context_data array
     */
    constructor(uuid, user, prompt, status, created, context_data) {
      this.uuid = uuid;
      this.user = user;
      this.prompt = prompt;
      this.status = status;
      this.created = created;
      this.context_data = context_data;  // Array of ContextDataItem
    }

    debug() {
      const contextDataDebug = this.context_data.map(data => data.debug()).join(", ");
      return `UserContextPrompt(id: ${this.uuid}, user: ${this.user}, status: ${this.status}, created: ${this.created}, context_data: [${contextDataDebug}])`;
    }
  },

  PromptPostRequestModel: class {
    constructor(uuid, prompt, user, status = "INITIALIZED") {
      this.uuid = uuid;
      this.prompt = prompt;
      this.user = user;
      this.status = status;
    }

    debug() {
      return `PromptPostRequestModel(uuid: ${this.uuid}, prompt: ${this.prompt}, user: ${this.user}, status: ${this.status})`;
    }
  },

  PromptPostResponseModel: class {
    constructor(uuid, prompt, user, status = "INITIALIZED", created) {
      this.uuid = uuid;
      this.prompt = prompt;
      this.user = user;
      this.status = status;
      this.created = created;
    }

    debug() {
      return `PromptPostResponseModel(id: ${this.id}, uuid: ${this.uuid}, prompt: ${this.prompt}, user: ${this.user}, status: ${this.status}, created: ${this.created})`;
    }
  },

  UserContextPostResponseModel: class {
    constructor(user, thread_id, prompt) {
      this.user = user;
      this.thread_id = thread_id;
      this.prompt = prompt;
    }

    debug() {
      return `UserContextPostResponseModel(user: ${this.user}, thread_id: ${this.thread_id}, prompt: ${this.prompt.debug()})`;
    }
  },

  UserContextPostRequestModel: class {
    constructor(uuid, user, thread_id, user_context_prompt) {
      this.uuid = uuid
      this.user = user;
      this.thread_id = thread_id;
      this.prompt = user_context_prompt;
    }

    debug() {
      return `UserContextPostRequestModel(user: ${this.user}, thread_id: ${this.thread_id}, prompt: ${this.prompt.debug()})`;
    }
  }
};
