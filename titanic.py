"""Building Command Line Interface to list countries and top countries of shipping data."""
from fuzzywuzzy import fuzz
# from matplotlib import pyplot as plt

from load_data import load_data


def get_all_ships():
    """Get all ships data from the file"""
    return load_data().get("data")


def help_menu(_data):  # _data indicates unused parameter
    """Prints a list of the available commands."""
    return """Available commands:
              help
              show_countries
              top_countries <num_countries>
              ships_by_types
              search_ship <ship_name>
              speed_histogram
            """


def show_countries(data):
    """Prints a list of all the countries of the ships, without duplicates.
    The countries should be ordered alphabetically."""
    ships, _commands = data

    return "\n".join(sorted({ship.get('COUNTRY') for ship in ships}))


def top_countries(data):
    """Prints a list of top countries with the most ships.
    For example, top_countries 5, prints a list of the 5 countries
    which have the most ships, along with the number of ships."""
    ships, commands = data
    _command, num_countries = commands

    num_countries = int(num_countries)

    if num_countries in (0, -1):
        raise ValueError("Please enter a positive number more than 0 for numb_countries.")

    countries_list = []
    for ship_dict in ships:
        countries_list.append(ship_dict.get('COUNTRY'))

    countries_dict = {}
    for country in countries_list:
        countries_dict[country] = countries_list.count(country)

    top_n_countries = \
        list(sorted(countries_dict.items(), key=lambda x: x[1], reverse=True))[:num_countries]

    return "\n".join([f"{country}: {numbers_of_ships}"
                      for country, numbers_of_ships in top_n_countries])


def ships_by_types(data):
    """displays how many ships there are from each type."""
    ships, _commands = data
    ships_types = [ship.get('TYPE_SUMMARY') for ship in ships]

    ship_type_count = {}
    for ship_type in ships_types:
        ship_type_count[ship_type] = ships_types.count(ship_type)

    return "\n".join([f"{s_type}: {numbers}" for s_type, numbers in ship_type_count.items()])


def get_median_ships_scores(ships_scores):
    """Get median ships scores."""
    # Get the values of the dictionary and store them in a list.
    scores_list = list(ships_scores.values())
    # Sort the list in ascending order.
    scores_list.sort()
    # Find the middle value(s) of the sorted list.
    length = len(scores_list)
    if length % 2 == 0:
        return (scores_list[length // 2 - 1] + scores_list[length // 2]) / 2

    return scores_list[length // 2]


def search_ship(data):
    """Search Ship By names, case-insensitive and find by partial name.
        For example, if I searched "disney", I should find the ship "DISNEY DREAM"."""
    ships, commands = data
    name = " ".join(commands[1:])  # ['search_ship', 'QUEEN', 'MARY', '2']

    scores = {}
    # A generator expression () is similar to a list comprehension list([]),
    # but it creates a generator object instead of a list.
    # This can be more memory-efficient for large lists,
    # as it generates the values on-the-fly instead of creating a new list in memory.
    for ship_name in (ship.get('SHIPNAME') for ship in ships):
        ratio = fuzz.ratio(name.lower(), ship_name.lower())
        scores[ship_name] = ratio

    # if score is 100 means ship name entered has the exact match in the ship list of dict.
    if 100 in scores.values():
        found_ships_list = [ship for ship in ships if name.lower() == ship.get('SHIPNAME').lower()]

        for ship_dict in found_ships_list:
            return "\n".join([f"{key}: {value}" for key, value in ship_dict.items()])
    # no exact match, need recommendations
    else:
        median_score = get_median_ships_scores(scores)

        # get the scores that is above the double of median score, return top half of the results.
        recommended_names = {}
        for ship_name, score in scores.items():
            if score > median_score * 2:
                recommended_names[ship_name] = score

        recommended_names_desc = \
            sorted(recommended_names.items(), key=lambda item: item[1], reverse=True)[:5]

        if median_score == 0:
            print(f"'{name}' ship not found.")
        print(f"Ship '{name}' not found, do you mean:")
        return "\n".join([ship_name for ship_name, score in recommended_names_desc])


def speed_histogram(data):
    """Add a new command speed_histogram that
        creates an histogram of the speed of the ships, and save it to a file."""
    ships_list_dict, _commands = data
    #
    chart_data = {}
    for ship_dict in ships_list_dict:
        chart_data[ship_dict.get('SHIPNAME')] = ship_dict.get('SPEED')

    # Using macOS, not sure why running plt caused
    # ModuleNotFoundError: No module named 'winreg'
    # plt worked fine previously in the movie.py project.

    # plt.bar(chart_data.keys(), chart_data.values())

    # # add the names to the body of the bars
    # # for i, v in enumerate(chart_data.values()):
    # #     plt.text(i, v, list(chart_data.keys())[i], ha='center', rotation=90, va='top')
    #
    # plt.title('Ships Speeds')
    # plt.xlabel('Ships Names')
    # plt.ylabel('Speeds')
    #
    # # save plot to file
    # file_name = ''
    # while not file_name.endswith('.png'):
    #     file_name = input(
    #         "Enter a file name to save the histogram ends with '.png'): \n")
    #
    # plt.savefig(file_name)
    # print(f"'{file_name}' file has been created.")
    pass


def main():
    """Main function to load menu and call functions based on user input command."""
    ships_list_dict = get_all_ships()

    command_dict = {'help': help_menu,
                    'show_countries': show_countries,
                    'top_countries': top_countries,
                    'ships_by_types': ships_by_types,
                    'search_ship': search_ship,
                    'speed_histogram': speed_histogram,
                    }

    print("\nWelcome to the Ships CLI! Enter 'help' to view available commands.")

    while True:
        commands = input().split()

        if len(commands) != 0:
            command = commands[0]

            if command not in command_dict:
                if command.strip():  # check if user input is not empty
                    print(f"Unknown command {command}")
                continue  # continue request user input if empty

            try:
                print(command_dict.get(command)([ships_list_dict, commands]))
                print()

            except ValueError:
                print("Please enter a positive number more than 0 for numb_countries.")
                continue
            except Exception as error:
                print(error)
                continue


if __name__ == "__main__":
    main()
