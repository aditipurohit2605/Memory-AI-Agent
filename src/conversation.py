class ConversationMemory:
    """
    Stores recent conversation messages
    for short-term memory.
    """

    def __init__(self, max_messages=10):
        self.messages = []
        self.max_messages = max_messages

    def add_user_message(self, message):
        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )
        self._limit_messages()

    def add_assistant_message(self, message):
        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )
        self._limit_messages()

    def get_messages(self):
        return self.messages

    def clear(self):
        self.messages = []

    def _limit_messages(self):
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]