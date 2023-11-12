import pandas as pd    
import random    
import datetime  

def main():      
    # Define the meals and days        
    meal_option = ['Fruit smoothie',    
                'Gyeran',    
                'Japchae',    
                'Kimchi fried rice',    
                'Kimbap bowl',    
                'No name stir fry',    
                'Omurice',    
                'Pajun',    
                'Pad woon sen',    
                'Ramen',    
                'Tilapia & baked vegetables',    
                'Tofu jorim, rice & seaweed']      
    
    day = ['Monday',     
        'Tuesday',    
        'Wednesday',    
        'Thursday',    
        'Friday',    
        'Saturday',    
        'Sunday']    
    
    # Generate the meals for each day        
    meal_dict = {}        
    for d in day:      
        selected_meals = [random.choice(meal_option)]      
        meal_dict[d] = selected_meals    
        
    # Convert the dictionary to a pandas DataFrame and save it to a CSV file    
    meal_df = pd.DataFrame.from_dict(meal_dict, orient='index', columns=['Meal'])    
    meal_df.index.name = 'Day'    
    meal_df = meal_df.T # transposing the df to show days of the week as column headers  
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")  
    folder = r"C:\Users\ckraftbot\Downloads\Meals"  
    filename = f"{folder}\meal_plan_{timestamp}.csv"  
    meal_df.to_csv(filename)    
    
    print('Meal plan is exported.')
    #print(meal_df)     

if __name__ == "__main__":    
    main()     