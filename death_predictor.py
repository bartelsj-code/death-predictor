'''
Written by Jonas Bartels
'''
from datetime import date, timedelta
from sys import argv
from SearchArgs import*
import random
from csv_reading import*

def initialize_data(data_file_name):
    ''' Takes in file_name and returns contained data as array'''
    return get_CSV_data_as_list(data_file_name)

def find_relevant_lines(data, search_info):
    ''' Takes in data array and search_info object and finds all lines that fit the search_info parameters'''
    relevant_lines = []
    total_relevant_deaths = 0
    for line in data:
        if equal_or_none(line[0], search_info.state) & equal_or_none(line[2], search_info.gender):
            if int(line[1]) >= int(search_info.age):
                relevant_lines.append(line)
                if line[5] == "under 10":
                    line[5] = 5
                total_relevant_deaths += int(line[5])
    return relevant_lines, total_relevant_deaths

def check_bounds(age_range,age):
    '''Takes a string of the format 'number-number' and checks whether age lies between the two (inclusive)'''
    bound_list = age_range.split("-") 
    bottom = int(bound_list[0])
    top = int(bound_list[1])
    if bottom-1 < age & age < top+1:
        return True
    else:
        return False

def get_codes_list(relevant_data,age):
    '''Creates a list of ICD-10 codes that should not be reused if a miscellanious option is called.'''
    codes_list = []
    for line in relevant_data:
        if line[1] == str(age):
            codes_list.append(line[4])
    return codes_list

def find_relevant_misc_lines(data, search_info, codes_list):
    ''' Creates a list of alternate deaths to replace a 'Miscellaneous' result'''
    relevant_lines = []
    total_relevant_deaths = 0
    for line in data:
        if equal_or_none(line[0], search_info.state) & equal_or_none(line[2], search_info.gender) & (line[4] not in codes_list):
            if check_bounds(line[1],int(search_info.age)):
                relevant_lines.append(line)
                total_relevant_deaths += int(line[5])
    return relevant_lines, total_relevant_deaths

def flip(data):
    ''' Takes in an array and reverses it'''
    new_list = []
    for i in range(len(data),0,-1):
        new_list.append(data[i-1])
    return new_list

def select_death(relevant_data, pick_number):
    ''' Takes in relevant_data array, and then returns the pick_number-th death (not line) counting from the end of the list'''
    flipped_data = flip(relevant_data)
    line_num = 0
    for line in flipped_data:
        for i in range(int(line[5])):
            line_num += 1
            if line_num == pick_number:
                return line

def find_death_circumstances(relevant_data, total_relevant_deaths):
    ''' generates a number between 0 and the total number of relevant deaths and then uses select_death() to pick one and returns that'''
    pick_number = random.randint(0, total_relevant_deaths)
    death_line = select_death(relevant_data, pick_number)
    return death_line

def equal_or_none(compared, value):
    '''detects if compared and value are equal or value is None, returns True if so'''
    return (value == compared) | (value == None)

def remove_zeros(number_string):
    while number_string[0] == '0':
        number_string = number_string[1:]
    return(number_string)

def get_DoB(date_of_birth_list):
    birth_day = int(remove_zeros(date_of_birth_list[1]))
    birth_month = int(remove_zeros(date_of_birth_list[0]))
    birth_year = int(date_of_birth_list[2])
    return date(birth_year, birth_month, birth_day)

def get_age(date_of_birth_list):
    date_of_birth = get_DoB(date_of_birth_list)
    date_today = date.today()
    difference_in_days = str(date_today - date_of_birth)
    difference_in_days = int(difference_in_days.split(' ')[0])
    difference_in_years = int(difference_in_days//365.25)
    
    return str(difference_in_years), date_of_birth

def get_gender(user_input):
    if user_input != 'M' and user_input != 'F':
        user_input = None
    return user_input

def find_death_date(date_of_birth, death_age):
    death_age_in_days = int(death_age*365.25)
    earliest_date_of_death = date_of_birth + timedelta(days = death_age_in_days)
    
    extra_days = random.randint(0,364)
    date_of_death = earliest_date_of_death + timedelta(days = extra_days)
    return date_of_death

def generate_seed(name, date_of_birth):
    inputs_string = name
    seed_string = ''
    seed_string2 = ''
    prev = 18.3
    for character in name:
        ascii_value = ord(character)
        rand_value = str(int(ascii_value * prev))
        prev = ascii_value
        seed_string += rand_value
    for character in str(date_of_birth):
        ascii_value = ord(character)
        rand_value = str(int(ascii_value * prev))
        prev = ascii_value
        seed_string2 += rand_value
    seed = int(seed_string)-int(seed_string2[:len(seed_string)-1])
    return seed

def set_seed(seed):
    random.seed(seed)

def reformat_date(date):
    listed = str(date).split('-')
    base = "{}/{}/{}"
    reformated = base.format(listed[1],listed[2],listed[0])
    return reformated


if __name__ == "__main__":
    name = input("Full Name:")
    state = input("State of Residence:")
    birthday = input("date of birth (XX/XX/XXXX):")
    gender = input("Gender (M/F/other):")
    
    gender = get_gender(gender)
    age, date_of_birth = get_age(str(birthday).split('/'))
    random_seed = generate_seed(name,date_of_birth)
    set_seed(random_seed)
    search_info = SearchArgs(state, age, gender, None)
    data = initialize_data("data.csv")
    misc_data = initialize_data("all_states_misc.csv")
    relevant_data, total_relevant_deaths = find_relevant_lines(data, search_info)

    stalled = True
    cause_of = None
    date_of = None
    age_at = None
    while stalled:
        death_line = find_death_circumstances(relevant_data, total_relevant_deaths)
        
        death_date = find_death_date(date_of_birth, int(death_line[1]))
        difference = str(death_date - date.today())
        days_diff = int(difference.split(' ')[0])
        
        if days_diff > 0:
            stalled = False
            cause_of = death_line[3]

            age_at = death_line[1]
            date_of = death_date
        else:
            random_seed+=1
            set_seed(random_seed)
    
    if cause_of == "Miscellaneous" or cause_of == "Other ill-defined and unspecified causes of mortality":
        codes_list = get_codes_list(relevant_data, age_at)
        search_info_misc = SearchArgs(None, age_at, gender, None)
        relevant_misc_lines, misc_deaths = find_relevant_misc_lines(misc_data, search_info_misc, codes_list)
        misc_line = find_death_circumstances(relevant_misc_lines, misc_deaths)
        message_base = "Date: {} | ({}) {} (at age {})"
        message = message_base.format(reformat_date(date_of),cause_of, misc_line[3],age_at)
    else:
        message_base = "Date: {} | {} (at age {})"
        message = message_base.format(reformat_date(date_of),cause_of,age_at)
    
    print("\n\n\n" + message + "\n")




