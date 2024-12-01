export const SocialMedia = {
  ImageMessage: class {
    constructor(user, api_id, group_id, caption) {
      this.user = user;
      this.api_id = api_id;
      this.group_id = group_id;
      this.caption = caption;
    }
  },

  Message: class {
    constructor(user, api_id, group_id, message) {
      this.user = user;
      this.api_id = api_id;
      this.group_id = group_id;
      this.message = message;
    }
  }
};