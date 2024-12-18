import random    
from win10toast import ToastNotifier  

def main():  
    # Define the activities and days    
    exercise = ['climb'
                'hike',
                'paddle board',
                'rock climb',
                'run',
                'stretch',
                'walk',
                ]  
    
    chore = ['do laundry', 
            'dust',
            'garden', 
            'grocery shop', 
            'mop',
            'mow the lawn', 
            'scoop the litter', 
            'trim cat nails',
            'vacuum',
            'wash car',
            'water plants',
            ]  
    
    leisure = ['call a family', 
            'call a friend', 
            'code',
            'journal', 
            'listen to music/podcast',
            'nap', 
            'play Xbox', 
            'practice a foreign language of choice', 
            'read a book', 
            'speed cube', 
            'watch a movie', 
            'watch a tv show']  


    activities = exercise + chore + leisure  # a combo of 1 exercise item , 2 chore items, 2 leisure items 
    print(activities)    

    day = ['Friday', 'Saturday', 'Sunday']    

    # Generate the activities for each day    
    itinerary = ''    
    for d in day:  
        itinerary += f"{d}:\n"  
        selected_activities = [random.choice(exercise)]  
        selected_activities += random.sample(chore, k=2)  
        selected_activities += random.sample(leisure, k=2)  
        for a in selected_activities:  
            itinerary += f"- {a}\n"  
        itinerary += '\n'  

    print(itinerary)    

    toaster = ToastNotifier()  
    toaster.show_toast("Your weekend itinerary", itinerary, duration=20)  

if __name__ == '__main__':    
    main()    
