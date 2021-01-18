
class InputValidator:
    """InputValidator is used to validate user input for GameBot"""

    def valid_game_url_input(self, input):
        """Validates a game search partial url contains alphanumeric values with forward slashes.

        Parameters:
        input (str): partial url for a game search

        """

        if not input or type(input) != str:
            return False

        input = input.strip()
        str_arr = input.split('/')

        for word in str_arr:
            if not word.isalnum() and word != '':
                return False

        return True


    def valid_search_input(self, input):
        """Validates search input is a str, less than 10 words, and is alphanumeric.
        
        Parameters:
        input (str): a game name 

        """

        if not input or type(input) != str:
            return False

        input = input.strip()
        str_arr = input.split(' ')

        if len(str_arr) > 10:
            return False

        for word in str_arr:
            if not word.isalnum():
                return False

        return True



if __name__ == "__main__":
    input_validator = InputValidator()
    print(input_validator.valid_search_string(None))
    print(input_validator.valid_search_string(''))
    print(input_validator.valid_search_string(' '))
    print(input_validator.valid_search_string('{}'))
    print(input_validator.valid_search_string('a!'))
    print(input_validator.valid_search_string('abs'))
    print(input_validator.valid_search_string('ab21'))
    print(input_validator.valid_search_string('123'))
    print(input_validator.valid_search_string('123 abn'))
    print(input_validator.valid_search_string('123 !'))
