class Censorer:
    def __init__(self, replace_ban_words_with=None):
        from better_profanity import profanity
        self.__profanity = profanity
        self.__profanity.load_censor_words(replace_ban_words_with)

    def update_custom_words(self, custom_words):
        self.__profanity.load_censor_words(custom_words)

    def __censor_text(self, text_to_censor, censor_char='*'):
        return self.__profanity.censor(text_to_censor, censor_char)

    def __contains_profanity(self, text_to_censor):
        return self.__profanity.contains_profanity(text_to_censor)

    def censor_it(self, text_to_censor: str,
                  return_empty_if_censored: bool = False, censor_char: str = "*") -> str:
        if return_empty_if_censored:
            if self.__contains_profanity(text_to_censor):
                return str("")
            else:
                return text_to_censor
        else:
            return self.__censor_text(text_to_censor, censor_char).strip()


if __name__ == "__main__":
    profanity = Censorer()

    text = ""
    while text != "/exit" or text != "exit":
        text = input("Enter text to censor:\n")
        censored_text = profanity.censor_it(text)
        print(censored_text)
