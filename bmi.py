
def calc_bmi_metric(weight, height):
        return (weight)/(height ** 2)

def calc_bmi_usa(weight, height):
        return (weight)/(height ** 2)*703


selection = input('Welcome to BMI calculator, select "1" for US or "2" for metric ')

while True:

    if selection == '1':

        pounds = float(input('What is your weight in pounds? '))
        inches = float(input('What is your height in inches? '))

        print('Your BMI is ' + str(round(calc_bmi_usa(pounds, inches),2)))
        break

    elif selection == '2':

        kilos = float(input('What is your weight in kilos? '))
        meters = float(input('What is your height in meters? '))

        print('Your BMI is ' + str(round(calc_bmi_metric(kilos, meters),2)))
        break

    else:
        selection = input('Please enter a correct selection ')
        pass
